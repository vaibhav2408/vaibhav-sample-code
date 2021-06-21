from elasticsearch import exceptions
from elasticsearch_dsl import Q, Search
from structlog import get_logger

from app.core.config import settings
from app.core.exception_handler.audit_trail_base_exception import (
    AuditTrailBaseException,
)
from app.data_access_layer import es_conn
from app.data_access_layer.elasticsearch import (
    elasticsearch_query_builder,
    elasticsearch_util,
)
from app.data_access_layer.utils.abstract_db_handler import AbstractDBHandler
from app.resources import constants
from app.utils.common_utils import get_epoch_millis

logger = get_logger()

current_index = ""

ES_INDEX_SHARDS_DEFAULT = 3
ES_INDEX_REPLICAS_DEFAULT = 1

AUDIT_TRAIL_ALIAS = "audit_trail_alias"

# Error messages
INDEX_NOT_FOUND_MESSAGE = "Index not found in the elasticsearch database"
QUERYING_FAILURE_MESSAGE = "Exception while fetching audit records from Elasticsearch"


class ElasticsearchDAL(AbstractDBHandler):
    """
    Data access layer for the audit-trail Elasticsearch.

    This Class contains basic Write/Read operations on documents.
    It has functions to add a new audit-trail document and
    fetch audit-trail document(s) based on the search parameters
    """

    AUDIT_TRAIL_INDEX_NAME = "audit_trail_{}"
    INTERNAL_SERVER_ERROR_MESSAGE = "Internal server error."

    def add_audit_records(self, data: dict, execution_context: dict):
        """
        Method to index an audit-trail entry to the elasticsearch
        Args:
            data: the data to be indexed into the ES
            execution_context: additional information required for indexing the data
        Returns:
            returns boolean based on the indexing result. True- success, False- Failure
        """
        try:
            index_name = elasticsearch_util.get_index()
            logger.info(
                "Inserting entry into the elasticsearch",
                index=index_name,
                elasticsearch_status=settings.elasticsearch_init_complete,
            )

            created_at = get_epoch_millis()
            data[constants.CREATED_AT_KEY] = created_at

            # TODO doc type hardcoded for COP, this should be handled properly.
            if settings.is_cop:
                res = es_conn.index(index=index_name, doc_type="audit_trail", body=data)
            else:
                res = es_conn.index(index=index_name, body=data)
            logger.info(
                "Done writing data to elasticsearch",
                index=index_name,
                audit_id=res["_id"],
                result=res,
            )
            return True, res["_id"]
        except exceptions.NotFoundError as nfe:
            logger.exception(
                INDEX_NOT_FOUND_MESSAGE,
                index_alias=AUDIT_TRAIL_ALIAS,
                exception=str(nfe),
            )
            raise AuditTrailBaseException(
                500, detail=self.INTERNAL_SERVER_ERROR_MESSAGE
            )
        except exceptions.SerializationError as se:
            logger.exception(
                f"Failed to index the document.", data=data, exception=str(se)
            )
            raise AuditTrailBaseException(
                500, detail=self.INTERNAL_SERVER_ERROR_MESSAGE
            )
        except exceptions.TransportError as te:
            logger.exception(
                f"Failed to index the document.", data=data, exception=str(te)
            )
            raise AuditTrailBaseException(
                500, detail=self.INTERNAL_SERVER_ERROR_MESSAGE
            )
        except AuditTrailBaseException as ae:
            logger.exception(
                f"Failed to index the document.", data=data, exception=str(ae)
            )
            raise AuditTrailBaseException(
                500, detail=self.INTERNAL_SERVER_ERROR_MESSAGE
            )

    def get_audit_records(self, data: dict, execution_context: dict):
        """
        Method to get audit-trail entries from the elasticsearch index
        Args:
            data: the data to be indexed into the ES
            execution_context: additional information required for reading the data
        Returns:
            returns the response & the count of audit-logs in the response
        """
        try:
            customer_id = data[constants.CUSTOMER_ID_KEY]
            logger.debug(
                "Performing audit-logs search",
                customer_id=customer_id,
                search_params=data,
            )

            limit = (
                int(data[constants.LIMIT_KEY])
                if constants.LIMIT_KEY in data
                else constants.DEFAULT_UI_LIMIT
            )
            offset = (
                int(data[constants.OFFSET_KEY])
                if constants.OFFSET_KEY in data
                else constants.DEFAULT_OFFSET
            )

            audit_query = elasticsearch_query_builder.get_search_query(
                search_params=data, execution_context=execution_context,
            )
            logger.info("Done building the ES search query", audit_query=audit_query)
            sort = data.pop("sort", None)

            index = AUDIT_TRAIL_ALIAS
            s = Search(index=index).query(audit_query)
            sort = sort.lstrip("+") if sort else "-created_at"
            s = s.sort(sort)
            s = s[offset : (offset + limit)]
            resp = s.execute()
            count = resp.hits.total

            # ES version handle v 5.xx and v7.xx
            if isinstance(count, int):
                return resp, count
            return resp, count["value"]

        except exceptions.NotFoundError as nfe:
            logger.exception(
                INDEX_NOT_FOUND_MESSAGE,
                index_alias=AUDIT_TRAIL_ALIAS,
                exception=str(nfe),
            )
            return None, None
        except exceptions.SerializationError as se:
            logger.exception(QUERYING_FAILURE_MESSAGE, data=data, exception=str(se))
            raise AuditTrailBaseException(
                500, detail=self.INTERNAL_SERVER_ERROR_MESSAGE
            )
        except exceptions.TransportError as te:
            logger.exception(QUERYING_FAILURE_MESSAGE, data=data, exception=str(te))
            raise AuditTrailBaseException(
                500, detail=self.INTERNAL_SERVER_ERROR_MESSAGE
            )
        except AuditTrailBaseException as ae:
            logger.exception(
                QUERYING_FAILURE_MESSAGE, exception=str(ae),
            )
            raise AuditTrailBaseException(500, self.INTERNAL_SERVER_ERROR_MESSAGE)
        except Exception as e:
            logger.exception(
                QUERYING_FAILURE_MESSAGE, exception=str(e),
            )
            raise AuditTrailBaseException(500, self.INTERNAL_SERVER_ERROR_MESSAGE)

    def get_audit_trail_details(self, index, audit_id):
        """
        Method to get audit-trail detail of a given document
        Args:
            index: ES index
            audit_id: the document id in the ES
        Returns:
            returns the audit-trail details
        """
        try:
            q = Q("bool", must=[Q("match", _id=audit_id)])
            s = Search(index=index).query(q)
            s = s.source(includes=[constants.AUDIT_DETAILS_KEY])
            resp = s.execute()

            result = dict()
            for item in resp.hits.hits:
                result["header"] = (
                    item["_source"][constants.AUDIT_DETAILS_KEY]["header"]
                    if item["_source"][constants.AUDIT_DETAILS_KEY]
                    else None
                )
                result["body"] = (
                    item["_source"][constants.AUDIT_DETAILS_KEY]["body"]
                    if item["_source"][constants.AUDIT_DETAILS_KEY]
                    else None
                )
            return result
        except exceptions.NotFoundError as nfe:
            logger.exception(
                INDEX_NOT_FOUND_MESSAGE,
                index=index,
                audit_id=audit_id,
                exception=str(nfe),
            )
            return None
        except exceptions.SerializationError as se:
            logger.exception(
                QUERYING_FAILURE_MESSAGE,
                index=index,
                audit_id=audit_id,
                exception=str(se),
            )
            raise AuditTrailBaseException(
                500, detail=self.INTERNAL_SERVER_ERROR_MESSAGE
            )
        except exceptions.TransportError as te:
            logger.exception(
                QUERYING_FAILURE_MESSAGE,
                index=index,
                audit_id=audit_id,
                exception=str(te),
            )
            raise AuditTrailBaseException(
                500, detail=self.INTERNAL_SERVER_ERROR_MESSAGE
            )
        except AuditTrailBaseException as e:
            logger.exception(
                QUERYING_FAILURE_MESSAGE,
                index=index,
                audit_id=audit_id,
                exception=str(e),
            )
            raise AuditTrailBaseException(500, self.INTERNAL_SERVER_ERROR_MESSAGE)
        except Exception as e:
            logger.exception(
                QUERYING_FAILURE_MESSAGE, index=index, audit_id=audit_id, error=str(e),
            )
            raise AuditTrailBaseException(500, self.INTERNAL_SERVER_ERROR_MESSAGE)

    def get_audit_count(self, data, execution_context):
        """
        Method to get the total number of audit-entries in the ES after a given time
        Args:
            data: the ES query params
            execution_context: additional data required for the operation
        Returns:
            the total number of audit entries
        """
        try:
            logger.info(
                "Fetching the number of documents in the index", index=AUDIT_TRAIL_ALIAS
            )
            es_conn.indices.refresh(AUDIT_TRAIL_ALIAS)
            audit_query = elasticsearch_query_builder.get_search_query(
                search_params=data, execution_context=execution_context,
            )
            logger.info("Done building the ES search query", audit_query=audit_query)
            index = AUDIT_TRAIL_ALIAS
            s = Search(index=index).query(audit_query)
            number_of_audits = s.count()
            return number_of_audits
        except exceptions.NotFoundError as nfe:
            logger.exception(
                INDEX_NOT_FOUND_MESSAGE,
                index_alias=AUDIT_TRAIL_ALIAS,
                exception=str(nfe),
            )
            return None
        except exceptions.SerializationError as se:
            logger.exception(
                QUERYING_FAILURE_MESSAGE, exception=str(se),
            )
            raise AuditTrailBaseException(500, self.INTERNAL_SERVER_ERROR_MESSAGE)
        except exceptions.TransportError as te:
            logger.exception(
                QUERYING_FAILURE_MESSAGE, exception=str(te),
            )
            raise AuditTrailBaseException(500, self.INTERNAL_SERVER_ERROR_MESSAGE)
        except AuditTrailBaseException as e:
            logger.exception(
                QUERYING_FAILURE_MESSAGE, exception=str(e),
            )
            raise AuditTrailBaseException(500, self.INTERNAL_SERVER_ERROR_MESSAGE)
        except Exception as e:
            logger.exception(
                QUERYING_FAILURE_MESSAGE, exception=str(e),
            )
            raise AuditTrailBaseException(500, self.INTERNAL_SERVER_ERROR_MESSAGE)

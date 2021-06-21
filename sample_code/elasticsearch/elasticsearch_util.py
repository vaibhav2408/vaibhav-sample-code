from datetime import datetime

from elasticsearch_dsl import Index
from structlog import get_logger

from app.core.exception_handler.audit_trail_base_exception import (
    AuditTrailBaseException,
)
from app.data_access_layer.elasticsearch.elasticsearch_constants import (
    ADDITIONAL_INFO_KEY,
    AUDIT_INFO_KEY,
    AUDIT_TRAIL_ALIAS,
    AUDIT_TRAIL_EXCLUDE_PARAMS,
    AUDIT_TRAIL_FIXED_FIELDS_PARENT_MAPPING,
    AUDIT_TRAIL_INDEX_NAME,
    ES_INDEX_REFRESH_INTERVAL_DEFAULT,
    ES_INDEX_REPLICAS_DEFAULT,
    ES_INDEX_SHARDS_DEFAULT,
    ES_MATCH_KEY,
    ES_QUERY_STRING_KEY,
    ES_RANGE_KEY,
    ES_REFRESH_INTERVAL,
    ES_REGEXP_KEY,
    KEY_OVERRIDE_WITH,
    NO_OF_RETENTION_DAYS,
    PARENT_KEY,
    THIRTY_DAYS,
)
from app.resources.constants import (
    ES_QUERY_PARAMS_KEY,
    EXACT_MATCH_KEY,
    MATCH_CRITERIA_KEY,
    PARTIAL_MATCH_KEY,
    QUERY_BY_KEY,
    RANGE_MATCH__KEY,
    REG_EX_MATCH_KEY,
    UNIVERSAL_SEARCH_KEY,
)

logger = get_logger()

current_index = ""


def get_index():
    """
    Method to get the index-name
    Returns:
        returns the ES index-name
    """
    index_name = _get_current_index(AUDIT_TRAIL_INDEX_NAME)
    if not is_index_created(index_name):
        create_index(index_name)
    return index_name


def is_index_created(index):
    """
    Method to check if the given index exists or not
    Args:
        index: the index value
    Returns:
        returns True if true else False
    """
    try:
        global current_index
        if not current_index:
            ind = Index(index)
            if ind.exists():
                current_index = index
        return index == current_index
    except AuditTrailBaseException as ex:
        logger.exception(
            "Exception while creating ES index", index=index, exception=str(ex)
        )
        raise AuditTrailBaseException(
            500, f"Exception while creating ES index: {index}"
        )


def create_index(index_name):
    """
    Method to create an index in ES
    Args:
        index_name: the name of the index to be created
    """
    global current_index
    create_index_with_properties(
        index_name, AUDIT_TRAIL_ALIAS, refresh_interval=ES_REFRESH_INTERVAL
    )
    current_index = index_name


def create_index_with_properties(
    name,
    alias,
    num_shards=ES_INDEX_SHARDS_DEFAULT,
    num_replicas=ES_INDEX_REPLICAS_DEFAULT,
    refresh_interval=ES_INDEX_REFRESH_INTERVAL_DEFAULT,
    analyzer_dict=None,
):
    """
    Method to create an index in with pre-defined properties
    Args:
        name: index name
        alias: the alias to be used for the index
        num_shards: number of shards
        num_replicas: number of replicas
        refresh_interval: refresh intervals
        analyzer_dict: ES analyzer
    """
    try:
        index = Index(name)

        """ Check if the index already exists. If it does, do nothing"""
        if index.exists():
            logger.info("Index {} already exists, can't create it".format(name))
            return
        settings_dict = dict(
            number_of_shards=num_shards,
            number_of_replicas=num_replicas,
            refresh_interval=refresh_interval,
        )
        if analyzer_dict:
            settings_dict["analysis"] = analyzer_dict
        """ Index doesn't exist. Set properties and create one """
        index.settings(**settings_dict)
        if alias:
            alias_kwargs = {alias: {}}
            index.aliases(**alias_kwargs)

        """ Create the index """
        index.create()
        logger.info("Created index {} in ElasticSearch".format(name))
    except AuditTrailBaseException as ex:
        logger.exception(f"Failed to create index {name}", exception=str(ex))
        raise AuditTrailBaseException(500, f"Failed to create index {name}")


def build_and_add_es_params(search_params: dict, params_meta_data: dict):
    """
    Method to build the search params for Elasticsearch search query
    Args:
        search_params: the search params received in the API request
        params_meta_data: the meta data of each field in the search_params
    """
    default_prefix = f"{AUDIT_INFO_KEY}.{ADDITIONAL_INFO_KEY}."
    es_search_params = dict()  # type: ignore
    for field, value in search_params.items():
        if field in AUDIT_TRAIL_EXCLUDE_PARAMS:
            continue
        final_field_name = _get_override_field_name(
            field, AUDIT_TRAIL_FIXED_FIELDS_PARENT_MAPPING
        )
        if (
            field in AUDIT_TRAIL_FIXED_FIELDS_PARENT_MAPPING
            and AUDIT_TRAIL_FIXED_FIELDS_PARENT_MAPPING.get(field).get(PARENT_KEY)
            is None
        ):
            # block for fields which are at the same level as audit-info
            query_by_value = _get_query_by(field, params_meta_data)
            es_search_params[final_field_name] = {
                "value": value,
                QUERY_BY_KEY: query_by_value,
            }
        elif (
            field in AUDIT_TRAIL_FIXED_FIELDS_PARENT_MAPPING
            and AUDIT_TRAIL_FIXED_FIELDS_PARENT_MAPPING.get(field).get(PARENT_KEY)
            is not None
        ):
            # block for fields which are inside the audit-info dict
            query_by_value = _get_query_by(field, params_meta_data)
            prefix = (
                AUDIT_TRAIL_FIXED_FIELDS_PARENT_MAPPING.get(field).get(PARENT_KEY) + "."
            )
            es_search_params[prefix + final_field_name] = {
                "value": value,
                QUERY_BY_KEY: query_by_value,
            }
        else:
            # block for fields which are inside the additional-info dict (which is inside the audit-info dict)
            query_by_value = _get_query_by(field, params_meta_data)
            es_search_params[default_prefix + final_field_name] = {
                "value": value,
                QUERY_BY_KEY: query_by_value,
            }
    search_params[ES_QUERY_PARAMS_KEY] = es_search_params


def _get_current_index(index_name_placeholder: str):
    """
    Returns the current index as per the syntax defined
    Args:
        index_name_placeholder: index name string format
    Returns:
        formatted index name
    """
    if NO_OF_RETENTION_DAYS == THIRTY_DAYS:
        index_suffix = _get_day_month_of_year(datetime.now())
    else:
        index_suffix = _get_month_of_year(datetime.now())
    return index_name_placeholder.format(index_suffix)


def _get_day_month_of_year(date):
    """
    Method to get the <Year>_<Month>_<Date> string corresponding to given date
    Args:
        date: date object
    Returns:
        formatted data string
    """
    year = int(date.strftime("%Y"))
    month = int(date.strftime("%m"))
    date = int(date.strftime("%d"))
    return "{}_{}_{}".format(year, month, date)


def _get_month_of_year(date):
    """
    Method to get the <Month>_<Date> string corresponding to given date
    Args:
        date: date object
    Returns:
        formatted data string
    """
    year = int(date.strftime("%Y"))
    month_of_year = int(date.strftime("%m"))
    return "{}_{}".format(year, month_of_year)


def _get_query_by(field: str, params_meta_data: dict):
    """
    Method to get the ES Query keyword associated with exact_match/partial_match match
    """
    if field not in params_meta_data:
        return ES_MATCH_KEY
    query_keyword = params_meta_data.get(field).get(MATCH_CRITERIA_KEY)
    if query_keyword is None:
        return ES_MATCH_KEY
    elif query_keyword == EXACT_MATCH_KEY:
        return ES_MATCH_KEY
    elif query_keyword == PARTIAL_MATCH_KEY or query_keyword == UNIVERSAL_SEARCH_KEY:
        return ES_QUERY_STRING_KEY
    elif query_keyword == REG_EX_MATCH_KEY:
        return ES_REGEXP_KEY
    elif query_keyword == RANGE_MATCH__KEY:
        return ES_RANGE_KEY
    else:
        return ES_MATCH_KEY


def _get_override_field_name(field, field_mapping):
    """
    Method to fetch the override field name for a given field from the mapping
    """
    if field in field_mapping and KEY_OVERRIDE_WITH in field_mapping.get(field):
        final_field_name = field_mapping.get(field).get(KEY_OVERRIDE_WITH)
    else:
        final_field_name = field
    return final_field_name

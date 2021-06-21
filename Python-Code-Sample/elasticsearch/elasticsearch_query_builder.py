from elasticsearch_dsl import Q
from structlog import get_logger

from app.core.audit_management import audit_role_manager
from app.core.exception_handler.audit_trail_base_exception import (
    AuditTrailBaseException,
)
from app.data_access_layer.elasticsearch.elasticsearch_constants import (
    ADDITIONAL_INFO_KEY,
    APP_SLUG_KEY,
    CUSTOMER_ID_KEY,
    END_TIME_KEY,
    ES_QUERY_STRING_KEY,
    ES_RANGE_KEY,
    ES_REGEXP_KEY,
    ES_SIMPLE_QUERY_STRING_KEY,
    LIMIT_KEY,
    OFFSET_KEY,
    START_TIME_KEY,
    STRICT_MATCHING_FIELDS,
)
from app.resources.constants import (
    AUDIT_INFO_KEY,
    CCS_INTERNAL_ID,
    CUSTOMER_NAME_KEY,
    ES_QUERY_PARAMS_KEY,
    MAX_AUDIT_TIME_LIMIT,
    MSP_ID_KEY,
    QUERY_BY_KEY,
    TENANT_NAME_KEY,
)
from app.utils.common_utils import (
    custom_special_char_check,
    get_epoch_millis,
    string_unquote,
)

logger = get_logger()


def get_search_query(search_params, execution_context):
    """
    Returns the ES query based on the given search params
    Args:
        search_params: the search params
        execution_context: operation related any additional info
    Returns:
        returns the final query object
    """
    try:
        return _build_es_search_query(search_params, execution_context)
    except AuditTrailBaseException as ex:
        logger.exception("Failed to search for audit trail.", exception=str(ex))
        raise AuditTrailBaseException(500, "Failed to search for audit trail.")


def _build_es_search_query(search_params, execution_context):
    """
    Method to build the search query for the fields mentioned in the input argument
    Args:
          search_params: the fields which need to be searched for in the ES and against what value
    Returns:
        returns a query ES query object
    """
    es_query = {}
    es_search_params = search_params.get(ES_QUERY_PARAMS_KEY)

    primary_query, es_processed_fields = _get_primary_search_query(
        search_params=search_params
    )

    for field, es_meta in es_search_params.items():
        if es_processed_fields and es_processed_fields.get(field):
            continue
        value = es_meta.get("value")
        field_query_by = es_meta.get(QUERY_BY_KEY)
        if value and field not in [
            START_TIME_KEY,
            END_TIME_KEY,
            LIMIT_KEY,
            OFFSET_KEY,
        ]:
            es_processed_fields[field] = True
            value, has_custom_special_character = custom_special_char_check(value)
            if _is_valid_for_simple_query_string(
                field, value, has_custom_special_character
            ):
                query_by, query_for = _get_es_simple_query_string(field, value)
            else:
                query_by, query_for = _get_query(field, value, field_query_by)
            q2 = Q({query_by: query_for})
            es_query = es_query & q2 if es_query else q2

    if execution_context.get(START_TIME_KEY):
        es_query = _get_start_time_range_query(execution_context, es_query)
    else:
        es_query = _get_end_time_range_query(execution_context, es_query)

    if primary_query:
        if es_query:
            query = Q(
                "bool", should=primary_query, must=[es_query], minimum_should_match=1
            )
        else:
            query = Q("bool", should=primary_query, minimum_should_match=1)
    else:
        query = Q("bool", must=[es_query])
    return query


def _get_primary_search_query(search_params):
    """
    Method to build a custom query for a few fields
    those cannot be made generic.
    Args:
        search_params:
    Returns:
        custom ES search query
    """
    primary_query = []
    # Map to maintain the fields which are added to the ES query, to avoid duplicates
    es_processed_fields = {}  # type: ignore

    if search_params.get(audit_role_manager.ALLOW_ADMIN_LEVEL_LOGS_KEY):
        query_for = {"default_field": CUSTOMER_ID_KEY, "query": "*"}
        primary_query = [Q({ES_QUERY_STRING_KEY: query_for})]

        _mark_fields_as_processed(
            es_processed_fields, CUSTOMER_ID_KEY,
        )
        return primary_query, es_processed_fields

    if search_params.get(MSP_ID_KEY):
        primary_query = [
            Q(
                "match",
                audit_info__additional_info__msp_id=search_params.get(MSP_ID_KEY),
            ),
            Q("match", customer_id=search_params.get(CUSTOMER_ID_KEY)),
        ]
        _mark_fields_as_processed(
            es_processed_fields,
            CUSTOMER_ID_KEY,
            f"{AUDIT_INFO_KEY}.{ADDITIONAL_INFO_KEY}.{MSP_ID_KEY}",
        )

    if not primary_query:
        primary_query = [
            Q("match", customer_id=search_params.get(CUSTOMER_ID_KEY)),
        ]
        _mark_fields_as_processed(
            es_processed_fields, CUSTOMER_ID_KEY,
        )

    if search_params.get(audit_role_manager.ALLOW_INTERNAL_AUDIT_LOGS_KEY):
        primary_query.append(Q("match", customer_id=CCS_INTERNAL_ID))
        _mark_fields_as_processed(es_processed_fields,)

    if search_params.get(TENANT_NAME_KEY):

        query_by, query_for = _get_query(
            f"{AUDIT_INFO_KEY}.{CUSTOMER_NAME_KEY}",
            search_params.get(TENANT_NAME_KEY),
            ES_QUERY_STRING_KEY,
        )

        query = Q({query_by: query_for})

        if search_params.get(MSP_ID_KEY):
            primary_query = [
                query
                & Q(
                    "match",
                    audit_info__additional_info__msp_id=search_params.get(MSP_ID_KEY),
                )
            ]
        else:
            primary_query = [query]

        if search_params.get(CUSTOMER_NAME_KEY):
            query_by, query_for = _get_query(
                f"{AUDIT_INFO_KEY}.{CUSTOMER_NAME_KEY}",
                search_params.get(CUSTOMER_NAME_KEY),
                ES_QUERY_STRING_KEY,
            )
            primary_query.append(Q({query_by: query_for}))

        _mark_fields_as_processed(
            es_processed_fields,
            CUSTOMER_ID_KEY,
            f"{AUDIT_INFO_KEY}.{CUSTOMER_NAME_KEY}",
            f"{AUDIT_INFO_KEY}.{ADDITIONAL_INFO_KEY}.{TENANT_NAME_KEY}",
            f"{AUDIT_INFO_KEY}.{ADDITIONAL_INFO_KEY}.{MSP_ID_KEY}",
        )

    return primary_query, es_processed_fields


def _get_es_simple_query_string(field, value):
    f"""
    Method to get elasticsearch query using 'query_string'.
    Args:
        field: the field on which the query is to be performed
        value: the value which needs to be queried
    Returns:
        query_by, query_for dict
    """
    default_operator = _get_default_operator(field)
    if not isinstance(value, list):
        value = string_unquote(value).split(" ")
        query = f" {default_operator.upper()} ".join(value)
    else:
        query = f" {default_operator.upper()} ".join(set(value))

    query_by = "simple_query_string"
    query_for = {
        "query": query,
        "fields": [field],
        "default_operator": default_operator,
    }
    return query_by, query_for


def _get_query(field, value, field_query_by):
    """
    Method to get elasticsearch query using the given query keyword
    Args:
        field: the field on which the query is to be performed
        value: the value which needs to be queried
        field_query_by: the ES query by keyword
    Returns:
        query_by, query_for dict
    """
    value = string_unquote(value)
    query_by = ES_QUERY_STRING_KEY if field_query_by is None else field_query_by
    if query_by == ES_QUERY_STRING_KEY:
        if isinstance(value, list):
            default_operator = _get_default_operator(field)
            value = f" {default_operator.upper()} ".join(
                f"*{string_unquote(entry.lower())}*" for entry in value
            )
        else:
            value = f"*{value.lower()}*"
        query_for = {"default_field": field, "query": value}
    elif query_by == ES_REGEXP_KEY:
        query_for = {field: ".*" + value.lower() + ".*"}
    elif query_by == ES_RANGE_KEY:
        query_for = {field: {"gte": value}}
    elif query_by == ES_SIMPLE_QUERY_STRING_KEY:
        query_by, query_for = _get_es_simple_query_string(field, value)
    else:
        query_for = {field: value}
    return query_by, query_for


def _get_start_time_range_query(execution_context, es_query):
    """
    Method to get elasticsearch range query using the start-time key
    Args:
        es_query: the main elastic query object
    Returns:
        the merged elasticsearch query
    """
    execution_context[END_TIME_KEY] = (
        int(execution_context.get(END_TIME_KEY))
        if execution_context.get(END_TIME_KEY)
        else get_epoch_millis()
    )
    if (
        int(execution_context.get(END_TIME_KEY))
        - int(execution_context.get(START_TIME_KEY))
    ) > MAX_AUDIT_TIME_LIMIT:
        execution_context[START_TIME_KEY] = (
            execution_context.get(END_TIME_KEY) - MAX_AUDIT_TIME_LIMIT
        )
    range_query = Q(
        ES_RANGE_KEY,
        audit_info__audit_created_at={
            "gte": execution_context.get(START_TIME_KEY),
            "lte": execution_context.get(END_TIME_KEY),
        },
    )
    return es_query & range_query if es_query else range_query


def _get_end_time_range_query(execution_context, es_query):
    """
    Method to get elasticsearch range query using the end-time key
    Args:
        es_query: the main elastic query object
    Returns:
        the merged elasticsearch query
    """
    execution_context[END_TIME_KEY] = (
        int(execution_context.get(END_TIME_KEY))
        if execution_context.get(END_TIME_KEY)
        else get_epoch_millis()
    )
    execution_context[START_TIME_KEY] = (
        execution_context[END_TIME_KEY] - MAX_AUDIT_TIME_LIMIT
    )
    range_query = Q(
        ES_RANGE_KEY,
        audit_info__audit_created_at={
            "gte": execution_context.get(START_TIME_KEY),
            "lte": execution_context.get(END_TIME_KEY),
        },
    )
    return es_query & range_query if es_query else range_query


def _get_default_operator(field):
    """
    Method to get the default operator for the simple-query-string search
    """
    if field == APP_SLUG_KEY:
        return "or"
    else:
        return "or" if field not in STRICT_MATCHING_FIELDS else "and"


def _is_valid_for_simple_query_string(
    field, value, has_custom_special_character
) -> bool:
    """
    Checks if a given value is eligible for query string or not
    Args:
        field:
        value:
        has_custom_special_character:
    Returns:
        True if eligible else False
    """
    if field != "*" and (
        isinstance(value, list)
        or ((isinstance(value, str) and " " in value) or has_custom_special_character)
    ):
        logger.debug(f"Field {field} is eligible for simple string query search.")
        return True
    else:
        return False


def _mark_fields_as_processed(dictionary, *args):
    """
    Method to set given keys to true in the dict
    Args:
        dictionary
        args
    """
    for arg in args:
        dictionary[arg] = True

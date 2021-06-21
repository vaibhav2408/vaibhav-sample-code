"""
All constants used by ES dal for performing search/indexing operations.
"""
from app.core.audit_management import audit_role_manager
from app.resources.constants import (
    ADDITIONAL_INFO_KEY,
    ALL_FIELDS_SEARCH_KEY,
    APP_ID_KEY,
    APP_INSTANCE_ID_KEY,
    APP_SLUG_KEY,
    AUDIT_CREATED_AT_KEY,
    AUDIT_INFO_KEY,
    CATEGORY_KEY,
    CUSTOMER_ID_KEY,
    CUSTOMER_NAME_KEY,
    DESCRIPTION_KEY,
    END_TIME_KEY,
    KEY_OVERRIDE_WITH,
    LIMIT_KEY,
    OFFSET_KEY,
    PARENT_KEY,
    START_TIME_KEY,
    USERNAME_KEY,
)

AUDIT_TRAIL_ALIAS = "audit_trail_alias"
ES_INDEX_SHARDS_DEFAULT = 3
ES_INDEX_REPLICAS_DEFAULT = 1
ES_INDEX_REFRESH_INTERVAL_DEFAULT = "300s"
AUDIT_TRAIL_INDEX_NAME = "audit_trail_{}"

# TODO: confirm on the retention period
NO_OF_RETENTION_DAYS = 365
THIRTY_DAYS = 30
ES_REFRESH_INTERVAL = "30s"

ES_RANGE_KEY = "range"
ES_REGEXP_KEY = "regexp"
ES_MATCH_KEY = "match"
ES_TERM_KEY = "term"
ES_SIMPLE_QUERY_STRING_KEY = "simple_query_string"
ES_QUERY_STRING_KEY = "query_string"

"""
This is a map holding all the keys with their parent (if any) & the override name (if any)
syntax- "field name" : {"parent": "parent_key", "key_override_with" : "value"(default: None)}
Example-
  1. "app_instance_id": {"parent": None}
  2. "audit_details": {"parent": None}
"""
AUDIT_TRAIL_FIXED_FIELDS_PARENT_MAPPING = {
    APP_INSTANCE_ID_KEY: {PARENT_KEY: None},
    CUSTOMER_ID_KEY: {PARENT_KEY: None},
    APP_SLUG_KEY: {PARENT_KEY: None},
    APP_ID_KEY: {PARENT_KEY: None},
    ALL_FIELDS_SEARCH_KEY: {PARENT_KEY: None, KEY_OVERRIDE_WITH: "*"},
    # Keys under the "audit_info" dict
    AUDIT_CREATED_AT_KEY: {PARENT_KEY: AUDIT_INFO_KEY},
    CATEGORY_KEY: {PARENT_KEY: AUDIT_INFO_KEY},
    CUSTOMER_NAME_KEY: {PARENT_KEY: AUDIT_INFO_KEY},
    DESCRIPTION_KEY: {PARENT_KEY: AUDIT_INFO_KEY},
    USERNAME_KEY: {PARENT_KEY: AUDIT_INFO_KEY},
    ADDITIONAL_INFO_KEY: {PARENT_KEY: AUDIT_INFO_KEY},
}

"""
The fields which require strict matching and may also 
contain any non-alphanumeric characters 
"""
STRICT_MATCHING_FIELDS = [
    APP_INSTANCE_ID_KEY,
    CUSTOMER_ID_KEY,
    APP_SLUG_KEY,
    APP_ID_KEY,
    f"{AUDIT_INFO_KEY}.{CUSTOMER_NAME_KEY}",
    f"{AUDIT_INFO_KEY}.{CATEGORY_KEY}",
]

# The fields on which the ES Search will not be performed
AUDIT_TRAIL_EXCLUDE_PARAMS = [
    OFFSET_KEY,
    LIMIT_KEY,
    START_TIME_KEY,
    END_TIME_KEY,
    AUDIT_CREATED_AT_KEY,
    audit_role_manager.ALLOW_ADMIN_LEVEL_LOGS_KEY,
    audit_role_manager.ALLOW_INTERNAL_AUDIT_LOGS_KEY,
]

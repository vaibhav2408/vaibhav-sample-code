"""
Manager class for audit-trail operations
"""
from typing import Any, Dict, List, Union

from fastapi.encoders import jsonable_encoder
from starlette import status
from structlog import get_logger

from app.api.client.account_management_client import (
    get_customer_details_from_cid,
    is_msp,
    is_msp_customer,
)
from app.api.client.app_catalog_client import (
    get_app_details_using_slug,
    get_app_instances_for_customer,
)
from app.core.audit_management import audit_role_manager
from app.core.exception_handler.audit_trail_base_exception import (
    AuditTrailBaseException,
)
from app.core.file_manager import constants, file_handler
from app.data_access_layer import backup_dal_instance
from app.data_access_layer.elasticsearch import elasticsearch_util
from app.data_access_layer.elasticsearch.elasticsearch_dal import ElasticsearchDAL
from app.models.audit.audit_payload import AuditPayload
from app.resources.constants import (
    ADDITIONAL_INFO_KEY,
    ALL_FIELDS_SEARCH_KEY,
    APP_ID_KEY,
    APP_INSTANCE_ID_KEY,
    APP_SLUG_KEY,
    AUDIT_CREATED_AT_KEY,
    AUDIT_DETAILS_KEY,
    AUDIT_ID_KEY,
    AUDIT_INFO_KEY,
    CATEGORY_KEY,
    CCS_INTERNAL_ID,
    CCS_INTERNAL_NAME,
    CUSTOMER_ID_KEY,
    CUSTOMER_NAME_KEY,
    DEVICE_TYPE_KEY,
    DEVICE_TYPES,
    END_TIME_KEY,
    HAS_DETAILS_KEY,
    INDEX_KEY,
    LIMIT_KEY,
    MAX_ES_DOC_LIMIT,
    MSP_ID_KEY,
    OFFSET_KEY,
    PARENT_KEY,
    START_TIME_KEY,
    TENANT_ID_KEY,
    TENANT_NAME_KEY,
    USERNAME_KEY,
)
from app.resources.enums.app_slug_enum import AppSlug
from app.resources.enums.file_extensions import FileExtensions
from app.utils.common_utils import (
    get_all_apps,
    get_categories_by_app_slug,
    get_epoch_millis,
    get_time_range,
    is_remaining_records,
    multiple_args_to_single_dict,
    pop_keys_from_dict,
    string_unquote,
    to_millis,
)

logger = get_logger()


def set_audit_trail(audit_payload: AuditPayload):
    """
    Sets the audit trail for a user
    Args:
        audit_payload: the message/event data payload
    Returns:
          True if audit-trail was set successfully for the user else False
    """

    audit_data = _build_audit_trail_data(audit_payload)
    return _insert_audit_trail_data(audit_data)


def get_audit_trail(search_params: dict, params_meta_data: dict, include_details=False):
    """
    Method to get the audit-trail using the given search params from the elasticsearch
    Args:
        search_params: the search params received from the user request
        params_meta_data: the meta data of each field in the search_params
        include_details: flag for whether to include audit-details in the response or not
    Returns:
        dict containing the fetched audit-info
    """

    customer_id = search_params.get(CUSTOMER_ID_KEY)
    app_slug = search_params.get(APP_SLUG_KEY)

    _get_customer_role(
        app_slug=app_slug, customer_id=customer_id, search_params=search_params
    )

    try:
        customer_apps = _get_customer_apps(customer_id, search_params.get(APP_SLUG_KEY))

        if not customer_apps:
            logger.error(
                f"No authorized applications found for the customer: {customer_id}"
            )
            raise AuditTrailBaseException(404, "No authorized applications found.")
        search_params[APP_SLUG_KEY] = customer_apps

        if CATEGORY_KEY in search_params:
            backend_compatible_category = _get_backend_compatible_category(
                app_slug, search_params.get(CATEGORY_KEY)
            )
            search_params[CATEGORY_KEY] = backend_compatible_category

        if ALL_FIELDS_SEARCH_KEY in search_params:
            """
            Checking if a category is passed in the universal search. If so, 
            we're converting it to backend compatible value for search.
            Converting the string to a list to enforce an OR operation on search.
            """
            try:
                logger.info(
                    "Checking if universal search text is a valid category or not."
                )
                universal_search_text = string_unquote(
                    search_params.get(ALL_FIELDS_SEARCH_KEY)
                )
                backend_compatible_category = _get_backend_compatible_category(
                    app_slug, universal_search_text
                )
                if (
                    backend_compatible_category.lower()
                    != search_params.get(ALL_FIELDS_SEARCH_KEY).lower()
                ):
                    universal_search_text_list = [
                        search_params.get(ALL_FIELDS_SEARCH_KEY),
                        backend_compatible_category,
                    ]
                    search_params[ALL_FIELDS_SEARCH_KEY] = universal_search_text_list
            except AuditTrailBaseException:
                logger.debug(
                    "The universal search text is not a valid category, moving on."
                )

        execution_context = {
            START_TIME_KEY: to_millis(search_params.get(START_TIME_KEY)),
            END_TIME_KEY: to_millis(search_params.get(END_TIME_KEY)),
        }
        elasticsearch_util.build_and_add_es_params(search_params, params_meta_data)

        logger.info(f"Reading audit-trail logs for {customer_id}")

        elasticsearch_dal = ElasticsearchDAL()
        result, count = elasticsearch_dal.get_audit_records(
            search_params, execution_context
        )

        return _build_audit_response(
            app_slug=app_slug,
            result=result,
            count=count,
            offset=search_params.get(OFFSET_KEY),
            limit=search_params.get(LIMIT_KEY),
            include_details=include_details,
        )
    except AuditTrailBaseException:
        logger.exception(
            f"Exception while fetching the audit-trail logs for {search_params.get(CUSTOMER_ID_KEY)}"
        )
        raise AuditTrailBaseException(
            detail="Exception while fetching the audit-trail logs for customer",
            error_code=500,
        )


def get_audit_trail_details(index, audit_id):
    """
    Method to get the audit-details of a given document at a given index
    Args:
         index: ES index value
         audit_id: the audit-document id in the ES
    Returns:
        the audit-detail dict
    """
    details = dict()
    result = _get_audit_trail_details(index, audit_id)
    if result is None:
        return None

    if result.get("header") is None and result.get("body") is None:
        return None

    details["header"] = result.get("header") if result.get("header") else ""
    details["body"] = list(result.get("body")) if result.get("body") else []

    return details


def get_audit_trail_count(
    customer_id, start_time: int, query_params: dict, params_meta_data: dict
):
    """
    Method to get the total number of audit-entries in the ES after a given time
    Args:
        customer_id:: customer id
        start_time: the start offset time for audit-entries
        query_params: the params for querying the ES
        params_meta_data: the meta data of each field in the search_params
    Returns:
        the total number of audit entries
    """
    elasticsearch_dal = ElasticsearchDAL()

    customer_apps = _get_customer_apps(
        query_params.get(CUSTOMER_ID_KEY), query_params.get(APP_SLUG_KEY)
    )
    if not customer_apps:
        logger.error(
            f"No authorized applications found for the customer: {customer_id}"
        )
        raise AuditTrailBaseException(404, f"No authorized applications found.")
    query_params[APP_SLUG_KEY] = customer_apps

    execution_context = {
        "start_time": to_millis(start_time),
        "end_time": to_millis(query_params.get(END_TIME_KEY)),
    }

    elasticsearch_util.build_and_add_es_params(query_params, params_meta_data)
    total_documents = elasticsearch_dal.get_audit_count(query_params, execution_context)
    if total_documents is None:
        return None
    logger.info(
        "Done fetching the total number of documents from the ES in a given index",
        count=total_documents,
    )
    return {"total": total_documents}


def generate_audit_file(
    search_params: dict,
    params_meta_data: dict,
    file_extension: FileExtensions,
    app_slug: AppSlug,
    columns: List[str],
):
    """
    Method to generate file with audit-trail data in the given format
    Args:
        search_params:
        params_meta_data:
        file_extension:
        app_slug:
        columns:
    Returns:
        the generated file path
    """
    if AUDIT_ID_KEY in columns:
        logger.exception(
            f"Column: {AUDIT_ID_KEY} is not supported as part of the query-param."
        )
        raise AuditTrailBaseException(400, f"Unsupported column: {AUDIT_ID_KEY}.")

    columns = sorted(
        set(columns), key=columns.index
    )  # removing duplicates & maintaining order
    if (
        file_extension == FileExtensions.PDF
        and len(columns) > constants.PDF_MAX_COLUMN_COUNT
    ):
        logger.exception(
            f"Not generating PDF file since requested number of columns: {len(columns)} "
            f"exceeded the permitted limit: {constants.PDF_MAX_COLUMN_COUNT}"
        )
        raise AuditTrailBaseException(
            error_code=400,
            detail=f"Maximum number of columns in a PDF can be: {constants.PDF_MAX_COLUMN_COUNT} for PDF.",
        )

    customer_id = search_params.get(CUSTOMER_ID_KEY)
    audit_data = get_audit_trail(
        search_params=search_params,
        params_meta_data=params_meta_data,
        include_details=True,
    )

    if audit_data is None:
        return None, None

    generation_time = get_epoch_millis() // 1000
    directory = f"{constants.AUDIT_TRAIL_FILE_DOWNLOAD_DIRECTORY}{customer_id}/"
    try:
        if file_extension == FileExtensions.CSV:
            return file_handler.audit_to_csv(
                app_slug, customer_id, generation_time, audit_data, directory, columns,
            )
        elif file_extension == FileExtensions.PDF:
            return file_handler.audit_to_pdf(
                app_slug, customer_id, generation_time, audit_data, directory, columns,
            )
    except AuditTrailBaseException as e:
        raise e
    except Exception:
        logger.exception(
            f"Exception while generating audit-trail file of {file_extension.value} format for customer {customer_id}"
        )
        raise AuditTrailBaseException(
            detail="Exception while generating the audit-trail file for customer",
            error_code=500,
        )
    return None, None


def get_audit_trail_categories(app_slug: AppSlug):
    """
    Method to fetch the categories for the given app-slug
    Args:
        app_slug:
    Returns:
        tuple of categories
    """
    return tuple(get_categories_by_app_slug(app_slug).values())


def _insert_audit_trail_data(audit_data: dict):
    """
    Inserts the audit-trail data to the database
    Args:
        audit_data: the audit-data
    Returns:
          True if data insertion is a success else False
    """

    elasticsearch_dal = ElasticsearchDAL()

    # First data is indexed into the elasticsearch & we get the result & audit-ID as response
    # The same audit-ID is maintained across dynamodb/cassandra datastore
    result_es, audit_id = elasticsearch_dal.add_audit_records(audit_data, {})

    execution_context = {AUDIT_ID_KEY: audit_id}
    result = backup_dal_instance.add_audit_records(audit_data, execution_context)
    return result_es and result


def _generate_audit_trail_data(audit_payload: AuditPayload):
    """
    This method generates audit-trail data, which includes the audit-info & audit-details
    Args:
        audit_payload: the message/event data payload
    Returns:
          audit_data
    """
    audit_data: Dict[str, Any] = dict()  # type: ignore
    audit_info: Dict[str, Any] = dict()  # type: ignore

    audit_payload_json = jsonable_encoder(audit_payload)

    _update_customer_details(audit_payload_json)

    # converting epoch to milli-seconds
    if AUDIT_CREATED_AT_KEY in audit_payload_json:
        audit_payload_json[AUDIT_CREATED_AT_KEY] = to_millis(
            audit_payload_json.get(AUDIT_CREATED_AT_KEY)
        )

    for field in audit_payload_json:
        if field in elasticsearch_util.AUDIT_TRAIL_FIXED_FIELDS_PARENT_MAPPING:
            parent = elasticsearch_util.AUDIT_TRAIL_FIXED_FIELDS_PARENT_MAPPING.get(
                field
            ).get(PARENT_KEY)
            if parent is None:
                audit_data[field] = audit_payload_json.get(field)
            elif parent.lower() == "audit_info":
                audit_info[field] = audit_payload_json.get(field)
            else:
                audit_data[parent][field] = audit_payload_json.get(field)
        else:
            audit_data[field] = audit_payload_json.get(field)

    audit_data[AUDIT_INFO_KEY] = audit_info
    if audit_data.get(AUDIT_DETAILS_KEY) and len(audit_data.get(AUDIT_DETAILS_KEY)) > 0:
        audit_info[HAS_DETAILS_KEY] = True

    logger.info(f"Done building audit-trail data for: {audit_payload.customer_id}")
    return audit_data


def _update_customer_details(audit_payload_json):
    """
    Sets the customer name & also check if the customer is the MSP or not & then sets the msp_id accordingly
    Args:
        audit_payload_json: the received payload
    """
    customer_id = audit_payload_json.get(CUSTOMER_ID_KEY)
    if customer_id == CCS_INTERNAL_ID:
        logger.info(
            f"Customer id is {CCS_INTERNAL_ID}, setting customer name to CCS default."
        )
        customer_details = {CUSTOMER_NAME_KEY: CCS_INTERNAL_NAME}
    else:
        customer_details = get_customer_details_from_cid(customer_id)
    if not customer_details:
        logger.error(f"Account details not found for the customer: {customer_id}")
        raise AuditTrailBaseException(404, "Account details not found.")

    if not audit_payload_json.get(CUSTOMER_NAME_KEY):
        customer_name = customer_details.get(CUSTOMER_NAME_KEY)
        logger.info(f"Updating the customer name to {customer_name} for {customer_id}")
        audit_payload_json[CUSTOMER_NAME_KEY] = customer_details.get(CUSTOMER_NAME_KEY)

    msp_id_received = None
    if audit_payload_json.get(ADDITIONAL_INFO_KEY):
        msp_id_received = audit_payload_json.get(ADDITIONAL_INFO_KEY).get(MSP_ID_KEY)
        if not msp_id_received:
            msp_id_received = customer_details.get(MSP_ID_KEY)
    msp_id = (
        customer_id if is_msp(customer_details.get(MSP_ID_KEY)) else msp_id_received
    )

    if msp_id is not None:
        if ADDITIONAL_INFO_KEY not in audit_payload_json:
            audit_payload_json[ADDITIONAL_INFO_KEY] = {}
        logger.info(f"Setting the msp ID of customer {customer_id} as {msp_id}")
        audit_payload_json[ADDITIONAL_INFO_KEY][MSP_ID_KEY] = msp_id


def _build_audit_trail_data(audit_payload: AuditPayload):
    """
    This method validated the prepared data & populates any missing field which
    is required
    Args:
        audit_payload: the message/event data payload
    Returns:
        audit-info, audit-details
    """

    # Generating the audit-trail data
    audit_data = _generate_audit_trail_data(audit_payload)

    logger.info(
        f"Validating the prepared data & populating any missing data for the customer: {audit_payload.customer_id}."
    )

    app_slug = audit_data[APP_SLUG_KEY]

    # Validating the audit-trail data
    _validate_audit_trail_data(audit_data, app_slug)

    logger.info(
        f"Done validating the prepared data & populating any missing data for the customer: {audit_payload.customer_id}."
    )
    # Formatting the audit-trail data before returning
    return _format_audit_trail_data(audit_data)


def _format_audit_trail_data(audit_data: dict):
    """
    This function formats the audit-trail data to comply with the
     data schema decided
    Args:
         audit_data: the data super set containing all the values
    Returns:
        formatted data in accordance with decided DB schema
    """
    data = multiple_args_to_single_dict(
        # Popping out the fields from audit-data which are not relevant to the user
        app_instance_id=audit_data.pop(APP_INSTANCE_ID_KEY),
        customer_id=audit_data.get(CUSTOMER_ID_KEY),
        app_slug=audit_data.pop(APP_SLUG_KEY),
        username=audit_data.get(AUDIT_INFO_KEY).get(USERNAME_KEY),
        audit_info=audit_data.get(AUDIT_INFO_KEY),
        audit_details=audit_data.pop(AUDIT_DETAILS_KEY, None),
    )
    return data


def _validate_audit_trail_data(audit_data, app_slug):
    """
    Validates the audit-trail data and throws AuditTrailBaseException with the error message if validation fails
    Args:
         audit_data: the audit-data received from the user payload
         app_slug: the application slug
    """
    customer_id = audit_data.get(CUSTOMER_ID_KEY)
    category = audit_data.get(AUDIT_INFO_KEY).get(CATEGORY_KEY)
    if (
        ADDITIONAL_INFO_KEY in audit_data.get(AUDIT_INFO_KEY)
        and audit_data.get(AUDIT_INFO_KEY).get(ADDITIONAL_INFO_KEY)
        and DEVICE_TYPE_KEY in audit_data.get(AUDIT_INFO_KEY).get(ADDITIONAL_INFO_KEY)
    ):
        device_type = (
            audit_data.get(AUDIT_INFO_KEY).get(ADDITIONAL_INFO_KEY).get(DEVICE_TYPE_KEY)
        )
    else:
        device_type = None

    if device_type and not _is_device_type_valid(device_type, customer_id):
        logger.error(
            f"Invalid device-type {device_type} received for the customer in the request: {customer_id}."
        )
        raise AuditTrailBaseException(
            400,
            f"Invalid device-type {device_type}. Not inserting data for customer {customer_id}.",
        )

    if not _is_valid_category(category, app_slug, customer_id):
        logger.error(
            f"Unrecognized category {category} for the customer {customer_id}."
        )
        raise AuditTrailBaseException(
            400,
            f"Unrecognized category {category}. Not inserting data for customer {customer_id}.",
        )
    else:
        backend_compatible_category = _get_backend_compatible_category(
            app_slug, category
        )
        audit_data[AUDIT_INFO_KEY][CATEGORY_KEY] = backend_compatible_category


def _get_audit_trail_details(index, audit_id):
    """
    Method to get the audit-log details from the ES
    Args:
        index: ES index
        audit_id: the document id in the ES
    Returns:
        returns the audit-trail details
    """
    elasticsearch_dal = ElasticsearchDAL()
    data = elasticsearch_dal.get_audit_trail_details(index, audit_id)
    return data


def _is_device_type_valid(device_type: str, customer_id: str):
    """
    Validates that device_type is not None & is
    present in the allowed device_types
    Args:
        device_type: the device-type
        customer_id: customer id
    Returns:
        True if (device-type is not None & is present in the allowed device-types) else False
    """
    try:
        if device_type not in DEVICE_TYPES:
            logger.error(
                f"Invalid device-type {device_type}, not inserting audit-data for customer: {customer_id}."
            )
            return False
        return True
    except AuditTrailBaseException as e:
        logger.exception(
            f"Exception while validating device-type {device_type} for customer: {customer_id}.",
            exception=str(e),
        )
        raise AuditTrailBaseException(
            500,
            f"Exception while validating device-type {device_type}. for customer: {customer_id}.",
        )


def _is_valid_category(category: str, app_slug: str, customer_id: str):
    """
    Validates whether the category is valid or not
    Args:
        category: the device-type
        app_slug: app slug
        customer_id: customer id
    Returns:
        True if it is valid else False
    """
    try:
        app_slug_enum: AppSlug = AppSlug(app_slug)
        if category not in get_categories_by_app_slug(app_slug_enum).values():
            return False
        return True
    except (AuditTrailBaseException, ValueError) as e:
        logger.exception(
            f"Exception while validating category {category} for customer: {customer_id}.",
            exception=str(e),
        )
        raise AuditTrailBaseException(
            500,
            f"Exception while validating category {category}. for customer: {customer_id}.",
        )


def _build_audit_response(
    app_slug, result, count, offset, limit, include_details=False
):
    """
        Method to build the audits from the result obtained from the ES query
        Args:
            app_slug: application slug
            result: the result of the ES query
            count: the total number of hist
            offset: starting point for the records
            limit: number of records
        Returns:
            dict containing the fetched audit-info
        """
    audits = []  # type:ignore
    if not result:
        return None
    app_specific_categories = get_categories_by_app_slug(AppSlug(app_slug))
    for audit in result:
        entry = {
            INDEX_KEY: audit.meta.index,
            AUDIT_ID_KEY: audit.meta.id,
            APP_SLUG_KEY: audit[APP_SLUG_KEY],
        }
        audit_info = audit[AUDIT_INFO_KEY].to_dict()
        customer_id = audit[CUSTOMER_ID_KEY]

        for field, value in audit_info.items():
            if field == USERNAME_KEY and value is None:
                entry[field] = "System"
            else:
                entry[field] = value
        entry[CUSTOMER_ID_KEY] = customer_id
        if include_details and AUDIT_DETAILS_KEY in audit and audit[AUDIT_DETAILS_KEY]:
            detail = audit[AUDIT_DETAILS_KEY]
            entry["header"] = detail["header"] if detail["header"] else ""
            entry["body"] = ". ".join(list(detail["body"])) if detail["body"] else ""
        _update_category_user_readable(
            audit_data=entry, app_specific_categories=app_specific_categories
        )
        audits.append(entry)

    remaining_records = is_remaining_records(count=count, offset=offset, limit=limit)
    if count > MAX_ES_DOC_LIMIT:
        count = MAX_ES_DOC_LIMIT
        remaining_records = True

    return multiple_args_to_single_dict(
        audits=audits,
        total_count=count,
        remaining_records=remaining_records,
        timestamp=get_time_range(),
    )


def _get_customer_apps(customer_id, app_slug):
    """
    Method to get the apps which are available for the customer.
    Args:
        customer_id:
        app_slug:
    Returns:
        set of apps slug
    """
    customer_authorized_apps_id = []
    app_id_slug_mapping = {}

    if app_slug == AppSlug.CCS.value:
        logger.info(
            f"No app instance for internal ccs service, returning {app_slug} for the data query"
        )
        return [app_slug]

    if app_slug != AppSlug.APP_ALL_APPS.value:
        _add_customer_app_id(app_slug, app_id_slug_mapping)
    else:
        app_slugs = get_all_apps(app_slug)
        for app_slug in app_slugs:
            _add_customer_app_id(app_slug, app_id_slug_mapping)

    app_instances_for_customer = get_app_instances_for_customer(customer_id).get(
        "instances"
    )

    if not app_instances_for_customer:
        logger.error(f"No app instances found for the customer: {customer_id}")
        raise AuditTrailBaseException(404, f"No app instances found.")

    for app_instance in app_instances_for_customer:
        app_id = app_instance.get(APP_ID_KEY)
        if app_id_slug_mapping.get(app_id):
            customer_authorized_apps_id.append(app_id_slug_mapping.get(app_id))
    customer_authorized_apps_id = set(customer_authorized_apps_id)
    logger.info(
        f"Fetched customer app for customer {customer_id}",
        apps=customer_authorized_apps_id,
    )
    return list(customer_authorized_apps_id)


def _add_customer_app_id(app_slug, app_id_slug_mapping):
    """
    Method to add customer app id against app_slug to the dict
    Args:
        app_slug: the app slug
        app_id_slug_mapping: dict holding app_id to app_slug mapping
    """
    app_details = get_app_details_using_slug(app_slug=app_slug)
    if app_details and app_details.get(APP_ID_KEY):
        app_id = app_details.get(APP_ID_KEY)
        app_id_slug_mapping[app_id] = app_slug


def _get_backend_compatible_category(app_slug: str, category: str):
    """
    Method to update the category with the backend-compatible value.
    Args:
        app_slug: the application whose categories will be loaded
        category: the category which will be updated
    """
    logger.debug(f"Updating the category: {category} to backend compatible.")
    app_specific_dict = get_categories_by_app_slug(AppSlug(app_slug))
    try:
        return list(app_specific_dict.keys())[
            list(app_specific_dict.values()).index(category)
        ]
    except ValueError:
        logger.error(f"Invalid category passed: {category} for app: {app_slug}")
        raise AuditTrailBaseException(400, f"Invalid category: {category}")


def _update_category_user_readable(audit_data: dict, app_specific_categories: dict):
    """
    Method to update the category with the user readable value.
    Args:
        audit_data: the audit-data received
        app_specific_categories: the application categories
    """
    category = audit_data[CATEGORY_KEY]
    if category not in app_specific_categories:
        raise AuditTrailBaseException(400, f"Invalid category: {category}")
    new_category_value = app_specific_categories[audit_data[CATEGORY_KEY]]
    audit_data[CATEGORY_KEY] = new_category_value


def _get_customer_role(app_slug: Union[str, AppSlug], customer_id, search_params):
    """
    Method to identify the customer role & set the appropriate flags.
    Args:
        app_slug:
        customer_id:
        search_params:
    """
    try:
        role_manager: audit_role_manager.RoleManager = audit_role_manager.RoleManager(
            app_slug=app_slug
        )

        if role_manager.restrict_audit_access():
            error_msg = (
                f"The customer {customer_id} is not authorized to view audit-logs"
            )
            logger.exception(error_msg)
            raise AuditTrailBaseException(
                detail=error_msg, error_code=status.HTTP_403_FORBIDDEN,
            )

        if role_manager.allow_admin_level_logs():
            search_params[audit_role_manager.ALLOW_ADMIN_LEVEL_LOGS_KEY] = True
        else:
            if role_manager.allow_msp_level_logs() or is_msp_customer(customer_id):
                # TODO: If the `ccs_login.current_msp_id()` is working
                #  as expected, remove the is_msp_customer() check
                role_manager.authorization_type = (
                    audit_role_manager.RoleManager.AuthorizationTypes.MSP_VIEW
                )
                msp_id = customer_id
                search_params[MSP_ID_KEY] = msp_id
            else:
                if role_manager.allow_self_logs():
                    search_params = pop_keys_from_dict(
                        search_params, MSP_ID_KEY, TENANT_ID_KEY, TENANT_NAME_KEY
                    )

        if role_manager.allow_internal_audit_logs():
            search_params[audit_role_manager.ALLOW_INTERNAL_AUDIT_LOGS_KEY] = True
    except AuditTrailBaseException:
        logger.exception(
            f"Error while getting role info for the customer {customer_id}"
        )
        raise AuditTrailBaseException(
            500, f"Error while getting role info for the customer {customer_id}"
        )

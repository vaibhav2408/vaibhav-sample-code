from typing import List, Tuple, Union

from fastapi import APIRouter, Path, Query, Request, status
from fastapi.responses import FileResponse
from structlog import get_logger

from app.api.tags import FunctionalTags
from app.api.utils import (
    APP_SLUG_DESCRIPTION,
    APP_SLUG_TITLE,
    build_search_query_params,
    get_customer_id,
)
from app.core.audit_management import audit_trail_service
from app.core.exception_handler.audit_trail_base_exception import (
    AuditTrailBaseException,
)
from app.core.generic_responses import Message
from app.models.audit.audit_count import AuditEntriesCount
from app.models.audit.audit_details import AuditDetail
from app.models.audit.audit_trail import Audits
from app.models.empty_response import EmptyResponse
from app.resources.constants import MAX_ES_DOC_LIMIT
from app.resources.enums.app_slug_enum import AppSlug
from app.resources.enums.file_extensions import FileExtensions

router = APIRouter()  # API router for UI APIs

logger = get_logger(__name__)


@router.get(
    "/search",
    response_model=Union[Audits, EmptyResponse],
    status_code=status.HTTP_200_OK,
    tags=[FunctionalTags.AUDIT_TRAIL_UI.value],
    summary="Get audit logs",
    description="Get the audit logs as per the search params",
    responses={status.HTTP_400_BAD_REQUEST: {"model": Message}},
    response_model_exclude_none=True,
)
@authorize(
    permission="ccs.audit-trail.view", application_resource="/ccs/audit-trail",
)
@login_required
async def get_audit_logs(
    request: Request,
    limit: int = Query(
        default=50,
        ge=1,
        le=2000,
        title="Pagination Limit",
        description="Maximum number of audit entries per request.",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        le=10000,
        title="Pagination offset",
        description="Starting index for the audit search.",
    ),
    app_slug: AppSlug = Query(
        ..., title=APP_SLUG_TITLE, description=APP_SLUG_DESCRIPTION,
    ),
):
    platform_cid = get_customer_id(current_session())

    search_query_params, app_supported_params = build_search_query_params(
        platform_cid=platform_cid,
        query_params=request.query_params,
        limit=limit,
        offset=offset,
        app_slug=app_slug,
    )

    result = audit_trail_service.get_audit_trail(
        search_query_params, app_supported_params
    )
    if not result:
        return EmptyResponse()
    return result


@router.get(
    "/{app_slug}/categories",
    response_model=Union[Tuple, EmptyResponse],
    status_code=status.HTTP_200_OK,
    tags=[FunctionalTags.AUDIT_TRAIL_UI.value],
    summary="Get Categories",
    description="Get the audit-logs categories for the specified app",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": Message},
        status.HTTP_404_NOT_FOUND: {"model": Message},
    },
)
@authorize(
    permission="ccs.audit-trail.view", application_resource="/ccs/audit-trail",
)
@login_required
async def get_fields(
    app_slug: AppSlug = Path(
        ..., title=APP_SLUG_TITLE, description=APP_SLUG_DESCRIPTION,
    ),
):
    fields = audit_trail_service.get_audit_trail_categories(app_slug=app_slug)
    if not fields:
        logger.error(f"Categories fields are None. No categories found for {app_slug}")
        return EmptyResponse()
    return fields


@router.get(
    "/details",
    response_model=AuditDetail,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
    tags=[FunctionalTags.AUDIT_TRAIL_UI.value],
    summary="Get audit detail",
    description="Get the audit detail(if any) for any audit-entry",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": Message},
        status.HTTP_404_NOT_FOUND: {"model": Message},
    },
)
@authorize(
    permission="ccs.audit-trail.view", application_resource="/ccs/audit-trail",
)
@login_required
async def get_audit_details(
    index: str = Query(
        ...,
        title="The elasticsearch index for the entry",
        description="elasticsearch index for the entry",
    ),
    audit_id: str = Query(
        ...,
        title="The document id in elasticsearch",
        description="The document_id assigned to the audit entry",
    ),
):
    result = audit_trail_service.get_audit_trail_details(index, audit_id)
    if not result:
        logger.error(
            f"Entry not found for the given index: {index} and audit_id: {audit_id}"
        )
        raise AuditTrailBaseException(
            error_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found for the given index and audit_id.",
        )
    return result


@router.get(
    "/count",
    response_model=Union[AuditEntriesCount, EmptyResponse],
    status_code=status.HTTP_200_OK,
    tags=[FunctionalTags.AUDIT_TRAIL_UI.value],
    summary="Get audit count",
    description="Get the number of audit logs in the system for the current customer-id from given timestamp",
    responses={status.HTTP_400_BAD_REQUEST: {"model": Message}},
)
@authorize(
    permission="ccs.audit-trail.view", application_resource="/ccs/audit-trail",
)
@login_required
async def get_audit_count(
    request: Request,
    start_time: int = Query(
        ...,
        title="the start time",
        description="The time from which the audit-entries count is requested for",
    ),
    app_slug: AppSlug = Query(
        ..., title=APP_SLUG_TITLE, description=APP_SLUG_DESCRIPTION,
    ),
):
    platform_cid = get_customer_id(current_session())

    query_params, params_meta_data = build_search_query_params(
        platform_cid=platform_cid,
        query_params=request.query_params,
        app_slug=app_slug,
        set_defaults=False,
    )
    result = audit_trail_service.get_audit_trail_count(
        platform_cid, start_time, query_params, params_meta_data
    )
    if not result:
        return EmptyResponse()
    return result


@router.get(
    "/download",
    status_code=status.HTTP_200_OK,
    tags=[FunctionalTags.AUDIT_TRAIL_UI.value],
    summary="Download audit logs in a file",
    description="Download audit logs in a file of the desired format.",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": Message},
        status.HTTP_404_NOT_FOUND: {"model": Message},
    },
)
@authorize(
    permission="ccs.audit-trail.view", application_resource="/ccs/audit-trail",
)
@login_required
async def download_audit_logs(
    request: Request,
    file_extension: FileExtensions = Query(
        FileExtensions.CSV,
        title="The downloading file extension",
        description="The file extension implying the format in which the audit-trail is to be downloaded",
    ),
    columns: List[str] = Query(
        ...,
        title="The file columns",
        description="The columns which are be present in the requested file",
    ),
    app_slug: AppSlug = Query(
        ..., title=APP_SLUG_TITLE, description=APP_SLUG_DESCRIPTION,
    ),
):
    platform_cid = get_customer_id(current_session())

    search_query_params, app_supported_params = build_search_query_params(
        platform_cid=platform_cid,
        query_params=request.query_params,
        limit=MAX_ES_DOC_LIMIT,
        offset=0,
        app_slug=app_slug,
    )

    audit_filename, audit_filepath = audit_trail_service.generate_audit_file(
        search_query_params, app_supported_params, file_extension, app_slug, columns,
    )
    if audit_filepath is None or audit_filename is None:
        return EmptyResponse()
    return FileResponse(path=audit_filepath, filename=audit_filename)

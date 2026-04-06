from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.usr_cloud import (
    UsrCloudAuthStatus,
    UsrCloudDeviceDetailResult,
    UsrCloudDeviceListResult,
    UsrCloudLoginResult,
)
from app.services.logging_service import write_runtime_log
from app.services.usr_cloud_service import (
    UsrCloudConfigurationError,
    UsrCloudLoginError,
    UsrCloudRequestError,
    usr_cloud_service,
)

router = APIRouter()


@router.get("/status", response_model=UsrCloudAuthStatus)
async def read_usr_cloud_status(
    _: User = Depends(get_current_admin),
) -> UsrCloudAuthStatus:
    return UsrCloudAuthStatus(**usr_cloud_service.status())


@router.post("/login", response_model=UsrCloudLoginResult)
async def login_usr_cloud(
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> UsrCloudLoginResult:
    try:
        token_state = await usr_cloud_service.login(force_refresh=True)
        await write_runtime_log(
            db,
            level="INFO",
            event="usr_cloud_login_success",
            message="USR cloud login succeeded",
            context={"uid": token_state.uid},
        )
        return UsrCloudLoginResult(
            success=True,
            api_base_url=usr_cloud_service.status()["api_base_url"],
            uid=token_state.uid,
            token_cached=True,
            token_expires_at=token_state.expires_at.isoformat(),
            message="USR cloud login succeeded",
        )
    except UsrCloudConfigurationError as exc:
        await write_runtime_log(
            db,
            level="ERROR",
            event="usr_cloud_login_configuration_error",
            message=str(exc),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except UsrCloudLoginError as exc:
        await write_runtime_log(
            db,
            level="ERROR",
            event="usr_cloud_login_failed",
            message=str(exc),
        )
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        await write_runtime_log(
            db,
            level="ERROR",
            event="usr_cloud_login_unhandled_error",
            message=str(exc),
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"USR cloud login raised unexpected error: {exc}",
        ) from exc


@router.get("/devices", response_model=UsrCloudDeviceListResult)
async def list_usr_cloud_devices(
    page: int | None = None,
    page_size: int | None = None,
    project_id: str | None = None,
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> UsrCloudDeviceListResult:
    try:
        path_used, raw, items, total = await usr_cloud_service.list_devices(
            page=page,
            page_size=page_size,
            project_id=project_id,
        )
        await write_runtime_log(
            db,
            level="INFO",
            event="usr_cloud_list_devices_success",
            message="USR cloud device list request succeeded",
            context={"path_used": path_used, "item_count": len(items)},
        )
        return UsrCloudDeviceListResult(
            success=True,
            path_used=path_used,
            total=total,
            items=items,
            raw=raw,
            message="USR cloud device list request succeeded",
        )
    except UsrCloudConfigurationError as exc:
        await write_runtime_log(
            db,
            level="ERROR",
            event="usr_cloud_list_devices_configuration_error",
            message=str(exc),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except (UsrCloudLoginError, UsrCloudRequestError) as exc:
        await write_runtime_log(
            db,
            level="ERROR",
            event="usr_cloud_list_devices_failed",
            message=str(exc),
        )
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        await write_runtime_log(
            db,
            level="ERROR",
            event="usr_cloud_list_devices_unhandled_error",
            message=str(exc),
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"USR cloud device list raised unexpected error: {exc}",
        ) from exc


@router.get("/devices/detail", response_model=UsrCloudDeviceDetailResult)
async def read_usr_cloud_device_detail(
    dev_id: str | None = None,
    device_id: str | None = None,
    device_no: str | None = None,
    cusdevice_no: str | None = None,
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> UsrCloudDeviceDetailResult:
    try:
        path_used, raw, item = await usr_cloud_service.get_device_detail(
            dev_id=dev_id,
            device_id=device_id,
            device_no=device_no,
            cusdevice_no=cusdevice_no,
        )
        await write_runtime_log(
            db,
            level="INFO",
            event="usr_cloud_get_device_detail_success",
            message="USR cloud device detail request succeeded",
            context={"path_used": path_used},
        )
        return UsrCloudDeviceDetailResult(
            success=True,
            path_used=path_used,
            item=item,
            raw=raw,
            message="USR cloud device detail request succeeded",
        )
    except UsrCloudConfigurationError as exc:
        await write_runtime_log(
            db,
            level="ERROR",
            event="usr_cloud_get_device_detail_configuration_error",
            message=str(exc),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except (UsrCloudLoginError, UsrCloudRequestError) as exc:
        await write_runtime_log(
            db,
            level="ERROR",
            event="usr_cloud_get_device_detail_failed",
            message=str(exc),
        )
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        await write_runtime_log(
            db,
            level="ERROR",
            event="usr_cloud_get_device_detail_unhandled_error",
            message=str(exc),
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"USR cloud device detail raised unexpected error: {exc}",
        ) from exc

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.logs import (
    CommunicationLogPage,
    CommunicationLogRead,
    LogsOverview,
    OperationLogPage,
    OperationLogRead,
    RuntimeLogPage,
    RuntimeLogRead,
)
from app.services.logging_service import (
    get_logs_overview,
    list_communication_logs,
    list_communication_logs_page,
    list_operation_logs,
    list_operation_logs_page,
    list_runtime_logs,
    list_runtime_logs_page,
)

router = APIRouter()


@router.get("/runtime", response_model=list[RuntimeLogRead])
async def read_runtime_logs(
    level: str | None = Query(default=None),
    event: str | None = Query(default=None),
    created_from: datetime | None = Query(default=None),
    created_to: datetime | None = Query(default=None),
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> list[RuntimeLogRead]:
    logs = await list_runtime_logs(db, level, event, created_from, created_to)
    return [RuntimeLogRead.model_validate(item) for item in logs]


@router.get("/runtime/page", response_model=RuntimeLogPage)
async def read_runtime_logs_page(
    level: str | None = Query(default=None),
    event: str | None = Query(default=None),
    created_from: datetime | None = Query(default=None),
    created_to: datetime | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> RuntimeLogPage:
    total, logs = await list_runtime_logs_page(
        db,
        level=level,
        event=event,
        created_from=created_from,
        created_to=created_to,
        limit=limit,
        offset=offset,
    )
    return RuntimeLogPage(
        total=total,
        items=[RuntimeLogRead.model_validate(item) for item in logs],
    )


@router.get("/operations", response_model=list[OperationLogRead])
async def read_operation_logs(
    action: str | None = Query(default=None),
    target_type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> list[OperationLogRead]:
    logs = await list_operation_logs(db, action, target_type, status)
    return [OperationLogRead.model_validate(item) for item in logs]


@router.get("/operations/page", response_model=OperationLogPage)
async def read_operation_logs_page(
    action: str | None = Query(default=None),
    target_type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> OperationLogPage:
    total, logs = await list_operation_logs_page(
        db,
        action=action,
        target_type=target_type,
        status=status,
        limit=limit,
        offset=offset,
    )
    return OperationLogPage(
        total=total,
        items=[OperationLogRead.model_validate(item) for item in logs],
    )


@router.get("/communication", response_model=list[CommunicationLogRead])
async def read_communication_logs(
    channel: str | None = Query(default=None),
    direction: str | None = Query(default=None),
    device_serial: str | None = Query(default=None),
    status: str | None = Query(default=None),
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> list[CommunicationLogRead]:
    logs = await list_communication_logs(db, channel, direction, device_serial, status)
    return [CommunicationLogRead.model_validate(item) for item in logs]


@router.get("/communication/page", response_model=CommunicationLogPage)
async def read_communication_logs_page(
    channel: str | None = Query(default=None),
    direction: str | None = Query(default=None),
    device_serial: str | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> CommunicationLogPage:
    total, logs = await list_communication_logs_page(
        db,
        channel=channel,
        direction=direction,
        device_serial=device_serial,
        status=status,
        limit=limit,
        offset=offset,
    )
    return CommunicationLogPage(
        total=total,
        items=[CommunicationLogRead.model_validate(item) for item in logs],
    )


@router.get("/overview", response_model=LogsOverview)
async def read_logs_overview(
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> LogsOverview:
    overview = await get_logs_overview(db)
    return LogsOverview(**overview)

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.logs import CommunicationLogRead, OperationLogRead, RuntimeLogRead
from app.services.logging_service import (
    list_communication_logs,
    list_operation_logs,
    list_runtime_logs,
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

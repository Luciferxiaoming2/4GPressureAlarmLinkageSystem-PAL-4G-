from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.relay import RelayCommandRead, RelayRetryResult
from app.services.linkage_service import list_relay_commands, retry_queued_relay_commands

router = APIRouter()


@router.get("", response_model=list[RelayCommandRead])
async def read_relay_commands(
    alarm_record_id: int | None = Query(default=None),
    execution_status: str | None = Query(default=None),
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> list[RelayCommandRead]:
    commands = await list_relay_commands(
        db,
        alarm_record_id=alarm_record_id,
        execution_status=execution_status,
    )
    return [RelayCommandRead.model_validate(command) for command in commands]


@router.post("/retry-pending", response_model=RelayRetryResult)
async def retry_pending_relay_commands(
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> RelayRetryResult:
    return await retry_queued_relay_commands(db)

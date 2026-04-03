from fastapi import APIRouter, Depends

from app.api.deps import get_current_admin
from app.models.user import User
from app.schemas.jobs import OfflineCheckResult, SchedulerStatus
from app.schemas.relay import RelayRetryResult
from app.services.scheduler_service import (
    mark_offline_modules,
    run_retry_pending_commands_job,
    scheduler,
)

router = APIRouter()


@router.get("/scheduler", response_model=SchedulerStatus)
async def read_scheduler_status(
    _: User = Depends(get_current_admin),
) -> SchedulerStatus:
    return SchedulerStatus(
        running=scheduler.running,
        jobs=[job.id for job in scheduler.get_jobs()],
    )


@router.post("/offline-check", response_model=OfflineCheckResult)
async def run_offline_check(
    _: User = Depends(get_current_admin),
) -> OfflineCheckResult:
    updated_count = await mark_offline_modules()
    return OfflineCheckResult(updated_count=updated_count)


@router.post("/retry-pending", response_model=RelayRetryResult)
async def run_retry_pending(
    _: User = Depends(get_current_admin),
) -> RelayRetryResult:
    result = await run_retry_pending_commands_job()
    return RelayRetryResult(**result)

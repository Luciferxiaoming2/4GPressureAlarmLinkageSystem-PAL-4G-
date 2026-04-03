from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.alarm import AlarmRecordCreate, AlarmRecordRead, AlarmRecordRecover
from app.services.alarm_service import (
    can_access_device,
    create_alarm_record,
    get_alarm_by_id,
    get_module_with_device,
    list_alarm_records,
    recover_alarm_record,
)
from app.services.linkage_service import dispatch_linkage_for_alarm, dispatch_recovery_for_alarm

router = APIRouter()


@router.get("", response_model=list[AlarmRecordRead])
async def read_alarm_records(
    alarm_type: str | None = Query(default=None),
    alarm_status: str | None = Query(default=None),
    module_id: int | None = Query(default=None),
    device_id: int | None = Query(default=None),
    source: str | None = Query(default=None),
    linkage_status: str | None = Query(default=None),
    triggered_from: datetime | None = Query(default=None),
    triggered_to: datetime | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AlarmRecordRead]:
    alarms = await list_alarm_records(
        db=db,
        user=current_user,
        alarm_type=alarm_type,
        alarm_status=alarm_status,
        module_id=module_id,
        device_id=device_id,
        source=source,
        linkage_status=linkage_status,
        triggered_from=triggered_from,
        triggered_to=triggered_to,
    )
    return [AlarmRecordRead.model_validate(alarm) for alarm in alarms]


@router.post("", response_model=AlarmRecordRead, status_code=status.HTTP_201_CREATED)
async def create_new_alarm_record(
    payload: AlarmRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlarmRecordRead:
    module = await get_module_with_device(db, payload.module_id)
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
    if not can_access_device(current_user, module.device):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    alarm = await create_alarm_record(db, payload)
    await dispatch_linkage_for_alarm(db, alarm)
    return AlarmRecordRead.model_validate(alarm)


@router.get("/{alarm_id}", response_model=AlarmRecordRead)
async def read_alarm_record(
    alarm_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlarmRecordRead:
    alarm = await get_alarm_by_id(db, alarm_id)
    if not alarm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alarm not found")

    module = await get_module_with_device(db, alarm.module_id)
    if not can_access_device(current_user, module.device if module else None):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return AlarmRecordRead.model_validate(alarm)


@router.post("/{alarm_id}/recover", response_model=AlarmRecordRead)
async def recover_alarm(
    alarm_id: int,
    payload: AlarmRecordRecover,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AlarmRecordRead:
    alarm = await get_alarm_by_id(db, alarm_id)
    if not alarm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alarm not found")

    module = await get_module_with_device(db, alarm.module_id)
    if not can_access_device(current_user, module.device if module else None):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    alarm = await recover_alarm_record(db, alarm, payload)
    # 报警恢复后自动尝试下发恢复指令；若用户在报警期间做过手动操作，则恢复逻辑会自动跳过。
    await dispatch_recovery_for_alarm(db, alarm)
    return AlarmRecordRead.model_validate(alarm)

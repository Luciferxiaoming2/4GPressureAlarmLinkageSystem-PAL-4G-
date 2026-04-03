from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.alarm_record import AlarmRecord
from app.models.device import Device
from app.models.module import Module
from app.models.user import User
from app.schemas.alarm import AlarmRecordCreate, AlarmRecordRecover


async def get_module_with_device(db: AsyncSession, module_id: int) -> Module | None:
    stmt = (
        select(Module)
        .options(selectinload(Module.device))
        .where(Module.id == module_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


def can_access_device(user: User, device: Device | None) -> bool:
    # 超级管理员可访问全部设备，普通用户仅可访问自己名下设备。
    if user.role == "super_admin":
        return True
    return bool(device and device.owner_id == user.id)


async def create_alarm_record(
    db: AsyncSession,
    payload: AlarmRecordCreate,
) -> AlarmRecord:
    # 当前先落一条独立报警记录，后续可在这里扩展联动结果、来源和去重策略。
    alarm = AlarmRecord(
        module_id=payload.module_id,
        alarm_type=payload.alarm_type,
        alarm_status="triggered",
        source=payload.source,
        linkage_status=payload.linkage_status,
        linkage_result=payload.linkage_result,
        message=payload.message,
    )
    db.add(alarm)
    await db.commit()
    await db.refresh(alarm)
    return alarm


async def get_alarm_by_id(db: AsyncSession, alarm_id: int) -> AlarmRecord | None:
    result = await db.execute(select(AlarmRecord).where(AlarmRecord.id == alarm_id))
    return result.scalar_one_or_none()


async def list_alarm_records(
    db: AsyncSession,
    user: User,
    alarm_type: str | None = None,
    alarm_status: str | None = None,
    module_id: int | None = None,
    device_id: int | None = None,
    source: str | None = None,
    linkage_status: str | None = None,
    triggered_from: datetime | None = None,
    triggered_to: datetime | None = None,
) -> list[AlarmRecord]:
    stmt = (
        select(AlarmRecord)
        .join(Module, AlarmRecord.module_id == Module.id)
        .join(Device, Module.device_id == Device.id)
    )

    if user.role != "super_admin":
        stmt = stmt.where(Device.owner_id == user.id)
    if alarm_type:
        stmt = stmt.where(AlarmRecord.alarm_type == alarm_type)
    if alarm_status:
        stmt = stmt.where(AlarmRecord.alarm_status == alarm_status)
    if module_id:
        stmt = stmt.where(AlarmRecord.module_id == module_id)
    if device_id:
        stmt = stmt.where(Device.id == device_id)
    if source:
        stmt = stmt.where(AlarmRecord.source == source)
    if linkage_status:
        stmt = stmt.where(AlarmRecord.linkage_status == linkage_status)
    if triggered_from:
        stmt = stmt.where(AlarmRecord.triggered_at >= triggered_from)
    if triggered_to:
        stmt = stmt.where(AlarmRecord.triggered_at <= triggered_to)

    stmt = stmt.order_by(AlarmRecord.triggered_at.desc(), AlarmRecord.id.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def recover_alarm_record(
    db: AsyncSession,
    alarm: AlarmRecord,
    payload: AlarmRecordRecover,
) -> AlarmRecord:
    # 恢复动作当前仅更新状态和恢复时间，后续可接入自动断开继电器等联动逻辑。
    alarm.alarm_status = "recovered"
    alarm.recovered_at = payload.recovered_at or datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(alarm)
    return alarm

import json
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.communication_log import CommunicationLog
from app.models.operation_log import OperationLog
from app.models.runtime_log import RuntimeLog


async def write_runtime_log(
    db: AsyncSession,
    level: str,
    event: str,
    message: str,
    context: dict | None = None,
) -> RuntimeLog:
    log = RuntimeLog(
        level=level,
        event=event,
        message=message,
        context=json.dumps(context, ensure_ascii=False) if context else None,
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log


async def write_operation_log(
    db: AsyncSession,
    action: str,
    target_type: str,
    actor_user_id: int | None = None,
    target_id: int | None = None,
    status: str = "success",
    detail: str | None = None,
) -> OperationLog:
    log = OperationLog(
        actor_user_id=actor_user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        status=status,
        detail=detail,
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log


async def write_communication_log(
    db: AsyncSession,
    channel: str,
    direction: str,
    status: str = "success",
    device_serial: str | None = None,
    module_code: str | None = None,
    payload: dict | None = None,
    message: str | None = None,
) -> CommunicationLog:
    log = CommunicationLog(
        channel=channel,
        direction=direction,
        status=status,
        device_serial=device_serial,
        module_code=module_code,
        payload=json.dumps(payload, ensure_ascii=False) if payload else None,
        message=message,
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log


async def list_runtime_logs(
    db: AsyncSession,
    level: str | None = None,
    event: str | None = None,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
) -> list[RuntimeLog]:
    stmt = select(RuntimeLog).order_by(RuntimeLog.created_at.desc(), RuntimeLog.id.desc())
    if level:
        stmt = stmt.where(RuntimeLog.level == level)
    if event:
        stmt = stmt.where(RuntimeLog.event == event)
    if created_from:
        stmt = stmt.where(RuntimeLog.created_at >= created_from)
    if created_to:
        stmt = stmt.where(RuntimeLog.created_at <= created_to)
    return list((await db.execute(stmt)).scalars().all())


async def list_operation_logs(
    db: AsyncSession,
    action: str | None = None,
    target_type: str | None = None,
    status: str | None = None,
) -> list[OperationLog]:
    stmt = select(OperationLog).order_by(
        OperationLog.created_at.desc(), OperationLog.id.desc()
    )
    if action:
        stmt = stmt.where(OperationLog.action == action)
    if target_type:
        stmt = stmt.where(OperationLog.target_type == target_type)
    if status:
        stmt = stmt.where(OperationLog.status == status)
    return list((await db.execute(stmt)).scalars().all())


async def list_communication_logs(
    db: AsyncSession,
    channel: str | None = None,
    direction: str | None = None,
    device_serial: str | None = None,
    status: str | None = None,
) -> list[CommunicationLog]:
    stmt = select(CommunicationLog).order_by(
        CommunicationLog.created_at.desc(), CommunicationLog.id.desc()
    )
    if channel:
        stmt = stmt.where(CommunicationLog.channel == channel)
    if direction:
        stmt = stmt.where(CommunicationLog.direction == direction)
    if device_serial:
        stmt = stmt.where(CommunicationLog.device_serial == device_serial)
    if status:
        stmt = stmt.where(CommunicationLog.status == status)
    return list((await db.execute(stmt)).scalars().all())

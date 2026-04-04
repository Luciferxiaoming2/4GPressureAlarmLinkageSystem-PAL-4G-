from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.alarm_record import AlarmRecord
from app.models.device import Device
from app.models.module import Module
from app.models.relay_command import RelayCommand
from app.schemas.alarm import AlarmLinkageDispatchResult
from app.schemas.relay import RelayCommandCreate, RelayCommandFeedback, RelayRetryResult
from app.services.realtime_service import realtime_service


async def _get_trigger_module_with_device(
    db: AsyncSession,
    alarm: AlarmRecord,
) -> Module | None:
    stmt = (
        select(Module)
        .options(selectinload(Module.device).selectinload(Device.linkage_group))
        .where(Module.id == alarm.module_id)
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def _get_linkage_target_modules(
    db: AsyncSession,
    trigger_module: Module,
) -> tuple[list[Module], str]:
    # 联动优先按设备组生效；没有分组时再回退到同设备内其他模块。
    if trigger_module.device and trigger_module.device.linkage_group_id:
        stmt = (
            select(Module)
            .join(Module.device)
            .where(
                Device.linkage_group_id == trigger_module.device.linkage_group_id,
                Module.id != trigger_module.id,
            )
        )
        no_target_message = "no linkage targets found in the same device group"
    else:
        stmt = select(Module).where(
            Module.device_id == trigger_module.device_id,
            Module.id != trigger_module.id,
        )
        no_target_message = "no linkage targets found in the same device"

    target_modules = list((await db.execute(stmt)).scalars().all())
    return target_modules, no_target_message


async def dispatch_linkage_for_alarm(
    db: AsyncSession,
    alarm: AlarmRecord,
) -> AlarmLinkageDispatchResult:
    trigger_module = await _get_trigger_module_with_device(db, alarm)
    if not trigger_module:
        alarm.linkage_status = "failed"
        alarm.linkage_result = "trigger module not found"
        await db.commit()
        await db.refresh(alarm)
        return AlarmLinkageDispatchResult(
            alarm_id=alarm.id,
            generated_command_count=0,
            dispatched_count=0,
            queued_count=0,
            skipped_count=0,
            linkage_status=alarm.linkage_status,
            linkage_result=alarm.linkage_result or "",
        )

    target_modules, no_target_message = await _get_linkage_target_modules(db, trigger_module)
    if not target_modules:
        alarm.linkage_status = "no_targets"
        alarm.linkage_result = no_target_message
        await db.commit()
        await db.refresh(alarm)
        return AlarmLinkageDispatchResult(
            alarm_id=alarm.id,
            generated_command_count=0,
            dispatched_count=0,
            queued_count=0,
            skipped_count=0,
            linkage_status=alarm.linkage_status,
            linkage_result=alarm.linkage_result or "",
        )

    generated_command_count = 0
    dispatched_count = 0
    queued_count = 0
    skipped_count = 0

    for target_module in target_modules:
        existing_stmt = select(RelayCommand).where(
            RelayCommand.alarm_record_id == alarm.id,
            RelayCommand.module_id == target_module.id,
            RelayCommand.command_source == "alarm_linkage",
        )
        existing_command = (await db.execute(existing_stmt)).scalar_one_or_none()
        if existing_command:
            skipped_count += 1
            continue

        is_online = target_module.is_online
        command = RelayCommand(
            alarm_record_id=alarm.id,
            module_id=target_module.id,
            command_source="alarm_linkage",
            target_state="closed",
            execution_status="dispatched" if is_online else "queued",
            execution_result=(
                "relay close command dispatched immediately"
                if is_online
                else "target module offline, waiting for retry"
            ),
            retry_count=1 if is_online else 0,
            last_attempt_at=datetime.now(timezone.utc) if is_online else None,
        )
        db.add(command)
        generated_command_count += 1
        if is_online:
            dispatched_count += 1
        else:
            queued_count += 1

    if generated_command_count == 0 and skipped_count > 0:
        linkage_status = alarm.linkage_status or "already_generated"
        linkage_result = "linkage commands already exist for this alarm"
    elif queued_count > 0 and dispatched_count > 0:
        linkage_status = "partial_dispatched"
        linkage_result = (
            f"{dispatched_count} commands dispatched, {queued_count} queued for retry"
        )
    elif queued_count > 0:
        linkage_status = "queued"
        linkage_result = f"{queued_count} linkage commands queued for offline modules"
    else:
        linkage_status = "dispatched"
        linkage_result = f"{dispatched_count} linkage commands dispatched"

    alarm.linkage_status = linkage_status
    alarm.linkage_result = linkage_result
    await db.commit()
    await db.refresh(alarm)

    relay_commands = list(
        (
            await db.execute(
                select(RelayCommand).where(
                    RelayCommand.alarm_record_id == alarm.id,
                    RelayCommand.command_source == "alarm_linkage",
                )
            )
        ).scalars().all()
    )
    for command in relay_commands:
        await realtime_service.broadcast(
            "relay_command.created",
            {
                "command_id": command.id,
                "alarm_record_id": command.alarm_record_id,
                "module_id": command.module_id,
                "command_source": command.command_source,
                "target_state": command.target_state,
                "execution_status": command.execution_status,
            },
            owner_id=trigger_module.device.owner_id if trigger_module.device else None,
        )

    return AlarmLinkageDispatchResult(
        alarm_id=alarm.id,
        generated_command_count=generated_command_count,
        dispatched_count=dispatched_count,
        queued_count=queued_count,
        skipped_count=skipped_count,
        linkage_status=alarm.linkage_status,
        linkage_result=alarm.linkage_result or "",
    )


async def dispatch_recovery_for_alarm(db: AsyncSession, alarm: AlarmRecord) -> dict[str, int | str]:
    trigger_module = await _get_trigger_module_with_device(db, alarm)
    if not trigger_module:
        alarm.linkage_status = "recovery_failed"
        alarm.linkage_result = "trigger module not found during recovery"
        await db.commit()
        await db.refresh(alarm)
        return {
            "generated_command_count": 0,
            "dispatched_count": 0,
            "queued_count": 0,
            "skipped_count": 0,
            "status": alarm.linkage_status,
        }

    target_modules, no_target_message = await _get_linkage_target_modules(db, trigger_module)
    if not target_modules:
        alarm.linkage_status = "recovery_no_targets"
        alarm.linkage_result = no_target_message
        await db.commit()
        await db.refresh(alarm)
        return {
            "generated_command_count": 0,
            "dispatched_count": 0,
            "queued_count": 0,
            "skipped_count": 0,
            "status": alarm.linkage_status,
        }

    generated_command_count = 0
    dispatched_count = 0
    queued_count = 0
    skipped_count = 0

    for target_module in target_modules:
        latest_manual_stmt = (
            select(RelayCommand)
            .where(
                RelayCommand.module_id == target_module.id,
                RelayCommand.command_source == "manual_control",
                # SQLite 默认时间精度较粗，给报警触发时间留 1 秒容差，避免同秒内的人工操作被漏判。
                RelayCommand.created_at >= alarm.triggered_at - timedelta(seconds=1),
            )
            .order_by(RelayCommand.created_at.desc(), RelayCommand.id.desc())
            .limit(1)
        )
        latest_manual_command = (await db.execute(latest_manual_stmt)).scalar_one_or_none()

        # 报警后如果用户手动控制过该模块，就跳过自动恢复，避免覆盖人工决策。
        if latest_manual_command:
            skipped_count += 1
            continue

        is_online = target_module.is_online
        command = RelayCommand(
            alarm_record_id=alarm.id,
            module_id=target_module.id,
            command_source="alarm_recovery",
            target_state="open",
            execution_status="dispatched" if is_online else "queued",
            execution_result=(
                "relay recovery command dispatched immediately"
                if is_online
                else "recovery command queued for offline module"
            ),
            retry_count=1 if is_online else 0,
            last_attempt_at=datetime.now(timezone.utc) if is_online else None,
        )
        db.add(command)
        generated_command_count += 1
        if is_online:
            dispatched_count += 1
        else:
            queued_count += 1

    if generated_command_count == 0 and skipped_count > 0:
        alarm.linkage_status = "recovery_skipped"
        alarm.linkage_result = "recovery skipped because newer manual commands exist"
    elif queued_count > 0 and dispatched_count > 0:
        alarm.linkage_status = "recovery_partial"
        alarm.linkage_result = (
            f"{dispatched_count} recovery commands dispatched, {queued_count} queued"
        )
    elif queued_count > 0:
        alarm.linkage_status = "recovery_queued"
        alarm.linkage_result = f"{queued_count} recovery commands queued for offline modules"
    else:
        alarm.linkage_status = "recovery_dispatched"
        alarm.linkage_result = f"{dispatched_count} recovery commands dispatched"

    await db.commit()
    await db.refresh(alarm)
    relay_commands = list(
        (
            await db.execute(
                select(RelayCommand).where(
                    RelayCommand.alarm_record_id == alarm.id,
                    RelayCommand.command_source == "alarm_recovery",
                )
            )
        ).scalars().all()
    )
    for command in relay_commands:
        await realtime_service.broadcast(
            "relay_command.created",
            {
                "command_id": command.id,
                "alarm_record_id": command.alarm_record_id,
                "module_id": command.module_id,
                "command_source": command.command_source,
                "target_state": command.target_state,
                "execution_status": command.execution_status,
            },
            owner_id=trigger_module.device.owner_id if trigger_module.device else None,
        )
    return {
        "generated_command_count": generated_command_count,
        "dispatched_count": dispatched_count,
        "queued_count": queued_count,
        "skipped_count": skipped_count,
        "status": alarm.linkage_status,
    }


async def retry_queued_relay_commands(db: AsyncSession) -> RelayRetryResult:
    queued_stmt = (
        select(RelayCommand)
        .options(selectinload(RelayCommand.module).selectinload(Module.device))
        .where(RelayCommand.execution_status.in_(["queued", "pending"]))
        .order_by(RelayCommand.created_at.asc(), RelayCommand.id.asc())
    )
    queued_commands = list((await db.execute(queued_stmt)).scalars().all())

    dispatched_count = 0
    still_queued_count = 0
    now = datetime.now(timezone.utc)

    for command in queued_commands:
        command.retry_count += 1
        command.last_attempt_at = now
        if command.module and command.module.is_online:
            command.execution_status = "dispatched"
            command.execution_result = "queued command dispatched after retry scan"
            dispatched_count += 1
        else:
            command.execution_status = "queued"
            command.execution_result = "target module still offline during retry scan"
            still_queued_count += 1

    await db.commit()

    for command in queued_commands:
        await realtime_service.broadcast(
            "relay_command.updated",
            {
                "command_id": command.id,
                "alarm_record_id": command.alarm_record_id,
                "module_id": command.module_id,
                "command_source": command.command_source,
                "target_state": command.target_state,
                "execution_status": command.execution_status,
                "execution_result": command.execution_result,
            },
            owner_id=command.module.device.owner_id
            if command.module and command.module.device
            else None,
        )

    return RelayRetryResult(
        total_scanned=len(queued_commands),
        dispatched_count=dispatched_count,
        still_queued_count=still_queued_count,
    )


async def list_relay_commands(
    db: AsyncSession,
    alarm_record_id: int | None = None,
    execution_status: str | None = None,
) -> list[RelayCommand]:
    stmt = select(RelayCommand).order_by(RelayCommand.created_at.desc(), RelayCommand.id.desc())
    if alarm_record_id:
        stmt = stmt.where(RelayCommand.alarm_record_id == alarm_record_id)
    if execution_status:
        stmt = stmt.where(RelayCommand.execution_status == execution_status)
    return list((await db.execute(stmt)).scalars().all())


async def get_relay_command_by_id(
    db: AsyncSession,
    command_id: int,
) -> RelayCommand | None:
    stmt = (
        select(RelayCommand)
        .options(selectinload(RelayCommand.module).selectinload(Module.device))
        .where(RelayCommand.id == command_id)
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def create_manual_relay_command(
    db: AsyncSession,
    payload: RelayCommandCreate,
) -> RelayCommand:
    module = (
        await db.execute(
            select(Module)
            .options(selectinload(Module.device))
            .where(Module.id == payload.module_id)
        )
    ).scalar_one_or_none()
    if not module:
        raise ValueError("Module not found")

    is_online = module.is_online
    now = datetime.now(timezone.utc)

    # 人工控制优先级高于自动联动。
    # 这里会把同模块尚未执行的自动联动/自动恢复指令取消，避免后续补发把人工决策覆盖回去。
    pending_auto_stmt = select(RelayCommand).where(
        RelayCommand.module_id == payload.module_id,
        RelayCommand.command_source.in_(["alarm_linkage", "alarm_recovery"]),
        RelayCommand.execution_status.in_(["queued", "pending"]),
    )
    pending_auto_commands = list((await db.execute(pending_auto_stmt)).scalars().all())
    for auto_command in pending_auto_commands:
        auto_command.execution_status = "cancelled"
        auto_command.execution_result = (
            f"cancelled because newer manual command overrides {auto_command.command_source}"
        )
        auto_command.last_attempt_at = now

    # 手动控制指令与报警联动指令分开记录，后续冲突处理会依赖 command_source 区分来源。
    command = RelayCommand(
        module_id=payload.module_id,
        command_source=payload.command_source,
        target_state=payload.target_state,
        execution_status="dispatched" if is_online else "queued",
        execution_result=(
            "manual relay command dispatched immediately"
            if is_online
            else "manual relay command queued for offline module"
        ),
        retry_count=1 if is_online else 0,
        last_attempt_at=now if is_online else None,
    )
    db.add(command)
    await db.commit()
    await db.refresh(command)
    await realtime_service.broadcast(
        "relay_command.created",
        {
            "command_id": command.id,
            "alarm_record_id": command.alarm_record_id,
            "module_id": command.module_id,
            "command_source": command.command_source,
            "target_state": command.target_state,
            "execution_status": command.execution_status,
        },
        owner_id=module.device.owner_id if module.device else None,
    )
    return command


async def apply_relay_command_feedback(
    db: AsyncSession,
    command: RelayCommand,
    payload: RelayCommandFeedback,
) -> RelayCommand:
    command.execution_status = payload.execution_status
    command.feedback_status = payload.feedback_status
    command.feedback_message = payload.feedback_message
    command.executed_at = datetime.now(timezone.utc)
    command.execution_result = payload.feedback_message or command.execution_result
    await db.commit()
    await db.refresh(command)
    await realtime_service.broadcast(
        "relay_command.updated",
        {
            "command_id": command.id,
            "alarm_record_id": command.alarm_record_id,
            "module_id": command.module_id,
            "command_source": command.command_source,
            "target_state": command.target_state,
            "execution_status": command.execution_status,
            "feedback_status": command.feedback_status,
            "feedback_message": command.feedback_message,
            "executed_at": command.executed_at.isoformat() if command.executed_at else None,
        },
        owner_id=command.module.device.owner_id
        if command.module and command.module.device
        else None,
    )
    return command

import logging
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.module import Module
from app.services.linkage_service import retry_queued_relay_commands
from app.services.logging_service import write_runtime_log

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler(timezone="UTC")


async def mark_offline_modules() -> int:
    timeout_at = datetime.now(timezone.utc) - timedelta(
        seconds=settings.HEARTBEAT_TIMEOUT_SECONDS
    )
    async with AsyncSessionLocal() as session:
        stmt = select(Module).where(
            Module.is_online.is_(True),
            Module.last_seen_at.is_not(None),
            Module.last_seen_at < timeout_at,
        )
        modules = list((await session.execute(stmt)).scalars().all())
        for module in modules:
            module.is_online = False
        await session.commit()
        if modules:
            await write_runtime_log(
                session,
                level="INFO",
                event="offline_check",
                message=f"updated {len(modules)} modules to offline",
                context={"module_count": len(modules)},
            )
        if modules:
            logger.info("离线检测已更新 %s 个模块为离线状态", len(modules))
        return len(modules)


async def run_retry_pending_commands_job() -> dict[str, int]:
    async with AsyncSessionLocal() as session:
        result = await retry_queued_relay_commands(session)
        await write_runtime_log(
            session,
            level="INFO",
            event="retry_pending_commands",
            message=(
                f"scanned {result.total_scanned}, dispatched {result.dispatched_count}, "
                f"still queued {result.still_queued_count}"
            ),
            context=result.model_dump(),
        )
        logger.info(
            "补发扫描完成，总扫描 %s，已补发 %s，仍排队 %s",
            result.total_scanned,
            result.dispatched_count,
            result.still_queued_count,
        )
        return result.model_dump()


def start_scheduler() -> None:
    if scheduler.running:
        return

    scheduler.add_job(
        mark_offline_modules,
        "interval",
        seconds=settings.OFFLINE_CHECK_INTERVAL_SECONDS,
        id="mark-offline-modules",
        replace_existing=True,
    )
    scheduler.add_job(
        run_retry_pending_commands_job,
        "interval",
        seconds=settings.RETRY_PENDING_COMMANDS_INTERVAL_SECONDS,
        id="retry-pending-relay-commands",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("APScheduler 已启动")


def shutdown_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler 已停止")

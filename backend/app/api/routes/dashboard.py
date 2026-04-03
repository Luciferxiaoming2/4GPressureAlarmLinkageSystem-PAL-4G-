from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.dashboard import (
    DashboardAlarmItem,
    DashboardAlarmPage,
    DashboardCharts,
    DashboardDeviceDetail,
    DashboardHome,
    DashboardRelayCommandItem,
    DashboardRelayCommandPage,
    MiniProgramAlarmItem,
    MiniProgramAlarmPage,
    MiniProgramDeviceItem,
    MiniProgramHome,
)
from app.services.dashboard_service import (
    build_alarm_export_csv,
    build_command_export_csv,
    get_dashboard_alarm_page,
    get_dashboard_charts,
    get_dashboard_command_page,
    get_dashboard_device_detail,
    get_dashboard_home,
    get_miniprogram_home,
    get_my_alarm_page,
    list_dashboard_recent_alarms,
    list_dashboard_recent_commands,
    list_my_devices,
    list_my_recent_alarms,
)

router = APIRouter()


@router.get("/home", response_model=DashboardHome)
async def read_dashboard_home(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardHome:
    return await get_dashboard_home(db, current_user)


@router.get("/recent-alarms", response_model=list[DashboardAlarmItem])
async def read_dashboard_recent_alarms(
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DashboardAlarmItem]:
    return await list_dashboard_recent_alarms(db, current_user, limit=limit)


@router.get("/alarms/page", response_model=DashboardAlarmPage)
async def read_dashboard_alarm_page(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardAlarmPage:
    return await get_dashboard_alarm_page(db, current_user, limit=limit, offset=offset)


@router.get("/recent-commands", response_model=list[DashboardRelayCommandItem])
async def read_dashboard_recent_commands(
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DashboardRelayCommandItem]:
    return await list_dashboard_recent_commands(db, current_user, limit=limit)


@router.get("/commands/page", response_model=DashboardRelayCommandPage)
async def read_dashboard_command_page(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardRelayCommandPage:
    return await get_dashboard_command_page(db, current_user, limit=limit, offset=offset)


@router.get("/my/devices", response_model=list[MiniProgramDeviceItem])
async def read_my_devices(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[MiniProgramDeviceItem]:
    # 小程序更常用“我的设备”摘要视图，这里直接返回压平后的结构。
    return await list_my_devices(db, current_user)


@router.get("/my/home", response_model=MiniProgramHome)
async def read_my_home(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MiniProgramHome:
    return await get_miniprogram_home(db, current_user)


@router.get("/my/alarms", response_model=list[MiniProgramAlarmItem])
async def read_my_recent_alarms(
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[MiniProgramAlarmItem]:
    return await list_my_recent_alarms(db, current_user, limit=limit)


@router.get("/my/alarms/page", response_model=MiniProgramAlarmPage)
async def read_my_alarm_page(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MiniProgramAlarmPage:
    return await get_my_alarm_page(db, current_user, limit=limit, offset=offset)


@router.get("/charts", response_model=DashboardCharts)
async def read_dashboard_charts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardCharts:
    return await get_dashboard_charts(db, current_user)


@router.get("/devices/{device_id}", response_model=DashboardDeviceDetail)
async def read_dashboard_device_detail(
    device_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardDeviceDetail:
    detail = await get_dashboard_device_detail(db, current_user, device_id)
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return detail


@router.get("/alarms/export")
async def export_dashboard_alarms(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    items = await list_dashboard_recent_alarms(db, current_user, limit=500)
    content = build_alarm_export_csv(items).encode("utf-8-sig")
    return StreamingResponse(
        BytesIO(content),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="dashboard-alarms.csv"'},
    )


@router.get("/commands/export")
async def export_dashboard_commands(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    items = await list_dashboard_recent_commands(db, current_user, limit=500)
    content = build_command_export_csv(items).encode("utf-8-sig")
    return StreamingResponse(
        BytesIO(content),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="dashboard-commands.csv"'},
    )

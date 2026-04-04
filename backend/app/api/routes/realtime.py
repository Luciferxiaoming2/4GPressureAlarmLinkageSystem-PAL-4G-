from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select

from app.core.security import decode_access_token
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.services.realtime_service import realtime_service

router = APIRouter()


@router.websocket("/events")
async def websocket_events(
    websocket: WebSocket,
    token: str = Query(...),
) -> None:
    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
        if not username:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        async with AsyncSessionLocal() as db:
            user = (
                await db.execute(select(User).where(User.username == username))
            ).scalar_one_or_none()
            if not user or not user.is_active:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return

            await realtime_service.connect(websocket, user.id, user.role)

        while True:
            # 当前先保持简单长连接，前端可按需发送 ping 文本保活。
            await websocket.receive_text()
    except WebSocketDisconnect:
        realtime_service.disconnect(websocket)

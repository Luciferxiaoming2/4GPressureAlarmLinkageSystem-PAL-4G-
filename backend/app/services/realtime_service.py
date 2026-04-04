from datetime import datetime, timezone

from fastapi import WebSocket


class RealtimeConnectionManager:
    def __init__(self) -> None:
        self._connections: list[dict] = []

    async def connect(self, websocket: WebSocket, user_id: int, role: str) -> None:
        await websocket.accept()
        self._connections.append(
            {"websocket": websocket, "user_id": user_id, "role": role}
        )

    def disconnect(self, websocket: WebSocket) -> None:
        self._connections = [
            item for item in self._connections if item["websocket"] is not websocket
        ]

    async def broadcast(
        self,
        event: str,
        data: dict,
        owner_id: int | None = None,
    ) -> None:
        payload = {
            "event": event,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }

        stale_connections: list[WebSocket] = []
        for item in self._connections:
            if item["role"] != "super_admin" and owner_id != item["user_id"]:
                continue
            try:
                await item["websocket"].send_json(payload)
            except Exception:
                stale_connections.append(item["websocket"])

        for websocket in stale_connections:
            self.disconnect(websocket)


realtime_service = RealtimeConnectionManager()

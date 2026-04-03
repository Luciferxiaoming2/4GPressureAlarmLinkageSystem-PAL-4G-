from fastapi import APIRouter

from app.api.routes.alarms import router as alarms_router
from app.api.routes.auth import router as auth_router
from app.api.routes.devices import router as devices_router
from app.api.routes.health import router as health_router
from app.api.routes.users import router as users_router

api_router = APIRouter()
api_router.include_router(alarms_router, prefix="/alarms", tags=["alarms"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(devices_router, prefix="/devices", tags=["devices"])
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(users_router, prefix="/users", tags=["users"])

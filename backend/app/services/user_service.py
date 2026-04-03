from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def ensure_default_admin(db: AsyncSession) -> None:
    existing_admin = await get_user_by_username(db, settings.DEFAULT_ADMIN_USERNAME)
    if existing_admin:
        return

    admin = User(
        username=settings.DEFAULT_ADMIN_USERNAME,
        password_hash=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
        role="super_admin",
        is_active=True,
    )
    db.add(admin)
    await db.commit()

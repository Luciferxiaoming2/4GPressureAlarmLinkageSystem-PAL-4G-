from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models.device import Device
from app.models.device_group import DeviceGroup
from app.models.operation_log import OperationLog
from app.models.user import User
from app.schemas.user import UserChangePassword, UserCreate, UserResetPassword, UserUpdate


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def list_users(db: AsyncSession) -> list[User]:
    result = await db.execute(select(User).order_by(User.id.desc()))
    return list(result.scalars().all())


async def list_users_page(
    db: AsyncSession,
    limit: int = 20,
    offset: int = 0,
) -> tuple[int, list[User]]:
    count_stmt = select(func.count(User.id))
    stmt = select(User).order_by(User.id.desc()).limit(limit).offset(offset)
    total = (await db.execute(count_stmt)).scalar_one() or 0
    users = list((await db.execute(stmt)).scalars().all())
    return total, users


async def create_user(db: AsyncSession, payload: UserCreate) -> User:
    # 统一在服务层做密码哈希，避免路由层直接处理敏感字段。
    user = User(
        username=payload.username,
        password_hash=get_password_hash(payload.password),
        role=payload.role,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, user: User, payload: UserUpdate) -> User:
    # 仅更新显式传入的字段，避免 patch 请求把未传字段误覆盖。
    if payload.password:
        user.password_hash = get_password_hash(payload.password)
    if payload.role:
        user.role = payload.role
    if payload.is_active is not None:
        user.is_active = payload.is_active
    await db.commit()
    await db.refresh(user)
    return user


async def reset_user_password(
    db: AsyncSession,
    user: User,
    payload: UserResetPassword,
) -> User:
    # 管理员重置密码不要求旧密码，直接覆盖为新哈希。
    user.password_hash = get_password_hash(payload.new_password)
    await db.commit()
    await db.refresh(user)
    return user


async def change_user_password(
    db: AsyncSession,
    user: User,
    payload: UserChangePassword,
) -> User:
    # 用户自行修改密码时必须校验旧密码，避免 token 泄漏后被直接改密。
    if not verify_password(payload.current_password, user.password_hash):
        raise ValueError("Current password is incorrect")
    user.password_hash = get_password_hash(payload.new_password)
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user: User) -> None:
    # 安全删除前先校验该用户是否还挂着设备，避免把设备归属关系直接打断。
    owned_device_count = (
        await db.execute(
            select(func.count(Device.id)).where(Device.owner_id == user.id)
        )
    ).scalar_one()
    if owned_device_count > 0:
        raise ValueError("User still owns devices and cannot be deleted")

    # 设备分组也可能绑定 owner_id，删除前同样需要清掉这类阻塞关系。
    owned_group_count = (
        await db.execute(
            select(func.count(DeviceGroup.id)).where(DeviceGroup.owner_id == user.id)
        )
    ).scalar_one()
    if owned_group_count > 0:
        raise ValueError("User still owns device groups and cannot be deleted")

    # 操作日志保留历史，但把外键置空，避免删除用户时触发约束错误。
    await db.execute(
        update(OperationLog)
        .where(OperationLog.actor_user_id == user.id)
        .values(actor_user_id=None)
    )
    await db.execute(delete(User).where(User.id == user.id))
    await db.commit()


async def ensure_default_admin(db: AsyncSession) -> None:
    existing_admin = await get_user_by_username(db, settings.DEFAULT_ADMIN_USERNAME)
    if existing_admin:
        return

    # 默认管理员只在系统首次启动且不存在时创建一次。
    admin = User(
        username=settings.DEFAULT_ADMIN_USERNAME,
        password_hash=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
        role="super_admin",
        is_active=True,
    )
    db.add(admin)
    await db.commit()

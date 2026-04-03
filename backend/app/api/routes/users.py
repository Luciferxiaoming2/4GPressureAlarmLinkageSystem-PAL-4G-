from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.user_service import (
    create_user,
    get_user_by_id,
    get_user_by_username,
    list_users,
    update_user,
)

router = APIRouter()


@router.get("", response_model=list[UserRead])
async def read_users(
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> list[UserRead]:
    users = await list_users(db)
    return [UserRead.model_validate(user) for user in users]


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_new_user(
    payload: UserCreate,
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    existing = await get_user_by_username(db, payload.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )
    user = await create_user(db, payload)
    return UserRead.model_validate(user)


@router.get("/{user_id}", response_model=UserRead)
async def read_user(
    user_id: int,
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserRead.model_validate(user)


@router.patch("/{user_id}", response_model=UserRead)
async def patch_user(
    user_id: int,
    payload: UserUpdate,
    current_admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.id == current_admin.id and payload.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current admin cannot deactivate self",
        )
    updated_user = await update_user(db, user, payload)
    return UserRead.model_validate(updated_user)

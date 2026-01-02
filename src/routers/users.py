from fastapi import APIRouter, Depends, HTTPException
from src.dependencies import get_current_user
from src.schemas import UserView

users_router = APIRouter()


@users_router.get("/{user_id}")
async def read_user(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    current_id = current_user.get("sub") or current_user.get("id")
    if current_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this user")

    # Возвращаем минимальную информацию о текущем пользователе (в этой простой реализации)
    return UserView(
        id=current_id,
        name=current_user.get("name"),
        email=current_user.get("email"),
        preferred_username=current_user.get("preferred_username"),
    )
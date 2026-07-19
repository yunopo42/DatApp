from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies.auth import get_current_user
from app.api.schemas.auth import CurrentUserResponse
from app.models import User

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.get("/me", response_model=CurrentUserResponse)
async def get_my_profile(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.schemas.workspace import WorkspaceCreateRequest, WorkspaceResponse
from app.core.exceptions import ConflictError
from app.db.session import get_db_session
from app.models import User, Workspace
from app.services.workspace import WorkspaceService

router = APIRouter(prefix="/api/v1/workspaces", tags=["workspaces"])


@router.get("", response_model=list[WorkspaceResponse])
async def list_workspaces(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[Workspace]:
    return await WorkspaceService(session).list_workspaces_for_user(current_user.id)


@router.post(
    "",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_workspace(
    payload: WorkspaceCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Workspace:
    try:
        return await WorkspaceService(session).create_workspace(
            owner_user_id=current_user.id,
            name=payload.name,
            slug=payload.slug,
        )
    except ConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A workspace with this slug already exists",
        ) from exc

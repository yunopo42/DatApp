from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.schemas.workspace import WorkspaceCreateRequest, WorkspaceResponse
from app.core.exceptions import ConflictError
from app.db.session import get_db_session
from app.models import User
from app.models.enums import WorkspaceRole
from app.services.workspace import WorkspaceAccess, WorkspaceService

router = APIRouter(prefix="/api/v1/workspaces", tags=["workspaces"])


@router.get("", response_model=list[WorkspaceResponse])
async def list_workspaces(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[WorkspaceResponse]:
    access_rows = await WorkspaceService(session).list_workspace_access_for_user(
        current_user.id
    )
    return [_workspace_response(access) for access in access_rows]


@router.post(
    "",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_workspace(
    payload: WorkspaceCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> WorkspaceResponse:
    try:
        workspace = await WorkspaceService(session).create_workspace(
            owner_user_id=current_user.id,
            name=payload.name,
            slug=payload.slug,
        )
        return _workspace_response(
            WorkspaceAccess(workspace=workspace, role=WorkspaceRole.OWNER)
        )
    except ConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A workspace with this slug already exists",
        ) from exc


def _workspace_response(access: WorkspaceAccess) -> WorkspaceResponse:
    workspace = access.workspace
    return WorkspaceResponse(
        id=workspace.id,
        name=workspace.name,
        slug=workspace.slug,
        plan=workspace.plan,
        role=access.role,
        owner_user_id=workspace.owner_user_id,
        created_at=workspace.created_at,
        updated_at=workspace.updated_at,
    )

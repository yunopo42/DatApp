from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.schemas.project import ProjectCreateRequest, ProjectResponse
from app.core.exceptions import PermissionDeniedError, ResourceNotFoundError
from app.db.session import get_db_session
from app.models import Project, User
from app.services.project import ProjectService

router = APIRouter(
    prefix="/api/v1/workspaces/{workspace_id}/projects",
    tags=["projects"],
)


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    workspace_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[Project]:
    try:
        return await ProjectService(session).list_projects_for_user(
            workspace_id=workspace_id,
            user_id=current_user.id,
        )
    except ResourceNotFoundError as exc:
        raise _workspace_not_found() from exc


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    workspace_id: UUID,
    payload: ProjectCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Project:
    try:
        return await ProjectService(session).create_project(
            workspace_id=workspace_id,
            user_id=current_user.id,
            name=payload.name,
            description=payload.description,
        )
    except ResourceNotFoundError as exc:
        raise _workspace_not_found() from exc
    except PermissionDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Workspace role cannot create projects",
        ) from exc


def _workspace_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Workspace not found",
    )

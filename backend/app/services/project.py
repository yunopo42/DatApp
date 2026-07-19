from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import PermissionDeniedError, ResourceNotFoundError
from app.models import Project
from app.models.enums import ProjectStatus, WorkspaceRole
from app.repositories.project import ProjectRepository
from app.repositories.workspace import WorkspaceRepository

PROJECT_EDITOR_ROLES = frozenset(
    {
        WorkspaceRole.OWNER,
        WorkspaceRole.ADMIN,
        WorkspaceRole.EDITOR,
    }
)


class ProjectService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._projects = ProjectRepository(session)
        self._workspaces = WorkspaceRepository(session)

    async def create_project(
        self,
        *,
        workspace_id: UUID,
        user_id: UUID,
        name: str,
        description: str | None = None,
    ) -> Project:
        membership = await self._workspaces.get_membership(workspace_id, user_id)
        if membership is None:
            raise ResourceNotFoundError("Workspace not found")
        if membership.role not in PROJECT_EDITOR_ROLES:
            raise PermissionDeniedError("Workspace role cannot create projects")

        project = Project(
            workspace_id=workspace_id,
            created_by=user_id,
            name=name,
            description=description,
            status=ProjectStatus.ACTIVE,
        )
        self._projects.add(project)
        await self._session.flush()
        return project

    async def get_project_for_user(
        self,
        *,
        project_id: UUID,
        user_id: UUID,
    ) -> Project:
        project = await self._projects.get_for_member(project_id, user_id)
        if project is None:
            raise ResourceNotFoundError("Project not found")
        return project

    async def list_projects_for_user(
        self,
        *,
        workspace_id: UUID,
        user_id: UUID,
    ) -> list[Project]:
        workspace = await self._workspaces.get_for_member(workspace_id, user_id)
        if workspace is None:
            raise ResourceNotFoundError("Workspace not found")

        return await self._projects.list_for_workspace_member(workspace_id, user_id)

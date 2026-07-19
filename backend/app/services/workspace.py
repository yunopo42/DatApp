from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, ResourceNotFoundError
from app.models import Workspace, WorkspaceMember
from app.models.enums import WorkspaceRole
from app.repositories.workspace import WorkspaceRepository


class WorkspaceService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._workspaces = WorkspaceRepository(session)

    async def create_workspace(
        self,
        *,
        owner_user_id: UUID,
        name: str,
        slug: str,
    ) -> Workspace:
        if await self._workspaces.slug_exists(slug):
            raise ConflictError("A workspace with this slug already exists")

        workspace = Workspace(
            owner_user_id=owner_user_id,
            name=name,
            slug=slug,
        )
        membership = WorkspaceMember(
            workspace=workspace,
            user_id=owner_user_id,
            role=WorkspaceRole.OWNER,
        )

        self._workspaces.add(workspace)
        self._session.add(membership)
        await self._session.flush()
        return workspace

    async def list_workspaces_for_user(self, user_id: UUID) -> list[Workspace]:
        return await self._workspaces.list_for_member(user_id)

    async def get_workspace_for_user(
        self,
        *,
        workspace_id: UUID,
        user_id: UUID,
    ) -> Workspace:
        workspace = await self._workspaces.get_for_member(workspace_id, user_id)
        if workspace is None:
            raise ResourceNotFoundError("Workspace not found")
        return workspace

from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Workspace, WorkspaceMember
from app.models.enums import WorkspaceRole


class WorkspaceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, workspace: Workspace) -> None:
        self._session.add(workspace)

    async def slug_exists(self, slug: str) -> bool:
        statement = select(exists().where(Workspace.slug == slug))
        return bool(await self._session.scalar(statement))

    async def get_for_member(
        self,
        workspace_id: UUID,
        user_id: UUID,
    ) -> Workspace | None:
        statement = (
            select(Workspace)
            .join(
                WorkspaceMember,
                WorkspaceMember.workspace_id == Workspace.id,
            )
            .where(
                Workspace.id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
        )
        return await self._session.scalar(statement)

    async def list_for_member(self, user_id: UUID) -> list[Workspace]:
        statement = (
            select(Workspace)
            .join(
                WorkspaceMember,
                WorkspaceMember.workspace_id == Workspace.id,
            )
            .where(WorkspaceMember.user_id == user_id)
            .order_by(Workspace.created_at.desc(), Workspace.id)
        )
        return list(await self._session.scalars(statement))

    async def list_access_for_member(
        self,
        user_id: UUID,
    ) -> list[tuple[Workspace, WorkspaceRole]]:
        statement = (
            select(Workspace, WorkspaceMember.role)
            .join(
                WorkspaceMember,
                WorkspaceMember.workspace_id == Workspace.id,
            )
            .where(WorkspaceMember.user_id == user_id)
            .order_by(Workspace.created_at.desc(), Workspace.id)
        )
        rows = (await self._session.execute(statement)).all()
        return [(workspace, role) for workspace, role in rows]

    async def get_membership(
        self,
        workspace_id: UUID,
        user_id: UUID,
    ) -> WorkspaceMember | None:
        statement = select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
        return await self._session.scalar(statement)

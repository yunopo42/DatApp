from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Project, WorkspaceMember


class ProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, project: Project) -> None:
        self._session.add(project)

    async def get_for_member(
        self,
        project_id: UUID,
        user_id: UUID,
    ) -> Project | None:
        statement = (
            select(Project)
            .join(
                WorkspaceMember,
                WorkspaceMember.workspace_id == Project.workspace_id,
            )
            .where(
                Project.id == project_id,
                WorkspaceMember.user_id == user_id,
            )
        )
        return await self._session.scalar(statement)

    async def list_for_workspace_member(
        self,
        workspace_id: UUID,
        user_id: UUID,
    ) -> list[Project]:
        statement = (
            select(Project)
            .join(
                WorkspaceMember,
                WorkspaceMember.workspace_id == Project.workspace_id,
            )
            .where(
                Project.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
            .order_by(Project.created_at.desc(), Project.id)
        )
        result = await self._session.scalars(statement)
        return list(result.all())

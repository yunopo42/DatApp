from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, user: User) -> None:
        self._session.add(user)

    async def get_by_auth_provider_id(self, provider_id: str) -> User | None:
        statement = select(User).where(User.auth_provider_id == provider_id)
        return await self._session.scalar(statement)

    async def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        return await self._session.scalar(statement)

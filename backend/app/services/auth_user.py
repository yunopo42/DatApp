from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import AuthenticatedIdentity
from app.core.exceptions import AuthenticationError, ConflictError
from app.models import User
from app.repositories.user import UserRepository


class AuthUserService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._users = UserRepository(session)

    async def resolve_user(self, identity: AuthenticatedIdentity) -> User:
        existing_user = await self._users.get_by_auth_provider_id(identity.subject)
        if existing_user is not None:
            return existing_user

        email = (identity.email or "").strip().lower()
        if not email or len(email) > 320:
            raise AuthenticationError("A valid email claim is required")

        email_owner = await self._users.get_by_email(email)
        if email_owner is not None:
            raise ConflictError("Email belongs to another authentication identity")

        display_name = (
            identity.display_name or email.split("@", maxsplit=1)[0]
        ).strip()
        user = User(
            email=email,
            display_name=(display_name or "DatApp User")[:120],
            auth_provider_id=identity.subject,
        )
        self._users.add(user)
        await self._session.flush()
        return user

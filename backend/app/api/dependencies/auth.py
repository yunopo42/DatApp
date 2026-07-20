import logging
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.auth.models import AuthenticatedIdentity
from app.auth.verifier import get_token_verifier
from app.core.exceptions import (
    AuthConfigurationError,
    AuthenticationError,
    AuthProviderUnavailableError,
    ConflictError,
)
from app.db.session import get_db_session
from app.models import User
from app.services.auth_user import AuthUserService

bearer_scheme = HTTPBearer(auto_error=False)
logger = logging.getLogger(__name__)


async def get_current_identity(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> AuthenticatedIdentity:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _unauthorized()

    try:
        verifier = get_token_verifier()
        return await run_in_threadpool(verifier.verify, credentials.credentials)
    except AuthenticationError as exc:
        raise _unauthorized() from exc
    except AuthConfigurationError as exc:
        logger.error("Authentication configuration is incomplete")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        ) from exc
    except AuthProviderUnavailableError as exc:
        logger.warning("Authentication provider JWKS is unavailable")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        ) from exc


async def get_current_user(
    identity: Annotated[AuthenticatedIdentity, Depends(get_current_identity)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> User:
    try:
        return await AuthUserService(session).resolve_user(identity)
    except AuthenticationError as exc:
        raise _unauthorized() from exc
    except ConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account identity conflict",
        ) from exc


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

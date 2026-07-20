from functools import lru_cache
from typing import Any, Protocol

import jwt
from jwt import PyJWKClient
from jwt.exceptions import (
    InvalidTokenError,
    PyJWKClientConnectionError,
    PyJWKClientError,
)

from app.auth.models import AuthenticatedIdentity
from app.core.config import get_settings
from app.core.exceptions import (
    AuthConfigurationError,
    AuthenticationError,
    AuthProviderUnavailableError,
)


class SigningKey(Protocol):
    key: Any


class SigningKeyClient(Protocol):
    def get_signing_key_from_jwt(self, token: str) -> SigningKey: ...


class OIDCTokenVerifier:
    def __init__(
        self,
        *,
        issuer: str,
        audience: str,
        jwks_url: str,
        algorithm: str,
        jwks_client: SigningKeyClient | None = None,
    ) -> None:
        self._issuer = issuer
        self._audience = audience
        self._algorithm = algorithm
        self._jwks_client = jwks_client or PyJWKClient(
            jwks_url,
            cache_keys=True,
            cache_jwk_set=True,
            lifespan=300,
            timeout=5,
        )

    def verify(self, token: str) -> AuthenticatedIdentity:
        try:
            signing_key = self._jwks_client.get_signing_key_from_jwt(token)
            claims = jwt.decode(
                token,
                signing_key.key,
                algorithms=[self._algorithm],
                audience=self._audience,
                issuer=self._issuer,
                options={
                    "require": ["aud", "exp", "iat", "iss", "sub"],
                    "strict_aud": True,
                },
            )
        except PyJWKClientConnectionError as exc:
            raise AuthProviderUnavailableError(
                "Authentication provider is unavailable"
            ) from exc
        except (InvalidTokenError, PyJWKClientError) as exc:
            raise AuthenticationError("Invalid authentication token") from exc

        subject_claim = claims["sub"]
        if not isinstance(subject_claim, str):
            raise AuthenticationError("Invalid authentication subject")

        subject = subject_claim.strip()
        if not subject or len(subject) > 255:
            raise AuthenticationError("Invalid authentication subject")

        email_claim = claims.get("email")
        name_claim = claims.get("name")
        user_metadata_claim = claims.get("user_metadata")
        if not isinstance(name_claim, str) and isinstance(user_metadata_claim, dict):
            name_claim = user_metadata_claim.get("display_name") or (
                user_metadata_claim.get("full_name")
            )
        email = email_claim if isinstance(email_claim, str) else None
        display_name = name_claim if isinstance(name_claim, str) else None

        return AuthenticatedIdentity(
            subject=subject,
            email=email,
            display_name=display_name,
        )


@lru_cache
def get_token_verifier() -> OIDCTokenVerifier:
    settings = get_settings()
    if (
        not settings.auth_issuer
        or not settings.auth_audience
        or not settings.auth_jwks_url
    ):
        raise AuthConfigurationError("Managed authentication is not configured")

    return OIDCTokenVerifier(
        issuer=settings.auth_issuer,
        audience=settings.auth_audience,
        jwks_url=settings.auth_jwks_url,
        algorithm=settings.auth_algorithm,
    )

from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from jwt.exceptions import PyJWKClientConnectionError

import app.api.dependencies.auth as auth_dependencies
from app.auth.models import AuthenticatedIdentity
from app.auth.verifier import OIDCTokenVerifier
from app.core.exceptions import (
    AuthConfigurationError,
    AuthenticationError,
    AuthProviderUnavailableError,
)

ISSUER = "https://issuer.example.com/"
AUDIENCE = "datapp-api"


class StaticSigningKey:
    def __init__(self, key) -> None:
        self.key = key


class StaticSigningKeyClient:
    def __init__(self, key) -> None:
        self._key = key

    def get_signing_key_from_jwt(self, token: str) -> StaticSigningKey:
        return StaticSigningKey(self._key)


class UnavailableSigningKeyClient:
    def get_signing_key_from_jwt(self, token: str) -> StaticSigningKey:
        raise PyJWKClientConnectionError("JWKS endpoint unavailable")


@pytest.fixture(scope="module")
def rsa_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private_key, private_key.public_key()


def build_token(private_key, **claim_overrides) -> str:
    now = datetime.now(UTC)
    claims = {
        "iss": ISSUER,
        "aud": AUDIENCE,
        "sub": "managed-user-123",
        "iat": now,
        "exp": now + timedelta(minutes=5),
        "email": "User@Example.com",
        "name": "Managed User",
    }
    claims.update(claim_overrides)
    return jwt.encode(
        claims,
        private_key,
        algorithm="RS256",
        headers={"kid": "test-key"},
    )


def build_verifier(public_key) -> OIDCTokenVerifier:
    return OIDCTokenVerifier(
        issuer=ISSUER,
        audience=AUDIENCE,
        jwks_url="https://issuer.example.com/.well-known/jwks.json",
        algorithm="RS256",
        jwks_client=StaticSigningKeyClient(public_key),
    )


def test_verifier_accepts_valid_signed_token(rsa_keys) -> None:
    private_key, public_key = rsa_keys

    identity = build_verifier(public_key).verify(build_token(private_key))

    assert identity.subject == "managed-user-123"
    assert identity.email == "User@Example.com"
    assert identity.display_name == "Managed User"


def test_verifier_rejects_wrong_audience(rsa_keys) -> None:
    private_key, public_key = rsa_keys
    token = build_token(private_key, aud="another-api")

    with pytest.raises(AuthenticationError):
        build_verifier(public_key).verify(token)


def test_verifier_requires_expiration_claim(rsa_keys) -> None:
    private_key, public_key = rsa_keys
    token = build_token(private_key)
    claims = jwt.decode(token, options={"verify_signature": False})
    claims.pop("exp")
    token_without_expiration = jwt.encode(
        claims,
        private_key,
        algorithm="RS256",
        headers={"kid": "test-key"},
    )

    with pytest.raises(AuthenticationError):
        build_verifier(public_key).verify(token_without_expiration)


def test_verifier_rejects_non_string_subject(rsa_keys) -> None:
    private_key, public_key = rsa_keys
    token = build_token(private_key, sub=123)

    with pytest.raises(AuthenticationError):
        build_verifier(public_key).verify(token)


def test_verifier_maps_jwks_outage_to_provider_unavailable() -> None:
    verifier = OIDCTokenVerifier(
        issuer=ISSUER,
        audience=AUDIENCE,
        jwks_url="https://issuer.example.com/.well-known/jwks.json",
        algorithm="RS256",
        jwks_client=UnavailableSigningKeyClient(),
    )

    with pytest.raises(AuthProviderUnavailableError):
        verifier.verify("opaque-token")


def build_protected_test_app() -> FastAPI:
    test_app = FastAPI()

    @test_app.get("/protected")
    async def protected_route(
        identity: Annotated[
            AuthenticatedIdentity,
            Depends(auth_dependencies.get_current_identity),
        ],
    ) -> dict[str, str]:
        return {"subject": identity.subject}

    return test_app


def test_protected_route_requires_bearer_credentials() -> None:
    with TestClient(build_protected_test_app()) as client:
        response = client.get("/protected")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.json() == {
        "detail": "Invalid or missing authentication credentials"
    }


def test_protected_route_hides_auth_configuration_details(monkeypatch) -> None:
    def unavailable_verifier() -> OIDCTokenVerifier:
        raise AuthConfigurationError("AUTH_ISSUER is missing")

    monkeypatch.setattr(
        auth_dependencies,
        "get_token_verifier",
        unavailable_verifier,
    )

    with TestClient(build_protected_test_app()) as client:
        response = client.get(
            "/protected",
            headers={"Authorization": "Bearer opaque-token"},
        )

    assert response.status_code == 503
    assert response.json() == {"detail": "Authentication service unavailable"}

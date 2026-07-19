from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.dependencies.auth import get_current_user
from app.main import app
from app.models import User
from app.models.enums import UserStatus


def test_current_user_endpoint_returns_safe_profile() -> None:
    now = datetime.now(UTC)
    user_id = uuid4()
    user = User(
        id=user_id,
        email="user@example.com",
        display_name="DatApp User",
        auth_provider_id="provider-private-subject",
        status=UserStatus.ACTIVE,
        locale="en",
        created_at=now,
        updated_at=now,
    )
    app.dependency_overrides[get_current_user] = lambda: user

    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/auth/me")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "id": str(user_id),
        "email": "user@example.com",
        "display_name": "DatApp User",
        "status": "active",
        "locale": "en",
        "created_at": now.isoformat().replace("+00:00", "Z"),
        "updated_at": now.isoformat().replace("+00:00", "Z"),
    }
    assert "auth_provider_id" not in response.json()


def test_current_user_endpoint_requires_authentication() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"

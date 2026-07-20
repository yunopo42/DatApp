from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

import app.api.routes.workspaces as workspace_routes
from app.api.dependencies.auth import get_current_user
from app.core.exceptions import ConflictError
from app.db.session import get_db_session
from app.main import app
from app.models import User, Workspace
from app.models.enums import WorkspaceRole
from app.services.workspace import WorkspaceAccess


class FakeWorkspaceService:
    def __init__(self, workspace: Workspace) -> None:
        self.workspace = workspace
        self.created_with: dict[str, object] | None = None

    async def list_workspace_access_for_user(
        self,
        user_id: UUID,
    ) -> list[WorkspaceAccess]:
        assert user_id == self.workspace.owner_user_id
        return [
            WorkspaceAccess(
                workspace=self.workspace,
                role=WorkspaceRole.VIEWER,
            )
        ]

    async def create_workspace(self, **values) -> Workspace:
        self.created_with = values
        return self.workspace


class ConflictingWorkspaceService(FakeWorkspaceService):
    async def create_workspace(self, **values) -> Workspace:
        raise ConflictError("slug collision")


def build_workspace() -> Workspace:
    now = datetime.now(UTC)
    owner_id = uuid4()
    return Workspace(
        id=uuid4(),
        name="Research Lab",
        slug="research-lab",
        plan="free",
        owner_user_id=owner_id,
        created_at=now,
        updated_at=now,
    )


def configure_workspace_overrides(
    monkeypatch,
    service: FakeWorkspaceService,
) -> None:
    user = User(id=service.workspace.owner_user_id)
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db_session] = lambda: object()
    monkeypatch.setattr(
        workspace_routes,
        "WorkspaceService",
        lambda session: service,
    )


def test_workspace_endpoints_list_and_create_for_current_user(monkeypatch) -> None:
    workspace = build_workspace()
    service = FakeWorkspaceService(workspace)
    configure_workspace_overrides(monkeypatch, service)

    try:
        with TestClient(app) as client:
            list_response = client.get("/api/v1/workspaces")
            create_response = client.post(
                "/api/v1/workspaces",
                json={"name": "  Research   Lab  ", "slug": "research-lab"},
            )
    finally:
        app.dependency_overrides.clear()

    assert list_response.status_code == 200
    assert list_response.json()[0]["id"] == str(workspace.id)
    assert list_response.json()[0]["role"] == "viewer"
    assert create_response.status_code == 201
    assert create_response.json()["slug"] == "research-lab"
    assert create_response.json()["role"] == "owner"
    assert service.created_with == {
        "owner_user_id": workspace.owner_user_id,
        "name": "Research Lab",
        "slug": "research-lab",
    }


def test_create_workspace_rejects_invalid_slug(monkeypatch) -> None:
    service = FakeWorkspaceService(build_workspace())
    configure_workspace_overrides(monkeypatch, service)

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/workspaces",
                json={"name": "Research Lab", "slug": "Invalid Slug!"},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    assert service.created_with is None


def test_create_workspace_returns_safe_conflict(monkeypatch) -> None:
    workspace = build_workspace()
    service = ConflictingWorkspaceService(workspace)
    configure_workspace_overrides(monkeypatch, service)

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/workspaces",
                json={"name": "Research Lab", "slug": "research-lab"},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json() == {"detail": "A workspace with this slug already exists"}


def test_workspace_endpoints_require_authentication() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/workspaces")

    assert response.status_code == 401

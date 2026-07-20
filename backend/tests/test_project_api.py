from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

import app.api.routes.projects as project_routes
from app.api.dependencies.auth import get_current_user
from app.core.exceptions import PermissionDeniedError, ResourceNotFoundError
from app.db.session import get_db_session
from app.main import app
from app.models import Project, User
from app.models.enums import ProjectStatus


class FakeProjectService:
    def __init__(self, project: Project) -> None:
        self.project = project
        self.created_with: dict[str, object] | None = None

    async def list_projects_for_user(self, **values) -> list[Project]:
        assert values == {
            "workspace_id": self.project.workspace_id,
            "user_id": self.project.created_by,
        }
        return [self.project]

    async def create_project(self, **values) -> Project:
        self.created_with = values
        return self.project


class ForbiddenProjectService(FakeProjectService):
    async def create_project(self, **values) -> Project:
        raise PermissionDeniedError("viewer cannot create projects")


class MissingWorkspaceProjectService(FakeProjectService):
    async def list_projects_for_user(self, **values) -> list[Project]:
        raise ResourceNotFoundError("workspace not found")


def build_project() -> Project:
    now = datetime.now(UTC)
    return Project(
        id=uuid4(),
        workspace_id=uuid4(),
        name="Customer Analysis",
        description="Review customer retention data.",
        status=ProjectStatus.ACTIVE,
        created_by=uuid4(),
        created_at=now,
        updated_at=now,
    )


def configure_project_overrides(monkeypatch, service: FakeProjectService) -> None:
    user = User(id=service.project.created_by)
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db_session] = lambda: object()
    monkeypatch.setattr(
        project_routes,
        "ProjectService",
        lambda session: service,
    )


def project_url(workspace_id: UUID) -> str:
    return f"/api/v1/workspaces/{workspace_id}/projects"


def test_project_endpoints_list_and_create_for_workspace_member(monkeypatch) -> None:
    project = build_project()
    service = FakeProjectService(project)
    configure_project_overrides(monkeypatch, service)

    try:
        with TestClient(app) as client:
            list_response = client.get(project_url(project.workspace_id))
            create_response = client.post(
                project_url(project.workspace_id),
                json={
                    "name": "  Customer   Analysis  ",
                    "description": "  Review customer retention data.  ",
                },
            )
    finally:
        app.dependency_overrides.clear()

    assert list_response.status_code == 200
    assert list_response.json()[0]["id"] == str(project.id)
    assert create_response.status_code == 201
    assert create_response.json()["status"] == "active"
    assert service.created_with == {
        "workspace_id": project.workspace_id,
        "user_id": project.created_by,
        "name": "Customer Analysis",
        "description": "Review customer retention data.",
    }


def test_create_project_rejects_invalid_payload(monkeypatch) -> None:
    project = build_project()
    service = FakeProjectService(project)
    configure_project_overrides(monkeypatch, service)

    try:
        with TestClient(app) as client:
            response = client.post(
                project_url(project.workspace_id),
                json={"name": "   ", "description": "x" * 2001},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    assert service.created_with is None


def test_viewer_cannot_create_project(monkeypatch) -> None:
    project = build_project()
    service = ForbiddenProjectService(project)
    configure_project_overrides(monkeypatch, service)

    try:
        with TestClient(app) as client:
            response = client.post(
                project_url(project.workspace_id),
                json={"name": "Forbidden Project"},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403
    assert response.json() == {"detail": "Workspace role cannot create projects"}


def test_outsider_cannot_discover_workspace_projects(monkeypatch) -> None:
    project = build_project()
    service = MissingWorkspaceProjectService(project)
    configure_project_overrides(monkeypatch, service)

    try:
        with TestClient(app) as client:
            response = client.get(project_url(project.workspace_id))
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {"detail": "Workspace not found"}


def test_project_endpoints_require_authentication() -> None:
    with TestClient(app) as client:
        response = client.get(project_url(uuid4()))

    assert response.status_code == 401

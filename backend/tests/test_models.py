from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, configure_mappers

from app.db.base import Base
from app.models import Project, User, Workspace, WorkspaceMember
from app.models.enums import WorkspaceRole


def test_model_metadata_contains_domain_tables() -> None:
    configure_mappers()

    assert set(Base.metadata.tables) == {
        "projects",
        "users",
        "workspace_members",
        "workspaces",
    }
    assert Base.metadata.naming_convention["pk"] == "pk_%(table_name)s"


@pytest.mark.integration
def test_identity_and_project_graph_uses_transaction_rollback(
    db_session: Session,
) -> None:
    suffix = uuid4().hex
    user = User(
        email=f"integration-{suffix}@example.com",
        display_name="Integration User",
        auth_provider_id=f"integration-provider-{suffix}",
    )
    workspace = Workspace(
        name="Integration Workspace",
        slug=f"integration-{suffix}",
        owner=user,
    )
    membership = WorkspaceMember(
        workspace=workspace,
        user=user,
        role=WorkspaceRole.OWNER,
    )
    project = Project(
        workspace=workspace,
        creator=user,
        name="Integration Project",
        description="Created inside a rolled-back test transaction.",
    )

    db_session.add_all([user, workspace, membership, project])
    db_session.flush()

    loaded_project = db_session.scalar(select(Project).where(Project.id == project.id))

    assert loaded_project is not None
    assert loaded_project.workspace.owner.id == user.id
    assert loaded_project.creator.id == user.id
    assert workspace.memberships == [membership]

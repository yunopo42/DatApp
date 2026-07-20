import asyncio
import sys
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session

from app.auth.models import AuthenticatedIdentity
from app.core.config import get_settings
from app.core.exceptions import (
    AuthenticationError,
    ConflictError,
    PermissionDeniedError,
    ResourceNotFoundError,
)
from app.models import User, WorkspaceMember
from app.models.enums import WorkspaceRole
from app.services.auth_user import AuthUserService
from app.services.project import ProjectService
from app.services.workspace import WorkspaceService


def run_async(coroutine):
    if sys.platform == "win32":
        return asyncio.run(coroutine, loop_factory=asyncio.SelectorEventLoop)
    return asyncio.run(coroutine)


@pytest.mark.integration
def test_workspace_and_project_services_enforce_scope_and_roles() -> None:
    suffix = uuid4().hex
    run_async(run_service_scenario(suffix))

    engine = create_engine(get_settings().database_url.get_secret_value())
    with Session(engine) as verification_session:
        remaining_users = verification_session.scalar(
            select(func.count())
            .select_from(User)
            .where(User.email.like(f"service-{suffix}-%"))
        )
    engine.dispose()

    assert remaining_users == 0


@pytest.mark.integration
def test_auth_user_provisioning_prevents_identity_collision() -> None:
    suffix = uuid4().hex
    run_async(run_auth_user_scenario(suffix))

    engine = create_engine(get_settings().database_url.get_secret_value())
    with Session(engine) as verification_session:
        remaining_users = verification_session.scalar(
            select(func.count())
            .select_from(User)
            .where(User.email.like(f"auth-{suffix}-%"))
        )
    engine.dispose()

    assert remaining_users == 0


async def run_service_scenario(suffix: str) -> None:
    engine = create_async_engine(get_settings().database_url.get_secret_value())

    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection, expire_on_commit=False)

        try:
            owner = User(
                email=f"service-{suffix}-owner@example.com",
                display_name="Owner",
                auth_provider_id=f"service-{suffix}-owner",
            )
            viewer = User(
                email=f"service-{suffix}-viewer@example.com",
                display_name="Viewer",
                auth_provider_id=f"service-{suffix}-viewer",
            )
            outsider = User(
                email=f"service-{suffix}-outsider@example.com",
                display_name="Outsider",
                auth_provider_id=f"service-{suffix}-outsider",
            )
            session.add_all([owner, viewer, outsider])
            await session.flush()

            workspace_service = WorkspaceService(session)
            project_service = ProjectService(session)
            workspace = await workspace_service.create_workspace(
                owner_user_id=owner.id,
                name="Service Test Workspace",
                slug=f"service-{suffix}",
            )
            viewer_membership = WorkspaceMember(
                workspace_id=workspace.id,
                user_id=viewer.id,
                role=WorkspaceRole.VIEWER,
            )
            session.add(viewer_membership)
            await session.flush()

            project = await project_service.create_project(
                workspace_id=workspace.id,
                user_id=owner.id,
                name="Authorized Project",
            )

            owner_workspace = await workspace_service.get_workspace_for_user(
                workspace_id=workspace.id,
                user_id=owner.id,
            )
            owner_workspaces = await workspace_service.list_workspaces_for_user(
                owner.id
            )
            owner_access = await workspace_service.list_workspace_access_for_user(
                owner.id
            )
            viewer_workspaces = await workspace_service.list_workspaces_for_user(
                viewer.id
            )
            viewer_access = await workspace_service.list_workspace_access_for_user(
                viewer.id
            )
            outsider_workspaces = await workspace_service.list_workspaces_for_user(
                outsider.id
            )
            viewer_project = await project_service.get_project_for_user(
                project_id=project.id,
                user_id=viewer.id,
            )
            viewer_projects = await project_service.list_projects_for_user(
                workspace_id=workspace.id,
                user_id=viewer.id,
            )

            assert owner_workspace.id == workspace.id
            assert [item.id for item in owner_workspaces] == [workspace.id]
            assert owner_access[0].workspace.id == workspace.id
            assert owner_access[0].role == WorkspaceRole.OWNER
            assert [item.id for item in viewer_workspaces] == [workspace.id]
            assert viewer_access[0].workspace.id == workspace.id
            assert viewer_access[0].role == WorkspaceRole.VIEWER
            assert outsider_workspaces == []
            assert viewer_project.id == project.id
            assert [item.id for item in viewer_projects] == [project.id]

            with pytest.raises(PermissionDeniedError):
                await project_service.create_project(
                    workspace_id=workspace.id,
                    user_id=viewer.id,
                    name="Forbidden Project",
                )

            with pytest.raises(ResourceNotFoundError):
                await workspace_service.get_workspace_for_user(
                    workspace_id=workspace.id,
                    user_id=outsider.id,
                )

            with pytest.raises(ResourceNotFoundError):
                await project_service.get_project_for_user(
                    project_id=project.id,
                    user_id=outsider.id,
                )

            with pytest.raises(ConflictError):
                await workspace_service.create_workspace(
                    owner_user_id=owner.id,
                    name="Duplicate Workspace",
                    slug=workspace.slug,
                )
        finally:
            await session.close()
            if transaction.is_active:
                await transaction.rollback()

    await engine.dispose()


async def run_auth_user_scenario(suffix: str) -> None:
    engine = create_async_engine(get_settings().database_url.get_secret_value())

    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection, expire_on_commit=False)

        try:
            service = AuthUserService(session)
            identity = AuthenticatedIdentity(
                subject=f"auth-provider-{suffix}-primary",
                email=f"AUTH-{suffix}-USER@EXAMPLE.COM",
                display_name="Managed User",
            )
            provisioned_user = await service.resolve_user(identity)
            resolved_again = await service.resolve_user(identity)

            assert provisioned_user.id == resolved_again.id
            assert provisioned_user.email == f"auth-{suffix}-user@example.com"

            with pytest.raises(ConflictError):
                await service.resolve_user(
                    AuthenticatedIdentity(
                        subject=f"auth-provider-{suffix}-collision",
                        email=identity.email,
                        display_name="Conflicting User",
                    )
                )

            with pytest.raises(AuthenticationError):
                await service.resolve_user(
                    AuthenticatedIdentity(
                        subject=f"auth-provider-{suffix}-missing-email",
                        email=None,
                        display_name=None,
                    )
                )
        finally:
            await session.close()
            if transaction.is_active:
                await transaction.rollback()

    await engine.dispose()

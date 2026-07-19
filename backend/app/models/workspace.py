from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import WorkspaceRole, enum_values

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import User


class Workspace(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(63),
        nullable=False,
        unique=True,
        index=True,
    )
    owner_user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    plan: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="free",
        server_default="free",
    )

    owner: Mapped["User"] = relationship(
        back_populates="owned_workspaces",
        foreign_keys=[owner_user_id],
    )
    memberships: Mapped[list["WorkspaceMember"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    projects: Mapped[list["Project"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class WorkspaceMember(Base):
    __tablename__ = "workspace_members"

    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    role: Mapped[WorkspaceRole] = mapped_column(
        Enum(
            WorkspaceRole,
            name="workspace_role",
            native_enum=False,
            create_constraint=True,
            values_callable=enum_values,
        ),
        nullable=False,
        default=WorkspaceRole.VIEWER,
        server_default=WorkspaceRole.VIEWER.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    workspace: Mapped[Workspace] = relationship(back_populates="memberships")
    user: Mapped["User"] = relationship(back_populates="workspace_memberships")

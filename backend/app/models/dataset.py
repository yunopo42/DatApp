from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import (
    DatasetStatus,
    StoredFileKind,
    StoredFileStatus,
    enum_values,
)

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import User


class Dataset(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "datasets"

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    status: Mapped[DatasetStatus] = mapped_column(
        Enum(
            DatasetStatus,
            name="dataset_status",
            native_enum=False,
            create_constraint=True,
            values_callable=enum_values,
        ),
        nullable=False,
        default=DatasetStatus.PENDING,
        server_default=DatasetStatus.PENDING.value,
    )
    created_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    project: Mapped["Project"] = relationship(back_populates="datasets")
    creator: Mapped["User"] = relationship(
        back_populates="created_datasets",
        foreign_keys=[created_by],
    )
    files: Mapped[list["StoredFile"]] = relationship(
        back_populates="dataset",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="StoredFile.version_number",
    )


class StoredFile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "stored_files"
    __table_args__ = (
        UniqueConstraint("dataset_id", "version_number"),
        CheckConstraint(
            "version_number >= 1",
            name="ck_stored_files_version_number_positive",
        ),
        CheckConstraint(
            "size_bytes >= 0",
            name="ck_stored_files_size_bytes_nonnegative",
        ),
        CheckConstraint(
            "char_length(sha256) = 64",
            name="ck_stored_files_sha256_length",
        ),
    )

    dataset_id: Mapped[UUID] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
    )
    storage_key: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        unique=True,
        index=True,
    )
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    kind: Mapped[StoredFileKind] = mapped_column(
        Enum(
            StoredFileKind,
            name="stored_file_kind",
            native_enum=False,
            create_constraint=True,
            values_callable=enum_values,
        ),
        nullable=False,
    )
    media_type: Mapped[str] = mapped_column(String(127), nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[StoredFileStatus] = mapped_column(
        Enum(
            StoredFileStatus,
            name="stored_file_status",
            native_enum=False,
            create_constraint=True,
            values_callable=enum_values,
        ),
        nullable=False,
        default=StoredFileStatus.PENDING,
        server_default=StoredFileStatus.PENDING.value,
    )
    created_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    dataset: Mapped[Dataset] = relationship(back_populates="files")
    uploader: Mapped["User"] = relationship(
        back_populates="uploaded_files",
        foreign_keys=[created_by],
    )

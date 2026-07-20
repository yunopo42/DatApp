from enum import StrEnum


class UserStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class WorkspaceRole(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class ProjectStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class DatasetStatus(StrEnum):
    PENDING = "pending"
    UPLOADED = "uploaded"
    VALIDATING = "validating"
    READY = "ready"
    FAILED = "failed"
    ARCHIVED = "archived"


class StoredFileKind(StrEnum):
    CSV = "csv"
    XLSX = "xlsx"


class StoredFileStatus(StrEnum):
    PENDING = "pending"
    AVAILABLE = "available"
    DELETED = "deleted"


def enum_values(enum_class: type[StrEnum]) -> list[str]:
    return [member.value for member in enum_class]

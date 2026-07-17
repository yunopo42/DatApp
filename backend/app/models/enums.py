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


def enum_values(enum_class: type[StrEnum]) -> list[str]:
    return [member.value for member in enum_class]

from dataclasses import dataclass
from pathlib import Path
from uuid import UUID, uuid4

from app.core.exceptions import UploadValidationError
from app.models.enums import StoredFileKind

MAX_FILENAME_LENGTH = 255

ALLOWED_MEDIA_TYPES: dict[StoredFileKind, frozenset[str]] = {
    StoredFileKind.CSV: frozenset(
        {
            "application/csv",
            "text/csv",
        }
    ),
    StoredFileKind.XLSX: frozenset(
        {
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }
    ),
}

FILE_KIND_BY_SUFFIX = {
    ".csv": StoredFileKind.CSV,
    ".xlsx": StoredFileKind.XLSX,
}


@dataclass(frozen=True, slots=True)
class ValidatedUploadMetadata:
    original_filename: str
    kind: StoredFileKind
    media_type: str
    size_bytes: int


def validate_upload_metadata(
    *,
    filename: str,
    media_type: str | None,
    size_bytes: int,
    max_size_bytes: int,
) -> ValidatedUploadMetadata:
    safe_filename = _validate_filename(filename)

    if size_bytes <= 0:
        raise UploadValidationError("The uploaded file is empty")
    if size_bytes > max_size_bytes:
        raise UploadValidationError("The uploaded file exceeds the size limit")

    suffix = Path(safe_filename).suffix.lower()
    kind = FILE_KIND_BY_SUFFIX.get(suffix)
    if kind is None:
        raise UploadValidationError("Only CSV and XLSX files are supported")

    normalized_media_type = _normalize_media_type(media_type)
    if normalized_media_type not in ALLOWED_MEDIA_TYPES[kind]:
        raise UploadValidationError(
            "The file content type does not match its extension"
        )

    return ValidatedUploadMetadata(
        original_filename=safe_filename,
        kind=kind,
        media_type=normalized_media_type,
        size_bytes=size_bytes,
    )


def build_storage_key(
    *,
    workspace_id: UUID,
    project_id: UUID,
    dataset_id: UUID,
    version_number: int,
    kind: StoredFileKind,
) -> str:
    if version_number < 1:
        raise ValueError("version_number must be positive")

    generated_name = f"{uuid4().hex}.{kind.value}"
    return "/".join(
        (
            "workspaces",
            str(workspace_id),
            "projects",
            str(project_id),
            "datasets",
            str(dataset_id),
            f"v{version_number}",
            generated_name,
        )
    )


def _validate_filename(filename: str) -> str:
    normalized = filename.strip()
    if not normalized:
        raise UploadValidationError("A filename is required")
    if len(normalized) > MAX_FILENAME_LENGTH:
        raise UploadValidationError("The filename is too long")
    if "/" in normalized or "\\" in normalized:
        raise UploadValidationError("The filename cannot contain a path")
    if normalized in {".", ".."}:
        raise UploadValidationError("The filename is invalid")
    if any(ord(character) < 32 or ord(character) == 127 for character in normalized):
        raise UploadValidationError("The filename contains invalid characters")
    return normalized


def _normalize_media_type(media_type: str | None) -> str:
    if media_type is None:
        return ""
    return media_type.partition(";")[0].strip().lower()

from uuid import uuid4

import pytest

from app.core.exceptions import UploadValidationError
from app.file_storage.policy import build_storage_key, validate_upload_metadata
from app.models.enums import StoredFileKind


@pytest.mark.parametrize(
    ("filename", "media_type", "expected_kind"),
    [
        ("customers.CSV", "text/csv; charset=utf-8", StoredFileKind.CSV),
        (
            "sales.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            StoredFileKind.XLSX,
        ),
    ],
)
def test_upload_policy_accepts_supported_metadata(
    filename: str,
    media_type: str,
    expected_kind: StoredFileKind,
) -> None:
    metadata = validate_upload_metadata(
        filename=filename,
        media_type=media_type,
        size_bytes=1024,
        max_size_bytes=2048,
    )

    assert metadata.original_filename == filename
    assert metadata.kind == expected_kind
    assert metadata.size_bytes == 1024


@pytest.mark.parametrize(
    ("filename", "media_type", "size_bytes", "message"),
    [
        ("", "text/csv", 10, "filename"),
        ("../secret.csv", "text/csv", 10, "path"),
        ("bad\x00name.csv", "text/csv", 10, "invalid characters"),
        (f"{'a' * 252}.csv", "text/csv", 10, "too long"),
        ("data.exe", "application/octet-stream", 10, "CSV and XLSX"),
        ("data.csv", "application/octet-stream", 10, "content type"),
        ("data.csv", "text/csv", 0, "empty"),
        ("data.csv", "text/csv", 2049, "size limit"),
    ],
)
def test_upload_policy_rejects_unsafe_metadata(
    filename: str,
    media_type: str,
    size_bytes: int,
    message: str,
) -> None:
    with pytest.raises(UploadValidationError, match=message):
        validate_upload_metadata(
            filename=filename,
            media_type=media_type,
            size_bytes=size_bytes,
            max_size_bytes=2048,
        )


def test_storage_keys_are_scoped_generated_and_unique() -> None:
    workspace_id = uuid4()
    project_id = uuid4()
    dataset_id = uuid4()

    first_key = build_storage_key(
        workspace_id=workspace_id,
        project_id=project_id,
        dataset_id=dataset_id,
        version_number=1,
        kind=StoredFileKind.CSV,
    )
    second_key = build_storage_key(
        workspace_id=workspace_id,
        project_id=project_id,
        dataset_id=dataset_id,
        version_number=1,
        kind=StoredFileKind.CSV,
    )

    assert first_key != second_key
    assert str(workspace_id) in first_key
    assert str(project_id) in first_key
    assert str(dataset_id) in first_key
    assert first_key.endswith(".csv")
    assert "customers" not in first_key


def test_storage_key_rejects_invalid_version() -> None:
    with pytest.raises(ValueError, match="positive"):
        build_storage_key(
            workspace_id=uuid4(),
            project_id=uuid4(),
            dataset_id=uuid4(),
            version_number=0,
            kind=StoredFileKind.XLSX,
        )

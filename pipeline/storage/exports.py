from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pymongo.collection import Collection

from apps.api.app.db import get_database

COLLECTION = "exports"


def _collection() -> Collection:
    return get_database()[COLLECTION]


def log_export(
    export_type: str,
    file_path: str,
    *,
    status: str = "completed",
    requested_by: str | None = None,
    row_count: int = 0,
    metadata: dict[str, Any] | None = None,
) -> str:
    """Log an export operation. Returns the export record ID."""
    doc: dict[str, Any] = {
        "exportType": export_type,
        "filePath": file_path,
        "status": status,
        "rowCount": row_count,
        "createdAt": datetime.now(timezone.utc),
    }
    if requested_by:
        doc["requestedBy"] = requested_by
    if metadata:
        doc["metadata"] = metadata
    result = _collection().insert_one(doc)
    return str(result.inserted_id)


def list_exports(limit: int = 50) -> list[dict[str, Any]]:
    """List recent exports."""
    return list(_collection().find().sort("createdAt", -1).limit(limit))

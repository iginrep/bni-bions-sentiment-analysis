from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pymongo.collection import Collection

from apps.api.app.db import get_database

COLLECTION = "collection_runs"


def _collection() -> Collection:
    return get_database()[COLLECTION]


def start_run(
    platform: str,
    keyword_id: str | None = None,
    provider_id: str | None = None,
    schedule_id: str | None = None,
    run_type: str = "scheduled",
    metadata: dict[str, Any] | None = None,
) -> str:
    """Create a collection run record. Returns the run ID."""
    doc: dict[str, Any] = {
        "platform": platform,
        "status": "running",
        "runType": run_type,
        "startedAt": datetime.now(timezone.utc),
        "collectedCount": 0,
        "persistedCount": 0,
        "errorCount": 0,
        "errors": [],
    }
    if keyword_id:
        doc["keywordId"] = keyword_id
    if provider_id:
        doc["providerId"] = provider_id
    if schedule_id:
        doc["scheduleId"] = schedule_id
    if metadata:
        doc["metadata"] = metadata
    result = _collection().insert_one(doc)
    return str(result.inserted_id)


def finish_run(
    run_id: str,
    *,
    status: str = "completed",
    collected_count: int = 0,
    persisted_count: int = 0,
    error_count: int = 0,
    errors: list[str] | None = None,
) -> None:
    """Mark a collection run as finished."""
    update: dict[str, Any] = {
        "$set": {
            "status": status,
            "finishedAt": datetime.now(timezone.utc),
            "collectedCount": collected_count,
            "persistedCount": persisted_count,
            "errorCount": error_count,
        }
    }
    if errors:
        update["$set"]["errors"] = errors
    _collection().update_one({"_id": run_id}, update)


def record_error(run_id: str, error: str) -> None:
    """Append an error to a running collection run."""
    _collection().update_one(
        {"_id": run_id},
        {
            "$inc": {"errorCount": 1},
            "$push": {"errors": error},
        },
    )


def list_runs(
    platform: str | None = None,
    status: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """List recent collection runs with optional filters."""
    query: dict[str, Any] = {}
    if platform:
        query["platform"] = platform
    if status:
        query["status"] = status
    return list(_collection().find(query).sort("startedAt", -1).limit(limit))


def get_run(run_id: str) -> dict[str, Any] | None:
    """Get a single collection run by ID."""
    return _collection().find_one({"_id": run_id})

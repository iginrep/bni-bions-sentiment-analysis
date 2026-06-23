from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pymongo.collection import Collection

from apps.api.app.db import get_database

COLLECTION = "sentiment_jobs"


def _collection() -> Collection:
    return get_database()[COLLECTION]


def start_job(
    method: str = "model",
    model_version: str = "indobenchmark/indobert-base-p2",
    *,
    total_items: int = 0,
) -> str:
    """Create a new sentiment job record. Returns the job ID."""
    doc = {
        "status": "running",
        "method": method,
        "modelVersion": model_version,
        "totalItems": total_items,
        "processedItems": 0,
        "errorItems": 0,
        "startedAt": datetime.now(timezone.utc),
    }
    result = _collection().insert_one(doc)
    return str(result.inserted_id)


def finish_job(
    job_id: str,
    *,
    status: str = "completed",
    processed_items: int = 0,
    error_items: int = 0,
    errors: list[str] | None = None,
) -> None:
    """Mark a sentiment job as finished."""
    update: dict[str, Any] = {
        "$set": {
            "status": status,
            "processedItems": processed_items,
            "errorItems": error_items,
            "finishedAt": datetime.now(timezone.utc),
        }
    }
    if errors:
        update["$set"]["errors"] = errors
    _collection().update_one({"_id": job_id}, update)


def record_progress(job_id: str, processed: int, errors: int = 0) -> None:
    """Update in-progress counters."""
    _collection().update_one(
        {"_id": job_id},
        {"$set": {"processedItems": processed, "errorItems": errors}},
    )


def list_jobs(method: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
    query: dict[str, Any] = {}
    if method:
        query["method"] = method
    return list(_collection().find(query).sort("startedAt", -1).limit(limit))

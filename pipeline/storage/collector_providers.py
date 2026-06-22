from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pymongo.collection import Collection

from apps.api.app.db import get_database

COLLECTION = "collector_providers"


def _collection() -> Collection:
    return get_database()[COLLECTION]


def update_provider_health(
    provider_id: str,
    *,
    status: str,
    error: str | None = None,
) -> None:
    """Update provider health status after a collection run."""
    now = datetime.now(timezone.utc)
    update: dict[str, Any] = {
        "$set": {
            "health.status": status,
            "health.lastCheckedAt": now,
            "updatedAt": now,
        }
    }
    if status == "healthy":
        update["$set"]["health.lastSuccessAt"] = now
        update["$set"]["health.lastError"] = None
    elif error:
        update["$set"]["health.lastError"] = error
    _collection().update_one({"_id": provider_id}, update)


def get_provider(provider_id: str) -> dict[str, Any] | None:
    """Get a single provider by ID."""
    return _collection().find_one({"_id": provider_id})


def list_providers(
    platform: str | None = None,
    enabled_only: bool = False,
) -> list[dict[str, Any]]:
    """List providers with optional filters."""
    query: dict[str, Any] = {}
    if platform:
        query["platform"] = platform
    if enabled_only:
        query["isEnabled"] = True
    return list(_collection().find(query))


def get_provider_by_platform(platform: str) -> dict[str, Any] | None:
    """Get the first enabled provider for a platform."""
    return _collection().find_one({"platform": platform, "isEnabled": True})

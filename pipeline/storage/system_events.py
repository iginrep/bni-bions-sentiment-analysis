from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pymongo.collection import Collection

from apps.api.app.db import get_database

COLLECTION = "system_events"


def _collection() -> Collection:
    return get_database()[COLLECTION]


def log_event(
    level: str,
    component: str,
    message: str,
    *,
    provider_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> str:
    """Log a system event. Returns the event ID."""
    doc: dict[str, Any] = {
        "level": level,
        "component": component,
        "message": message,
        "createdAt": datetime.now(timezone.utc),
    }
    if provider_id:
        doc["providerId"] = provider_id
    if metadata:
        doc["metadata"] = metadata
    result = _collection().insert_one(doc)
    return str(result.inserted_id)


def log_error(component: str, message: str, **kwargs: Any) -> str:
    return log_event("error", component, message, **kwargs)


def log_warning(component: str, message: str, **kwargs: Any) -> str:
    return log_event("warning", component, message, **kwargs)


def log_info(component: str, message: str, **kwargs: Any) -> str:
    return log_event("info", component, message, **kwargs)


def list_events(
    level: str | None = None,
    component: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """List recent system events with optional filters."""
    query: dict[str, Any] = {}
    if level:
        query["level"] = level
    if component:
        query["component"] = component
    return list(_collection().find(query).sort("createdAt", -1).limit(limit))

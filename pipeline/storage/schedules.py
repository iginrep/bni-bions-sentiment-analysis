from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pymongo.collection import Collection

from apps.api.app.db import get_database

COLLECTION = "schedules"


def _collection() -> Collection:
    return get_database()[COLLECTION]


def list_schedules(active_only: bool = True) -> list[dict[str, Any]]:
    query: dict[str, Any] = {}
    if active_only:
        query["isActive"] = True
    return list(_collection().find(query).sort("priority", -1))


def get_schedule(schedule_id: str) -> dict[str, Any] | None:
    return _collection().find_one({"_id": schedule_id})


def touch_schedule(schedule_id: str, *, status: str = "ok") -> None:
    _collection().update_one(
        {"_id": schedule_id},
        {"$set": {"lastRunAt": datetime.now(timezone.utc), "lastRunStatus": status}},
    )


def toggle_schedule(schedule_id: str, is_active: bool) -> bool:
    res = _collection().update_one(
        {"_id": schedule_id},
        {"$set": {"isActive": is_active, "updatedAt": datetime.now(timezone.utc)}}
    )
    return res.modified_count > 0

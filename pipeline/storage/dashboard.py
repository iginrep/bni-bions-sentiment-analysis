from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pymongo.collection import Collection

from apps.api.app.db import get_database

VIEWS = "dashboard_views"
ACTIONS = "dashboard_actions"


def _views() -> Collection:
    return get_database()[VIEWS]


def _actions() -> Collection:
    return get_database()[ACTIONS]


def list_dashboard_views(created_by: str | None = None) -> list[dict[str, Any]]:
    query: dict[str, Any] = {}
    if created_by:
        query["createdBy"] = created_by
    return list(_views().find(query).sort("isDefault", -1))


def upsert_dashboard_view(name: str, config: dict[str, Any], *, created_by: str = "system", is_default: bool = False) -> str:
    now = datetime.now(timezone.utc)
    _views().update_one(
        {"name": name},
        {
            "$set": {"config": config, "updatedAt": now, "isDefault": is_default},
            "$setOnInsert": {"name": name, "createdBy": created_by, "createdAt": now},
        },
        upsert=True,
    )
    doc = _views().find_one({"name": name}, {"_id": 1})
    return str(doc["_id"]) if doc else ""


def log_dashboard_action(
    action_type: str,
    *,
    social_item_id: str | None = None,
    user_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> str:
    doc: dict[str, Any] = {
        "actionType": action_type,
        "createdAt": datetime.now(timezone.utc),
    }
    if social_item_id:
        doc["socialItemId"] = social_item_id
    if user_id:
        doc["userId"] = user_id
    if metadata:
        doc["metadata"] = metadata
    result = _actions().insert_one(doc)
    return str(result.inserted_id)


def list_dashboard_actions(limit: int = 100) -> list[dict[str, Any]]:
    return list(_actions().find().sort("createdAt", -1).limit(limit))

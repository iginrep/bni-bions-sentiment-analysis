from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pymongo.collection import Collection

from apps.api.app.db import get_database

COLLECTION = "model_versions"


def _collection() -> Collection:
    return get_database()[COLLECTION]


def ensure_model_version(method: str, version: str, *, active: bool = True) -> None:
    now = datetime.now(timezone.utc)
    _collection().update_one(
        {"method": method, "version": version},
        {
            "$setOnInsert": {"method": method, "version": version, "createdAt": now},
            "$set": {"isActive": active, "updatedAt": now},
        },
        upsert=True,
    )


def get_active_model(method: str) -> dict[str, Any] | None:
    return _collection().find_one({"method": method, "isActive": True})


def list_model_versions(method: str | None = None) -> list[dict[str, Any]]:
    query: dict[str, Any] = {}
    if method:
        query["method"] = method
    return list(_collection().find(query).sort("createdAt", -1))

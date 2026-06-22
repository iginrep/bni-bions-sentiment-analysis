from __future__ import annotations

from typing import Any

from pymongo.collection import Collection

from apps.api.app.db import get_database

COLLECTION = "keywords"


def _collection() -> Collection:
    return get_database()[COLLECTION]


def list_keywords(platform: str | None = None, active_only: bool = True) -> list[dict[str, Any]]:
    query: dict[str, Any] = {}
    if platform:
        query["platform"] = platform
    if active_only:
        query["isActive"] = True
    return list(_collection().find(query).sort("priority", -1))


def get_keyword(keyword_id: str) -> dict[str, Any] | None:
    return _collection().find_one({"_id": keyword_id})


def active_keywords_by_platform(platform: str) -> list[dict[str, Any]]:
    return list_keywords(platform=platform, active_only=True)

from __future__ import annotations

from typing import Any
from pymongo import ASCENDING, DESCENDING
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError

from apps.api.app.db import get_database


COLLECTION = "social_items"


def collection() -> Collection:
    return get_database()[COLLECTION]


def ensure_indexes() -> None:
    col = collection()
    col.create_index([("platform", ASCENDING), ("sourceId", ASCENDING)], unique=True)
    col.create_index([("targetEntity", ASCENDING), ("postedAt", DESCENDING)])
    col.create_index([("platform", ASCENDING), ("postedAt", DESCENDING)])
    col.create_index([("sentiment.label", ASCENDING), ("postedAt", DESCENDING)])
    col.create_index([("sentiment.topics", ASCENDING), ("postedAt", DESCENDING)])
    col.create_index([("keywordId", ASCENDING), ("collectedAt", DESCENDING)])
    col.create_index([("content.contentHash", ASCENDING)])
    col.create_index([("content.text", "text"), ("content.cleanedText", "text")])


def upsert_social_item(item: dict[str, Any]) -> tuple[bool, str]:
    """Insert canonical item. Returns (inserted, id). Duplicate platform/sourceId is ignored."""
    try:
        result = collection().insert_one(item)
        return True, str(result.inserted_id)
    except DuplicateKeyError:
        existing = collection().find_one(
            {"platform": item["platform"], "sourceId": item["sourceId"]},
            {"_id": 1},
        )
        return False, str(existing["_id"]) if existing else ""


def list_social_items(filters: dict[str, Any], limit: int = 50) -> list[dict[str, Any]]:
    limit = max(1, min(limit, 200))
    query: dict[str, Any] = {}
    for key in ("platform", "targetEntity"):
        if filters.get(key):
            query[key] = filters[key]
    if filters.get("sentimentLabel"):
        query["sentiment.label"] = filters["sentimentLabel"]
    return list(collection().find(query).sort("postedAt", DESCENDING).limit(limit))

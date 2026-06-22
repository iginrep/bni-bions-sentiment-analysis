from __future__ import annotations

from datetime import datetime
from typing import Any
from pymongo.errors import DuplicateKeyError

from apps.api.app.db import get_database
from pipeline.collector.base import RawSocialItem

COLLECTION = "social_items"


def _collection():
    return get_database()[COLLECTION]


def to_canonical_doc(item: RawSocialItem | dict[str, Any]) -> dict[str, Any]:
    raw = item if isinstance(item, dict) else item.as_dict()
    source_id = raw.get("sourceId") or raw.get("source_id") or ""
    return {
        "platform": raw.get("platform"),
        "sourceId": source_id,
        "sourceType": raw.get("sourceType") or raw.get("source_type"),
        "rootSourceId": raw.get("rootSourceId") or raw.get("root_source_id"),
        "parentSourceId": raw.get("parentSourceId") or raw.get("parent_source_id"),
        "conversationId": raw.get("conversationId") or raw.get("conversation_id"),
        "depth": raw.get("depth"),
        "relationType": raw.get("relationType") or raw.get("relation_type"),
        "keyword": raw.get("keyword"),
        "targetEntity": raw.get("targetEntity") or raw.get("target_entity"),
        "text": raw.get("text"),
        "authorId": raw.get("authorId") or raw.get("author_id"),
        "authorUsername": raw.get("authorUsername") or raw.get("author_username"),
        "authorDisplayName": raw.get("authorDisplayName") or raw.get("author_display_name"),
        "sourceUrl": raw.get("sourceUrl") or raw.get("source_url"),
        "postedAt": raw.get("postedAt") or raw.get("posted_at"),
        "collectedAt": raw.get("collectedAt") or raw.get("collected_at"),
        "metrics": raw.get("metrics"),
        "language": raw.get("language"),
        "collectionMethod": raw.get("collectionMethod") or raw.get("collection_method"),
        "accessRisk": raw.get("accessRisk") or raw.get("access_risk"),
        "rawPayload": raw.get("rawPayload") or raw.get("raw_payload"),
    }


def persist_social_items(items: list[RawSocialItem | dict[str, Any]]) -> int:
    inserted = 0
    col = _collection()
    for item in items:
        doc = to_canonical_doc(item)
        if not doc.get("platform") or not doc.get("sourceId"):
            continue
        try:
            col.insert_one(doc)
            inserted += 1
        except DuplicateKeyError:
            continue
    return inserted


def _posted_at_window_query(start: Any, end: Any) -> dict[str, Any]:
    clauses = [{"postedAt": {"$gte": start, "$lt": end}}]
    if isinstance(start, datetime) and isinstance(end, datetime):
        clauses.append({"postedAt": {"$gte": start.isoformat(), "$lt": end.isoformat()}})
        clauses.append({"postedAt": {"$gte": start.replace(tzinfo=None).isoformat(), "$lt": end.replace(tzinfo=None).isoformat()}})
    return {"$or": clauses}


def social_items_exist(platform: str, start: Any, end: Any) -> bool:
    return _collection().find_one(
        {
            "platform": platform,
            **_posted_at_window_query(start, end),
        },
        {"_id": 1},
    ) is not None

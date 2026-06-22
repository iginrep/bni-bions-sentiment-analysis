from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pymongo.collection import Collection

from apps.api.app.db import get_database

COLLECTION = "labeled_examples"


def _collection() -> Collection:
    return get_database()[COLLECTION]


def add_labeled_example(
    social_item_id: str,
    label: str,
    *,
    topics: list[str] | None = None,
    annotator: str | None = None,
    notes: str | None = None,
) -> str:
    doc: dict[str, Any] = {
        "socialItemId": social_item_id,
        "label": label,
        "topics": topics or [],
        "createdAt": datetime.now(timezone.utc),
    }
    if annotator:
        doc["annotator"] = annotator
    if notes:
        doc["notes"] = notes
    result = _collection().insert_one(doc)
    return str(result.inserted_id)


def list_labeled_examples(label: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
    query: dict[str, Any] = {}
    if label:
        query["label"] = label
    return list(_collection().find(query).sort("createdAt", -1).limit(limit))

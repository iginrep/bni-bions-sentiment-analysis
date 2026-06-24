from __future__ import annotations

from typing import Any
from pymongo import DESCENDING
from pymongo.collection import Collection

from apps.api.app.db import get_database

COLLECTION = "social_items_labeled"


def collection() -> Collection:
    return get_database()[COLLECTION]


def list_labeled_social_items(filters: dict[str, Any], limit: int = 100) -> list[dict[str, Any]]:
    limit = max(1, min(limit, 1000))
    query: dict[str, Any] = {}
    for key in ("platform", "targetEntity"):
        if filters.get(key):
            query[key] = filters[key]
    if filters.get("sentimentLabel"):
        query["labeling_review"] = filters["sentimentLabel"]
    return list(collection().find(query).sort("postedAt", DESCENDING).limit(limit))


def get_labeled_stats() -> dict[str, Any]:
    col = collection()
    pipeline = [
        {
            "$group": {
                "_id": {
                    "platform": "$platform",
                    "label": "$labeling_review"
                },
                "count": {"$sum": 1}
            }
        }
    ]
    results = list(col.aggregate(pipeline))
    
    stats = {
        "total": 0,
        "labels": {"Positif": 0, "Negatif": 0, "Netral": 0},
        "platforms": {}
    }
    
    for r in results:
        group = r["_id"] or {}
        count = r["count"] or 0
        platform = group.get("platform") or "unknown"
        label = group.get("label") or "Netral"
        
        # Normalize label casing just in case
        label = str(label).strip().capitalize()
        if label not in ["Positif", "Negatif", "Netral"]:
            label = "Netral"
            
        stats["total"] += count
        stats["labels"][label] = stats["labels"].get(label, 0) + count
        
        if platform not in stats["platforms"]:
            stats["platforms"][platform] = {"Positif": 0, "Negatif": 0, "Netral": 0}
        
        stats["platforms"][platform][label] = stats["platforms"][platform].get(label, 0) + count
        
    return stats

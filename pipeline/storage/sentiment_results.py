from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from pymongo.collection import Collection

from apps.api.app.db import get_database
from pipeline.sentiment.quality import build_quality_flags, is_excluded_from_analysis
from pipeline.storage.datasets import persist_processed_record, persist_raw_social_item


def _object_id(value: str):
    try:
        return ObjectId(value)
    except Exception:
        return value

COLLECTION = "sentiment_results"
SOCIAL_ITEMS = "social_items"


def _collection() -> Collection:
    return get_database()[COLLECTION]


def _social_items() -> Collection:
    return get_database()[SOCIAL_ITEMS]


def persist_sentiment_result(
    social_item_id: str,
    result: dict[str, Any],
    *,
    run_id: str | None = None,
) -> str:
    """Store a sentiment classification result and update the social_item.

    Returns the sentiment_results document ID.
    """
    social_doc = _social_items().find_one({"_id": _object_id(social_item_id)}) or {}
    quality = build_quality_flags(social_doc, result)
    doc: dict[str, Any] = {
        "socialItemId": social_item_id,
        "label": result.get("label", "unknown"),
        "score": result.get("score", 0.0),
        "confidence": result.get("confidence", 0.0),
        "topics": result.get("topics", []),
        "method": result.get("method", "model"),
        "modelVersion": result.get("model_version", "indobenchmark/indobert-base-p2"),
        "cleanedText": result.get("cleaned_text", ""),
        "quality": quality,
        "createdAt": datetime.now(timezone.utc),
    }
    if run_id:
        doc["collectionRunId"] = run_id

    ins = _collection().insert_one(doc)
    if social_doc:
        persist_raw_social_item(social_doc)
        persist_processed_record(social_doc, doc)

    # update social_items with sentiment + mark analyzed
    _social_items().update_one(
        {"_id": _object_id(social_item_id)},
        {
            "$set": {
                "sentiment.label": doc["label"],
                "sentiment.score": doc["score"],
                "sentiment.confidence": doc["confidence"],
                "sentiment.topics": doc["topics"],
                "sentiment.method": doc["method"],
                "sentiment.modelVersion": doc["modelVersion"],
                "sentiment.resultId": str(ins.inserted_id),
                "processing.analysisStatus": "completed",
                "processing.analyzedAt": datetime.now(timezone.utc),
                "quality": quality,
            }
        },
    )

    return str(ins.inserted_id)


def persist_sentiment_batch(
    results: list[dict[str, Any]],
    *,
    run_id: str | None = None,
) -> int:
    """Batch persist sentiment results. Each entry: {social_item_id, result}.

    Returns count of persisted results.
    """
    if not results:
        return 0

    now = datetime.now(timezone.utc)
    docs = []
    updates = []
    for entry in results:
        social_item_id = entry["social_item_id"]
        result = entry["result"]
        social_doc = _social_items().find_one({"_id": _object_id(social_item_id)}) or {}
        quality = build_quality_flags(social_doc, result)
        doc = {
            "socialItemId": social_item_id,
            "label": result.get("label", "unknown"),
            "score": result.get("score", 0.0),
            "confidence": result.get("confidence", 0.0),
            "topics": result.get("topics", []),
            "method": result.get("method", "model"),
            "modelVersion": result.get("model_version", "indobenchmark/indobert-base-p2"),
            "cleanedText": result.get("cleaned_text", ""),
            "quality": quality,
            "createdAt": now,
        }
        if run_id:
            doc["collectionRunId"] = run_id
        docs.append(doc)
        updates.append((social_item_id, doc))

    if docs:
        for doc in docs:
            _collection().update_one(
                {"socialItemId": doc["socialItemId"], "method": doc["method"]},
                {"$set": doc},
                upsert=True,
            )

    # update social_items in batch
    for social_item_id, doc in updates:
        social_doc = _social_items().find_one({"_id": _object_id(social_item_id)}) or {}
        if social_doc:
            persist_raw_social_item(social_doc)
            persist_processed_record(social_doc, doc)
        _social_items().update_one(
            {"_id": _object_id(social_item_id)},
            {
                "$set": {
                    "sentiment.label": doc["label"],
                    "sentiment.score": doc["score"],
                    "sentiment.confidence": doc["confidence"],
                    "sentiment.topics": doc["topics"],
                    "sentiment.method": doc["method"],
                    "sentiment.modelVersion": doc["modelVersion"],
                    "processing.analysisStatus": "completed",
                    "processing.analyzedAt": now,
                    "quality": doc["quality"],
                }
            },
        )

    return len(docs)


def get_results_for_item(social_item_id: str) -> list[dict[str, Any]]:
    """Get all sentiment results for a social item."""
    return list(
        _collection()
        .find({"socialItemId": social_item_id})
        .sort("createdAt", -1)
    )


def get_unanalyzed_items(limit: int = 100) -> list[dict[str, Any]]:
    """Get social_items that haven't been sentiment-analyzed yet, excluding known noise."""
    docs = list(
        _social_items()
        .find(
            {
                "$or": [
                    {"processing.analysisStatus": {"$exists": False}},
                    {"processing.analysisStatus": "pending"},
                ]
            }
        )
        .limit(limit)
    )
    return [doc for doc in docs if not is_excluded_from_analysis(doc)]


def get_analyzable_items(limit: int = 500) -> list[dict[str, Any]]:
    """Get all social_items eligible for sentiment analysis, excluding known noise."""
    return [doc for doc in _social_items().find({}).limit(limit) if not is_excluded_from_analysis(doc)]


def list_results(
    label: str | None = None,
    method: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """List sentiment results with optional filters."""
    query: dict[str, Any] = {}
    if label:
        query["label"] = label
    if method:
        query["method"] = method
    return list(_collection().find(query).sort("createdAt", -1).limit(limit))

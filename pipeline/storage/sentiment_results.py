from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from pymongo.collection import Collection

from apps.api.app.db import get_database


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
    doc: dict[str, Any] = {
        "socialItemId": social_item_id,
        "label": result.get("label", "unknown"),
        "score": result.get("score", 0.0),
        "confidence": result.get("confidence", 0.0),
        "topics": result.get("topics", []),
        "method": result.get("method", "indobert"),
        "modelVersion": result.get("model_version", "intanm/indonesian_financial_sentiment_analysis"),
        "cleanedText": result.get("cleaned_text", ""),
        "createdAt": datetime.now(timezone.utc),
    }
    if run_id:
        doc["collectionRunId"] = run_id

    ins = _collection().insert_one(doc)

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
        doc = {
            "socialItemId": social_item_id,
            "label": result.get("label", "unknown"),
            "score": result.get("score", 0.0),
            "confidence": result.get("confidence", 0.0),
            "topics": result.get("topics", []),
            "method": result.get("method", "indobert"),
            "modelVersion": result.get("model_version", "intanm/indonesian_financial_sentiment_analysis"),
            "cleanedText": result.get("cleaned_text", ""),
            "createdAt": now,
        }
        if run_id:
            doc["collectionRunId"] = run_id
        docs.append(doc)
        updates.append((social_item_id, doc))

    if docs:
        _collection().insert_many(docs)

    # update social_items in batch
    for social_item_id, doc in updates:
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
    """Get social_items that haven't been sentiment-analyzed yet."""
    return list(
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

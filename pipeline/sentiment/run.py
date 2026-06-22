from __future__ import annotations
from typing import cast

from pipeline.collector.base import RawSocialItem
from pipeline.collector.run import collect_sample
from pipeline.sentiment.classifier import classify


def run_sentiment_analysis(write: bool = False) -> list[dict]:
    """Collect + classify + optionally persist sentiment results."""
    items = cast(list[RawSocialItem], collect_sample(write=write))
    results = []
    job_id: str | None = None

    if write:
        try:
            from pipeline.storage.sentiment_jobs import start_job
            job_id = start_job(total_items=len(items))
        except Exception:
            pass

    processed = 0
    errors = 0
    for item in items:
        sentiment = classify(item.text)
        entry = {"item": item.as_dict(), "sentiment": sentiment}
        results.append(entry)

        if write:
            try:
                from pipeline.storage.sentiment_results import persist_sentiment_result
                from apps.api.app.db import get_database

                db = get_database()
                doc = db.social_items.find_one(
                    {"platform": item.platform, "sourceId": item.source_id}
                )
                if doc:
                    persist_sentiment_result(str(doc["_id"]), sentiment)
                processed += 1
            except Exception:
                errors += 1

    if job_id:
        try:
            from pipeline.storage.sentiment_jobs import finish_job
            finish_job(job_id, status="completed", processed_items=processed, error_items=errors)
        except Exception:
            pass

    return results


def backfill_sentiment(limit: int = 500) -> int:
    """Classify and persist sentiment for all unanalyzed social_items in DB.

    Does NOT re-collect — works on items already in social_items collection.
    Returns count of items processed.
    """
    try:
        from pipeline.storage.sentiment_results import persist_sentiment_batch, get_unanalyzed_items
        from pipeline.storage.sentiment_jobs import start_job, finish_job
    except Exception:
        return 0

    items = get_unanalyzed_items(limit=limit)
    if not items:
        return 0

    job_id = start_job(total_items=len(items))
    batch = []
    processed = 0
    error_count = 0

    for doc in items:
        text = doc.get("content", {}).get("text") or doc.get("text", "")
        if not text:
            continue
        try:
            sentiment = classify(text)
            batch.append({"social_item_id": str(doc["_id"]), "result": sentiment})
            processed += 1
        except Exception:
            error_count += 1

    persist_sentiment_batch(batch)
    finish_job(job_id, status="completed", processed_items=processed, error_items=error_count)
    return processed


if __name__ == "__main__":
    for entry in run_sentiment_analysis():
        print(entry["item"]["text"], "=>", entry["sentiment"])

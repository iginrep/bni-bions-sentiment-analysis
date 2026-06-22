from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from apps.api.app.db import get_database

COLLECTION = "collection_checkpoints"


def _collection():
    return get_database()[COLLECTION]


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _key(platform: str, start: datetime, end: datetime) -> dict[str, Any]:
    return {"platform": platform, "windowStart": _utc(start).isoformat(), "windowEnd": _utc(end).isoformat()}


class MongoBackfillCheckpointStore:
    def get_status(self, platform: str, start: datetime, end: datetime) -> str | None:
        doc = _collection().find_one(_key(platform, start, end), {"status": 1})
        if not doc:
            return None
        status = doc.get("status")
        return str(status) if status else None

    def mark_complete(self, platform: str, start: datetime, end: datetime, collected: int, inserted: int) -> None:
        now = datetime.now(timezone.utc).isoformat()
        _collection().update_one(
            _key(platform, start, end),
            {
                "$set": {
                    "status": "complete",
                    "collected": collected,
                    "inserted": inserted,
                    "completedAt": now,
                    "updatedAt": now,
                    "lastError": None,
                },
                "$setOnInsert": {"createdAt": now},
            },
            upsert=True,
        )

    def mark_partial(self, platform: str, start: datetime, end: datetime, collected: int, inserted: int, error: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        _collection().update_one(
            _key(platform, start, end),
            {
                "$set": {
                    "status": "partial",
                    "collected": collected,
                    "inserted": inserted,
                    "lastError": error,
                    "updatedAt": now,
                },
                "$setOnInsert": {"createdAt": now},
            },
            upsert=True,
        )

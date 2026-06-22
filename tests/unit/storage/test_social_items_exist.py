from __future__ import annotations

from datetime import datetime, timezone

import pytest

from pipeline.storage.social_items import social_items_exist


pytestmark = pytest.mark.unit


class FakeCollection:
    def __init__(self) -> None:
        self.query = None

    def find_one(self, query, projection):
        self.query = query
        return {"_id": "hit"}


def test_social_items_exist_queries_datetime_and_iso_string_bounds(monkeypatch) -> None:
    col = FakeCollection()
    monkeypatch.setattr("pipeline.storage.social_items._collection", lambda: col)

    exists = social_items_exist(
        "youtube",
        datetime(2026, 6, 1, tzinfo=timezone.utc),
        datetime(2026, 6, 22, tzinfo=timezone.utc),
    )

    assert exists is True
    assert col.query["platform"] == "youtube"
    assert "$or" in col.query
    assert {"postedAt": {"$gte": "2026-06-01T00:00:00+00:00", "$lt": "2026-06-22T00:00:00+00:00"}} in col.query["$or"]
    assert {"postedAt": {"$gte": "2026-06-01T00:00:00", "$lt": "2026-06-22T00:00:00"}} in col.query["$or"]

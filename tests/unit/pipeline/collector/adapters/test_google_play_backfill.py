from __future__ import annotations

from datetime import datetime, timezone

import pytest

from pipeline.collector.adapters.google_play import GooglePlayAdapter


pytestmark = pytest.mark.unit


def test_google_play_collect_backfill_uses_continuation_until_window_start(monkeypatch):
    calls: list[object] = []

    def fake_reviews(*args, **kwargs):
        calls.append(kwargs.get("continuation_token"))
        if len(calls) == 1:
            return ([{"reviewId": "r1", "content": "ok", "at": datetime(2026, 6, 1, tzinfo=timezone.utc)}], "token1")
        if len(calls) == 2:
            return ([{"reviewId": "r2", "content": "bad", "at": datetime(2026, 5, 1, tzinfo=timezone.utc)}], "token2")
        return ([{"reviewId": "r3", "content": "old", "at": datetime(2026, 3, 1, tzinfo=timezone.utc)}], None)

    monkeypatch.setattr("google_play_scraper.reviews", fake_reviews)

    rows = GooglePlayAdapter().collect_backfill(
        keyword="bions",
        target_entity="bions",
        since=datetime(2026, 4, 1, tzinfo=timezone.utc),
        until=datetime(2026, 6, 15, tzinfo=timezone.utc),
        limit=10,
    )

    assert [row.source_id for row in rows] == ["r1", "r2"]
    assert calls == [None, "token1", "token2"]


def test_google_play_collect_backfill_respects_limit(monkeypatch):
    def fake_reviews(*args, **kwargs):
        return (
            [
                {"reviewId": "r1", "content": "one", "at": datetime(2026, 6, 1, tzinfo=timezone.utc)},
                {"reviewId": "r2", "content": "two", "at": datetime(2026, 5, 1, tzinfo=timezone.utc)},
            ],
            None,
        )

    monkeypatch.setattr("google_play_scraper.reviews", fake_reviews)

    rows = GooglePlayAdapter().collect_backfill(
        keyword="bions",
        target_entity="bions",
        since=datetime(2026, 1, 1, tzinfo=timezone.utc),
        until=datetime(2026, 7, 1, tzinfo=timezone.utc),
        limit=1,
    )

    assert [row.source_id for row in rows] == ["r1"]

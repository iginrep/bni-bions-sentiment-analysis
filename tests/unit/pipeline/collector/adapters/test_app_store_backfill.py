from __future__ import annotations

from datetime import datetime, timezone

import httpx
import pytest

from pipeline.collector.adapters.app_store import AppStoreAdapter


pytestmark = pytest.mark.unit


def _payload(review_id: str, updated: str) -> dict:
    return {
        "feed": {
            "entry": [
                {"id": {"label": review_id}, "title": {"label": "BIONS"}, "content": {"label": "good app"}, "updated": {"label": updated}}
            ]
        }
    }


def test_app_store_collect_backfill_pages_until_window_start(monkeypatch):
    requested: list[str] = []
    payloads = {
        1: _payload("r1", "2026-06-01T00:00:00+00:00"),
        2: _payload("r2", "2026-05-01T00:00:00+00:00"),
        3: _payload("r3", "2026-03-01T00:00:00+00:00"),
    }

    def fake_get(url: str, timeout: float):
        requested.append(url)
        page = int(url.split("page=")[1].split("/")[0])
        return httpx.Response(200, json=payloads[page], request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx, "get", fake_get)

    rows = AppStoreAdapter().collect_backfill(
        keyword="bions",
        target_entity="bions",
        since=datetime(2026, 4, 1, tzinfo=timezone.utc),
        until=datetime(2026, 6, 15, tzinfo=timezone.utc),
        limit=10,
    )

    assert [row.source_id for row in rows] == ["r1", "r2"]
    assert len(requested) == 3


def test_app_store_collect_backfill_respects_limit(monkeypatch):
    def fake_get(url: str, timeout: float):
        return httpx.Response(
            200,
            json={
                "feed": {
                    "entry": [
                        {"id": {"label": "r1"}, "title": {"label": "one"}, "content": {"label": "ok"}, "updated": {"label": "2026-06-01T00:00:00+00:00"}},
                        {"id": {"label": "r2"}, "title": {"label": "two"}, "content": {"label": "ok"}, "updated": {"label": "2026-05-01T00:00:00+00:00"}},
                    ]
                }
            },
            request=httpx.Request("GET", url),
        )

    monkeypatch.setattr(httpx, "get", fake_get)

    rows = AppStoreAdapter().collect_backfill(
        keyword="bions",
        target_entity="bions",
        since=datetime(2026, 1, 1, tzinfo=timezone.utc),
        until=datetime(2026, 7, 1, tzinfo=timezone.utc),
        limit=1,
    )

    assert [row.source_id for row in rows] == ["r1"]

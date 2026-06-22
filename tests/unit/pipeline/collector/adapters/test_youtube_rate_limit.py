from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx
import pytest

from pipeline.collector.adapters.youtube import YouTubeAdapter
from pipeline.collector.exceptions import CollectorStopped


pytestmark = pytest.mark.unit


def _response(payload: dict, request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=payload, request=request)


def test_youtube_backfill_stops_before_request_budget_is_exhausted(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "test-key")
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls > 2:
            raise AssertionError("request budget guard failed")
        if request.url.path.endswith("/search"):
            return _response({"items": [{"id": {"videoId": "video-1"}}, {"id": {"videoId": "video-2"}}]}, request)
        if request.url.path.endswith("/commentThreads"):
            return _response(
                {
                    "items": [
                        {
                            "id": "thread-1",
                            "snippet": {
                                "videoId": "video-1",
                                "topLevelComment": {
                                    "id": "comment-1",
                                    "snippet": {"textOriginal": "ok", "publishedAt": "2026-01-01T00:00:00Z"},
                                },
                            },
                        }
                    ]
                },
                request,
            )
        raise AssertionError(str(request.url))

    adapter = YouTubeAdapter(
        channel_urls=["https://www.youtube.com/channel/UC_TEST"],
        client=httpx.Client(transport=httpx.MockTransport(handler)),
        max_backfill_requests=2,
    )

    with pytest.raises(CollectorStopped, match="youtube backfill request budget exhausted"):
        adapter.collect_backfill(
            keyword="bions",
            target_entity="bions",
            since=datetime(2025, 6, 22, tzinfo=timezone.utc),
            until=datetime(2026, 6, 22, tzinfo=timezone.utc),
            limit=10,
        )

    assert calls == 2


def test_youtube_backfill_reads_request_budget_from_env(monkeypatch):
    monkeypatch.setenv("YOUTUBE_BACKFILL_MAX_REQUESTS", "7")

    adapter = YouTubeAdapter(channel_urls=["https://www.youtube.com/channel/UC_TEST"], client=httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200, request=request))))

    assert adapter.max_backfill_requests == 7


def test_youtube_backfill_uses_request_delay(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "test-key")
    sleeps: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if urlparse(str(request.url)).path.endswith("/search"):
            return _response({"items": []}, request)
        raise AssertionError(str(request.url))

    adapter = YouTubeAdapter(
        channel_urls=["https://www.youtube.com/channel/UC_TEST"],
        client=httpx.Client(transport=httpx.MockTransport(handler)),
        max_backfill_requests=5,
        request_delay_seconds=0.25,
        sleep_fn=sleeps.append,
    )

    adapter.collect_backfill(
        keyword="bions",
        target_entity="bions",
        since=datetime(2025, 6, 22, tzinfo=timezone.utc),
        until=datetime(2026, 6, 22, tzinfo=timezone.utc),
        limit=10,
    )

    assert sleeps == [0.25]

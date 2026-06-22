from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

import httpx
import pytest

from pipeline.collector.adapters.youtube import YouTubeAdapter


pytestmark = pytest.mark.unit


def _response(payload: dict, request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=payload, request=request)


def test_youtube_collect_backfill_discovers_channel_videos_by_window_and_collects_comments(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "test-key")
    seen: list[tuple[str, dict[str, list[str]]]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        qs = parse_qs(urlparse(str(request.url)).query)
        seen.append((request.url.path, qs))
        if request.url.path.endswith("/search"):
            assert qs["channelId"] == ["UC_TEST"]
            assert qs["publishedAfter"] == ["2025-06-22T00:00:00Z"]
            assert qs["publishedBefore"] == ["2026-06-22T00:00:00Z"]
            return _response(
                {
                    "items": [
                        {"id": {"videoId": "video-1"}, "snippet": {"publishedAt": "2026-01-01T00:00:00Z", "title": "BIONS update"}}
                    ]
                },
                request,
            )
        if request.url.path.endswith("/commentThreads"):
            assert qs["videoId"] == ["video-1"]
            return _response(
                {
                    "items": [
                        {
                            "id": "thread-1",
                            "snippet": {
                                "videoId": "video-1",
                                "totalReplyCount": 0,
                                "topLevelComment": {
                                    "id": "comment-1",
                                    "snippet": {"textOriginal": "BIONS mantap", "publishedAt": "2026-01-02T00:00:00Z"},
                                },
                            },
                        }
                    ]
                },
                request,
            )
        raise AssertionError(str(request.url))

    adapter = YouTubeAdapter(channel_urls=["https://www.youtube.com/channel/UC_TEST"], client=httpx.Client(transport=httpx.MockTransport(handler)), max_backfill_requests=20, request_delay_seconds=0)

    rows = adapter.collect_backfill(
        keyword="bions",
        target_entity="bions",
        since=datetime(2025, 6, 22, tzinfo=timezone.utc),
        until=datetime(2026, 6, 22, tzinfo=timezone.utc),
        limit=10,
    )

    assert [row.source_id for row in rows] == ["comment-1"]
    assert [path for path, _ in seen] == ["/youtube/v3/search", "/youtube/v3/commentThreads"]


def test_youtube_collect_backfill_pages_search_and_comment_threads(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "test-key")
    search_tokens: list[list[str] | None] = []
    comment_tokens: list[list[str] | None] = []

    def handler(request: httpx.Request) -> httpx.Response:
        qs = parse_qs(urlparse(str(request.url)).query)
        if request.url.path.endswith("/search"):
            search_tokens.append(qs.get("pageToken"))
            if "pageToken" not in qs:
                return _response({"nextPageToken": "s2", "items": [{"id": {"videoId": "video-1"}}]}, request)
            return _response({"items": [{"id": {"videoId": "video-2"}}]}, request)
        if request.url.path.endswith("/commentThreads"):
            comment_tokens.append(qs.get("pageToken"))
            video_id = qs["videoId"][0]
            if video_id == "video-1" and "pageToken" not in qs:
                return _response(
                    {
                        "nextPageToken": "c2",
                        "items": [
                            {
                                "id": "thread-1",
                                "snippet": {"videoId": video_id, "topLevelComment": {"id": "c1", "snippet": {"textOriginal": "one", "publishedAt": "2026-01-02T00:00:00Z"}}},
                            }
                        ],
                    },
                    request,
                )
            return _response(
                {
                    "items": [
                        {
                            "id": f"thread-{video_id}",
                            "snippet": {"videoId": video_id, "topLevelComment": {"id": f"c-{video_id}", "snippet": {"textOriginal": "two", "publishedAt": "2026-01-03T00:00:00Z"}}},
                        }
                    ]
                },
                request,
            )
        raise AssertionError(str(request.url))

    adapter = YouTubeAdapter(channel_urls=["https://www.youtube.com/channel/UC_TEST"], client=httpx.Client(transport=httpx.MockTransport(handler)), max_backfill_requests=20, request_delay_seconds=0)

    rows = adapter.collect_backfill(
        keyword="bions",
        target_entity="bions",
        since=datetime(2025, 6, 22, tzinfo=timezone.utc),
        until=datetime(2026, 6, 22, tzinfo=timezone.utc),
        limit=10,
    )

    assert [row.source_id for row in rows] == ["c1", "c-video-1", "c-video-2"]
    assert search_tokens == [None, ["s2"]]
    assert comment_tokens[:2] == [None, ["c2"]]


def test_youtube_collect_backfill_filters_comments_outside_window(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "test-key")

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/search"):
            return _response({"items": [{"id": {"videoId": "video-1"}}]}, request)
        return _response(
            {
                "items": [
                    {
                        "id": "thread-old",
                        "snippet": {"videoId": "video-1", "topLevelComment": {"id": "old", "snippet": {"textOriginal": "old", "publishedAt": "2024-01-01T00:00:00Z"}}},
                    },
                    {
                        "id": "thread-new",
                        "snippet": {"videoId": "video-1", "topLevelComment": {"id": "new", "snippet": {"textOriginal": "new", "publishedAt": "2026-01-01T00:00:00Z"}}},
                    },
                ]
            },
            request,
        )

    adapter = YouTubeAdapter(channel_urls=["https://www.youtube.com/channel/UC_TEST"], client=httpx.Client(transport=httpx.MockTransport(handler)), max_backfill_requests=20, request_delay_seconds=0)

    rows = adapter.collect_backfill(
        keyword="bions",
        target_entity="bions",
        since=datetime(2025, 6, 22, tzinfo=timezone.utc),
        until=datetime(2026, 6, 22, tzinfo=timezone.utc),
        limit=10,
    )

    assert [row.source_id for row in rows] == ["new"]

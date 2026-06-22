from __future__ import annotations

import httpx
import pytest

from pipeline.collector.adapters.instagram import InstagramAdapter, parse_instagram_hashtag_media
from pipeline.collector.adapters.threads import ThreadsAdapter, parse_threads_keyword_search


pytestmark = pytest.mark.unit


def test_threads_keyword_search_collects_public_mentions():
    urls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        urls.append(str(request.url))
        if "keyword_search" in str(request.url):
            return httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "id": "post1",
                            "text": "BIONS app error",
                            "media_type": "TEXT",
                            "permalink": "https://www.threads.net/@user/post/abc",
                            "timestamp": "2026-06-22T01:02:03+0000",
                            "username": "user",
                            "has_replies": True,
                            "is_quote_post": False,
                            "is_reply": False,
                        }
                    ]
                },
            )
        return httpx.Response(200, json={"data": []})

    rows = ThreadsAdapter(
        access_token="token",
        media_ids=[],
        search_queries=["BIONS error"],
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    ).collect("BIONS", "BIONS", limit=10)

    assert any("keyword_search" in url and "q=BIONS+error" in url for url in urls)
    assert rows[0].source_type == "post"
    assert rows[0].source_id == "post1"
    assert rows[0].root_source_id == "post1"
    assert rows[0].conversation_id == "post1"
    assert rows[0].relation_type == "mention"
    assert rows[0].collection_method == "official_threads_keyword_search"


def test_instagram_hashtag_search_discovers_media_and_fetches_comments():
    urls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        urls.append(str(request.url))
        if "ig_hashtag_search" in str(request.url):
            return httpx.Response(200, json={"data": [{"id": "hash1", "name": "BIONS"}]})
        if "hash1/recent_media" in str(request.url):
            return httpx.Response(
                200,
                json={"data": [{"id": "media1", "caption": "BIONS mention", "permalink": "https://instagram.com/p/media1/", "timestamp": "2026-06-22T01:02:03+0000", "comments_count": 1, "like_count": 2}]},
            )
        if "media1/comments" in str(request.url):
            return httpx.Response(200, json={"data": [{"id": "c1", "text": "BIONS error", "timestamp": "2026-06-22T01:03:03+0000", "username": "u1"}]})
        return httpx.Response(404)

    rows = InstagramAdapter(
        access_token="token",
        media_ids=[],
        ig_user_id="iguser1",
        hashtag_queries=["BIONS"],
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    ).collect("BIONS", "BIONS", limit=10)

    assert any("iguser1/ig_hashtag_search" in url and "q=BIONS" in url for url in urls)
    assert any("hash1/recent_media" in url for url in urls)
    assert any("media1/comments" in url for url in urls)
    assert rows[0].source_type == "post"
    assert rows[0].source_id == "media1"
    assert rows[0].relation_type == "mention"
    assert rows[0].collection_method == "official_instagram_hashtag_search"
    assert rows[1].source_type == "comment"
    assert rows[1].root_source_id == "media1"
    assert rows[1].relation_type == "comment"


def test_threads_keyword_search_parser_maps_public_posts():
    rows = parse_threads_keyword_search(
        {"data": [{"id": "p1", "text": "BNI Sekuritas", "timestamp": "2026-06-22T01:02:03+0000", "username": "u", "permalink": "https://threads.net/@u/post/a"}]},
        query="BNI Sekuritas",
        keyword="bions",
        target_entity="bions",
    )

    assert rows[0].keyword == "BNI Sekuritas"
    assert rows[0].root_source_id == "p1"
    assert rows[0].relation_type == "mention"


def test_instagram_hashtag_media_parser_maps_public_media():
    rows = parse_instagram_hashtag_media(
        {"data": [{"id": "m1", "caption": "#BIONS", "timestamp": "2026-06-22T01:02:03+0000", "permalink": "https://instagram.com/p/m1/", "comments_count": 3}]},
        query="BIONS",
        keyword="bions",
        target_entity="bions",
    )

    assert rows[0].keyword == "BIONS"
    assert rows[0].source_type == "post"
    assert rows[0].metrics["comments_count"] == 3
    assert rows[0].relation_type == "mention"

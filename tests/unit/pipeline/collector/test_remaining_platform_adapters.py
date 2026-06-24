from __future__ import annotations

import pytest

from pipeline.collector.adapters.app_store import AppStoreAdapter, parse_app_store_reviews
from pipeline.collector.adapters.google_play import GooglePlayAdapter
from pipeline.collector.adapters.instagram import InstagramAdapter
from pipeline.collector.adapters.stockbit import StockbitAdapter
from pipeline.collector.adapters.threads import ThreadsAdapter
from pipeline.collector.adapters.tiktok import TikTokAdapter
from pipeline.collector.adapters.twitter import TwitterAdapter
from pipeline.collector.adapters.youtube import YouTubeAdapter
from pipeline.collector.exceptions import CollectorNotConfigured
from pipeline.collector.run import remaining_platform_adapters


pytestmark = pytest.mark.unit

def test_remaining_platform_adapter_registry_includes_default_public_collectors():
    platforms = [adapter.platform for adapter in remaining_platform_adapters(include_risky=True)]

    assert "app_store" in platforms
    assert "youtube" in platforms
    assert "google_play" in platforms
    assert {"stockbit", "x", "tiktok", "instagram", "threads"}.issubset(set(platforms))
    assert GooglePlayAdapter().access_mode == "scraper"
    assert YouTubeAdapter().access_mode == "rss+youtube_data_api"


def test_parse_app_store_reviews_feed():
    payload = {
        "feed": {
            "entry": [
                {"im:name": {"label": "BIONS"}},
                {
                    "id": {"label": "review-1"},
                    "title": {"label": "Sulit login"},
                    "content": {"label": "Aplikasi BIONS susah login otp lambat"},
                    "author": {"name": {"label": "user publik"}, "uri": {"label": "https://example.test/user/1"}},
                    "im:rating": {"label": "1"},
                    "im:version": {"label": "1.2.3"},
                    "updated": {"label": "2026-06-01T10:00:00-07:00"},
                    "link": {"attributes": {"href": "https://apps.apple.com/id/review?id=review-1"}},
                },
            ]
        }
    }

    items = parse_app_store_reviews(payload, keyword="bions", target_entity="bions")

    assert len(items) == 1
    item = items[0]
    assert item.platform == "app_store"
    assert item.source_id == "review-1"
    assert item.author_display_name == "user publik"
    assert item.metrics["rating"] == 1
    assert item.raw_payload["app_version"] == "1.2.3"
    assert "susah login" in item.text


def test_app_store_adapter_builds_country_feed_url():
    adapter = AppStoreAdapter(app_id="6736508566", country="id")

    assert adapter.review_feed_url(1).startswith("https://itunes.apple.com/id/rss/customerreviews")
    assert "id=6736508566" in adapter.review_feed_url(1)


def test_parse_app_store_reviews_with_config():
    payload = {
        "feed": {
            "entry": [
                {
                    "id": {"label": "review-1"},
                    "title": {"label": "Sulit login"},
                    "content": {"label": "Aplikasi BIONS susah login otp lambat"},
                    "author": {"name": {"label": "user publik"}, "uri": {"label": "https://itunes.apple.com/id/reviews/id1608763018"}},
                    "im:rating": {"label": "1"},
                    "updated": {"label": "2026-06-01T10:00:00-07:00"},
                    "link": {"attributes": {"href": "https://itunes.apple.com/id/review?id=6736508566&type=Purple%20Software"}},
                }
            ]
        }
    }
    # For BIONS app ID
    items = parse_app_store_reviews(payload, keyword="bions", target_entity="bions", app_id="6736508566", country="id")
    assert items[0].source_url == "https://apps.apple.com/id/app/bions/id6736508566"
    assert items[0].raw_payload["author"]["uri"]["label"] == "https://apps.apple.com/id/reviews/id1608763018"
    assert items[0].raw_payload["link"]["attributes"]["href"] == "https://apps.apple.com/id/app/bions/id6736508566"

    # For other app ID
    items_other = parse_app_store_reviews(payload, keyword="other", target_entity="other", app_id="12345", country="us")
    assert items_other[0].source_url == "https://apps.apple.com/us/app/id12345"
    assert items_other[0].raw_payload["link"]["attributes"]["href"] == "https://apps.apple.com/us/app/id12345"


def test_script_collectors_stop_without_required_runtime_config():
    adapters = [StockbitAdapter(), TwitterAdapter(), TikTokAdapter(), InstagramAdapter(), ThreadsAdapter()]

    for adapter in adapters:
        assert adapter.enabled_by_default is False
        assert adapter.access_mode in {"public_http", "public_oembed", "official_api", "official_graph_api", "official_threads_api"}
        with pytest.raises(CollectorNotConfigured):
            adapter.collect(keyword="bions", target_entity="bions", limit=10)

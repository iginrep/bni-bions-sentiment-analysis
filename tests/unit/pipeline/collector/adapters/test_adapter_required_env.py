from __future__ import annotations

import pytest
from pipeline.collector.adapters.twitter import TwitterAdapter
from pipeline.collector.adapters.instagram import InstagramAdapter
from pipeline.collector.adapters.threads import ThreadsAdapter
from pipeline.collector.adapters.tiktok import TikTokAdapter, TikTokResearchAdapter
from pipeline.collector.adapters.youtube import YouTubeAdapter

pytestmark = pytest.mark.unit


def test_twitter_adapter_declares_required_env():
    assert "X_BEARER_TOKEN" in TwitterAdapter.required_env


def test_instagram_adapter_declares_required_env():
    assert "INSTAGRAM_GRAPH_ACCESS_TOKEN" in InstagramAdapter.required_env


def test_threads_adapter_declares_required_env():
    assert "THREADS_ACCESS_TOKEN" in ThreadsAdapter.required_env


def test_tiktok_adapters_declare_required_env():
    assert "TIKTOK_TARGET_URLS" in TikTokAdapter.required_env
    assert "TIKTOK_RESEARCH_ACCESS_TOKEN" in TikTokResearchAdapter.required_env


def test_youtube_adapter_declares_required_env():
    assert "YOUTUBE_API_KEY" in YouTubeAdapter.required_env

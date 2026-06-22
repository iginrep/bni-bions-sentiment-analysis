from __future__ import annotations

import pytest

from pipeline.collector.adapters.instagram import InstagramAdapter
from pipeline.collector.adapters.threads import ThreadsAdapter

pytestmark = pytest.mark.unit


def test_instagram_adapter_declares_required_token_and_accepts_two_lanes():
    assert hasattr(InstagramAdapter, "required_env")
    assert "INSTAGRAM_GRAPH_ACCESS_TOKEN" in InstagramAdapter.required_env

    adapter = InstagramAdapter(
        access_token="token",
        media_ids=[],
        ig_user_id="17841405309211844",
        hashtag_queries=["BIONS"],
    )
    assert adapter.media_ids == []
    assert adapter.hashtag_queries == ["BIONS"]


def test_threads_adapter_declares_required_token_and_accepts_two_lanes():
    assert hasattr(ThreadsAdapter, "required_env")
    assert "THREADS_ACCESS_TOKEN" in ThreadsAdapter.required_env

    adapter = ThreadsAdapter(access_token="token", media_ids=[], search_queries=["BIONS"])
    assert adapter.media_ids == []
    assert adapter.search_queries == ["BIONS"]

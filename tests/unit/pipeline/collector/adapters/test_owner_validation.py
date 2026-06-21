from __future__ import annotations

import pytest
from pipeline.collector.adapters.instagram import InstagramAdapter
from pipeline.collector.adapters.threads import ThreadsAdapter

pytestmark = pytest.mark.unit


def test_instagram_adapter_has_media_ids_field():
    assert hasattr(InstagramAdapter, "required_env")
    assert "INSTAGRAM_MEDIA_IDS" in InstagramAdapter.required_env


def test_threads_adapter_has_media_ids_field():
    assert hasattr(ThreadsAdapter, "required_env")
    assert "THREADS_MEDIA_IDS" in ThreadsAdapter.required_env

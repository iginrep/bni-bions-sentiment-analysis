from __future__ import annotations

import httpx
import pytest
from pipeline.collector.http import ResilientClient

pytestmark = pytest.mark.unit


def test_resilient_client_retries_on_500_then_succeeds():
    attempt = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        attempt["n"] += 1
        if attempt["n"] == 1:
            return httpx.Response(500)
        return httpx.Response(200, text="ok")

    client = ResilientClient(transport=httpx.MockTransport(handler), max_retries=1, backoff=0)
    response = client.get("https://example.com")
    assert response.status_code == 200
    assert attempt["n"] == 2
    client.close()


def test_resilient_client_returns_429_without_retry():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429)

    client = ResilientClient(transport=httpx.MockTransport(handler), max_retries=3, backoff=0)
    response = client.get("https://example.com")
    assert response.status_code == 429
    client.close()

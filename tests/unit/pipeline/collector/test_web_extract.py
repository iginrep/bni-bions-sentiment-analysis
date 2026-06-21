from __future__ import annotations

import httpx
import pytest
from pipeline.collector.web_extract import fetch_public_html

pytestmark = pytest.mark.unit


def test_fetch_public_html_stops_on_403():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, text="forbidden")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    with pytest.raises(Exception):
        fetch_public_html("https://example.com", client=client)
    client.close()


def test_fetch_public_html_stops_on_401():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, text="unauthorized")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    with pytest.raises(Exception):
        fetch_public_html("https://example.com", client=client)
    client.close()


def test_fetch_public_html_stops_on_429():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, text="rate limited")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    with pytest.raises(Exception):
        fetch_public_html("https://example.com", client=client)
    client.close()

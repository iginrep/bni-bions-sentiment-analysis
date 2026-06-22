from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


def test_health_endpoint(api_client: TestClient):
    response = api_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.skipif(
    not pytest.importorskip("torch", reason="torch not installed"),
    reason="IndoBERT requires torch",
)
def test_sentiment_classify_endpoint_returns_valid_label(api_client: TestClient):
    response = api_client.post("/sentiment/classify", json={"text": "BIONS error login gagal"})

    assert response.status_code == 200
    data = response.json()
    assert data["label"] in ("positive", "negative", "neutral")
    assert isinstance(data["score"], (int, float))
    assert data["method"] == "indobert"

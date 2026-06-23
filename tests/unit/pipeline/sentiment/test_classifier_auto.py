from __future__ import annotations

import pytest

from pipeline.sentiment.classifier import classify_document

pytestmark = pytest.mark.unit


def test_classify_document_auto_uses_openrouter_first_when_key_exists(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr("pipeline.sentiment.classifier._classify_openrouter", lambda text: {"label": "negative", "confidence": 0.9, "score": -0.8, "topics": [], "method": "openrouter", "model_version": "openrouter/free"})
    monkeypatch.setattr("pipeline.sentiment.classifier._classify_model", lambda text: pytest.fail("model should not run"))

    doc = {"content": {"text": "aplikasi error"}, "engagement": {"rating": 1}}

    result = classify_document(doc, method="auto")

    assert result["label"] == "negative"
    assert result["method"] == "openrouter"
    assert result["model_version"] == "openrouter/free"
    assert "quality" in result


def test_classify_document_auto_falls_back_to_model_without_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setattr("pipeline.sentiment.classifier._classify_model", lambda text: {"label": "neutral", "confidence": 0.7, "score": 0.0, "topics": [], "method": "model", "model_version": "test"})

    result = classify_document({"content": {"text": "bions"}}, method="auto")

    assert result["method"] == "model"

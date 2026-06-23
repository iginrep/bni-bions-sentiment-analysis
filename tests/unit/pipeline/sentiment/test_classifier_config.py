from __future__ import annotations

import pytest

from pipeline.sentiment.classifier import DEFAULT_MODEL, _get_model

pytestmark = pytest.mark.unit


def test_default_model_is_base_p2():
    assert DEFAULT_MODEL == "indobenchmark/indobert-base-p2"


def test_get_model_uses_default_base_p2_model(monkeypatch):
    calls: list[str] = []

    class FakeTokenizer:
        @classmethod
        def from_pretrained(cls, model_name: str):
            calls.append(model_name)
            return object()

    class FakeModel:
        config = type("Config", (), {"id2label": {0: "negative", 1: "neutral", 2: "positive"}})()

        @classmethod
        def from_pretrained(cls, model_name: str, **kwargs):
            calls.append(model_name)
            return cls()

        def eval(self):
            return None

    monkeypatch.delenv("MODEL_NAME", raising=False)
    monkeypatch.setattr("pipeline.sentiment.classifier._model_tokenizer", None)
    monkeypatch.setattr("pipeline.sentiment.classifier._model", None)
    monkeypatch.setattr("pipeline.sentiment.classifier._model_name", None)
    monkeypatch.setattr("pipeline.sentiment.classifier._model_labels", None)
    monkeypatch.setattr("transformers.AutoTokenizer", FakeTokenizer)
    monkeypatch.setattr("transformers.AutoModelForSequenceClassification", FakeModel)

    _get_model()

    assert calls == ["indobenchmark/indobert-base-p2", "indobenchmark/indobert-base-p2"]


def test_get_model_configures_sentiment_labels_for_base_checkpoint(monkeypatch):
    kwargs_seen: dict = {}

    class FakeTokenizer:
        @classmethod
        def from_pretrained(cls, model_name: str):
            return object()

    class FakeModel:
        config = type("Config", (), {"id2label": {0: "negative", 1: "neutral", 2: "positive"}})()

        @classmethod
        def from_pretrained(cls, model_name: str, **kwargs):
            kwargs_seen.update(kwargs)
            return cls()

        def eval(self):
            return None

    monkeypatch.delenv("MODEL_NAME", raising=False)
    monkeypatch.setattr("pipeline.sentiment.classifier._model_tokenizer", None)
    monkeypatch.setattr("pipeline.sentiment.classifier._model", None)
    monkeypatch.setattr("pipeline.sentiment.classifier._model_name", None)
    monkeypatch.setattr("pipeline.sentiment.classifier._model_labels", None)
    monkeypatch.setattr("transformers.AutoTokenizer", FakeTokenizer)
    monkeypatch.setattr("transformers.AutoModelForSequenceClassification", FakeModel)

    _get_model()

    assert kwargs_seen["num_labels"] == 3
    assert kwargs_seen["id2label"] == {0: "negative", 1: "neutral", 2: "positive"}
    assert kwargs_seen["label2id"] == {"negative": 0, "neutral": 1, "positive": 2}
    assert kwargs_seen["ignore_mismatched_sizes"] is True

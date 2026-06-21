from __future__ import annotations

import pytest
from pipeline.collector.config_validator import detect_missing_env, summarize_collector_env

pytestmark = pytest.mark.unit


def test_detect_missing_env_returns_expected_names():
    assert detect_missing_env(["A", "B"]) == ["A", "B"]


def test_summarize_collector_env_marks_configured_when_present(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("X_BEARER_TOKEN", "token")
    summary = summarize_collector_env({"x": ["X_BEARER_TOKEN"]})
    assert summary["x"]["configured"] is True
    assert summary["x"]["missing_env"] == []

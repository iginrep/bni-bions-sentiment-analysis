from __future__ import annotations

import pytest
from pipeline.collector.run import build_report, validate_collectors
from pipeline.collector.base import RawSocialItem

pytestmark = pytest.mark.unit


def test_validate_collectors_returns_all_platforms():
    result = validate_collectors()
    assert "app_store" in result
    assert "x" in result
    assert "instagram" in result
    assert "threads" in result


def test_validate_collectors_marks_missing_tokens():
    result = validate_collectors()
    assert result["x"]["configured"] is False
    assert "X_BEARER_TOKEN" in result["x"]["missing_env"]


def test_validate_collectors_marks_env_free_platforms():
    result = validate_collectors()
    assert result["app_store"]["configured"] is True
    assert result["google_play"]["configured"] is True


def test_build_report_returns_validation_and_count():
    report = build_report(items=[])
    assert "validation" in report
    assert report["collected_count"] == 0

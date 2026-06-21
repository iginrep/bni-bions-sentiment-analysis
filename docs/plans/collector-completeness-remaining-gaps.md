# Collector Completeness Implementation Plan

> **For Hermes:** Use this plan as the implementation blueprint for the remaining collector gaps in `/home/hp/dev/work/bni-bions-sentiment-analysis`.

**Goal:** finish the remaining collector work by adding config validation, startup checks, retry/throttle, safer public scraper gates, owner validation where supported, and the first pass of write-path support.

**Architecture:** keep the current script-first collector shape, but split concerns into adapter execution, config validation, resilient HTTP, and storage. collectors stay read-only until the end of the pipeline unless explicitly routed to storage through a narrow write helper.

**Tech stack:** python, httpx, pytest, pydantic/pydantic-settings, pymongo, optional tenacity for backoff.

---

## Task 1: add config validation

**Objective:** create a small validation module that can inspect adapters/env vars before collection runs.

**Files:**
- Create: `pipeline/collector/config_validator.py`
- Create: `tests/unit/pipeline/collector/test_config_validator.py`
- Modify: `pipeline/collector/run.py` (later task only if needed)

**Step 1: write failing test**

```python
import pytest
from pipeline.collector.config_validator import detect_missing_env

pytestmark = pytest.mark.unit

def test_detect_missing_env_returns_expected_names():
    assert detect_missing_env(["A", "B"]) == ["A", "B"]
```

**Step 2: run test to verify failure**

Run: `pytest tests/unit/pipeline/collector/test_config_validator.py -v`
Expected: FAIL

**Step 3: write minimal implementation**

```python
from __future__ import annotations
import os

def detect_missing_env(names: list[str]) -> list[str]:
    return [name for name in names if not os.getenv(name)]
```

**Step 4: run test to verify pass**

Run: `pytest tests/unit/pipeline/collector/test_config_validator.py -v`
Expected: PASS

---

## Task 2: add adapter required-env metadata

**Objective:** give each adapter an explicit list of required env vars so startup checks are consistent.

**Files:**
- Modify: `pipeline/collector/adapters/app_store.py`
- Modify: `pipeline/collector/adapters/google_play.py`
- Modify: `pipeline/collector/adapters/youtube.py`
- Modify: `pipeline/collector/adapters/twitter.py`
- Modify: `pipeline/collector/adapters/tiktok.py`
- Modify: `pipeline/collector/adapters/instagram.py`
- Modify: `pipeline/collector/adapters/threads.py`
- Modify: `pipeline/collector/adapters/stockbit.py`
- Create: `tests/unit/pipeline/collector/adapters/test_adapter_required_env.py`

**Step 1: write failing test**

```python
import pytest
from pipeline.collector.adapters.twitter import TwitterAdapter

pytestmark = pytest.mark.unit

def test_twitter_adapter_declares_required_env():
    assert "X_BEARER_TOKEN" in TwitterAdapter.required_env
```

**Step 2: run test to verify failure**

Run: `pytest tests/unit/pipeline/collector/adapters/test_adapter_required_env.py -v`
Expected: FAIL

**Step 3: implement**

add `required_env: list[str]` class attribute to each adapter. examples:
- `TwitterAdapter`: `["X_BEARER_TOKEN"]`
- `InstagramAdapter`: `["INSTAGRAM_GRAPH_ACCESS_TOKEN", "INSTAGRAM_MEDIA_IDS"]`
- `ThreadsAdapter`: `["THREADS_ACCESS_TOKEN", "THREADS_MEDIA_IDS"]`
- `TikTokResearchAdapter`: `["TIKTOK_RESEARCH_ACCESS_TOKEN", "TIKTOK_VIDEO_IDS"]`
- `StockbitAdapter`: `["STOCKBIT_TARGET_URLS"]`
- `YouTubeAdapter`: `[]` (token optional for comments but not for full collection)
- `GooglePlayAdapter`: `[]`
- `AppStoreAdapter`: `[]`

**Step 4: run test to verify pass**

Run: `pytest tests/unit/pipeline/collector/adapters/test_adapter_required_env.py -v`
Expected: PASS

---

## Task 3: add startup collector validation

**Objective:** add a CLI-visible validation pass that reports missing config without running adapters.

**Files:**
- Modify: `pipeline/collector/run.py`
- Create: `tests/unit/pipeline/collector/test_run_validation.py`

**Step 1: write failing test**

```python
import pytest
from pipeline.collector.run import build_report

pytestmark = pytest.mark.unit

def test_build_report_marks_missing_token_adapter_not_configured():
    adapters = {"x": object()}
    report = build_report(items=[], adapters=adapters)
    assert "x" in report
```

**Step 2: run test to verify failure**

Run: `pytest tests/unit/pipeline/collector/test_run_validation.py -v`
Expected: FAIL

**Step 3: implement**

add `validate_collectors()` or expand `build_report()` so run can report `status=not_configured` when adapter metadata or env presence is insufficient.

**Step 4: run test to verify pass**

Run: `pytest tests/unit/pipeline/collector/test_run_validation.py -v`
Expected: PASS

---

## Task 4: add resilient request wrapper

**Objective:** add one shared helper for transient retry, throttle, and stop-gate behavior.

**Files:**
- Create: `pipeline/collector/http.py`
- Create: `tests/unit/pipeline/collector/test_http.py`

**Step 1: write failing test**

```python
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

    client = ResilientClient(transport=httpx.MockTransport(handler), max_retries=1)
    response = client.get("https://example.com")
    assert response.status_code == 200
    assert attempt["n"] == 2
```

**Step 2: run test to verify failure**

Run: `pytest tests/unit/pipeline/collector/test_http.py -v`
Expected: FAIL

**Step 3: implement minimal wrapper**

build `ResilientClient` around `httpx.Client` with:
- retry on 5xx network/transient failures
- sleep/backoff for 429
- stop on 401/403/429 after threshold if needed
- read-only by default

**Step 4: run test to verify pass**

Run: `pytest tests/unit/pipeline/collector/test_http.py -v`
Expected: PASS

---

## Task 5: wire adapters to resilient client

**Objective:** replace raw `httpx.get/post` usage in adapters with the shared resilient client.

**Files:**
- Modify: `pipeline/collector/adapters/twitter.py`
- Modify: `pipeline/collector/adapters/youtube.py`
- Modify: `pipeline/collector/adapters/instagram.py`
- Modify: `pipeline/collector/adapters/threads.py`
- Modify: `pipeline/collector/adapters/tiktok.py`
- Modify: `pipeline/collector/adapters/app_store.py`

**Step 1: run regression tests first**

Run: `pytest -q`
Expected: existing suite still passes.

**Step 2: refactor one adapter at a time**

start with `TwitterAdapter`, then `AppStoreAdapter`, then others.

**Step 3: run regression after each change**

Run: `pytest -q`
Expected: PASS

---

## Task 6: improve public scraper gates

**Objective:** make stockbit/tiktok public scraping safer and more debuggable.

**Files:**
- Modify: `pipeline/collector/web_extract.py`
- Modify: `pipeline/collector/adapters/stockbit.py`
- Modify: `pipeline/collector/adapters/tiktok.py`
- Create: `tests/unit/pipeline/collector/test_web_extract.py`

**Step 1: write failing test**

```python
import httpx
import pytest
from pipeline.collector.web_extract import fetch_public_html

pytestmark = pytest.mark.unit

def test_fetch_public_html_stops_on_403():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    with pytest.raises(Exception):
        fetch_public_html("https://example.com", client=client)
```

**Step 2: run test to verify failure**

Run: `pytest tests/unit/pipeline/collector/test_web_extract.py -v`
Expected: FAIL

**Step 3: implement**

add explicit response validation, optional delay, timeout enforcement, and clean stop on login/captcha/403/429.

**Step 4: run test to verify pass**

Run: `pytest tests/unit/pipeline/collector/test_web_extract.py -v`
Expected: PASS

---

## Task 7: add owner-validation where APIs support it

**Objective:** tighten owned-content lanes by checking author/username/post owner before treating content as official.

**Files:**
- Modify: `pipeline/collector/adapters/twitter.py`
- Modify: `pipeline/collector/adapters/youtube.py`
- Modify: `pipeline/collector/adapters/instagram.py`
- Modify: `pipeline/collector/adapters/threads.py`
- Create: `tests/unit/pipeline/collector/adapters/test_owner_validation.py`

**Step 1: write failing test**

```python
import pytest
from pipeline.collector.adapters.threads import ThreadsAdapter

pytestmark = pytest.mark.unit

def test_threads_adapter_has_owner_field():
    assert hasattr(ThreadsAdapter, "official_media_ids") or hasattr(ThreadsAdapter, "media_ids")
```

**Step 2: run test to verify failure or partial fail**
Expected: may fail depending on current attribute naming.

**Step 3: implement**

add `official_usernames`, `official_media_ids`, or equivalent fields so adapters can skip/unmark replies from unknown owners.

**Step 4: run tests**

Run: `pytest tests/unit/pipeline/collector/adapters/test_owner_validation.py -v`
Expected: PASS

---

## Task 8: add narrow write-path helper

**Objective:** add the first pass of storage support without bloating adapters.

**Files:**
- Create: `pipeline/storage/social_items.py`
- Create: `tests/unit/pipeline/storage/test_social_items.py`

**Step 1: write failing test**

```python
import pytest
from pipeline.storage.social_items import to_canonical_doc

pytestmark = pytest.mark.unit

def test_to_canonical_doc_sets_platform_source_id():
    doc = to_canonical_doc({"platform": "x", "source_id": "1"})
    assert doc["platform"] == "x"
    assert doc["sourceId"] == "1"
```

**Step 2: run test to verify failure**

Run: `pytest tests/unit/pipeline/storage/test_social_items.py -v`
Expected: FAIL

**Step 3: implement**

create a mapper from `RawSocialItem`/runner dicts into the canonical mongo doc shape used by `apps.api.app.repositories.social_items.upsert_social_item`.

**Step 4: run test to verify pass**

Run: `pytest tests/unit/pipeline/storage/test_social_items.py -v`
Expected: PASS

---

## Task 9: add optional CLI write flag

**Objective:** allow `collect_sample` / runner to optionally persist rows.

**Files:**
- Modify: `pipeline/collector/run.py`
- Create: `tests/unit/pipeline/collector/test_run_write.py`

**Step 1: write failing test**

```python
import pytest
from pipeline.collector.run import collect_sample

pytestmark = pytest.mark.unit

def test_collect_sample_write_flag_does_not_crash_when_storage_missing():
    items, report = collect_sample(write=False)
    assert isinstance(report, dict)
```

**Step 2: run test to verify pass**

Run: `pytest tests/unit/pipeline/collector/test_run_write.py -v`
Expected: PASS

**Step 3: implement flag**

add `write=False` parameter and conditional persistence path.

**Step 4: run regression**

Run: `pytest -q`
Expected: PASS

---

## Task 10: refresh docs and env sample

**Objective:** make the project state explicit for future runs.

**Files:**
- Modify: `.env.example`
- Modify: `docs/data-collector-target-strategy.md`
- Create: `tests/unit/pipeline/collector/test_docs_consistency.py`

**Step 1: write failing test**

```python
from pathlib import Path
import pytest

pytestmark = pytest.mark.unit

def test_env_example_mentions_instagram_graph_access_token():
    text = Path(".env.example").read_text()
    assert "INSTAGRAM_GRAPH_ACCESS_TOKEN" in text
```

**Step 2: run test to verify failure or pass**

run and fix content until missing fields are documented.

**Step 3: implement**

update `.env.example` with full documented vars and update strategy doc with validation/retry notes.

**Step 4: run test to verify pass**

Run: `pytest tests/unit/pipeline/collector/test_docs_consistency.py -v`
Expected: PASS

---

## Final verification

Run:
```bash
pytest -q
node --check db/mongo-init.js
git diff --check
```

Expected: all tests pass, no secret leakage, no uncommitted config contradictions.

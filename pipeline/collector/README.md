# collector pipeline

Platform collection layer for public BNI/BIONS feedback.

## Purpose

Collectors fetch source-specific data and normalize it into `RawSocialItem` from `pipeline/collector/base.py`.

## Canonical model

Important fields:

```txt
platform
source_type
source_id
keyword
target_entity
text
author_id
author_username
author_display_name
language
source_url
posted_at
collected_at
metrics
raw_payload
content_hash
collection_method
access_risk
collector_version
```

## Adapter contract

Each adapter implements:

```python
collect(keyword: str, target_entity: str, limit: int = 50) -> list[RawSocialItem]
```

Adapter metadata:

```txt
platform
access_mode
cost_level
risk_level
enabled_by_default
```

## Approved enabled sources

| Adapter | Source | Default |
| --- | --- | --- |
| `google_play.py` | BIONS Google Play reviews | enabled |
| `app_store.py` | BIONS Apple App Store reviews | enabled |
| `youtube.py` | approved BNI/BIONS YouTube channels | enabled with `YOUTUBE_API_KEY` |

## Disabled risky sources

| Adapter | Reason |
| --- | --- |
| `stockbit.py` | likely login/session automation. |
| `twitter.py` | official paid path or high-risk unofficial scraping. |
| `tiktok.py` | unstable public access, CAPTCHA risk. |
| `instagram.py` | login/API limitations. |
| `threads.py` | limited public discovery/API. |

Do not enable disabled adapters without explicit current-task approval.

## Stop conditions

Stop on 401/403, 429, CAPTCHA, login wall, quota exhaustion, private/deleted content, or repeated server failures.

## Tests

```bash
. .venv/bin/activate
pytest -q tests/test_normalizer.py tests/test_dedupe.py
```

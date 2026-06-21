# Apple App Store Reviews Collector

Collects latest BIONS app reviews from Apple App Store using the public RSS feed. No API key needed.

## What it collects

- Review title and text
- Star rating
- Author display name
- App version at time of review
- Post date

## Prerequisites

- Virtual environment activated (see [Prerequisites](00-prerequisites.md))
- No env vars needed -- works out of the box

## Run it

From the project root:

```bash
python3 -m pipeline.collector.adapters.app_store
```

Or use the runner:

```bash
python3 -m pipeline.collector.run
```

## What you will see

Each line is a JSON object representing one review:

```json
{
  "platform": "app_store",
  "source_type": "app_review",
  "source_id": "1234567890",
  "text": "fitur bagus tapi lambat",
  "metrics": {"rating": 3},
  "posted_at": "2025-01-10T08:00:00+00:00",
  "collection_method": "rss",
  "access_risk": "low"
}
```

## How to verify it worked

You should see reviews printed. The RSS feed returns up to 50 reviews per page and scrolls through pages automatically until the limit is reached.

## Customize

```python
from pipeline.collector.adapters.app_store import AppStoreAdapter

adapter = AppStoreAdapter(app_id="6736508566", country="id")
items = adapter.collect(keyword="bions", target_entity="bions", limit=30)
print(f"Collected {len(items)} reviews")
```

## Troubleshooting

| Problem | Fix |
| --- | --- |
| Empty results | The RSS feed may be temporarily unavailable. Try again in a few minutes |
| HTTP error | Apple may be blocking rapid requests. Wait and retry |

---

**Next:** [03 - YouTube](03-youtube.md) | **Back:** [01 - Google Play](01-google-play.md)

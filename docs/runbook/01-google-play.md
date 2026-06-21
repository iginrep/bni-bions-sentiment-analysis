# Google Play Reviews Collector

Collects latest BIONS app reviews from Google Play Store. No API key needed.

## What it collects

- Review text, star rating, thumbs up count
- Author display name (anonymous on Google Play)
- App version at time of review
- Post date

## Prerequisites

- Virtual environment activated (see [Prerequisites](00-prerequisites.md))
- No env vars needed -- works out of the box

## Run it

From the project root:

```bash
python3 -m pipeline.collector.adapters.google_play
```

Or use the runner (collects from all enabled platforms):

```bash
python3 -m pipeline.collector.run
```

## What you will see

Each line is a JSON object representing one review:

```json
{
  "platform": "google_play",
  "source_type": "app_review",
  "source_id": "gp_review_abc123",
  "text": "aplikasinya sering crash pas buka menu trading",
  "metrics": {"rating": 2, "thumbs_up": 5},
  "posted_at": "2025-01-15T10:30:00+00:00",
  "collection_method": "scraper",
  "access_risk": "low"
}
```

## How to verify it worked

You should see 10 reviews printed (default limit). If you see an empty list, the scraper may have hit a temporary block -- try again in a few minutes.

## Customize

To change how many reviews to collect:

```python
from pipeline.collector.adapters.google_play import GooglePlayAdapter

adapter = GooglePlayAdapter()
items = adapter.collect(keyword="bions", target_entity="bions", limit=20)
print(f"Collected {len(items)} reviews")
```

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `ModuleNotFoundError: No module named 'google_play_scraper'` | Run `pip install -e '.[collectors]'` |
| Empty results | Google Play may be rate-limiting. Wait 5-10 minutes and try again |
| `CollectorStopped` error | The scraper hit a block. This is expected occasionally. |

---

**Next:** [02 - Apple App Store](02-app-store.md) | **Back:** [00 - Prerequisites](00-prerequisites.md)

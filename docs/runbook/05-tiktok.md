# TikTok Comments Collector

Two modes available:
- **oembed (free, no key):** fetches video metadata from known TikTok URLs
- **Research API (needs access):** fetches comments on specific videos

## What it collects

### oembed mode
- Video title/caption
- Author username and display name
- Video URL

### Research API mode
- Comment text, like count, reply count
- Thread structure (parent/child comments)
- Author info

## Prerequisites

- Virtual environment activated (see [Prerequisites](00-prerequisites.md))

### oembed mode (no setup)
No env vars needed. You provide TikTok video URLs.

### Research API mode
- `TIKTOK_RESEARCH_ACCESS_TOKEN` set in `.env`
- `TIKTOK_VIDEO_IDS` set in `.env` (comma-separated video IDs)

### How to get TikTok Research API access

1. Go to [developers.tiktok.com](https://developers.tiktok.com/)
2. Apply for **Research API** access (requires approval -- academic or enterprise use)
3. Once approved, generate an access token
4. Add to `.env`:
   ```
   TIKTOK_RESEARCH_ACCESS_TOKEN=***
   TIKTOK_VIDEO_IDS=7301234567890123456,7309876543210987654
   ```
   Find video IDs from the TikTok URL: `tiktok.com/@user/video/`**`7301234567890123456`**

## Run it

### oembed mode

```bash
python3 -c "
from pipeline.collector.adapters.tiktok import TikTokAdapter

adapter = TikTokAdapter(target_urls=[
    'https://www.tiktok.com/@user/video/7301234567890123456',
])
items = adapter.collect(keyword='bions', target_entity='bions', limit=10)
for item in items:
    print(item.text[:80])
"
```

### Research API mode

```bash
python3 -m pipeline.collector.adapters.tiktok
```

Or use the runner:

```bash
python3 -m pipeline.collector.run
```

## What you will see

oembed:

```json
{
  "platform": "tiktok",
  "source_type": "video",
  "source_id": "7301234567890123456",
  "text": "review BIONS app dari saya",
  "author_username": "user123",
  "collection_method": "public_oembed",
  "access_risk": "medium"
}
```

Research API comments:

```json
{
  "platform": "tiktok",
  "source_type": "comment",
  "source_id": "comment_abc",
  "root_source_id": "7301234567890123456",
  "depth": 1,
  "relation_type": "comment",
  "text": "aplikasi ini susah login",
  "metrics": {"like_count": 5, "reply_count": 1},
  "collection_method": "official_research_api"
}
```

## How to verify it worked

- oembed mode: you should see video metadata for each URL you provided
- Research API: you should see comments on the specified video IDs

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `CollectorNotConfigured: TIKTOK_TARGET_URLS missing` | Add TikTok URLs to `.env` as `TIKTOK_TARGET_URLS=url1,url2` |
| `CollectorNotConfigured: TIKTOK_RESEARCH_ACCESS_TOKEN missing` | Apply for Research API access first |
| 403 Forbidden | Token expired or video is private. Check token and URLs |
| oembed returns empty | TikTok may have changed their oembed endpoint. Check the URL format |
| Rate limiting | Add delays between requests. TikTok is aggressive with rate limits |

---

**Next:** [06 - Instagram](06-instagram.md) | **Back:** [04 - X/Twitter](04-x-twitter.md)

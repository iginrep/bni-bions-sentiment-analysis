# YouTube Comments Collector

Collects videos and comments from approved BNI/BIONS YouTube channels. Uses RSS for video discovery and YouTube Data API v3 for comments.

## What it collects

- Video titles and metadata (from RSS, free)
- Top-level comments on each video
- Reply threads on comments
- Like counts, reply counts
- Author display names

## Prerequisites

- Virtual environment activated (see [Prerequisites](00-prerequisites.md))
- `YOUTUBE_API_KEY` set in `.env` -- without this, only video titles are collected (no comments)

### How to get a YouTube API key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or use an existing one)
3. Enable the **YouTube Data API v3**
4. Go to **Credentials** -> **Create Credentials** -> **API Key**
5. Copy the key into your `.env` file:
   ```
   YOUTUBE_API_KEY=your_key_here
   ```

Free tier gives 10,000 units/day. Each comment thread costs ~1 unit, so you can fetch thousands of comments daily for free.

## Run it

From the project root:

```bash
python3 -m pipeline.collector.adapters.youtube
```

Or use the runner:

```bash
python3 -m pipeline.collector.run
```

## What you will see

Without API key (video titles only):

```json
{
  "platform": "youtube",
  "source_type": "video",
  "source_id": "dQw4w9WgXcQ",
  "text": "Cara Daftar BIONS - Tutorial Lengkap",
  "collection_method": "rss"
}
```

With API key (comments):

```json
{
  "platform": "youtube",
  "source_type": "comment",
  "source_id": "abc123",
  "root_source_id": "dQw4w9WgXcQ",
  "depth": 1,
  "relation_type": "comment",
  "text": "aplikasinya bagus tapi login susah",
  "metrics": {"like_count": 3, "reply_count": 2},
  "collection_method": "youtube_data_api"
}
```

## How to verify it worked

- Without API key: you should see video titles from `@BNI1946` and `@bnisekuritas46`
- With API key: you should see comments and replies on those videos

## Customize

```python
from pipeline.collector.adapters.youtube import YouTubeAdapter

adapter = YouTubeAdapter(channel_urls=["https://www.youtube.com/@BNI1946"])
items = adapter.collect(keyword="bions", target_entity="bions", limit=50)
print(f"Collected {len(items)} items")
```

## Troubleshooting

| Problem | Fix |
| --- | --- |
| Only video titles, no comments | `YOUTUBE_API_KEY` is missing or invalid. Check `.env` |
| `YOUTUBE_API_KEY missing` error | Add the key to `.env` as shown above |
| Quota exceeded | You hit the 10,000 unit/day free limit. Wait 24 hours or create a new project |
| Empty results | The channels may have no recent videos. Check the channels exist |

---

**Next:** [04 - X/Twitter](04-x-twitter.md) | **Back:** [02 - App Store](02-app-store.md)

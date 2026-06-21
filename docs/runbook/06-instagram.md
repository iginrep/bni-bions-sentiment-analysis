# Instagram Comments Collector

Two modes available:
- **public HTTP (free, no key):** fetches post metadata from public Instagram URLs
- **Graph API (needs token):** fetches comments on specific media posts

## What it collects

### public HTTP mode
- Post caption/text from JSON-LD metadata
- Author username
- Like count (if available in metadata)

### Graph API mode
- Comment text, author username, timestamp
- Reply threads on comments
- Full conversation structure

## Prerequisites

- Virtual environment activated (see [Prerequisites](00-prerequisites.md))

### Graph API mode (recommended)

- `INSTAGRAM_GRAPH_ACCESS_TOKEN` set in `.env`
- `INSTAGRAM_MEDIA_IDS` set in `.env` (comma-separated media IDs)

### How to get an Instagram Graph API token

1. Go to [developers.facebook.com](https://developers.facebook.com/)
2. Create an **App** -> select **Business** type
3. Add the **Instagram Graph API** product
4. Go to **Graph API Explorer** -> generate a token with `instagram_basic` and `instagram_manage_comments` permissions
5. Find your media IDs using the Graph API:
   ```
   GET /me/media?fields=id,caption,timestamp&access_token=YOUR_TOKEN
   ```
6. Add to `.env`:
   ```
   INSTAGRAM_GRAPH_ACCESS_TOKEN=***
   INSTAGRAM_MEDIA_IDS=1789012345678901234,1789012345678905678
   ```

**Important:** The Instagram Graph API requires a Facebook Page connected to an Instagram Business or Creator account. Personal Instagram accounts cannot use the Graph API.

### public HTTP mode (limited)

No env vars needed. Provide Instagram post URLs. This only extracts post metadata from the page HTML -- it cannot fetch comments.

## Run it

### Graph API mode

```bash
python3 -m pipeline.collector.adapters.instagram
```

Or use the runner:

```bash
python3 -m pipeline.collector.run
```

### public HTTP mode

```python
from pipeline.collector.adapters.instagram import InstagramAdapter
from pipeline.collector.web_extract import fetch_public_html

# This extracts post metadata only (no comments)
url = "https://www.instagram.com/p/ABC123/"
html = fetch_public_html(url)
```

## What you will see

Graph API comment:

```json
{
  "platform": "instagram",
  "source_type": "comment",
  "source_id": "1789012345678909999",
  "root_source_id": "1789012345678901234",
  "depth": 1,
  "relation_type": "comment",
  "text": "BIONS mantap!",
  "author_username": "user123",
  "posted_at": "2025-01-15T10:30:00+00:00",
  "collection_method": "official_graph_api"
}
```

Reply to a comment:

```json
{
  "platform": "instagram",
  "source_type": "comment",
  "source_id": "1789012345678911111",
  "root_source_id": "1789012345678901234",
  "parent_source_id": "1789012345678909999",
  "depth": 2,
  "relation_type": "reply",
  "text": "setuju banget",
  "collection_method": "official_graph_api"
}
```

## How to verify it worked

- With Graph API token: you should see comments and replies on the specified media IDs
- Without token: only post metadata from public URLs (no comments)

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `INSTAGRAM_GRAPH_ACCESS_TOKEN missing` | Add the token to `.env` |
| `INSTAGRAM_MEDIA_IDS missing` | Add media IDs to `.env`. Use Graph API Explorer to find them |
| 401 Unauthorized | Token expired. Generate a new one in Graph API Explorer |
| 400 Bad Request | Media ID may be invalid. Verify with Graph API Explorer |
| Empty comments | The post may have no comments, or the token lacks `instagram_manage_comments` permission |
| Personal account error | Must use Business or Creator account connected to a Facebook Page |

---

**Next:** [07 - Threads](07-threads.md) | **Back:** [05 - TikTok](05-tiktok.md)

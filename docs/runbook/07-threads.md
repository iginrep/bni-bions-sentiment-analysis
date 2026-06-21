# Threads Comments Collector

Two modes available:
- **public HTTP (free, no key):** fetches post metadata from public Threads URLs
- **Threads API (needs token):** fetches full conversation threads

## What it collects

### public HTTP mode
- Post text from JSON-LD metadata
- Author username

### Threads API mode
- Full conversation: original post + all replies
- Thread structure (root post, reply-to relationships)
- Timestamps, author usernames

## Prerequisites

- Virtual environment activated (see [Prerequisites](00-prerequisites.md))

### Threads API mode (recommended)

- `THREADS_ACCESS_TOKEN` set in `.env`
- `THREADS_MEDIA_IDS` set in `.env` (comma-separated media IDs)

### How to get a Threads API token

1. Go to [developers.facebook.com](https://developers.facebook.com/)
2. Create an **App** -> select **Business** type
3. Add the **Threads API** product
4. Go to **Graph API Explorer** -> select your app
5. Generate a token with `threads_basic` and `threads_read_replies` permissions
6. Find media IDs:
   ```
   GET /me/threads?fields=id,caption,timestamp&access_token=YOUR_TOKEN
   ```
7. Add to `.env`:
   ```
   THREADS_ACCESS_TOKEN=***
   THREADS_MEDIA_IDS=1789012345678901234
   ```

### public HTTP mode (limited)

No env vars needed. Provide Threads post URLs. Only extracts post metadata -- no replies.

## Run it

### Threads API mode

```bash
python3 -m pipeline.collector.adapters.threads
```

Or use the runner:

```bash
python3 -m pipeline.collector.run
```

### public HTTP mode

```python
from pipeline.collector.web_extract import fetch_public_html

url = "https://www.threads.net/@user/post/ABC123"
html = fetch_public_html(url)
```

## What you will see

Original post:

```json
{
  "platform": "threads",
  "source_type": "post",
  "source_id": "1789012345678901234",
  "root_source_id": "1789012345678901234",
  "depth": 0,
  "text": "fitur baru BIONS keren banget",
  "author_username": "bni1946",
  "collection_method": "official_threads_api"
}
```

Reply:

```json
{
  "platform": "threads",
  "source_type": "reply",
  "source_id": "1789012345678909999",
  "root_source_id": "1789012345678901234",
  "replied_to": "1789012345678901234",
  "depth": 1,
  "relation_type": "reply",
  "text": "mantap emang",
  "author_username": "user456"
}
```

## How to verify it worked

- With API token: you should see the full conversation tree for each media ID
- Without token: only post metadata from public URLs (no replies)

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `THREADS_ACCESS_TOKEN missing` | Add the token to `.env` |
| `THREADS_MEDIA_IDS missing` | Add media IDs to `.env` |
| 401 Unauthorized | Token expired. Generate a new one |
| Empty results | The post may have no replies, or the token lacks `threads_read_replies` permission |
| Rate limiting | Threads API has rate limits. Add delays between requests |

---

**Next:** [08 - Stockbit](08-stockbit.md) | **Back:** [06 - Instagram](06-instagram.md)

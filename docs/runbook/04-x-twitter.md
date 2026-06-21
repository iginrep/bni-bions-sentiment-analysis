# X/Twitter Mentions Collector

Collects public mentions of BNI/BIONS on X (Twitter) and replies on official posts. Uses the official X API v2.

## What it collects

- **Lane A -- Public mentions:** tweets matching search queries like "BIONS" or "BNI Sekuritas"
- **Lane B -- Official post replies:** replies to recent tweets from `@BNI1946` and `@bnisekuritas46`
- Tweet text, like/retweet/reply counts
- Author username and display name
- Conversation thread structure

## Prerequisites

- Virtual environment activated (see [Prerequisites](00-prerequisites.md))
- `X_BEARER_TOKEN` set in `.env`

### How to get an X Bearer Token

1. Go to [developer.x.com](https://developer.x.com/) and apply for a developer account
2. Create a **Project** and **App**
3. Under **Keys and tokens**, find the **Bearer Token**
4. Copy it into your `.env` file:
   ```
   X_BEARER_TOKEN=***
   ```
5. Optionally configure search queries and official usernames:
   ```
   X_OFFICIAL_USERNAMES=BNI1946,bnisekuritas46
   X_SEARCH_QUERIES="BIONS" lang:id -is:retweet,"BNI Sekuritas" lang:id -is:retweet
   ```

### X API access levels

| Level | What you get | Cost |
| --- | --- | --- |
| Free | 1,500 tweets/month read, tweet creation only | Free |
| Basic | 10,000 tweets/month read, full search | $100/month |
| Pro | 1,000,000 tweets/month read, full search | $5,000/month |

The collector uses the **Recent Search** endpoint (`/2/tweets/search/recent`), which requires **Basic** tier or higher. Free tier will return 403.

## Run it

From the project root:

```bash
python3 -m pipeline.collector.adapters.twitter
```

Or use the runner:

```bash
python3 -m pipeline.collector.run
```

## What you will see

Public mention (Lane A):

```json
{
  "platform": "x",
  "source_type": "tweet",
  "source_id": "1234567890",
  "text": "BIONS bagus banget buat trading saham",
  "author_id": "9876543210",
  "language": "id",
  "depth": 0,
  "relation_type": null,
  "metrics": {"like_count": 12, "retweet_count": 3, "reply_count": 2},
  "collection_method": "official_api"
}
```

Official post reply (Lane B):

```json
{
  "platform": "x",
  "source_type": "tweet",
  "source_id": "1234567891",
  "root_source_id": "1234567890",
  "depth": 1,
  "relation_type": "reply",
  "text": "@BNI1946 kok error ya appnya",
  "collection_method": "official_api"
}
```

## How to verify it worked

- Without `X_BEARER_TOKEN`: you will see `CollectorNotConfigured` error
- With free tier token: you may get 403 (need Basic tier for search)
- With Basic/Pro tier: you should see tweets matching your search queries

## Customize

```python
from pipeline.collector.adapters.twitter import TwitterAdapter

adapter = TwitterAdapter(
    bearer_token="your_token_here",
    search_queries=['"BIONS" lang:id -is:retweet'],
    official_usernames=["BNI1946"],
)
items = adapter.collect(keyword="bions", target_entity="bions", limit=50)
print(f"Collected {len(items)} tweets")
```

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `CollectorNotConfigured: X_BEARER_TOKEN missing` | Add the token to `.env` |
| 403 Forbidden | Your X API tier does not include Recent Search. Upgrade to Basic ($100/mo) |
| 429 Too Many Requests | Rate limited. Wait a few minutes |
| 401 Unauthorized | Token is invalid or revoked. Regenerate in developer portal |
| Empty results | Search queries may not match recent tweets. Adjust `X_SEARCH_QUERIES` |

---

**Next:** [05 - TikTok](05-tiktok.md) | **Back:** [03 - YouTube](03-youtube.md)

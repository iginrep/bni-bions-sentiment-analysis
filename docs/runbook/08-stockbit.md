# Stockbit Discussion Collector

Collects public Stockbit discussion pages related to BNI/BIONS. Uses public HTTP scraping -- no API key needed, but this is the riskiest collector.

## What it collects

- Discussion text (HTML stripped, first 5000 chars)
- Post URL

## Important warnings

- **High risk:** Stockbit may block scrapers aggressively
- **No official API:** There is no Stockbit API. This collector scrapes public HTML
- **CAPTCHA:** You may hit CAPTCHA walls if you run this too frequently
- **Limited data:** Only gets the page text, not structured comment data

## Prerequisites

- Virtual environment activated (see [Prerequisites](00-prerequisites.md))
- `STOCKBIT_TARGET_URLS` set in `.env` (comma-separated Stockbit discussion URLs)

### How to find Stockbit URLs

1. Go to [stockbit.com](https://www.stockbit.com/)
2. Search for BNI or BIONS discussions
3. Copy the URLs of discussions you want to monitor
4. Add to `.env`:
   ```
   STOCKBIT_TARGET_URLS=https://www.stockbit.com/post/abc123,https://www.stockbit.com/post/def456
   ```

## Run it

```bash
python3 -m pipeline.collector.adapters.stockbit
```

Or use the runner:

```bash
python3 -m pipeline.collector.run
```

## What you will see

```json
{
  "platform": "stockbit",
  "source_type": "post",
  "source_id": "stockbit_abc123",
  "text": "BIONS app review discussion content here...",
  "source_url": "https://www.stockbit.com/post/abc123",
  "collection_method": "public_http",
  "access_risk": "high"
}
```

## How to verify it worked

- You should see text content from each Stockbit URL you provided
- If you see empty results, the page may require JavaScript rendering or login

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `STOCKBIT_TARGET_URLS missing` | Add Stockbit URLs to `.env` |
| Empty results | Stockbit may require login or JavaScript. This collector only works on public pages |
| 403 Forbidden | Stockbit is blocking the request. Wait and try again later |
| CAPTCHA | You hit a CAPTCHA wall. Reduce request frequency or stop |
| HTML garbage in text | Stockbit pages may have changed structure. The text is HTML-stripped but may include navigation elements |

---

**Next:** [09 - Run All](09-run-all.md) | **Back:** [07 - Threads](07-threads.md)

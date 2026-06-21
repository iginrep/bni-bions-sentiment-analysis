# Prerequisites

Everything you need before running any collector script.

## 1. Install Python 3.11+

Check your version:

```bash
python3 --version
```

If you see `3.11` or higher, you are good. If not, install from [python.org](https://www.python.org/downloads/).

## 2. Clone the project

```bash
git clone https://github.com/iginrep/social-media-data-collector.git
cd social-media-data-collector
```

## 3. Create a virtual environment

This keeps project dependencies separate from your system Python.

```bash
python3 -m venv .venv
. .venv/bin/activate
```

You should see `(.venv)` at the start of your terminal prompt. Every time you open a new terminal to work on this project, run the `. .venv/bin/activate` line first.

## 4. Install dependencies

```bash
pip install -e '.[dev]'
```

For collector-specific packages (TikTok oembed, Instagram public scrape):

```bash
pip install -e '.[collectors]'
```

## 5. Set up configuration

Copy the example config and fill in your values:

```bash
cp .env.example .env
```

Open `.env` in any text editor. Each collector has its own section. You only need to fill in the sections for collectors you want to run.

### What goes where

| Collector | What to fill in | Where to get it |
| --- | --- | --- |
| Google Play | nothing | works out of the box |
| Apple App Store | nothing | works out of the box |
| YouTube | `YOUTUBE_API_KEY` | [Google Cloud Console](https://console.cloud.google.com/) -> APIs -> YouTube Data API v3 |
| X/Twitter | `X_BEARER_TOKEN` | [X Developer Portal](https://developer.x.com/) -> App -> Bearer Token |
| TikTok | `TIKTOK_RESEARCH_ACCESS_TOKEN` + `TIKTOK_VIDEO_IDS` | [TikTok Developer Portal](https://developers.tiktok.com/) -> Research API access |
| Instagram | `INSTAGRAM_GRAPH_ACCESS_TOKEN` + `INSTAGRAM_MEDIA_IDS` | [Meta for Developers](https://developers.facebook.com/) -> Graph API Explorer |
| Threads | `THREADS_ACCESS_TOKEN` + `THREADS_MEDIA_IDS` | [Meta for Developers](https://developers.facebook.com/) -> Threads API |
| Stockbit | `STOCKBIT_TARGET_URLS` | manually copy the Stockbit discussion URLs you want to monitor |

## 6. Verify it works

Run the tests to confirm everything is installed correctly:

```bash
. .venv/bin/activate
pytest -q
```

You should see something like `53 passed`. If you see errors, check that you activated the virtual environment and ran `pip install -e '.[dev]'`.

## 7. Check which collectors are ready

```bash
python3 -c "
from pipeline.collector.run import validate_collectors
for p, v in validate_collectors().items():
    status = 'READY' if v['configured'] else f'MISSING: {v[\"missing_env\"]}'
    print(f'  {p}: {status}')
'
```

Platforms showing `READY` can be run immediately. Platforms showing `MISSING` need their env vars filled in first.

---

**Next:** Pick a collector from the list below and follow its guide.

- [01 - Google Play](01-google-play.md) (no setup needed)
- [02 - Apple App Store](02-app-store.md) (no setup needed)
- [03 - YouTube](03-youtube.md) (needs API key)
- [04 - X/Twitter](04-x-twitter.md) (needs bearer token)
- [05 - TikTok](05-tiktok.md) (needs research token + video IDs)
- [06 - Instagram](06-instagram.md) (needs graph token + media IDs)
- [07 - Threads](07-threads.md) (needs access token + media IDs)
- [08 - Stockbit](08-stockbit.md) (needs target URLs)
- [09 - Run All](09-run-all.md)
- [10 - Troubleshooting](10-troubleshooting.md)

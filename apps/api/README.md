# API app

FastAPI backend for BNI/BIONS sentiment data.

## Purpose

The API provides a stable interface over collected social/app-review data, sentiment results, keywords, schedules, and exports.

## Entry point

```txt
apps/api/app/main.py
```

FastAPI app metadata:

```txt
title: BNI BIONS Sentiment API
version: 0.1.0
```

## Routes

| Prefix | Module | Purpose |
| --- | --- | --- |
| `/` | `routes/health.py` | Health check. |
| `/comments` | `routes/comments.py` | Collected item/comment access. |
| `/sentiment` | `routes/sentiment.py` | Sentiment classification endpoint. |
| `/exports` | `routes/exports.py` | CSV/XLSX export hooks. |
| `/keywords` | `routes/keywords.py` | Keyword/source config hooks. |
| `/schedules` | `routes/schedules.py` | Schedule config hooks. |

## Configuration

Settings live in `apps/api/app/config.py`.

Current defaults:

```txt
app_timezone=Asia/Jakarta
sentiment_method=model
mongodb_uri=mongodb://localhost:27017
mongodb_database=bni_bions_sentiment
```

Future env loading should preserve these names:

```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=bni_bions_sentiment
SENTIMENT_METHOD=model
APP_TIMEZONE=Asia/Jakarta
```

## Local run

```bash
cd /home/hp/dev/work/bni-bions-sentiment-analysis
. .venv/bin/activate
python3 -m uvicorn apps.api.app.main:app --reload
```

Open:

```txt
http://127.0.0.1:8000/docs
```

## Tests

```bash
. .venv/bin/activate
pytest -q tests/test_api.py
```

## Implementation rules

- Keep response schemas stable once used by the dashboard.
- Do not leak secrets or raw tokens.
- Do not expose raw payloads through default user-facing endpoints.
- Prefer repositories under `apps/api/app/repositories/` for database access.
- Keep route handlers thin: validate input, call pipeline/repository code, return schema.

# apps

Application layer for the BNI/BIONS sentiment system.

This directory contains user-facing services that sit on top of the collector, sentiment, database, and export pipeline.

## Modules

| Path | Purpose |
| --- | --- |
| `api/` | FastAPI backend for health checks, comments, sentiment, exports, keywords, schedules. |
| `dashboard/` | Next.js dashboard scaffold for sentiment charts, comment tables, keyword/schedule management, exports. |

## Data flow

```txt
MongoDB + pipeline outputs
  -> apps/api
  -> apps/dashboard
  -> analyst/user
```

## How to run

Backend:

```bash
cd /home/hp/dev/work/bni-bions-sentiment-analysis
. .venv/bin/activate
python3 -m uvicorn apps.api.app.main:app --reload
```

Dashboard:

```bash
cd apps/dashboard
npm install
npm run dev
```

## Safety notes

- Do not expose raw payloads, secrets, cookies, tokens, or connection strings in API responses.
- Avoid returning usernames in broad public exports unless the use case needs them.
- Keep raw data endpoints internal/admin if added later.

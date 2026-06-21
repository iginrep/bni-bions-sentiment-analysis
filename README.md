# BNI/BIONS Sentiment Analysis

A cheapest-first, safety-first monitoring system for public feedback about BNI Sekuritas and the BIONS app.

The project collects public app reviews and social comments, normalizes them into one canonical data model, classifies sentiment, then exposes results through API, dashboard, and exports.

## What this solves

BNI/BIONS teams need a repeatable way to see:

- what users complain about in the BIONS app.
- whether sentiment is improving or worsening.
- which topics drive negative feedback: login, OTP, trading, deposits, withdrawals, fees, app stability, performance, customer service.
- which data sources are useful enough to justify paid APIs/vendors later.

## Current strategy

Cheapest-first validation.

1. Start with public/free low-risk sources.
2. Keep risky platforms disabled by default.
3. Build a stable collector + sentiment + reporting pipeline.
4. Upgrade to official paid APIs/vendors only after a source proves value.

Approved MVP sources:

| Source | Target | Status | Risk |
| --- | --- | --- | --- |
| Google Play | `id.bions.bnis.android` | enabled | low/medium |
| Apple App Store | app id `6736508566` | enabled | low |
| YouTube | `@BNI1946`, `@bnisekuritas46` | enabled, needs `YOUTUBE_API_KEY` | low |
| Stockbit | BNI/BIONS terms | disabled | high |
| X/Twitter | BNI/BIONS terms | disabled | high |
| TikTok | BNI/BIONS terms | disabled | high |
| Instagram | BNI/BIONS terms | disabled | high |
| Threads | BNI/BIONS terms | disabled | high |

## Architecture

```txt
keywords + schedules
  -> collector adapters
  -> RawSocialItem normalization
  -> dedupe + preprocessing
  -> sentiment classification
  -> MongoDB
  -> FastAPI
  -> dashboard + exports
```

Core modules:

| Path | Purpose |
| --- | --- |
| `apps/api/` | FastAPI service for health, comments, sentiment, exports, keywords, schedules. |
| `apps/dashboard/` | Next.js dashboard scaffold. |
| `pipeline/collector/` | Platform adapters, canonical data model, normalization, dedupe. |
| `pipeline/sentiment/` | Text preprocessing, rule-based sentiment, future model hooks. |
| `pipeline/scheduler/` | Scheduled collector/analyzer jobs. |
| `pipeline/export/` | CSV/XLSX export helpers. |
| `db/` | MongoDB init, indexes, seed keywords, legacy SQL notes. |
| `docs/` | Human-facing strategy, architecture, contracts, research. |
| `.agents/` | AI-agent project context and operating rules. |

## Quick start

```bash
cd /home/hp/dev/work/bni-bions-sentiment-analysis
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
pytest -q
```

Optional collector deps:

```bash
pip install -e '.[collectors]'
```

Run pipeline pieces:

```bash
make collect
make analyze
make export
make api
```

Equivalent direct commands:

```bash
python3 -m pipeline.collector.run
python3 -m pipeline.sentiment.run
python3 -m pipeline.export.csv_export
python3 -m uvicorn apps.api.app.main:app --reload
```

## Configuration

Local secrets belong in `.env`. Do not commit `.env`.

Required when using YouTube collector:

```env
YOUTUBE_API_KEY=...
```

Default runtime settings are currently defined in `apps/api/app/config.py`:

```txt
APP_TIMEZONE=Asia/Jakarta
SENTIMENT_METHOD=rule_based
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=bni_bions_sentiment
```

## Safe operating defaults

Use these until there are 14 clean days of successful runs:

```yaml
global:
  schedule: "1x/day"
  timezone: Asia/Jakarta
  initial_backfill_days: 30
  rolling_backfill_days: 7
  raw_retention_days: 180
  aggregate_retention_days: 365

google_play:
  max_items_per_run: 100
  rate_limit: "1 request / 5-10 sec"

apple_app_store:
  max_items_per_run: 100
  rate_limit: "1 request / 5-10 sec"

youtube:
  max_comments_per_run: 200
  max_videos_per_run: 50
  daily_quota_budget_units: 500
```

Stop collection on auth errors, rate limits, CAPTCHA, login walls, quota budget exhaustion, private/deleted content, or repeated server failures.

## Data model

All collectors should emit `RawSocialItem` from `pipeline/collector/base.py`.

Important fields:

```txt
platform
source_type
source_id
keyword
target_entity
text
author_username
author_display_name
posted_at
collected_at
metrics
raw_payload
content_hash
collection_method
access_risk
collector_version
```

User approved saving public usernames/display names. Still redact secrets, emails, phone numbers, NIK/KTP-like values, account/card-like numbers, and passwords from stored/exported data.

## Documentation map

Start here:

| Document | Use |
| --- | --- |
| `AGENTS.md` | AI coding agent entrypoint. |
| `.agents/README.md` | AI-agent doc map. |
| `docs/architecture.md` | System architecture explanation. |
| `docs/data-contract.md` | Canonical item reference. |
| `docs/collector-strategy.md` | Collector plan and source priorities. |
| `docs/provider-decision-matrix.md` | Source/vendor tradeoffs. |
| `docs/human-approval-checklist.md` | Approved sources and risk gates. |
| `docs/labeling-guideline.md` | Sentiment labeling guide. |

## Development workflow

Before claiming work complete:

```bash
. .venv/bin/activate
pytest -q
node --check db/mongo-init.js
git diff --check
```

Before commit, scan staged diff for accidental secrets:

```bash
git diff --staged | grep -Ei 'password|secret|api[_-]?key|token|cookie|authorization|bearer' || true
```

## Current limitations

- Google Play/App Store/YouTube collectors are the first implementation priority.
- Risky social sources are intentionally disabled.
- Sentiment is currently rule-based and should be improved with labeled Indonesian finance/app-review examples.
- `db/schema.sql` and `db/seed_keywords.sql` are legacy SQL references while the active database target is MongoDB.

## License

Internal project scaffold unless a license is added.

# AGENTS.md

This file is the entry point for AI coding agents working on this repository.

## What this project is

BNI/BIONS sentiment monitoring system for public social/app-review data.

Goal: collect public feedback about BNI Sekuritas and the BIONS app, normalize it into one data contract, classify sentiment, expose it through an API/dashboard/export flow, and keep the collection strategy safe, cheap, and auditable.

Primary targets approved by the user:

```yaml
google_play:
  app_id: id.bions.bnis.android
  url: https://play.google.com/store/apps/details?id=id.bions.bnis.android&hl=id
  enabled: true

apple_app_store:
  app_id: "6736508566"
  url: https://apps.apple.com/id/app/bions/id6736508566
  enabled: true

youtube:
  channels:
    - https://www.youtube.com/@BNI1946
    - https://www.youtube.com/@bnisekuritas46
  enabled: true
  api_key_env: YOUTUBE_API_KEY

username_retention:
  save_public_usernames: true
```

Strategic rule: cheapest-first MVP. Start with public/free low-risk sources. Upgrade to official paid APIs or vendors only after the source proves value.

## Commands first

Run from repo root:

```bash
cd /home/hp/dev/work/bni-bions-sentiment-analysis
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

Verification:

```bash
. .venv/bin/activate
pytest -q
node --check db/mongo-init.js
```

Run pipeline pieces:

```bash
make collect
make analyze
make export
make api
```

Equivalent commands:

```bash
python3 -m pipeline.collector.run
python3 -m pipeline.sentiment.run
python3 -m pipeline.export.csv_export
python3 -m uvicorn apps.api.app.main:app --reload
```

## Required safety boundaries

Never do these without explicit user approval in the current task:

- commit `.env`, API keys, tokens, cookies, passwords, connection strings, screenshots with secrets, raw data dumps, or browser profiles.
- enable Stockbit, X/Twitter, TikTok, Instagram, or Threads collection.
- log into third-party accounts.
- import cookies/session files.
- bypass CAPTCHA, anti-bot, rate limits, login walls, robots controls, deleted/private content restrictions.
- send data to paid vendors or external APIs except approved collectors.
- publish, email, post, or contact third parties.

Stop collection immediately on:

```txt
401/403 auth or permission error
429 rate limit
CAPTCHA
login wall
forced relogin
3 consecutive 5xx
daily quota budget exceeded
duplicate rate >80% after first page
private/deleted/login-only content
```

Secrets live only in `.env` or a proper secret manager. `.env` is ignored by git.

## Safe operating defaults

Use these unless user changes them:

```yaml
global:
  timezone: Asia/Jakarta
  schedule: "1x/day initially"
  initial_backfill_days: 30
  rolling_backfill_days: 7
  raw_retention_days: 180
  aggregate_retention_days: 365
  pii_redaction: true

google_play:
  max_items_per_run: 100
  rate_limit: "1 request / 5-10 sec"
  stop_after_pages: 5

apple_app_store:
  max_items_per_run: 100
  rate_limit: "1 request / 5-10 sec"

youtube:
  max_comments_per_run: 200
  max_videos_per_run: 50
  daily_quota_budget_units: 500
  avoid_routine_search: true
  use_known_channels_first: true

stockbit: { enabled: false }
x: { enabled: false }
tiktok: { enabled: false }
instagram: { enabled: false }
threads: { enabled: false }
```

## Project structure

```txt
apps/api/app/                 FastAPI app, routes, settings, Mongo client
pipeline/collector/           collector contract, adapters, normalizer, dedupe
pipeline/collector/adapters/  per-platform adapters
pipeline/sentiment/           preprocessing, rules, classifier/model hooks
pipeline/scheduler/           APScheduler jobs
pipeline/export/              CSV/XLSX export helpers
db/                           Mongo init/schema notes
docs/                         human docs, strategy, research, contracts
.agents/                      agent-focused context and runbooks
tests/                        pytest tests
```

Core docs:

```txt
.agents/README.md
.agents/project-context.md
.agents/safety-and-compliance.md
.agents/workflows.md
.agents/collector-contract.md
docs/collector-strategy.md
docs/provider-decision-matrix.md
docs/human-approval-checklist.md
docs/data-contract.md
docs/architecture.md
```

## Architecture summary

Data flow:

```txt
keyword/schedule
  -> collector adapter
  -> RawSocialItem normalized item
  -> dedupe/preprocess
  -> sentiment classification
  -> MongoDB
  -> FastAPI/dashboard/export
```

Design rules:

- every source is behind an adapter.
- store raw payload for audit/reprocessing, subject to retention/redaction rules.
- normalize every platform into the canonical `RawSocialItem` shape.
- dedupe by platform/source id first, content hash second.
- API/dashboard must not know whether data came from official API, RSS, package, browser automation, or vendor.
- risky collectors stay disabled by default.

## Canonical item shape

See `docs/data-contract.md` and `.agents/collector-contract.md`.

Required normalized fields:

```python
RawSocialItem(
  platform,
  source_type,
  source_id,
  parent_source_id,
  conversation_id,
  keyword,
  target_entity,
  author_id,
  author_username,
  author_display_name,
  text,
  language,
  source_url,
  posted_at,
  collected_at,
  metrics,
  raw_payload,
  content_hash,
)
```

Add provenance fields when implementing collectors:

```json
{
  "collectionMethod": "official_api | unofficial_api | automation | rss | vendor",
  "accessRisk": "low | medium | high",
  "collectorVersion": "v0.1"
}
```

## Implementation priorities

Current build order:

1. Google Play review collector for `id.bions.bnis.android`.
2. Apple App Store review collector for `6736508566`.
3. YouTube Data API collector for approved channels.
4. Normalize + Mongo insert.
5. Sentiment run.
6. API/dashboard/export.
7. Only then consider risky platforms with explicit approval.

Do not start with Stockbit/X/TikTok/Instagram/Threads.

## Testing expectations

Before claiming done:

```bash
. .venv/bin/activate
pytest -q
node --check db/mongo-init.js
```

If changing a collector:

- add/adjust tests for normalization and dedupe.
- test empty responses, duplicate responses, malformed payloads, rate/stop conditions.
- do not require live network for unit tests.
- mock external APIs/packages.

If changing API routes:

- use FastAPI TestClient tests.
- keep response schemas stable.

## Git rules

- keep commits small and atomic.
- commit message format: `<type>: <short description>`.
- run tests before commit.
- inspect staged diff before commit.
- run a secret scan over staged diff:

```bash
git diff --staged | grep -Ei 'password|secret|api[_-]?key|token|cookie|authorization|bearer' || true
```

Placeholder text in docs is okay. Real secrets are not.

## Agent documentation approach used here

Best-practice research found AGENTS.md should be a README for agents: predictable, project-specific, command-first, boundary-heavy, stack-specific, with real examples. Strong agent docs cover commands, testing, project structure, code style, git workflow, and boundaries. This repo follows that structure, with deeper topic files under `.agents/`.

Sources used for this approach:

- https://agents.md/
- https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/

## When unsure

Prefer safety over data volume.

Prefer public, official, low-rate collection over scraping.

Prefer adding docs/tests before adding risky behavior.

Ask the user before enabling anything that touches login, paid vendors, third-party writes, or high-risk scraping.

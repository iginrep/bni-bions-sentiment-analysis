# Architecture

Media sosial -> collector adapters -> normalized social_items -> preprocessing -> sentiment engine -> database -> api -> dashboard/export.

Backfill flow:

```txt
backfill runner (pipeline/collector/backfill.py)
  -> adapter.collect_backfill() per window
  -> checkpoint store (complete/partial per window)
  -> social_items persistence (Mongo upsert)
  -> recent overlap refresh (7d default)
  -> skip complete old windows
  -> resume partial windows on rerun
```

Core design rule: keep platform payload raw, then normalize to one canonical contract.

Collector rule: cheapest useful source first. Official/paid APIs are promotion targets after the source proves value.

Storage: 14 MongoDB collections accessed via `pipeline/storage/`:
- `social_items` — canonical normalized items (collector writes, API reads)
- `collection_checkpoints` — backfill window status (skip/resume)
- `collection_runs` — per-run audit trail (platform, status, counts, duration)
- `collector_providers` — adapter registry + health tracking
- `keywords` — search keyword registry
- `schedules` — cron schedule definitions (scheduler reads)
- `sentiment_results` — classification output per item
- `sentiment_jobs` — sentiment run metadata (method, status, timing)
- `exports` — CSV/XLSX export log
- `dashboard_views` — saved dashboard filter configs
- `dashboard_actions` — user action audit (view, favorite, comment)
- `system_events` — pipeline event log (info, error, warn)
- `labeled_examples` — manual label annotations for training
- `model_versions` — active model registry (method, version, active flag)

# pipeline

Core data pipeline for BNI/BIONS sentiment monitoring.

## Purpose

The pipeline collects public feedback, converts platform-specific payloads into the canonical `RawSocialItem` model, deduplicates items, classifies sentiment, schedules recurring jobs, and exports results.

## Modules

| Path | Purpose |
| --- | --- |
| `collector/` | Platform adapters, canonical item model, normalization, dedupe, sample collector runner. |
| `sentiment/` | Text preprocessing, rule-based classifier, topic helpers, future IndoBERT hook. |
| `scheduler/` | APScheduler job definitions and runner. |
| `export/` | CSV and Excel export helpers. |

## Run commands

```bash
cd /home/hp/dev/work/bni-bions-sentiment-analysis
. .venv/bin/activate
python3 -m pipeline.collector.run
python3 -m pipeline.sentiment.run
python3 -m pipeline.export.csv_export
python3 -m pipeline.scheduler.run
```

## Design rules

- collectors return normalized items, not platform-specific objects.
- unit tests should not require live network.
- risky collectors remain disabled by default.
- sentiment logic must preserve `positive`, `neutral`, `negative` labels unless taxonomy changes.
- exports must not leak secrets or raw credentials.

## Verification

```bash
. .venv/bin/activate
pytest -q
```

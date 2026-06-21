# export pipeline

Export helpers for BNI/BIONS sentiment outputs.

## Purpose

Create analyst-friendly exports from normalized items and sentiment results.

Current outputs:

| File | Purpose |
| --- | --- |
| `csv_export.py` | CSV export helper and CLI entrypoint. |
| `excel_export.py` | Excel export helper. |

## Run

```bash
cd /home/hp/dev/work/bni-bions-sentiment-analysis
. .venv/bin/activate
python3 -m pipeline.export.csv_export
make export
```

## Output policy

- Write generated files under `data/exports/`.
- Do not commit generated exports.
- Do not include secrets, tokens, cookies, or raw credentials.
- Avoid exporting raw usernames unless the analysis needs them.
- Prefer aggregate exports for shareable reports.

## Useful columns

Recommended export columns:

```txt
platform
source_type
source_id
posted_at
collected_at
target_entity
keyword
sentiment
score/topic fields
text
source_url
metrics
```

# scheduler pipeline

Scheduler for recurring BNI/BIONS collection and sentiment jobs.

## Purpose

Run collectors and downstream processing on a predictable schedule without increasing platform risk.

Current scheduler uses APScheduler and Asia/Jakarta timezone.

## Files

| File | Purpose |
| --- | --- |
| `jobs.py` | Scheduled job functions. |
| `run.py` | Blocking scheduler entrypoint. |

## Run

```bash
cd /home/hp/dev/work/bni-bions-sentiment-analysis
. .venv/bin/activate
python3 -m pipeline.scheduler.run
```

## Safe default cadence

```yaml
timezone: Asia/Jakarta
schedule: "1x/day initially"
initial_backfill_days: 30
rolling_backfill_days: 7
```

Do not schedule high-frequency collection until 14 clean days of stable runs.

## Stop rules

Scheduler jobs should stop a platform run on auth errors, rate limits, CAPTCHA, login walls, quota exhaustion, private/deleted content, or repeated server failures.

Never hide repeated failures. Record/report them.

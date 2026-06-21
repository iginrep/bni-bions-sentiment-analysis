# Troubleshooting

Common errors and how to fix them.

## Setup errors

### `ModuleNotFoundError: No module named 'xyz'`

The dependency is not installed.

```bash
. .venv/bin/activate
pip install -e '.[dev]'
pip install -e '.[collectors]'
```

### `No such file or directory: .env`

You haven't created the config file.

```bash
cp .env.example .env
```

Then edit `.env` with your values.

### `(.venv)` not showing in terminal prompt

Virtual environment not activated.

```bash
. .venv/bin/activate
```

## Collector errors

### `CollectorNotConfigured: XXX missing`

The collector needs env vars that are not set. The error message tells you exactly which ones.

Fix: open `.env` and add the missing values. See each collector's runbook for where to get the keys.

### `CollectorStopped: status 401`

Authentication failed. The API token is invalid or expired.

Fix: regenerate the token in the platform's developer portal and update `.env`.

### `CollectorStopped: status 403`

Forbidden. Usually means:
- Your API tier doesn't include the endpoint you need (e.g., X Free tier can't use search)
- The token doesn't have the right permissions
- The platform is blocking your IP

Fix: check your API tier and token permissions. For IP blocks, wait and retry.

### `CollectorStopped: status 429`

Rate limited. Too many requests.

Fix: wait 5-10 minutes before retrying. Consider adding delays between requests if running repeatedly.

### Empty results

Could mean:
- The platform has no recent data matching your criteria
- The scraper was blocked silently
- Your search queries don't match anything

Fix: try with a broader keyword or check if the platform is accessible from your network.

## Test errors

### `pytest` shows failures after changes

```bash
. .venv/bin/activate
pytest -v   # verbose to see which tests fail
```

Check the error message. Common causes:
- Missing import (add it to the file)
- Changed function signature (update the test)
- Missing env var (some tests need `.env` configured)

### `node --check db/mongo-init.js` fails

JavaScript syntax error in the MongoDB init script. Check for missing commas or brackets.

## Network issues

### `httpx.ConnectError`

Cannot reach the platform. Check:
- Internet connection
- VPN/proxy settings
- Platform status (is it down?)

### `httpx.TimeoutException`

Request took too long. The default timeout is 20 seconds.

Fix: check your internet speed, or the platform may be slow. Try again later.

## Getting more help

1. Run with verbose output: `pytest -v` for test details
2. Check the adapter source code in `pipeline/collector/adapters/`
3. Look at the base model in `pipeline/collector/base.py` for field definitions
4. Read the strategy doc: `docs/data-collector-target-strategy.md`

---

**Back:** [09 - Run All](09-run-all.md) | **Top:** [00 - Prerequisites](00-prerequisites.md)

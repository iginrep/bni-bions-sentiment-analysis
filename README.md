# social-media-data-collector

Monorepo sederhana untuk monitoring sentimen BNI Sekuritas dan aplikasi BIONS.

Database: MongoDB (`bni_bions_sentiment`)

Pipeline:

1. keyword + schedule
2. social collector adapters
3. canonical raw social item normalization
4. dedupe + preprocessing
5. sentiment classification: positive / neutral / negative
6. api + dashboard
7. csv/xlsx export

## Quick start

```bash
cd /home/hp/dev/work/bni-bions-sentiment-analysis
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
make test
make collect
make analyze
make export
make api
```

## Collector strategy

Cheapest-first. Use free/public/unofficial collectors for MVP, keep risky collectors disabled by default, then upgrade to official API/vendor after the source proves value.

Docs:

- `docs/collector-strategy.md`
- `docs/provider-decision-matrix.md`
- `docs/source-limitations.md`

MVP priority:

1. Google Play reviews: `google-play-scraper`
2. Apple App Store reviews: RSS JSON via `httpx`
3. YouTube comments: official Data API v3 free quota
4. News/RSS context: `httpx` + extraction
5. Stockbit: Playwright PoC with dedicated account, disabled by default
6. X/Instagram/TikTok/Threads: only after exact targets or vendor/API budget

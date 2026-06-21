# sentiment pipeline

Sentiment classification layer for normalized BNI/BIONS feedback.

## Purpose

Transform cleaned Indonesian app/social text into sentiment labels and topic signals.

Current classifier: rule-based.

Future path: labeled-data evaluation, then IndoBERT or another Indonesian model if the rule-based approach is not enough.

## Files

| File | Purpose |
| --- | --- |
| `preprocess.py` | Clean and normalize text. |
| `rules.py` | Rule-based positive/neutral/negative classification. |
| `classifier.py` | Public classifier function. |
| `topics.py` | Topic/category helpers. |
| `model_indobert.py` | Placeholder/future model integration. |
| `run.py` | CLI-style sample runner. |

## Labels

Supported labels:

```txt
positive
neutral
negative
```

Keep this taxonomy stable unless the user approves a taxonomy change.

## Run

```bash
cd /home/hp/dev/work/bni-bions-sentiment-analysis
. .venv/bin/activate
python3 -m pipeline.sentiment.run
```

## Development rules

- Keep Indonesian language quirks in mind.
- Preserve the original text; classify on cleaned text.
- Add examples when adding rules.
- Prefer explainable rules until enough labeled data exists.
- Track `method` and `model_version` in classifier output.

## Tests

```bash
. .venv/bin/activate
pytest -q tests/test_sentiment_rules.py
```

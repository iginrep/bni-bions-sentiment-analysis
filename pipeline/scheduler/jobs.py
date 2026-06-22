from __future__ import annotations
from pipeline.sentiment.run import run_sentiment_analysis


def collect_and_analyze() -> list[dict]:
    """Scheduled collection + analysis. Writes to Mongo collections."""
    return run_sentiment_analysis(write=True)

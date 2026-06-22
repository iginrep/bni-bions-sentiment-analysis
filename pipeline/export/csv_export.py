from __future__ import annotations
from pathlib import Path
import pandas as pd
from pipeline.scheduler.jobs import collect_and_analyze


def export_csv(path: str = "data/exports/sample_sentiment.csv") -> str:
    rows = []
    for row in collect_and_analyze():
        item = row["item"]
        sentiment = row["sentiment"]
        rows.append({
            "platform": item["platform"],
            "source_type": item["source_type"],
            "text": item["text"],
            "source_url": item["source_url"],
            "label": sentiment["label"],
            "score": sentiment["score"],
            "confidence": sentiment["confidence"],
            "topics": ",".join(sentiment["topics"]),
        })
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    try:
        from pipeline.storage.exports import log_export

        log_export("csv", str(out), row_count=len(rows))
    except Exception:
        pass
    return str(out)


if __name__ == "__main__":
    print(export_csv())

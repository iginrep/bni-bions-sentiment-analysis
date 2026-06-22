from pathlib import Path
import pandas as pd
from pipeline.export.csv_export import export_csv


def export_excel(path: str = "data/exports/sample_sentiment.xlsx") -> str:
    csv_path = export_csv("data/exports/.tmp_sample.csv")
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(csv_path)
    df.to_excel(out, index=False)
    try:
        from pipeline.storage.exports import log_export

        log_export("xlsx", str(out), row_count=len(df))
    except Exception:
        pass
    return str(out)

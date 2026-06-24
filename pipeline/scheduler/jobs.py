from __future__ import annotations
from typing import Any
from pipeline.collector.run import collect_sample
from sentiment_labeling import run_labeling


def collect_and_analyze(schedule_id: str | None = None) -> dict[str, Any]:
    """Scheduled BIONS data collection and sentiment labeling."""
    if schedule_id:
        from pipeline.storage.schedules import get_schedule
        sched = get_schedule(schedule_id)
        if not sched or not sched.get("isActive"):
            print(f"Schedule '{schedule_id}' is inactive or deleted. Skipping run.")
            return {"status": "skipped"}

    print("[*] Scheduled Run: Memulai penarikan data (extraction)...")
    try:
        collected = collect_sample(write=True)
        print(f"[✓] Penarikan data selesai. Jumlah item ditarik: {len(collected)}")
    except Exception as e:
        print(f"[X] Gagal melakukan penarikan data: {e}")
        collected = []

    print("[*] Scheduled Run: Memulai pelabelan sentimen dengan Gemini...")
    try:
        summary = run_labeling()
        print(f"[✓] Pelabelan sentimen selesai: {summary}")
    except Exception as e:
        print(f"[X] Gagal melakukan pelabelan sentimen: {e}")
        summary = {}

    return {
        "collected_count": len(collected),
        "labeling_summary": summary
    }

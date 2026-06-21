from __future__ import annotations

import os


def detect_missing_env(names: list[str]) -> list[str]:
    return [name for name in names if not os.getenv(name)]


def summarize_collector_env(required_by_platform: dict[str, list[str]]) -> dict[str, dict[str, object]]:
    summary: dict[str, dict[str, object]] = {}
    for platform, names in required_by_platform.items():
        missing = detect_missing_env(names)
        summary[platform] = {
            "required_env": names,
            "missing_env": missing,
            "configured": len(missing) == 0,
        }
    return summary

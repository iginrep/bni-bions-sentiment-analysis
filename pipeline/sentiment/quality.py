from __future__ import annotations
from typing import Any

def build_quality_flags(doc: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    """Analyze document and classification result to produce quality flags."""
    text = doc.get("text") or doc.get("content", {}).get("text") or ""
    
    # Simple heuristic checks
    is_empty = not text.strip()
    is_short = len(text.strip()) < 5
    is_profane = any(word in text.lower() for word in ["anjing", "bangsat", "tolol", "jelek"])
    
    return {
        "isEmpty": is_empty,
        "isShort": is_short,
        "isProfane": is_profane,
        "isSpam": False,
        "confidenceScore": result.get("confidence", 1.0)
    }

def is_excluded_from_analysis(doc: dict[str, Any]) -> bool:
    """Check if the document should be excluded from analysis due to bad quality."""
    text = doc.get("text") or doc.get("content", {}).get("text") or ""
    if not text.strip():
        return True
    if len(text.strip()) < 3:
        return True
    return False

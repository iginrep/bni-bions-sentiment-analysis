from __future__ import annotations

"""
IndoBERT classifier wrapper — delegates to the unified classifier.

Usage:
    from pipeline.sentiment.model_indobert import IndoBertClassifier

    clf = IndoBertClassifier()
    result = clf.classify("aplikasi ini bagus sekali")
"""

from pipeline.sentiment.classifier import classify


class IndoBertClassifier:
    """IndoBERT sentiment classifier for Indonesian text."""

    def __init__(self, model_name: str = "indobenchmark/indobert-base-p1"):
        self.model_name = model_name

    def classify(self, text: str) -> dict:
        """Classify sentiment of a single text."""
        return classify(text, method="indobert")

    def classify_batch(self, texts: list[str]) -> list[dict]:
        """Classify sentiment of multiple texts."""
        return [classify(t, method="indobert") for t in texts]

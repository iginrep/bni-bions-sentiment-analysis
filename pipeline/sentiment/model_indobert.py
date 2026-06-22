from __future__ import annotations

"""
IndoBERT classifier wrapper — delegates to the unified classifier.

Usage:
    from pipeline.sentiment.model_indobert import IndoBertClassifier

    clf = IndoBertClassifier()
    result = clf.predict("Aplikasi ini error terus")
"""

from pipeline.sentiment.classifier import classify, DEFAULT_MODEL


class IndoBertClassifier:
    """Sentiment classifier using IndoBERT (fine-tuned financial model)."""

    def __init__(self, model_name: str | None = None):
        """Initialize with optional custom model name.

        Args:
            model_name: HuggingFace model ID. Defaults to intanm/indonesian_financial_sentiment_analysis.
        """
        if model_name:
            import os
            os.environ["INDOBERT_MODEL_NAME"] = model_name

    def predict(self, text: str) -> dict:
        """Classify sentiment of Indonesian text.

        Returns:
            dict with: label, score, confidence, topics, cleaned_text, method, model_version
        """
        return classify(text, method="indobert")

    @classmethod
    def from_pretrained(cls, model_name: str) -> "IndoBertClassifier":
        """Factory: create classifier from a specific HuggingFace model."""
        return cls(model_name=model_name)

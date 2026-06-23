from __future__ import annotations

"""
Model classifier wrapper — delegates to the unified classifier.

Usage:
    from pipeline.sentiment.model import ModelClassifier

    clf = ModelClassifier()
    result = clf.predict("Aplikasi ini error terus")
"""

from pipeline.sentiment.classifier import classify, DEFAULT_MODEL


class ModelClassifier:
    """Sentiment classifier using model (fine-tuned financial model)."""

    def __init__(self, model_name: str | None = None):
        """Initialize with optional custom model name.

        Args:
            model_name: HuggingFace model ID. Defaults to indobenchmark/indobert-base-p2.
        """
        if model_name:
            import os
            os.environ["MODEL_NAME"] = model_name

    def predict(self, text: str) -> dict:
        """Classify sentiment of Indonesian text.

        Returns:
            dict with: label, score, confidence, topics, cleaned_text, method, model_version
        """
        return classify(text, method="model")

    @classmethod
    def from_pretrained(cls, model_name: str) -> "ModelClassifier":
        """Factory: create classifier from a specific HuggingFace model."""
        return cls(model_name=model_name)

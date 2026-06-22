from __future__ import annotations

"""
Sentiment classifier — supports rule-based and IndoBERT modes.

Usage:
    from pipeline.sentiment.classifier import classify

    # rule-based (default, fast, no GPU needed)
    result = classify("aplikasi ini bagus")

    # IndoBERT (slower, needs torch, higher accuracy)
    result = classify("aplikasi ini bagus", method="indobert")
"""

from pipeline.sentiment.preprocess import clean_text
from pipeline.sentiment.preprocessing import preprocess
from pipeline.sentiment.rules import classify_rule_based

MODEL_VERSION_RULES = "rules-v0.1"
MODEL_VERSION_INDOBERT = "indobert-base-p1"

# Lazy-loaded IndoBERT components
_indobert_tokenizer = None
_indobert_model = None


def _get_indobert():
    """Lazy-load IndoBERT model + tokenizer (heavy, only when needed)."""
    global _indobert_tokenizer, _indobert_model
    if _indobert_tokenizer is None:
        from pipeline.sentiment.tokenizer import IndoBertTokenizer
        _indobert_tokenizer = IndoBertTokenizer()
    if _indobert_model is None:
        from transformers import AutoModelForSequenceClassification
        _indobert_model = AutoModelForSequenceClassification.from_pretrained(
            "indobenchmark/indobert-base-p1",
            num_labels=3,  # positive, negative, neutral
        )
        _indobert_model.eval()
    return _indobert_tokenizer, _indobert_model


def _classify_indobert(text: str) -> dict:
    """Classify using IndoBERT. Returns label, score, confidence, topics."""
    import torch

    tok, model = _get_indobert()

    # Preprocess + tokenize
    cleaned = preprocess(text, mode="indobert")
    inputs = tok.encode(cleaned, return_tensors="pt")

    # Forward pass
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = torch.softmax(logits, dim=-1)

    # Map to labels
    labels = ["negative", "neutral", "positive"]
    pred_idx = probs.argmax(dim=-1).item()
    label = labels[pred_idx]
    confidence = probs[0][pred_idx].item()

    # Score: positive → positive score, negative → negative score
    pos_score = probs[0][2].item()
    neg_score = probs[0][0].item()
    score = pos_score - neg_score  # range [-1, 1]

    # Topic detection (reuse rule-based topic rules)
    from pipeline.sentiment.rules import TOPIC_RULES
    tokens = set(cleaned.split())
    topics = [name for name, words in TOPIC_RULES.items() if tokens & words]

    return {
        "label": label,
        "score": round(score, 4),
        "confidence": round(confidence, 4),
        "topics": topics,
    }


def classify(text: str, method: str = "rule_based") -> dict:
    """Classify sentiment of Indonesian text.

    Args:
        text: raw input text
        method: "rule_based" (fast) or "indobert" (accurate)

    Returns:
        dict with: label, score, confidence, topics, cleaned_text, method, model_version
    """
    if method == "indobert":
        result = _classify_indobert(text)
        result["method"] = "indobert"
        result["model_version"] = MODEL_VERSION_INDOBERT
        result["cleaned_text"] = preprocess(text, mode="indobert")
    else:
        cleaned = clean_text(text)
        result = classify_rule_based(cleaned)
        result["cleaned_text"] = cleaned
        result["method"] = "rule_based"
        result["model_version"] = MODEL_VERSION_RULES

    # Log model version
    try:
        from pipeline.storage.model_versions import ensure_model_version
        ensure_model_version(result["method"], result["model_version"], active=True)
    except Exception:
        pass

    return result

from __future__ import annotations

"""
Sentiment classifier — supports rule-based and IndoBERT modes.

Usage:
    from pipeline.sentiment.classifier import classify

    # rule-based (default, fast, no GPU needed)
    result = classify("aplikasi ini bagus")

    # IndoBERT (slower, needs torch, higher accuracy)
    result = classify("aplikasi ini bagus", method="indobert")

Environment variables:
    INDOBERT_MODEL_NAME: HuggingFace model ID (default: intanm/indonesian_financial_sentiment_analysis)
"""

import os
from pipeline.sentiment.preprocess import clean_text
from pipeline.sentiment.preprocessing import preprocess
from pipeline.sentiment.rules import classify_rule_based

MODEL_VERSION_RULES = "rules-v0.1"

# Default: Indonesian financial sentiment model (fine-tuned, 3-label)
# Alternatives tested:
#   - indobenchmark/indobert-base-p1 → base encoder, NO classification head, random labels
#   - ShinyQ/indobert-sentiment-analysis-indonesian-university-reviews → wrong domain, over-neutral
#   - intanm/indonesian_financial_sentiment_analysis → financial domain, NEGATIVE/NEUTRAL/POSITIVE ✓
DEFAULT_MODEL = "intanm/indonesian_financial_sentiment_analysis"

# Lazy-loaded IndoBERT components
_indobert_tokenizer = None
_indobert_model = None
_indobert_model_name = None
_indobert_labels = None


def _get_indobert():
    """Lazy-load IndoBERT model + tokenizer (heavy, only when needed).

    Uses INDOBERT_MODEL_NAME env var if set, otherwise defaults to
    intanm/indonesian_financial_sentiment_analysis.
    """
    global _indobert_tokenizer, _indobert_model, _indobert_model_name, _indobert_labels

    model_name = os.environ.get("INDOBERT_MODEL_NAME", DEFAULT_MODEL)

    # Re-init if model changed
    if _indobert_model is not None and _indobert_model_name != model_name:
        _indobert_tokenizer = None
        _indobert_model = None

    if _indobert_tokenizer is None:
        from transformers import AutoTokenizer
        _indobert_tokenizer = AutoTokenizer.from_pretrained(model_name)

    if _indobert_model is None:
        from transformers import AutoModelForSequenceClassification
        _indobert_model = AutoModelForSequenceClassification.from_pretrained(model_name)
        _indobert_model.eval()
        _indobert_model_name = model_name
        _indobert_labels = _indobert_model.config.id2label  # {0: 'NEGATIVE', 1: 'NEUTRAL', 2: 'POSITIVE'}

    return _indobert_tokenizer, _indobert_model, _indobert_labels


def _classify_indobert(text: str) -> dict:
    """Classify using IndoBERT. Returns label, score, confidence, topics."""
    import torch

    tok, model, id2label = _get_indobert()
    num_labels = model.config.num_labels

    # Preprocess + tokenize
    cleaned = preprocess(text, mode="indobert")
    inputs = tok(cleaned, return_tensors="pt", truncation=True, padding="max_length", max_length=128)

    # Forward pass
    with torch.no_grad():
        probs = torch.softmax(model(**inputs).logits, dim=-1)[0]

    # Map to labels using model's own id2label
    pred_idx = probs.argmax().item()
    raw_label = id2label[pred_idx]
    label = raw_label.lower()

    confidence = probs[pred_idx].item()

    # Score: pos - neg, range [-1, 1]
    # Find pos/neg indices by label name
    neg_idx = next((i for i, l in id2label.items() if "neg" in l.lower()), 0)
    pos_idx = next((i for i, l in id2label.items() if "pos" in l.lower()), num_labels - 1)
    score = probs[pos_idx].item() - probs[neg_idx].item()

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
        method: "rule_based" (fast) or "indobert" (accurate, needs torch)

    Returns:
        dict with: label, score, confidence, topics, cleaned_text, method, model_version
    """
    if method == "indobert":
        model_name = os.environ.get("INDOBERT_MODEL_NAME", DEFAULT_MODEL)
        result = _classify_indobert(text)
        result["method"] = "indobert"
        result["model_version"] = model_name
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

from __future__ import annotations

"""
Sentiment classifier — supports IndoBERT and OpenRouter generative AI modes.

Usage:
    from pipeline.sentiment.classifier import classify

    # IndoBERT (default, needs torch)
    result = classify("aplikasi ini bagus")

    # OpenRouter generative AI (needs OPENROUTER_API_KEY)
    result = classify("aplikasi ini bagus", method="openrouter")

Environment variables:
    INDOBERT_MODEL_NAME: HuggingFace model ID (default: intanm/indonesian_financial_sentiment_analysis)
    OPENROUTER_API_KEY: API key for OpenRouter generative AI (optional)
    OPENROUTER_MODEL: Model ID for OpenRouter (default: google/gemini-2.0-flash-001)
"""

import os
from pipeline.sentiment.preprocessing import preprocess

# Default: Indonesian financial sentiment model (fine-tuned, 3-label)
DEFAULT_MODEL = "intanm/indonesian_financial_sentiment_analysis"

# OpenRouter defaults
DEFAULT_OPENROUTER_MODEL = "google/gemini-2.0-flash-001"

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
    neg_idx = next((i for i, l in id2label.items() if "neg" in l.lower()), 0)
    pos_idx = next((i for i, l in id2label.items() if "pos" in l.lower()), num_labels - 1)
    score = probs[pos_idx].item() - probs[neg_idx].item()

    # Topic detection (keyword-based, not sentiment)
    from pipeline.sentiment.rules import TOPIC_RULES
    tokens = set(cleaned.split())
    topics = [name for name, words in TOPIC_RULES.items() if tokens & words]

    return {
        "label": label,
        "score": round(score, 4),
        "confidence": round(confidence, 4),
        "topics": topics,
    }


def _classify_openrouter(text: str) -> dict:
    """Classify using OpenRouter generative AI. Returns label, score, confidence, topics."""
    import json
    import urllib.request
    import urllib.error

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set")

    model = os.environ.get("OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL)
    cleaned = preprocess(text, mode="indobert")

    prompt = f"""Classify the sentiment of this Indonesian financial text. Return ONLY a JSON object with these fields:
- "label": one of "positive", "negative", "neutral"
- "score": float from -1.0 (very negative) to 1.0 (very positive), 0.0 for neutral
- "confidence": float from 0.0 to 1.0
- "topics": list of topic strings from: login_otp, order_execution, app_stability, performance_speed, customer_service, fees_commission

Text: {cleaned}

JSON:"""

    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 200,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"OpenRouter API error: {e.code} {e.read().decode()}")

    content = data["choices"][0]["message"]["content"].strip()

    # Parse JSON from response (handle markdown code blocks)
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()

    result = json.loads(content)

    # Validate fields
    label = result.get("label", "neutral")
    if label not in ("positive", "negative", "neutral"):
        label = "neutral"

    return {
        "label": label,
        "score": round(float(result.get("score", 0.0)), 4),
        "confidence": round(float(result.get("confidence", 0.5)), 4),
        "topics": result.get("topics", []),
        "cleaned_text": cleaned,
        "method": "openrouter",
        "model_version": model,
    }


def classify(text: str, method: str = "indobert") -> dict:
    """Classify sentiment of Indonesian text.

    Args:
        text: raw input text
        method: "indobert" (default, needs torch) or "openrouter" (needs OPENROUTER_API_KEY)

    Returns:
        dict with: label, score, confidence, topics, cleaned_text, method, model_version
    """
    if method == "openrouter":
        result = _classify_openrouter(text)
    else:
        model_name = os.environ.get("INDOBERT_MODEL_NAME", DEFAULT_MODEL)
        result = _classify_indobert(text)
        result["method"] = "indobert"
        result["model_version"] = model_name
        result["cleaned_text"] = preprocess(text, mode="indobert")

    # Log model version
    try:
        from pipeline.storage.model_versions import ensure_model_version
        ensure_model_version(result["method"], result["model_version"], active=True)
    except Exception:
        pass

    return result

from __future__ import annotations

"""
Sentiment classifier — supports model and OpenRouter generative AI modes.

Usage:
    from pipeline.sentiment.classifier import classify

    # Model (default, needs torch)
    result = classify("aplikasi ini bagus")

    # OpenRouter generative AI (needs OPENROUTER_API_KEY)
    result = classify("aplikasi ini bagus", method="openrouter")

Environment variables:
    MODEL_NAME: HuggingFace model ID (default: indobenchmark/indobert-base-p2)
    OPENROUTER_API_KEY: API key for OpenRouter generative AI (optional)
    OPENROUTER_MODEL: Model ID for OpenRouter (default: openrouter/free)
"""

import os
from typing import Any
from pipeline.sentiment.preprocessing import preprocess
from pipeline.sentiment.quality import build_quality_flags
from pipeline.sentiment.rules import TOPIC_RULES

# Default model checkpoint requested for local NLP sentiment mode.
DEFAULT_MODEL = "indobenchmark/indobert-base-p2"
DEFAULT_ID2LABEL = {0: "negative", 1: "neutral", 2: "positive"}
DEFAULT_LABEL2ID = {label: idx for idx, label in DEFAULT_ID2LABEL.items()}

# OpenRouter defaults
DEFAULT_OPENROUTER_MODEL = "openrouter/free"
OPENROUTER_BATCH_SIZE = 5
OPENROUTER_BATCH_DELAY_SECONDS = 2.0
VALID_LABELS = {"positive", "negative", "neutral"}

# Lazy-loaded model components
_model_tokenizer = None
_model = None
_model_name = None
_model_labels = None


def _get_model():
    """Lazy-load local model + tokenizer (heavy, only when needed).

    Uses MODEL_NAME env var if set, otherwise defaults to
    indobenchmark/indobert-base-p2.
    """
    global _model_tokenizer, _model, _model_name, _model_labels

    model_name = os.environ.get("MODEL_NAME", DEFAULT_MODEL)

    # Re-init if model changed
    if _model is not None and _model_name != model_name:
        _model_tokenizer = None
        _model = None

    if _model_tokenizer is None:
        from transformers import AutoTokenizer
        _model_tokenizer = AutoTokenizer.from_pretrained(model_name)

    if _model is None:
        from transformers import AutoModelForSequenceClassification
        _model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            num_labels=3,
            id2label=DEFAULT_ID2LABEL,
            label2id=DEFAULT_LABEL2ID,
            ignore_mismatched_sizes=True,
        )
        _model.eval()
        _model_name = model_name
        _model_labels = _model.config.id2label

    return _model_tokenizer, _model, _model_labels


def _classify_model(text: str) -> dict:
    """Classify using model. Returns label, score, confidence, topics."""
    import torch

    tok, model, id2label = _get_model()
    num_labels = model.config.num_labels

    # Preprocess + tokenize
    cleaned = preprocess(text, mode="model")
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
    from pipeline.sentiment.topics import detect_topics
    topics = detect_topics(cleaned)

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
    cleaned = preprocess(text, mode="model")

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
        "topics": _valid_topics(result.get("topics", [])),
        "cleaned_text": cleaned,
        "method": "openrouter",
        "model_version": model,
    }


def _valid_topics(topics: Any) -> list[str]:
    if not isinstance(topics, list):
        return []
    allowed = set(TOPIC_RULES)
    return [topic for topic in topics if topic in allowed]


def _score_value(value: Any) -> float:
    return max(-1.0, min(1.0, float(value)))


def _confidence_value(value: Any) -> float:
    return max(0.0, min(1.0, float(value)))


def _json_content(content: str) -> str:
    content = content.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()
    start = content.find("{")
    end = content.rfind("}")
    if start >= 0 and end >= start:
        return content[start:end + 1]
    return content


def _batch_prompt(docs: list[dict]) -> str:
    topics = "\n".join(f"- {name}: {', '.join(sorted(rules)[:12])}" for name, rules in TOPIC_RULES.items())
    rows = []
    for idx, doc in enumerate(docs):
        doc_id = str(doc.get("_id") or doc.get("id") or idx)
        text = preprocess(_doc_text(doc), mode="model")
        rows.append({"id": doc_id, "text": text[:700], "rating": (doc.get("engagement") or {}).get("rating")})
    import json
    return f"""Classify Indonesian BIONS/BNI Sekuritas feedback in batch. Return ONLY valid JSON with key \"items\".
Each item must include:
- id: same id from input
- label: one of positive, neutral, negative
- score: float -1.0 to 1.0
- confidence: float 0.0 to 1.0
- topics: zero or more exact topic ids from allowed list

Rating is context only. Do not convert 1-star into negative unless text is negative. 1-star with non-negative text may be misclick.

Allowed topics:
{topics}

Input items:
{json.dumps(rows, ensure_ascii=False)}

JSON:"""


def _classify_openrouter_batch_once(docs: list[dict]) -> list[dict]:
    import json
    import urllib.error
    import urllib.request

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set")
    model = os.environ.get("OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL)
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": _batch_prompt(docs)}],
        "temperature": 0.0,
        "max_tokens": min(3500, 180 + 140 * len(docs)),
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"OpenRouter API error: {e.code} {e.read().decode()}")
    content = data["choices"][0]["message"].get("content")
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("OpenRouter returned empty content")
    parsed = json.loads(_json_content(content))
    by_id = {str(item.get("id")): item for item in parsed.get("items", [])}
    out = []
    for idx, doc in enumerate(docs):
        doc_id = str(doc.get("_id") or doc.get("id") or idx)
        item = by_id.get(doc_id, {})
        label = item.get("label", "neutral")
        if label not in VALID_LABELS:
            label = "neutral"
        out.append({
            "label": label,
            "score": round(_score_value(item.get("score", 0.0)), 4),
            "confidence": round(_confidence_value(item.get("confidence", 0.5)), 4),
            "topics": _valid_topics(item.get("topics", [])),
            "cleaned_text": preprocess(_doc_text(doc), mode="model"),
            "method": "openrouter",
            "model_version": model,
        })
    return out


def _openrouter_batch_size(batch_size: int | None = None) -> int:
    requested = batch_size or int(os.environ.get("OPENROUTER_BATCH_SIZE", OPENROUTER_BATCH_SIZE))
    return max(1, min(requested, OPENROUTER_BATCH_SIZE))


def _openrouter_batch_delay() -> float:
    return max(0.0, float(os.environ.get("OPENROUTER_BATCH_DELAY_SECONDS", OPENROUTER_BATCH_DELAY_SECONDS)))


def classify_documents_batch(docs: list[dict], method: str = "auto", batch_size: int | None = None) -> list[dict]:
    import time

    size = _openrouter_batch_size(batch_size)
    delay = _openrouter_batch_delay()
    results: list[dict] = []
    for start in range(0, len(docs), size):
        chunk = docs[start:start + size]
        if method in ("auto", "openrouter") and os.environ.get("OPENROUTER_API_KEY"):
            try:
                chunk_results = _classify_openrouter_batch_once(chunk)
            except Exception:
                chunk_results = [classify_document(doc, method="model") for doc in chunk]
        else:
            chunk_results = [classify_document(doc, method="model") for doc in chunk]
        for doc, result in zip(chunk, chunk_results):
            result["quality"] = build_quality_flags(doc, result)
            results.append(result)
        if delay and start + size < len(docs):
            time.sleep(delay)
    return results


def classify(text: str, method: str = "model") -> dict:
    """Classify sentiment of Indonesian text.

    Args:
        text: raw input text
        method: "model" (default, needs torch) or "openrouter" (needs OPENROUTER_API_KEY)

    Returns:
        dict with: label, score, confidence, topics, cleaned_text, method, model_version
    """
    if method == "openrouter":
        result = _classify_openrouter(text)
    else:
        model_name = os.environ.get("MODEL_NAME", DEFAULT_MODEL)
        result = _classify_model(text)
        result["method"] = "model"
        result["model_version"] = model_name
        result["cleaned_text"] = preprocess(text, mode="model")

    # Log model version
    try:
        from pipeline.storage.model_versions import ensure_model_version
        ensure_model_version(result["method"], result["model_version"], active=True)
    except Exception:
        pass

    return result


def _doc_text(doc: dict) -> str:
    return (doc.get("content") or {}).get("text") or doc.get("text") or ""


def classify_document(doc: dict, method: str = "openrouter") -> dict:
    """Classify a social item. OpenRouter-first when configured; local model fallback."""
    text = _doc_text(doc)
    if method == "auto":
        method = "openrouter" if os.environ.get("OPENROUTER_API_KEY") else "model"
    if method == "openrouter":
        try:
            result = classify(text, method="openrouter")
        except Exception:
            result = classify(text, method="model")
    else:
        result = classify(text, method=method)
    result["quality"] = build_quality_flags(doc, result)
    return result

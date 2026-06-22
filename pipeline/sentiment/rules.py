from __future__ import annotations

"""
Topic detection rules — keyword-based topic classification (not sentiment).

Used by classifier.py to detect which topics a text relates to.
Sentiment is handled by NLP models (IndoBERT / OpenRouter), NOT word matching.
"""

TOPIC_RULES = {
    "login_otp": {"login", "otp", "password", "masuk"},
    "order_execution": {"order", "beli", "jual", "nyangkut", "reject", "tertahan", "ditolak"},
    "app_stability": {"error", "crash", "bug", "galat", "macet", "kesalahan"},
    "performance_speed": {"lemot", "lambat", "cepat", "lancar"},
    "customer_service": {"cs", "customer", "service", "respon", "responsif", "layanan", "pelanggan"},
    "fees_commission": {"fee", "komisi", "biaya"},
}

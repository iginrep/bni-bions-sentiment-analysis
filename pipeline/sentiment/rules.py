from __future__ import annotations

"""
Topic detection rules — keyword-based topic classification (not sentiment).

Used by classifier.py to detect which topics a text relates to.
Sentiment is handled by NLP models (IndoBERT / OpenRouter), NOT word matching.

Topics cover the full BIONS user journey:
  app → register → learn → trade → complain → compare
"""

TOPIC_RULES: dict[str, set[str]] = {
    # 1. App performance, bugs, crashes, UI/UX, updates
    "app_experience": {
        "app", "aplikasi", "bions", "bions", "tampilan", "ui", "ux",
        "update", "versi", "fitur", "menu", "tombol", "layar",
        "loading", "memuat", "buffering",
    },
    # 2. Order placement, fill speed, errors during trade
    "trading_execution": {
        "order", "beli", "jual", "sell", "buy", "nyangkut",
        "reject", "tertahan", "ditolak", "gagal", "pending",
        "eksekusi", "match", "partial",
    },
    # 3. Registration, verification, KYC
    "account_kyc": {
        "daftar", "register", "registrasi", "verifikasi", "kyc",
        "dokumen", "ktp", "selfie", "rekening", "aktivasi",
        "buka rekening", "open account",
    },
    # 4. Commissions, platform fees, admin fees
    "fees_pricing": {
        "fee", "komisi", "biaya", "admin", "potongan",
        "gratis", "murah", "mahal", "worth",
    },
    # 5. Real-time quotes, charts, watchlist, news
    "market_data_features": {
        "data", "chart", "grafik", "watchlist", "saham",
        "kuotasi", "realtime", "real-time", "indeks", "ihsg",
        "news", "berita", "riset", "analisis", "fundamental", "teknikal",
    },
    # 6. Support responsiveness, complaint handling
    "customer_service": {
        "cs", "customer", "service", "respon", "responsif",
        "layanan", "pelanggan", "bantuan", "hubungi",
        "complain", "keluhan", "helpdesk", "support",
    },
    # 7. Platform stability, data security, regulatory
    "trust_reliability": {
        "aman", "terpercaya", "terdaftar", "ojk",
        "dana", "deposit", "withdrawal", "penarikan",
        "keamanan", "security", "enkripsi",
    },
    # 8. Comparisons with other brokers
    "competition_comparison": {
        "mirae", "mandiri", "bca", "stockbit", "astra",
        "phillip", "trimegah", "bilateral", "sekuritas",
        "lebih bagus", "pindah", "switch", "ganti broker",
    },
}

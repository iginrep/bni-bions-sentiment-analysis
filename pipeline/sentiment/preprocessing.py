from __future__ import annotations

"""
Comprehensive Indonesian text preprocessing for BNI/BIONS sentiment analysis.

Two modes:
  - rule_based: full pipeline (clean → normalize → stopwords → stemming)
  - indobert: lighter pipeline (clean → normalize → tokenizer handles the rest)

IndoBERT was pre-trained on formal Indonesian. Slang normalization is critical.
Stopword removal and stemming HURT IndoBERT performance — skip them for that mode.
"""

import re
import unicodedata
from typing import Literal

# ---------------------------------------------------------------------------
# 1. SLANG / INFORMAL → FORMAL MAPPING
# ---------------------------------------------------------------------------

SLANG_MAP: dict[str, str] = {
    # negation
    "gk": "tidak", "ga": "tidak", "gak": "tidak", "nggak": "tidak",
    "g": "tidak", "tdk": "tidak", "enggak": "tidak", "kagak": "tidak",
    "blm": "belum", "blum": "belum", "belom": "belum",
    "jgn": "jangan", "jngn": "jangan",
    # common informal
    "yg": "yang", "utk": "untuk", "utuk": "untuk", "buat": "untuk",
    "bgt": "banget", "bngt": "banget", "bngtt": "banget",
    "bener": "benar", "bnr": "benar",
    "aja": "saja", "aj": "saja",
    "dong": "saja", "sih": "saja",
    "klo": "kalau", "kalo": "kalau", "kl": "kalau",
    "tp": "tapi", "tpi": "tapi",
    "sm": "sama", "sama": "sama",
    "gw": "saya", "gue": "saya", "ane": "saya", "gw": "saya",
    "lu": "kamu", "lo": "kamu", "loe": "kamu",
    "dr": "dari", "dri": "dari",
    "pd": "pada",
    "bs": "bisa", "bisa": "bisa",
    "udh": "sudah", "udah": "sudah", "sdh": "sudah",
    "lg": "lagi", "lgi": "lagi", "lagi": "lagi",
    "dgn": "dengan", "dg": "dengan",
    "krn": "karena", "karna": "karena",
    "klo": "kalau", "kalo": "kalau",
    # app-specific (BNI/BIONS)
    "login": "masuk", "log in": "masuk",
    "loading": "memuat", "ld": "memuat",
    "error": "galat", "eror": "galat",
    "crash": "macet", "force close": "macet",
    "bug": "kesalahan",
    "lemot": "lambat", "lambat": "lambat",
    "nyangkut": "tertahan", "stuck": "tertahan",
    "reject": "ditolak",
    "cs": "layanan pelanggan", "customer service": "layanan pelanggan",
    # intensifiers / fillers
    "banget": "sekali", "bgt": "sekali",
    "sering": "sering",
    "parah": "buruk", "parahh": "buruk",
    "jelek": "buruk", "jlek": "buruk",
    "bagus": "bagus", "bgus": "bagus",
    "mantap": "bagus", "mantul": "bagus",
    "ok": "bagus", "oke": "bagus", "okk": "bagus",
    "puas": "puas",
    "ribet": "rumit", "ribettt": "rumit",
    "susah": "sulit", "susaah": "sulit",
    "gagal": "gagal",
    "lancar": "lancar",
    "cepat": "cepat", "cpt": "cepat",
    "mudah": "mudah",
    "responsif": "responsif", "respon": "responsif",
}

# Words to keep even if in stopword list (sentiment-bearing)
SENTIMENT_KEEPERS = {
    "tidak", "bukan", "belum", "jangan", "kurang",
    "bagus", "buruk", "jelek", "parah", "mantap", "puas",
    "cepat", "lambat", "lemot", "lancar", "susah", "mudah",
    "gagal", "error", "crash", "bug",
    "suka", "senang", "kesal", "kecewa",
    "sering", "selalu", "kadang",
    "sekali", "sangat", "amat", "paling",
}

# Repeated character normalization map
REPEAT_MAP = {
    "k": 2, "s": 2, "t": 2, "p": 2, "l": 2, "b": 2, "g": 2,
}

# ---------------------------------------------------------------------------
# 2. CLEANING
# ---------------------------------------------------------------------------

_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_HTML_RE = re.compile(r"<[^>]+>")
_EMOJI_RE = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "\U0001f926-\U0001f937"
    "\U00010000-\U0010ffff"
    "]+",
    flags=re.UNICODE,
)
_MENTION_RE = re.compile(r"@\w+")
_HASH_RE = re.compile(r"#(\w+)")
_MULTI_SPACE_RE = re.compile(r"\s+")
_NON_ALPHA_RE = re.compile(r"[^a-z0-9\s]")  # after lowercasing
_NUMBER_RE = re.compile(r"\b\d+\b")


def remove_urls(text: str) -> str:
    return _URL_RE.sub(" ", text)


def remove_html(text: str) -> str:
    return _HTML_RE.sub(" ", text)


def remove_emojis(text: str) -> str:
    return _EMOJI_RE.sub(" ", text)


def remove_mentions(text: str) -> str:
    return _MENTION_RE.sub(" ", text)


def extract_hashtags(text: str) -> list[str]:
    """Extract hashtags before stripping the # symbol."""
    return _HASH_RE.findall(text)


def remove_hashtag_symbol(text: str) -> str:
    """Keep the word, drop the #."""
    return _HASH_RE.sub(r"\1", text)


def normalize_repeated_chars(text: str) -> str:
    """Reduce character repeats: 'bagusss' → 'bagus', 'loadingg' → 'loading'.

    Strategy: collapse any run of 3+ identical chars to 2.
    """
    return re.sub(r"(.)\1{2,}", r"\1\1", text)


def remove_numbers(text: str) -> str:
    return _NUMBER_RE.sub(" ", text)


def remove_special_chars(text: str) -> str:
    """Keep only lowercase letters, digits, and whitespace."""
    return _NON_ALPHA_RE.sub(" ", text)


def normalize_whitespace(text: str) -> str:
    return _MULTI_SPACE_RE.sub(" ", text).strip()


def remove_accents(text: str) -> str:
    """NFD decomposition → strip combining marks. 'é' → 'e'."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


# ---------------------------------------------------------------------------
# 3. NORMALIZATION (Indonesian-specific)
# ---------------------------------------------------------------------------

def normalize_slang(text: str) -> str:
    """Map informal/slang words to formal Indonesian."""
    words = text.split()
    return " ".join(SLANG_MAP.get(w, w) for w in words)


def normalize_unicode(text: str) -> str:
    """NFC normalize to standard form."""
    return unicodedata.normalize("NFC", text)


# ---------------------------------------------------------------------------
# 4. STOPWORD REMOVAL
# ---------------------------------------------------------------------------

# Curated Indonesian stopword list (Sastrawi base + sentiment-domain additions)
# fmt: off
INDONESIAN_STOPWORDS: set[str] = {
    # Sastrawi default set
    "ada", "adalah", "adanya", "adapun", "agak", "agaknya", "agar",
    "akan", "akankah", "akhir", "akhiri", "akhirnya", "aku", "akulah",
    "amat", "amatlah", "anda", "andalah", "antar", "antara",
    "antaranya", "apa", "apaan", "apabila", "apakah", "apalagi",
    "apatah", "atau", "ataukah", "atauserta", "atau", "aya",
    "bagaimana", "bagaimanakah", "bagaimanapun", "bagi", "bagian",
    "bahawa", "bahwasannya", "bahwasanya", "baik", "baiklah",
    "bakal", "bakalan", "balik", "banyak", "banyaknya",
    "baru", "barulah", "bawah", "begini", "beginian", "beginikah",
    "beginilah", "begitu", "begitukah", "begitulah", "begitupun",
    "bekerja", "belakangan", "belum", "belumlah", "benar",
    "benarkah", "benarlah", "berada", "berarti", "berawal",
    "berbagai", "berdatangan", "beri", "berikan", "berikut",
    "berikutnya", "berkali-kali", "berkata", "berkehendak",
    "berkenaan", "berlalu", "berlangsung", "berlebihan", "bermacam",
    "bermacam-macam", "bermaksud", "bermula", "bersama", "bersama-sama",
    "bersiap", "bersiap-siap", "bertanya", "berturut", "berturut-turut",
    "berupa", "berbagai", "besar", "besarnya", "beta",
    "bilamana", "bila", "bilakah", "bisa", "bisakah",
    "boleh", "bolehkah", "bolehlah", "buat", "bukan",
    "bukankah", "bukanlah", "bukannya", "bulan", "bung",
    # common function words
    "dahulu", "dalam", "dan", "dapat", "dari", "daripd",
    "datang", "dekat", "demikian", "demikianlah", "dan", "dengan",
    "di", "dia", "diakhir", "diakhirinya", "dialah", "diantara",
    "diantaranya", "diberi", "diberikan", "diberikannya",
    "didapat", "digunakan", "digunakan", "dijadikan", "dikatakan",
    "dikarenakan", "dilakukan", "dilalui", "dilihat",
    "dimaksud", "dimaksudkan", "dimiliki", "dimiliki",
    "diperlukan", "dipergunakan", "diplih", "ditanya",
    "ditanyai", "ditempuh", "ditinggalkan", "ditunjuk",
    "ditunjukkan", "ditunjuki", "diturunkan", "diyakini",
    "dulu", "dulu", "eh", "enak", "enggak",
    "entah", "entahlah",
    "hal", "hampir", "hanya", "hanyalah", "harus",
    "haruslah", "harusnya", "helo", "hingga", "hingganya",
    "hp", "hu", "ia", "ialah", "ibarat", "ibaratkan",
    "ibaratnya", "ikut", "ilustrasi", "ini", "inikah",
    "inilah", "itu", "itukah", "itulah",
    "jangan", "jangankan", "janganlah", "jika", "jikalau",
    "juga", "jugakah", "jugalah", "jujur", "justru",
    "kami", "kamilah", "kamu", "kamulah", "kan",
    "kapan", "kapankah", "kapanpun", "karena", "karenanya",
    "kasih", "kata", "katakan", "katakanlah", "ke", "kedua",
    "keduanya", "kelak", "kelihatan", "kelihatannya", "kelima",
    "keluar", "kembali", "kemudian", "kemudianlah", "kena",
    "kenapa", "kepada", "kepadanya", "kerap", "kerap kali",
    "keseluruhan", "keseluruhannya", "ketika", "khawatir",
    "kini", "kinilah", "kira", "kira-kira", "kiranya",
    "kisah", "kl", "km", "knapa", "ko", "kok",
    "kurang", "kurangnya",
    "lagi", "lagian", "lah", "lain", "lainnya", "lalu",
    "lanjut", "lanjutnya", "lebih", "lebih-lebih", "lewat",
    "lg", "lgsg", "lihat", "lho", "loh",
    "lo", "lu",
    "maka", "makanya", "makin", "malah", "malahan",
    "mampu", "mampukah", "mana", "manakala", "manalagi",
    "manis", "masa", "masalah", "masalahnya", "masing",
    "masing-masing", "mau", "maukah", "melainkan",
    "melakukan", "melalui", "melihat", "menjadi",
    "menjadi", "mendatang", "mengapa", "mengenai",
    "mengerjakan", "mengetahui", "menggunakan", "menghancurkan",
    "mengingat", "mengingatkan", "menginginkan", "mengucapkan",
    "mengundang", "menjadi", "menjelang", "menunjuk",
    "menunjukkan", "menyatakan", "menyediakan", "menyukai",
    "merasa", "mereka", "mereka", "merupakan",
    "meski", "meskipun", "meyakini", "meyakinkan",
    "minta", "mirip", "misal", "misalkan", "misalnya",
    "mohon", "mohon", "mu", "mulai", "mulailah",
    "mulanya", "mungkin", "mungkinkah", "musim",
    "masing", "nanti", "nantinya", "nah", "naik",
    "nantinya", "new", "nggak", "nggak", "nobody",
    "nomor", "nomor", "ny", "nyaris",
    "oleh", "olehnya", "pada", "padahal", "padanya",
    "pak", "paling", "panjang", "pantas",
    "para", "para", "parameter", "paska", "pasca",
    "pasti", "pastilah", "peka", "penuh", "per",
    "perlu", "perlukah", "perlu", "pernah", "pernah",
    "persoalan", "pertama", "pertama-tama", "pertama",
    "pertanyaan", "pertanyakan", "pihak", "pihaknya",
    "pula", "pun", "punya",
    "ragu", "rasa", "rasanya", "resmi",
    "ria", "risau", "rupa", "rupanya",
    "saat", "saatnya", "saja", "sajalah", "saling",
    "sama", "sama-sama", "sambil", "sampai",
    "sampai-sampai", "sampaikan", "sana", "sangat",
    "sangatlah", "saya", "sayalah", "sebab",
    "sebabnya", "sebagai", "sebagaimana", "sebagainya",
    "sebaik", "sebaik-baiknya", "sebaiknya", "sebaliknya",
    "sebanyak", "sebegini", "sebegitu", "sebelum",
    "sebelumnya", "sebenarnya", "seberapa", "sebesar",
    "sebetulnya", "sebidang", "seblum", "sedang",
    "sedangkan", "sedemikian", "sedikit", "sedikitnya",
    "segala", "segalanya", "segera", "segeralah",
    "segmen", "seharusnya", "sehingga", "seingat",
    "sejauh", "sejenak", "sejumlah", "sekadar",
    "sekadarnya", "sekali", "sekalian", "sekaligus",
    "sekalipun", "sekian", "sekian-kalinya", "sekitar",
    "sekitarnya", "sekurang-kurangnya", "sekurangnya",
    "sela", "selagi", "selain", "selainnya", "selalu",
    "selama", "selama-lamanya", "selanjutnya", "seluruh",
    "seluruhnya", "semacam", "semakin", "semampai",
    "semau", "sementara", "semestinya", "semouga",
    "semua", "semuanya", "semula", "sendiri",
    "sendirian", "sendirinya", "seorang", "seoraang",
    "sepanjang", "sepantun", "seperti", "sepertinya",
    "sepihak", "seram", "serang", "serangkaian",
    "serius", "serta", "serupa", "sesaat",
    "sesama", "sesampai", "sesegera", "sesekali",
    "seseorang", "sesuatu", "sesuatunya", "sesudah",
    "sesudahnya", "setelah", "setempat", "setengah",
    "seterusnya", "setiap", "setibanya", "setidak-tidaknya",
    "setidaknya", "setinggi", "seusai", "sewaktu",
    "siap", "siapa", "siapakah", "siapapun",
    "sini", "sinilah", "soal", "soalnya", "solusi",
    "suatu", "sudah", "sudahkah", "sudahlah",
    "supaya", "sy", "sye", "ta", "tadi",
    "tadinya", "tahu", "tahun", "tak",
    "talam", "tama", "tamat", "tanda", "tandas",
    "tangan", "tangannya", "tapi", "tapi", "tatkala",
    "tegas", "tegaskan", "telah", "tempoh", "tentang",
    "tentu", "tentulah", "tentunya", "tepat",
    "tepatnya", "terasa", "terbagi", "terdahulu",
    "terdapat", "terdiri", "terhadap", "terhadapnya",
    "terjadi", "terjadilah", "terjadinya", "terkira",
    "terlalu", "terlebih", "terlihat", "termasuk",
    "ternyata", "tersampaikan", "tersebut", "tersebutlah",
    "tertentu", "tertuju", "terus", "terutama",
    "tertentu", "tetapi", "tiap", "tiba",
    "tiba-tiba", "timbul", "tinggal", "tinggal",
    "toh", "turut", "turut",
    "tutur", "tuturnya",
    "ucap", "ucapnya", "ufti", "uh",
    "untuk", "untuknya", "usah", "usai",
    "waduh", "wah", "wahai", "waktu", "waktunya",
    "walau", "walaupun", "walhasil", "wang", "wanita",
    "wow",
    "ya", "yaitu", "yakin", "yakni", "yang",
    "yong",
}
# fmt: on

# Remove sentiment-bearing words from stopwords
INDONESIAN_STOPWORDS -= SENTIMENT_KEEPERS


def remove_stopwords(text: str, extra_keep: set[str] | None = None) -> str:
    """Remove Indonesian stopwords, keeping sentiment-bearing words."""
    keep = SENTIMENT_KEEPERS | (extra_keep or set())
    words = text.split()
    return " ".join(w for w in words if w in keep or w not in INDONESIAN_STOPWORDS)


# ---------------------------------------------------------------------------
# 5. STEMMING (Sastrawi)
# ---------------------------------------------------------------------------

_stemmer = None


def _get_stemmer():
    global _stemmer
    if _stemmer is None:
        from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
        _stemmer = StemmerFactory().create_stemmer()
    return _stemmer


def stem_indonesian(text: str) -> str:
    """Stem Indonesian text using Sastrawi. Cached after first call."""
    return _get_stemmer().stem(text)


# ---------------------------------------------------------------------------
# 6. FULL PIPELINES
# ---------------------------------------------------------------------------

PipelineMode = Literal["rule_based", "indobert"]


def preprocess(
    text: str,
    mode: PipelineMode = "rule_based",
    *,
    remove_nums: bool = False,
    do_stemming: bool = True,
    do_stopwords: bool = True,
    extra_keep_words: set[str] | None = None,
) -> str:
    """Full preprocessing pipeline.

    mode="rule_based":  clean → normalize → stopwords → stemming
    mode="indobert":    clean → normalize only (tokenizer handles the rest)

    Args:
        text: raw input text
        mode: "rule_based" for classical NLP, "indobert" for transformer input
        remove_nums: whether to strip numbers
        do_stemming: whether to apply Sastrawi stemmer (rule_based only)
        do_stopwords: whether to remove stopwords (rule_based only)
        extra_keep_words: additional words to preserve from stopword removal
    """
    if not text or not text.strip():
        return ""

    # --- Stage 1: Cleaning (always) ---
    text = text.lower()
    text = remove_urls(text)
    text = remove_html(text)
    text = remove_emojis(text)
    text = remove_mentions(text)
    text = remove_hashtag_symbol(text)
    text = normalize_repeated_chars(text)
    text = normalize_unicode(text)
    text = remove_accents(text)
    text = remove_special_chars(text)
    if remove_nums:
        text = remove_numbers(text)
    text = normalize_whitespace(text)

    if not text:
        return ""

    # --- Stage 2: Slang normalization (always) ---
    text = normalize_slang(text)

    # --- Stage 3: Mode-specific ---
    if mode == "indobert":
        # IndoBERT tokenizer handles tokenization, stopwords, subwords.
        # Only cleaning + slang normalization is needed.
        return normalize_whitespace(text)

    # rule_based mode
    if do_stopwords:
        text = remove_stopwords(text, extra_keep=extra_keep_words)
    if do_stemming:
        text = stem_indonesian(text)
    return normalize_whitespace(text)


# ---------------------------------------------------------------------------
# 7. BATCH PREPROCESSING
# ---------------------------------------------------------------------------


def preprocess_batch(
    texts: list[str],
    mode: PipelineMode = "rule_based",
    **kwargs,
) -> list[str]:
    """Preprocess a list of texts. Applies stemmer lazily (once)."""
    return [preprocess(t, mode=mode, **kwargs) for t in texts]


# ---------------------------------------------------------------------------
# 8. FEATURE EXTRACTION (for rule-based / classical models)
# ---------------------------------------------------------------------------


def extract_features(text: str) -> dict:
    """Extract linguistic features from preprocessed text."""
    words = text.split()
    return {
        "word_count": len(words),
        "char_count": len(text),
        "avg_word_length": sum(len(w) for w in words) / max(len(words), 1),
        "unique_words": len(set(words)),
        "has_negation": bool({"tidak", "bukan", "belum", "jangan", "kurang"} & set(words)),
        "has_positive": bool(SENTIMENT_KEEPERS & {"bagus", "mantap", "puas", "lancar", "cepat", "mudah"} & set(words)),
        "has_negative": bool(SENTIMENT_KEEPERS & {"buruk", "jelek", "parah", "gagal", "lemot", "susah"} & set(words)),
        "exclamation_count": text.count("!"),
        "question_count": text.count("?"),
        "repeated_char_count": len(re.findall(r"(.)\1", text)),
    }

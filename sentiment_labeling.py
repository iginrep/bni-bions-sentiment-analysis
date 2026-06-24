#!/usr/bin/env python3
"""
Script to label sentiment of social media items stored in MongoDB
using Google GenAI SDK with automatic model fallback.
"""

from __future__ import annotations

import os
import sys
import time
from typing import Any
import pymongo
from pymongo import MongoClient

# Try to load environment variables from .env file if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ---------------------------------------------------------------------------
# KONFIGURASI API GEMINI & MONGODB (MENDUKUNG ROTASI API KEYS)
# ---------------------------------------------------------------------------
# Anda dapat memasukkan beberapa API Key di bawah ini untuk rotasi otomatis saat terkena rate limit.
# Jika dibiarkan kosong, script akan membaca dari env variable GEMINI_API_KEYS (dipisah koma).
GEMINI_API_KEYS = []

# Jika ada di environment variable / .env, gunakan itu sebagai prioritas
env_keys = os.environ.get("GEMINI_API_KEYS", "")
if env_keys:
    GEMINI_API_KEYS = [k.strip() for k in env_keys.split(",") if k.strip()]

# Backup jika ada GEMINI_API_KEY single di env
single_key = os.environ.get("GEMINI_API_KEY")
if single_key and single_key not in GEMINI_API_KEYS:
    GEMINI_API_KEYS.insert(0, single_key)

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "bni_bions_sentiment"
SOURCE_COLLECTION = "social_items"
TARGET_COLLECTION = "social_items_labeled"

# Daftar model untuk mekanisme fallback secara berurutan
MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash-tts",
    "gemini-3-flash",
    "gemini-3.1-flash-lite",
    "gemini-3.1-flash-tts",
    "gemini-3.5-flash"
]

current_model_idx = 0
current_key_idx = 0

# ---------------------------------------------------------------------------
# INITIALIZATION & VERIFICATION
# ---------------------------------------------------------------------------
try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Error: Library 'google-genai' belum terinstall.")
    print("Silakan jalankan perintah berikut untuk menginstall:")
    print("  pip install google-genai")
    sys.exit(1)

# Pastikan ada minimal satu key yang valid
valid_keys = [k for k in GEMINI_API_KEYS if k and k != "PLACEHOLDER"]
if not valid_keys:
    print("WARNING: Tidak ada GEMINI_API_KEYS yang valid dikonfigurasi.")
    print("Silakan isi API Key Anda di dalam file ini atau di .env.")
    print("-" * 60)
else:
    GEMINI_API_KEYS = valid_keys


def get_sentiment_label(text: str) -> str:
    """
    Mengirim teks ke API Gemini untuk mendapatkan label sentimen ('Positif', 'Negatif', 'Netral').
    Memiliki mekanisme fallback otomatis:
    1. Mencoba daftar model cadangan secara berurutan.
    2. Jika seluruh model gagal pada API Key saat ini, beralih ke API Key berikutnya.
    3. Jika seluruh API Key dan model gagal, tidur 60 detik sebelum mengulang kembali.
    """
    global current_model_idx, current_key_idx
    
    # Pre-checks untuk membersihkan input text
    cleaned_text = (text or "").strip()
    if not cleaned_text:
        return "Netral"
        
    while True:
        model_name = MODELS[current_model_idx]
        api_key = GEMINI_API_KEYS[current_key_idx]
        
        # Masking API Key untuk log konsol yang aman
        masked_key = api_key[:10] + "..." + api_key[-5:] if len(api_key) > 15 else "INVALID"
        
        try:
            # Inisialisasi client GenAI dengan key saat ini
            client = genai.Client(api_key=api_key)
            
            response = client.models.generate_content(
                model=model_name,
                contents=cleaned_text,
                config=types.GenerateContentConfig(
                    system_instruction=(
                        "Anda adalah ahli analisis sentimen yang sangat ketat untuk ulasan aplikasi BIONS / BNI Sekuritas.\n"
                        "Tugas Anda adalah membaca ulasan/teks feedback dan mengelompokkannya menjadi salah satu dari tiga label berikut:\n"
                        "- 'Positif': untuk ulasan yang menyatakan kepuasan, pujian, kenyamanan, atau sentimen baik.\n"
                        "- 'Negatif': untuk ulasan yang menyatakan ketidakpuasan, error, bug, kritik, kekecewaan, kelambatan, atau sentimen buruk.\n"
                        "- 'Netral': untuk ulasan berupa pertanyaan umum, pernyataan fakta datar, informasi umum, atau sentimen netral.\n\n"
                        "Aturan penting:\n"
                        "1. Output Anda HARUS HANYA berupa satu kata saja: 'Positif', 'Negatif', atau 'Netral'.\n"
                        "2. Jangan tambahkan penjelasan, jangan gunakan tanda baca, jangan gunakan format markdown, jangan berikan spasi tambahan.\n\n"
                        "Contoh few-shot:\n"
                        "Ulasan: Bagus sekali aplikasinya, transaksinya sangat cepat.\n"
                        "Output: Positif\n\n"
                        "Ulasan: Susah login OTP lambat masuk.\n"
                        "Output: Negatif\n\n"
                        "Ulasan: Apakah aplikasi ini aman digunakan?\n"
                        "Output: Netral\n\n"
                        "Ulasan: BIONS sering error pas market open pagi ini.\n"
                        "Output: Negatif\n\n"
                        "Ulasan: Saya pengguna baru.\n"
                        "Output: Netral"
                    ),
                    temperature=0.0,
                    max_output_tokens=10,  # membatasi output agar efisien dan terarah
                )
            )
            
            if response.text:
                raw_label = response.text.strip().capitalize()
                if raw_label in ["Positif", "Negatif", "Netral"]:
                    return raw_label
                
                # Fallback substring mapping jika LLM menghasilkan teks tambahan
                lower_text = response.text.lower()
                if "positif" in lower_text:
                    return "Positif"
                elif "negatif" in lower_text:
                    return "Negatif"
                elif "netral" in lower_text:
                    return "Netral"
                
                return "Netral"
            else:
                raise ValueError("Response text dari Gemini kosong.")
                
        except Exception as e:
            print(f"  [!] Gagal memproses dengan model '{model_name}' menggunakan Key '{masked_key}': {e}")
            
            # Pindah ke model berikutnya dalam daftar
            old_model = model_name
            current_model_idx += 1
            
            if current_model_idx >= len(MODELS):
                # Jika semua model di key saat ini habis, ganti ke API Key berikutnya
                print(f"  [!] Semua model di API Key '{masked_key}' habis atau terkena limit.")
                current_model_idx = 0
                current_key_idx += 1
                
                if current_key_idx >= len(GEMINI_API_KEYS):
                    # Jika seluruh API Key habis/limit juga, tidur 60 detik
                    print(f"  [!] Seluruh ({len(GEMINI_API_KEYS)}) API Key dan seluruh model telah dicoba.")
                    print("  [!] Menunggu selama 60 detik sebelum kembali mencoba dari Key pertama...")
                    time.sleep(60)
                    current_key_idx = 0
                
                next_key = GEMINI_API_KEYS[current_key_idx]
                next_masked = next_key[:10] + "..." + next_key[-5:] if len(next_key) > 15 else "INVALID"
                print(f"  [*] Beralih ke API Key berikutnya: {next_masked}")
            else:
                print(f"  [*] Beralih dari model '{old_model}' ke '{MODELS[current_model_idx]}' dengan Key '{masked_key}'...")


def run_labeling() -> dict[str, int]:
    """
    Menjalankan pelabelan sentimen ulasan secara terdeduplikasi.
    Membaca dari social_items dan menulis ke social_items_labeled.
    Mengembalikan ringkasan statistik proses.
    """
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]
        source_col = db[SOURCE_COLLECTION]
        target_col = db[TARGET_COLLECTION]
        client.server_info()
    except Exception as e:
        print(f"ERROR: Tidak dapat terhubung ke MongoDB pada {MONGO_URI}: {e}")
        raise ConnectionError(f"Gagal koneksi ke MongoDB: {e}")

    try:
        documents = list(source_col.find({}))
        total_docs = len(documents)
    except Exception as e:
        print(f"ERROR: Gagal membaca data dari collection '{SOURCE_COLLECTION}': {e}")
        raise e

    if total_docs == 0:
        return {"total": 0, "success": 0, "skipped": 0, "failed": 0}

    processed_count = 0
    skipped_count = 0
    success_count = 0
    failed_count = 0

    for idx, doc in enumerate(documents, 1):
        try:
            platform = doc.get("platform")
            source_id = doc.get("sourceId")
            doc_id = doc.get("_id")
            
            # Ambil konten teks
            text = doc.get("text")
            if not text and isinstance(doc.get("content"), dict):
                text = doc.get("content", {}).get("text")

            # Cek duplikasi di collection target
            existing = target_col.find_one({
                "$or": [
                    {"_id": doc_id},
                    {"platform": platform, "sourceId": source_id}
                ]
            })

            if existing:
                skipped_count += 1
                continue

            # Jalankan labeling jika belum diproses
            if not text:
                label = "Netral"
            else:
                label = get_sentiment_label(text)

            # Salin data asli dan tambahkan labeling_review
            new_doc = dict(doc)
            new_doc["labeling_review"] = label

            # Simpan ke target collection
            target_col.insert_one(new_doc)
            success_count += 1
            processed_count += 1

        except Exception as e:
            print(f"  [X] Gagal memproses dokumen ID {doc.get('_id')}: {e}")
            failed_count += 1
            continue

    return {
        "total": total_docs,
        "success": success_count,
        "skipped": skipped_count,
        "failed": failed_count
    }


def main():
    print("=" * 60)
    print("MULAI PROSES LABELING SENTIMEN MENGGUNAKAN GEMINI")
    print("=" * 60)
    print(f"[*] Menghubungkan ke MongoDB...")
    try:
        stats = run_labeling()
        print("\n" + "=" * 60)
        print("RINGKASAN PROSES LABELING SENTIMEN:")
        print("=" * 60)
        print(f"Total Ulasan Asal        : {stats['total']}")
        print(f"Ulasan Berhasil Diproses : {stats['success']}")
        print(f"Ulasan Dilewati (Skipped): {stats['skipped']}")
        print(f"Ulasan Gagal/Error       : {stats['failed']}")
        print(f"Selesai! Data disimpan di collection '{TARGET_COLLECTION}'.")
        print("=" * 60)
    except Exception as e:
        print(f"PROSES GAGAL: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

# check_models.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Error: Pastikan GEMINI_API_KEY ada di file .env Anda!")
else:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print("Mencari model yang tersedia untuk Kunci API Anda...")
        print("="*40)
        
        # Ini adalah inti dari skrip
        found_models = False
        for model in genai.list_models():
            # Kita HANYA tertarik pada model yang bisa 'generateContent'
            if 'generateContent' in model.supported_generation_methods:
                print(f"✅ Model Ditemukan: {model.name}")
                found_models = True
        
        print("="*40)
        if found_models:
            print("Silakan salin salah satu 'Model Ditemukan' di atas (idealnya yang ada 'gemini' di namanya) dan kirimkan ke saya.")
        else:
            print("Tidak ada model yang mendukung 'generateContent' ditemukan untuk Kunci API ini.")

    except Exception as e:
        print(f"Terjadi kesalahan saat menghubungi API: {e}")
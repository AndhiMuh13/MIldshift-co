# copilot.py

import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# --- PERSIAPAN ---
# 1. Muat Kunci API dari file .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("Error: Kunci API GEMINI_API_KEY tidak ditemukan di file .env!")
    exit()

# 2. Inisialisasi Klien Gemini
# Model yang digunakan: gemini-2.5-flash (cepat & efisien untuk koding)
client = genai.Client(api_key=API_KEY)
MODEL_NAME = "gemini-2.5-flash" 

# 3. SYSTEM INSTRUCTION (Jantung Logika Copilot)
SYSTEM_PROMPT = """
Anda adalah AI Code Copilot yang canggih dan fokus pada fungsionalitas.
Tugas Anda adalah mengubah ide bahasa alami pengguna menjadi kode yang utuh, berfungsi, dan siap pakai.
Prioritas keluaran adalah: Aplikasi Web Sederhana (Flask/Node.js) atau Aplikasi Mobile (Flutter/Dart).
OUTPUT HANYA BERUPA KODE, tanpa penjelasan naratif tambahan (kecuali dalam komentar kode).
Sertakan komentar singkat di awal kode yang menjelaskan prasyarat dan cara menjalankannya (misal: "Install flask", "python app.py").
"""

# --- FUNGSI UTAMA ---
def generate_code_from_idea(idea: str):
    """Fungsi untuk memanggil Gemini API dan menghasilkan kode."""
    
    prompt = f"Ide pengguna:\n---\n'{idea}'\n---\n\nBuatkan kode lengkapnya SEKARANG."
    
    # Konfigurasi Model
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        temperature=0.3, # Suhu rendah untuk konsistensi kode
    )

    print("---")
    print("🤖 AI Copilot sedang memproses ide Anda...")
    print("---")
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[prompt],
            config=config,
        )
        
        # 4. Tampilkan Hasil
        code_output = response.text.strip()
        
        print("\n" + "="*70)
        print("🎉 KODE HASIL GENERASI AI COPILOT (SIAP SALIN):")
        print("="*70)
        
        # Output kode ke terminal
        print(code_output)
        
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n[ERROR] Terjadi kesalahan saat memanggil API: {e}")
        print("Cek kembali kunci API di file .env dan pastikan Anda memiliki kuota penggunaan.")

# --- MAIN PROGRAM ---
if __name__ == "__main__":
    print("\n[AI Code Copilot Lokal - Gemini Pro] Selamat Datang!")
    print("-----------------------------------------------------")
    
    # Loop untuk input ide berulang kali
    while True:
        user_idea = input("Masukkan ide koding Anda (atau ketik 'exit' untuk keluar):\n> ")
        
        if user_idea.lower() == 'exit':
            print("Terima kasih. Sampai jumpa!")
            break
            
        if user_idea.strip():
            generate_code_from_idea(user_idea)
        else:
            print("Ide tidak boleh kosong. Silakan coba lagi.")
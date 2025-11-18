# copilot_web.py (Versi Web App TERBARU dengan Tombol Download)
# Ini adalah pengembangan dari copilot.py

import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import streamlit as st # Membutuhkan: pip install streamlit

# --- FUNGSI AI (SAMA SEPERTI SEBELUMNYA) ---

# 1. Muat Kunci API
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Cek API Key saat start (Penting untuk Streamlit)
if not API_KEY:
    # Menampilkan error di UI web, bukan terminal
    st.error("Error: Kunci API 'GEMINI_API_KEY' tidak ditemukan di file .env!")
    st.stop() # Hentikan eksekusi jika key tidak ada

# 2. Inisialisasi Klien Gemini
try:
    client = genai.Client(api_key=API_KEY)
    MODEL_NAME = "gemini-2.5-flash" 
except Exception as e:
    st.error(f"Gagal menginisialisasi Klien Gemini: {e}")
    st.stop()

# 3. SYSTEM INSTRUCTION (Prompt yang lebih baik untuk desain)
SYSTEM_PROMPT = """
Anda adalah AI Code Copilot yang canggih dengan fokus pada UI/UX (Desain Tampilan).
Tugas Anda adalah mengubah ide pengguna menjadi kode yang utuh, berfungsi, dan siap pakai.
Prioritas: Aplikasi Web (HTML/CSS/JS) atau Aplikasi Mobile (Flutter/Dart).
PENTING: Untuk aplikasi web, Anda WAJIB menyertakan CSS modern (inline atau dalam tag <style>) agar tampilannya (desainnya) menarik secara visual.
OUTPUT HANYA BERUPA KODE, tanpa penjelasan naratif tambahan (kecuali dalam komentar kode).
Sertakan komentar singkat di awal kode yang menjelaskan prasyarat dan cara menjalankannya.
"""

def generate_code_from_idea(idea: str):
    """Fungsi untuk memanggil Gemini API dan menghasilkan kode."""
    
    prompt = f"Ide pengguna:\n---\n'{idea}'\n---\n\nBuatkan kode lengkapnya SEKARANG."
    
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        temperature=0.3, # Suhu rendah untuk konsistensi kode
    )

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[prompt],
            config=config,
        )
        return response.text.strip()
        
    except Exception as e:
        # Menampilkan error di UI web
        st.error(f"Terjadi kesalahan saat memanggil API: {e}")
        return None

# --- UI (User Interface) STREAMLIT ---

# 1. Konfigurasi dan Judul Halaman
st.set_page_config(page_title="🤖 AI Code Copilot", layout="wide")
st.title("🤖 AI Code Copilot Anda")
st.caption("Didukung oleh Google Gemini Pro | Dibuat dengan Streamlit")

# 2. Input Ide Pengguna
user_idea = st.text_area(
    "Masukkan ide aplikasi Anda di sini:", 
    height=100,
    placeholder="Contoh: 'Buatkan halaman login sederhana dengan kotak username, password, dan tombol kirim'"
)

# 3. Tombol Generate
if st.button("🚀 Generate Kode", type="primary", use_container_width=True):
    if user_idea.strip():
        # Tampilkan status "Loading..."
        with st.spinner("🤖 AI Copilot sedang memproses ide Anda..."):
            
            # Panggil fungsi AI
            generated_code = generate_code_from_idea(user_idea)
            
            if generated_code:
                st.subheader("🎉 Kode Hasil Generasi:")
                
                # Menampilkan kode dengan highlight sintaks
                st.code(generated_code, language=None, line_numbers=True)
                
                # --- FITUR PRATINJAU DESAIN ---
                if "<html" in generated_code.lower() and "</html" in generated_code.lower():
                    st.subheader("🖥️ Pratinjau Desain (Render HTML/CSS):")
                    st.components.v1.html(generated_code, height=600, scrolling=True)

                # --- [UPDATE TERBARU DITAMBAHKAN DI SINI] ---
                st.subheader("⬇️ Simpan Kode")

                # Tentukan nama file berdasarkan konten
                file_name = "output.py" # Default
                if "<html" in generated_code.lower():
                    file_name = "index.html"
                elif "flutter" in generated_code.lower() or "dart" in generated_code.lower():
                    file_name = "main.dart"
                elif "node.js" in generated_code.lower() or "const" in generated_code.lower():
                    file_name = "app.js"
                elif "flask" in generated_code.lower():
                    file_name = "app.py"

                # Buat Tombol Download
                st.download_button(
                    label=f"Download sebagai {file_name}",
                    data=generated_code,
                    file_name=file_name,
                    mime="text/plain", # MIME type 'text/plain' aman untuk semua kode
                    use_container_width=True
                )
                # --- [AKHIR UPDATE] ---

    else:
        st.warning("Harap masukkan ide Anda terlebih dahulu.")
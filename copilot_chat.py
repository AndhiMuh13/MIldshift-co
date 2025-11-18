# copilot_chat.py
# VERSI UPDATE: Menambahkan Tombol "Chat Baru" di Sidebar
# Ini untuk memisahkan topik/konteks

import os
import google.generativeai as genai
from google.generativeai import types
from dotenv import load_dotenv
import streamlit as st

# --- KONFIGURASI AWAL (Sama seperti sebelumnya) ---

# 1. Muat Kunci API
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("Error: Kunci API 'GEMINI_API_KEY' tidak ditemukan di file .env!")
    st.stop()

# 2. Konfigurasi Klien genai
try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error(f"Gagal mengkonfigurasi Klien Gemini: {e}")
    st.stop()

# 3. SYSTEM INSTRUCTION (Sama)
SYSTEM_PROMPT = """
Anda adalah AI Code Copilot yang canggih (seperti Emergent.sh) dalam sebuah sesi chat.
Tugas Anda adalah membantu pengguna secara iteratif membangun aplikasi.
Anda akan menerima seluruh riwayat obrolan. JANGAN ulangi kode sebelumnya kecuali diminta.
Fokus pada permintaan baru pengguna dan gunakan riwayat sebagai KONTEKS.
Jika pengguna meminta kode baru, buatlah. Jika mereka meminta untuk MENGUBAH kode terakhir, berikan kode yang telah dimodifikasi.
Prioritas: Aplikasi Web (HTML/CSS/JS) atau Aplikasi Mobile (Flutter/Dart).
Selalu sertakan CSS untuk desain yang menarik.
OUTPUT HANYA BERUPA KODE, atau penjelasan singkat jika ditanya.
"""

# 4. Inisialisasi Model (Sama)
try:
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_PROMPT,
        generation_config=types.GenerationConfig(temperature=0.3)
    )
except Exception as e:
    st.error(f"Gagal memuat model Gemini: {e}")
    st.stop()


# --- UI (User Interface) STREAMLIT ---

st.set_page_config(page_title="🤖 AI Copilot Agent", layout="wide")
st.title("🤖 AI Code Copilot (Agent Version)")
st.caption("Dengan memori percakapan DAN pemisah topik")

# --- [UPDATE TERBARU DITAMBAHKAN DI SINI] ---
# 5. Kontrol Sidebar (Tombol Chat Baru)

with st.sidebar:
    st.header("Kontrol Sesi")
    st.write("Gunakan tombol ini untuk memulai topik baru (misal: beralih dari Web ke Flutter).")
    
    # Tombol untuk membersihkan memori
    if st.button("Mulai Chat Baru", use_container_width=True, type="primary"):
        # Hapus memori UI (messages)
        if "messages" in st.session_state:
            del st.session_state.messages
        # Hapus memori API (chat_session)
        if "chat_session" in st.session_state:
            del st.session_state.chat_session
        
        # Muat ulang halaman untuk memulai dari awal
        st.rerun()

# --- [AKHIR UPDATE] ---


# 6. Inisialisasi Memori Chat (Session State)
# Ini hanya akan berjalan jika belum ada atau SETELAH di-reset
if "messages" not in st.session_state:
    st.session_state.messages = [] # Untuk TAMPILAN UI
if "chat_session" not in st.session_state:
    # Memulai sesi chat API yang baru
    st.session_state.chat_session = model.start_chat(history=[])

# 7. Tampilkan semua pesan dari memori (Tampilan)
for message in st.session_state.messages:
    role = "assistant" if message["role"] == "model" else "user"
    with st.chat_message(role):
        st.markdown(message["content"])

# 8. Gunakan st.chat_input (UI Chat Baru)
if prompt := st.chat_input("Masukkan ide Anda atau minta modifikasi..."):
    
    # A. Tampilkan pesan pengguna di UI
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # B. Tambahkan pesan pengguna ke 'memori TAMPILAN'
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # C. Dapatkan respons AI
    with st.chat_message("assistant"):
        with st.spinner("🤖 Agent sedang berpikir..."):
            
            try:
                # Kirim pesan ke sesi chat API
                response = st.session_state.chat_session.send_message(prompt)
                response_content = response.text.strip()

                if response_content:
                    # Tampilkan respons AI (kode)
                    st.markdown(response_content)
                    
                    # Tampilkan Fitur Pratinjau & Download
                    if "<html" in response_content.lower() and "</html" in response_content.lower():
                        st.subheader("🖥️ Pratinjau Desain:")
                        st.components.v1.html(response_content, height=400, scrolling=True)

                    file_name = "output.py" # Default
                    if "<html" in response_content.lower(): file_name = "index.html"
                    elif "flutter" in response_content.lower(): file_name = "main.dart"
                    
                    st.download_button(
                        label=f"Download {file_name}",
                        data=response_content,
                        file_name=file_name,
                        mime="text/plain"
                    )
                    
                    # D. Tambahkan respons AI ke 'memori TAMPILAN'
                    st.session_state.messages.append({"role": "model", "content": response_content})
                else:
                    st.error("Gagal mendapatkan respons dari AI.")
            
            except Exception as e:
                st.error(f"Terjadi kesalahan saat memanggil API: {e}")
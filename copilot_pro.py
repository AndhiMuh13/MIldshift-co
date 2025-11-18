# copilot_pro.py
# VERSI UPDATE: Mengembalikan "Pratinjau Gabungan" untuk Multi-File

import os
import google.generativeai as genai
from google.generativeai import types
from dotenv import load_dotenv
import streamlit as st
import json # Untuk mengurai respons AI
import zipfile # Untuk membuat file ZIP
import io # Untuk mengelola ZIP di memori

# --- KONFIGURASI AWAL (Sama) ---

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("Error: Kunci API 'GEMINI_API_KEY' tidak ditemukan di file .env!")
    st.stop()

try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error(f"Gagal mengkonfigurasi Klien Gemini: {e}")
    st.stop()

SYSTEM_PROMPT = """
Anda adalah AI Arsitek Kode.
Ubah ide pengguna menjadi STRUKTUR PROYEK multi-file yang lengkap.
Anda HARUS SELALU merespons HANYA dengan JSON.
Format JSON HARUS berupa daftar (list) dari objek, di mana setiap objek memiliki "nama_file" dan "isi_kode".
Pastikan nama file menyertakan path jika diperlukan (misal: "static/style.css").

Contoh Respons JSON:
[
  {
    "nama_file": "index.html",
    "isi_kode": "<html><head></head><body>...</body></html>"
  },
  {
    "nama_file": "static/style.css",
    "isi_kode": "body { ... }"
  },
  {
    "nama_file": "static/script.js",
    "isi_kode": "console.log('hello');"
  }
]
"""

try:
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_PROMPT,
        generation_config=types.GenerationConfig(
            temperature=0.2,
            response_mime_type="application/json" 
        )
    )
except Exception as e:
    st.error(f"Gagal memuat model Gemini: {e}")
    st.stop()

# --- [FUNGSI HELPER BARU DITAMBAHKAN DI SINI] ---

def create_previewable_html(file_structure: list) -> str | None:
    """
    Menggabungkan file HTML, CSS, dan JS dari struktur JSON
    menjadi satu string HTML untuk pratinjau Streamlit.
    """
    html_content = ""
    css_content = ""
    js_content = ""

    # 1. Ekstrak semua kode HTML, CSS, dan JS
    for file_data in file_structure:
        if file_data["nama_file"].endswith(".html"):
            html_content = file_data["isi_kode"]
        elif file_data["nama_file"].endswith(".css"):
            css_content += file_data["isi_kode"] + "\n"
        elif file_data["nama_file"].endswith(".js"):
            js_content += file_data["isi_kode"] + "\n"

    # Jika tidak ada HTML, tidak ada pratinjau
    if not html_content:
        return None

    # 2. Suntikkan CSS ke dalam <head>
    if css_content:
        css_tag = f"<style>\n{css_content}\n</style>"
        if "</head>" in html_content:
            html_content = html_content.replace("</head>", f"{css_tag}\n</head>", 1)
        else:
            html_content = f"{css_tag}\n{html_content}" # Fallback jika tidak ada <head>

    # 3. Suntikkan JS ke dalam <body>
    if js_content:
        js_tag = f"<script>\n{js_content}\n</script>"
        if "</body>" in html_content:
            html_content = html_content.replace("</body>", f"{js_tag}\n</body>", 1)
        else:
            html_content = f"{html_content}\n{js_tag}" # Fallback jika tidak ada <body>

    return html_content

# --- [AKHIR FUNGSI HELPER BARU] ---


# --- UI (User Interface) STREAMLIT ---

st.set_page_config(page_title="🤖 Mildshift Copilot", layout="wide")
st.title("🤖 Mildshift Copilot (Pro)")
st.caption("Membangun proyek multi-file dengan Pratinjau | Didukung Gemini Pro")

# Sidebar (Sama)
with st.sidebar:
    st.header("Kontrol Proyek")
    if st.button("Mulai Proyek Baru", use_container_width=True, type="primary"):
        if "messages" in st.session_state: del st.session_state.messages
        if "chat_session" in st.session_state: del st.session_state.chat_session
        st.rerun()

# Inisialisasi Memori Chat (Sama)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# --- Tampilkan riwayat obrolan (DIMODIFIKASI) ---
for message in st.session_state.messages:
    role = "assistant" if message["role"] == "model" else "user"
    with st.chat_message(role):
        
        if role == "user":
            st.markdown(message["content"])
        else:
            # 'content' dari model adalah list file
            file_structure = message["content"] 
            
            # --- [UPDATE DI SINI] ---
            # Coba buat pratinjau gabungan
            preview_html = create_previewable_html(file_structure)
            if preview_html:
                st.subheader("🖥️ Pratinjau Desain (Gabungan)")
                st.components.v1.html(preview_html, height=500, scrolling=True)
            # --- [AKHIR UPDATE] ---

            # Buat file ZIP di memori
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for file_data in file_structure:
                    zf.writestr(file_data["nama_file"], file_data["isi_kode"])
            
            st.download_button(
                label="⬇️ Download Proyek (.zip)",
                data=zip_buffer.getvalue(),
                file_name="proyek_mildshift.zip",
                mime="application/zip",
            )

            # Buat Tabs untuk setiap file
            tab_names = [file["nama_file"] for file in file_structure]
            tabs = st.tabs(tab_names)
            for i, tab in enumerate(tabs):
                with tab:
                    st.code(file_structure[i]["isi_kode"], language="auto", line_numbers=True)


# --- Input Chat (DIMODIFIKASI) ---
if prompt := st.chat_input("Jelaskan proyek yang ingin Anda buat..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        with st.spinner("🤖 Mildshift sedang membangun arsitektur..."):
            
            try:
                response = st.session_state.chat_session.send_message(prompt)
                response_content = response.text.strip()
                
                try:
                    if response_content.startswith("```json"):
                        response_content = response_content[7:-3].strip()
                    
                    file_structure = json.loads(response_content) 
                    
                    if not isinstance(file_structure, list):
                        raise ValueError("JSON tidak dalam format list")

                    # --- [UPDATE DI SINI] ---
                    # Coba buat pratinjau gabungan
                    preview_html = create_previewable_html(file_structure)
                    if preview_html:
                        st.subheader("🖥️ Pratinjau Desain (Gabungan)")
                        st.components.v1.html(preview_html, height=500, scrolling=True)
                    # --- [AKHIR UPDATE] ---

                    # Buat file ZIP
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                        for file_data in file_structure:
                            zf.writestr(file_data["nama_file"], file_data["isi_kode"])
                    
                    st.download_button(
                        label="⬇️ Download Proyek (.zip)",
                        data=zip_buffer.getvalue(),
                        file_name="proyek_mildshift.zip",
                        mime="application/zip",
                    )

                    # Buat Tabs
                    tab_names = [file["nama_file"] for file in file_structure]
                    tabs = st.tabs(tab_names)
                    for i, tab in enumerate(tabs):
                        with tab:
                            st.code(file_structure[i]["isi_kode"], language="auto", line_numbers=True)

                    st.session_state.messages.append({"role": "model", "content": file_structure})

                except (json.JSONDecodeError, ValueError) as e:
                    st.error(f"Gagal mengurai respons AI sebagai JSON: {e}")
                    st.markdown("Respons mentah dari AI (bukan JSON):")
                    st.code(response_content)
                    st.session_state.messages.append({"role": "model", "content": [{"nama_file": "error.txt", "isi_kode": response_content}]})

            except Exception as e:
                st.error(f"Terjadi kesalahan saat memanggil API: {e}")
# modes/mode_pro.py
# [PERBAIKAN 12]: Menambahkan 'safety check' JSON untuk menangani respons teks biasa

import streamlit as st
import google.generativeai as genai
from google.generativeai import types
import json
import zipfile
import io
from prompts import SYSTEM_PROMPT_PRO
from utils import create_previewable_html

def run_pro_mode():
    st.title("🤖 Mildshift Copilot (Pro)")
    st.caption("Mode: Proyek Canggih (Multi-File JSON, Tanpa Riset)")
    
    try:
        if "pro_model" not in st.session_state: 
            st.session_state.pro_model = genai.GenerativeModel(
                model_name="gemini-2.5-pro", 
                system_instruction=SYSTEM_PROMPT_PRO, 
                generation_config=types.GenerationConfig(temperature=0.2, response_mime_type="application/json")
            )
        if "pro_chat_session" not in st.session_state: st.session_state.pro_chat_session = st.session_state.pro_model.start_chat(history=[])
        if "pro_messages" not in st.session_state: st.session_state.pro_messages = []
    except Exception as e: st.error(f"Gagal memuat model: {e}"); st.stop()
    
    for i, message in enumerate(st.session_state.pro_messages):
        role = "assistant" if message["role"] == "model" else "user"
        with st.chat_message(role):
            if role == "user": st.markdown(message["content"])
            else:
                # 'content' di sini seharusnya adalah 'file_structure' (list)
                file_structure = message["content"]
                preview_html = create_previewable_html(file_structure)
                
                if preview_html: 
                    st.subheader("🖥️ Pratinjau Desain (HTML/CSS Sederhana)")
                    st.components.v1.html(preview_html, height=500, scrolling=True)
                else: 
                    st.info("Pratinjau tidak tersedia untuk proyek non-HTML statis (seperti React). Gunakan 'Download .zip'.")
                
                zip_buffer = io.BytesIO();
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                    for file_data in file_structure: zf.writestr(file_data["nama_file"], file_data["isi_kode"])
                st.download_button("⬇️ Download Proyek (.zip)", zip_buffer.getvalue(), "proyek_mildshift.zip", "application/zip", key=f"pro_zip_{i}")
                
                tab_names = [file["nama_file"] for file in file_structure]
                tabs = st.tabs(tab_names)
                for j, tab in enumerate(tabs):
                    with tab: st.code(file_structure[j]["isi_kode"], language="auto", line_numbers=True)
    
    if prompt := st.chat_input("Jelaskan proyek canggih yang ingin Anda buat..."):
        st.session_state.pro_messages.append({"role": "user", "content": prompt});
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("🤖 Mildshift sedang membangun arsitektur..."):
                try:
                    response = st.session_state.pro_chat_session.send_message(prompt)
                    response_content = response.text.strip()
                    
                    # --- [PERBAIKAN ADA DI SINI] ---
                    # 1. Membersihkan markdown fences (untuk jaga-jaga)
                    if response_content.startswith("```json"):
                        response_content = response_content[7:-3].strip()
                    elif response_content.startswith("```"):
                         response_content = response_content[3:-3].strip()
                    
                    # 2. Menambahkan "Safety Check"
                    if response_content.startswith("[") or response_content.startswith("{"):
                        # Ini adalah JSON, lanjutkan seperti biasa
                        file_structure = json.loads(response_content, strict=False)
                        if not isinstance(file_structure, list): raise ValueError("JSON bukan list")
                        
                        preview_html = create_previewable_html(file_structure)
                        if preview_html: 
                            st.subheader("🖥️ Pratinjau Desain (HTML/CSS Sederhana)")
                            st.components.v1.html(preview_html, height=500, scrolling=True)
                        else: 
                            st.info("Pratinjau tidak tersedia untuk proyek non-HTML statis (seperti React). Gunakan 'Download .zip'.")
                        
                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                            for file_data in file_structure: zf.writestr(file_data["nama_file"], file_data["isi_kode"])
                        st.download_button("⬇️ Download Proyek (.zip)", zip_buffer.getvalue(), "proyek_mildshift.zip", "application/zip", key="pro_zip_new")
                        
                        tab_names = [file["nama_file"] for file in file_structure]
                        tabs = st.tabs(tab_names)
                        for k, tab in enumerate(tabs):
                            with tab: st.code(file_structure[k]["isi_kode"], language="auto", line_numbers=True)
                        
                        # Simpan struktur file (JSON) ke memori
                        st.session_state.pro_messages.append({"role": "model", "content": file_structure})
                    
                    else:
                        # Ini adalah TEKS BIASA, bukan JSON
                        st.warning("AI merespons dengan teks biasa, bukan JSON. Mode ini tidak dirancang untuk obrolan iteratif. Coba gunakan 'Prototipe Visual' atau 'UI/UX Designer'.")
                        st.code(response_content)
                        # Jangan simpan respons ini ke memori karena formatnya salah
                    # --- [AKHIR PERBAIKAN] ---

                except (json.JSONDecodeError, ValueError) as e: 
                    st.error(f"Gagal mengurai respons AI sebagai JSON: {e}")
                    st.code(response_content) # Tampilkan apa yang menyebabkan error
                except Exception as e: 
                    st.error(f"Terjadi kesalahan saat memanggil API: {e}")
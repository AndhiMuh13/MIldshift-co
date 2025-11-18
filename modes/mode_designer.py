# modes/mode_designer.py
import streamlit as st
import google.generativeai as genai
from google.generativeai import types
import json
import zipfile
import io
from prompts import SYSTEM_PROMPT_DESIGNER
from tools import google_search_tool
from utils import run_chat_loop_with_tools

def run_designer_mode():
    st.title("✨ Mildshift UI/UX Designer (v.Riset)")
    st.caption("Mode: Desain & Konsep UI/UX (Dengan Riset Google)")
    
    try:
        if "design_model" not in st.session_state:
            st.session_state.design_model = genai.GenerativeModel(
                model_name="gemini-2.5-pro",
                system_instruction=SYSTEM_PROMPT_DESIGNER,
                generation_config=types.GenerationConfig(temperature=0.3),
                tools=[google_search_tool] 
            )
        if "design_chat_session" not in st.session_state:
            st.session_state.design_chat_session = st.session_state.design_model.start_chat(history=[])
        if "design_messages" not in st.session_state:
            st.session_state.design_messages = []
    except Exception as e: st.error(f"Gagal memuat model: {e}"); st.stop()

    def display_design_response(content, unique_key):
        try:
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                 content = content[3:-3].strip()
            
            file_structure = []
            
            # --- [PERBAIKAN ADA DI SINI] ---
            parsed_json = json.loads(content, strict=False)
            # --- [AKHIR PERBAIKAN] ---
            
            if isinstance(parsed_json, list):
                file_structure = parsed_json
                if "nama_file" not in file_structure[0]:
                    new_structure = []
                    for item in file_structure:
                        for file_name, file_code in item.items():
                            new_structure.append({"nama_file": file_name, "isi_kode": file_code})
                    file_structure = new_structure
            elif isinstance(parsed_json, dict):
                for file_name, file_code in parsed_json.items():
                    file_structure.append({"nama_file": file_name, "isi_kode": file_code})
            else:
                raise ValueError("Format JSON tidak dikenali (bukan list atau dict).")
            
            readme_content = ""
            html_content = None
            for file in file_structure:
                if file["nama_file"].endswith(".md"): readme_content = file["isi_kode"]
                elif file["nama_file"].endswith(".html"): html_content = file["isi_kode"]
            
            st.subheader("💡 Konsep Desain & Hasil Riset")
            st.markdown(readme_content)
            
            if html_content:
                st.subheader("🖥️ Pratinjau Desain (Live)")
                st.components.v1.html(html_content, height=600, scrolling=True)
            
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for file_data in file_structure: zf.writestr(file_data["nama_file"], file_data["isi_kode"])
            st.download_button("⬇️ Download Proyek (.zip)", zip_buffer.getvalue(), "proyek_desain.zip", "application/zip", key=f"design_zip_{unique_key}")
            
            tab_names = [file["nama_file"] for file in file_structure]
            tabs = st.tabs(tab_names)
            for j, tab in enumerate(tabs):
                with tab: st.code(file_structure[j]["isi_kode"], language="auto", line_numbers=True)
        except Exception as e:
            st.error(f"Gagal memproses respons JSON: {e}"); st.code(content)
    
    run_chat_loop_with_tools(
        st.session_state.design_model,
        st.session_state.design_chat_session,
        "design_messages",
        display_design_response,
        "🤖 Mildshift sedang meneliti tren desain..."
    )
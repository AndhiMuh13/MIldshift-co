# modes/mode_preview.py
import streamlit as st
import google.generativeai as genai
from google.generativeai import types
import json
from prompts import SYSTEM_PROMPT_PREVIEW
from tools import google_search_tool
from utils import run_chat_loop_with_tools

def run_preview_mode():
    st.title("🎨 Mildshift Prototyper (v.Cerdas)")
    st.caption("Mode: Prototipe Visual (Single-File, Dengan Riset Google)")
    
    try:
        if "preview_model" not in st.session_state:
            st.session_state.preview_model = genai.GenerativeModel(
                model_name="gemini-2.5-pro",
                system_instruction=SYSTEM_PROMPT_PREVIEW,
                generation_config=types.GenerationConfig(temperature=0.2),
                tools=[google_search_tool] 
            )
        if "preview_chat_session" not in st.session_state:
            st.session_state.preview_chat_session = st.session_state.preview_model.start_chat(history=[])
        if "preview_messages" not in st.session_state:
            st.session_state.preview_messages = []
    except Exception as e: st.error(f"Gagal memuat model: {e}"); st.stop()

    def display_preview_response(content, unique_key):
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
            elif isinstance(parsed_json, dict):
                for file_name, file_code in parsed_json.items():
                    file_structure.append({"nama_file": file_name, "isi_kode": file_code})
            else:
                raise ValueError("Format JSON tidak dikenali (bukan list atau dict).")

            html_content = file_structure[0]["isi_kode"]
            st.subheader("🖥️ Pratinjau Desain (Live via Babel/CDN)")
            st.components.v1.html(html_content, height=600, scrolling=True)
            st.download_button("⬇️ Download (index.html)", html_content, "index.html", "text/html", key=unique_key)
            st.code(html_content, language="html", line_numbers=True)
        except Exception as e:
            st.error(f"Gagal memproses respons JSON: {e}"); st.code(content)
    
    run_chat_loop_with_tools(
        st.session_state.preview_model,
        st.session_state.preview_chat_session,
        "preview_messages",
        display_preview_response,
        "🤖 Mildshift sedang membangun prototipe..."
    )
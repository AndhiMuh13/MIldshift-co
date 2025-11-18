# modes/mode_review.py
import streamlit as st
import google.generativeai as genai
from google.generativeai import types
from prompts import SYSTEM_PROMPT_REVIEW
from tools import google_search_tool
from utils import run_chat_loop_with_tools

def run_review_mode():
    st.title("🔍 Mildshift Code Reviewer (v.Cerdas)")
    st.caption("Mode: Analisis Kualitas Kode (Dengan Riset Google)")
    
    st.info("ℹ️ **Cara Penggunaan:**\nAnda sekarang bisa bertanya: 'Tinjau kode ini' ATAU 'Cari best practices React 19 dan perbaiki kode saya'.")
    
    try:
        if "review_model" not in st.session_state:
            st.session_state.review_model = genai.GenerativeModel(
                model_name="gemini-2.5-pro",
                system_instruction=SYSTEM_PROMPT_REVIEW,
                generation_config=types.GenerationConfig(temperature=0.1),
                tools=[google_search_tool] 
            )
        if "review_chat_session" not in st.session_state:
            st.session_state.review_chat_session = st.session_state.review_model.start_chat(history=[])
        if "review_messages" not in st.session_state:
            st.session_state.review_messages = []
    except Exception as e: st.error(f"Gagal memuat model: {e}"); st.stop()

    def display_review_response(content, unique_key):
        # [PENTING] Fungsi ini HANYA menampilkan Teks Markdown
        # Tidak ada parsing JSON sama sekali.
        try:
            st.markdown(content)
        except Exception as e:
            st.error(f"Gagal menampilkan respons markdown: {e}")
            st.code(content)
    
    run_chat_loop_with_tools(
        st.session_state.review_model,
        st.session_state.review_chat_session,
        "review_messages",
        display_review_response,
        "🤖 Reviewer sedang menganalisis kode..."
    )
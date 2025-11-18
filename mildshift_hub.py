# mildshift_hub.py
# VERSI FINAL SUPER: Support JPG, PNG, PDF, TXT, MD untuk Konteks

import os
import google.generativeai as genai
from dotenv import load_dotenv
import streamlit as st
import PyPDF2 # Library baru untuk PDF
from PIL import Image # Library untuk Gambar

# Impor mode-mode
from modes.mode_pro import run_pro_mode
from modes.mode_preview import run_preview_mode
from modes.mode_review import run_review_mode
from modes.mode_designer import run_designer_mode

# --- KONFIGURASI AWAL ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GSEARCH_API_KEY = os.getenv("GSEARCH_API_KEY")
GSEARCH_CX_ID = os.getenv("GSEARCH_CX_ID")

if not GEMINI_API_KEY: st.error("Error: Kunci API tidak ditemukan!"); st.stop()
    
try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(f"Gagal mengkonfigurasi Klien Gemini: {e}"); st.stop()

# --- LOGIKA APLIKASI ---

st.set_page_config(page_title="🤖 Mildshift Hub (v.Multimodal)", layout="wide")

def return_to_hub():
    st.session_state.mode = None
    for key in list(st.session_state.keys()):
        if key.startswith("pro_") or key.startswith("preview_") or key.startswith("review_") or key.startswith("design_"):
            del st.session_state[key]
    st.rerun()

if "mode" not in st.session_state: st.session_state.mode = None
# Kita simpan dua jenis memori: Teks (dari PDF/TXT) dan Gambar (dari JPG/PNG)
if "kb_text" not in st.session_state: st.session_state.kb_text = ""
if "kb_image" not in st.session_state: st.session_state.kb_image = None

# ===================================================================
# MODE 0: HUB PILIHAN
# ===================================================================
def render_hub_selection():
    st.title("🤖 Selamat Datang di Mildshift Hub")
    st.image("https://i.imgur.com/gY97J2R.png", width=600) 
    st.subheader("Apa yang ingin Anda bangun hari ini?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Buat Proyek Canggih", use_container_width=True, type="primary"):
            st.session_state.mode = "pro"; st.rerun()
        st.info("Membangun fondasi proyek (multi-file, .zip).")
        if st.button("🔍 Analisis & Perbaikan Kode", use_container_width=True, type="secondary"):
            st.session_state.mode = "review"; st.rerun()
        st.info("Review kode dengan standar tinggi.")
    with col2:
        if st.button("🎨 Buat Prototipe Visual", use_container_width=True, type="secondary"):
            st.session_state.mode = "preview"; st.rerun()
        st.info("Prototipe visual (single-file) dengan riset.")
        if st.button("✨ UI/UX Designer + Researcher", use_container_width=True, type="primary", help="Mode Paling Canggih"):
            st.session_state.mode = "designer"; st.rerun()
        st.info("Riset tren, Konsep Desain, dan Prototipe.")

# --- FUNGSI SIDEBAR PINTAR (PDF/JPG SUPPORT) ---
def render_common_sidebar():
    """Sidebar yang bisa membaca Gambar dan PDF."""
    with st.sidebar:
        st.header("Kontrol Sesi")
        if st.button("Kembali ke Hub", use_container_width=True, type="secondary"):
            return_to_hub()
        
        st.divider()
        
        st.header("🧠 Basis Pengetahuan")
        st.info("Unggah referensi agar AI meniru gaya Anda. Support: PDF, Gambar, Txt.")
        
        # [UPDATE] Menerima banyak format
        uploaded_file = st.file_uploader("Unggah File", type=["txt", "md", "pdf", "jpg", "png", "jpeg"])
        
        if uploaded_file is not None:
            file_type = uploaded_file.type
            
            # 1. JIKA GAMBAR (JPG/PNG)
            if "image" in file_type:
                try:
                    image = Image.open(uploaded_file)
                    st.session_state.kb_image = image
                    st.session_state.kb_text = "" # Reset teks jika ganti ke gambar
                    st.success("✅ Gambar referensi dimuat! AI bisa 'melihat' desain ini.")
                    st.image(image, caption="Referensi Aktif", use_column_width=True)
                except Exception as e:
                    st.error(f"Gagal memuat gambar: {e}")

            # 2. JIKA PDF
            elif "pdf" in file_type:
                try:
                    reader = PyPDF2.PdfReader(uploaded_file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    st.session_state.kb_text = text
                    st.session_state.kb_image = None # Reset gambar jika ganti ke PDF
                    st.success(f"✅ PDF dimuat! ({len(reader.pages)} halaman). AI sudah membacanya.")
                except Exception as e:
                    st.error(f"Gagal membaca PDF: {e}")

            # 3. JIKA TEXT/MD
            else:
                try:
                    string_data = uploaded_file.getvalue().decode("utf-8")
                    st.session_state.kb_text = string_data
                    st.session_state.kb_image = None
                    st.success("✅ Teks konteks dimuat!")
                except Exception as e:
                    st.error(f"Gagal membaca file: {e}")
        
        # Tombol Hapus
        if st.session_state.kb_text or st.session_state.kb_image:
            if st.button("Hapus Referensi", use_container_width=True):
                st.session_state.kb_text = ""
                st.session_state.kb_image = None
                st.rerun()

# --- ROUTER UTAMA ---
if st.session_state.mode is None:
    render_hub_selection()
elif st.session_state.mode in ["pro", "preview", "review", "designer"]:
    render_common_sidebar()
    if st.session_state.mode == "pro": run_pro_mode()
    elif st.session_state.mode == "preview": run_preview_mode()
    elif st.session_state.mode == "review": run_review_mode()
    elif st.session_state.mode == "designer": run_designer_mode()
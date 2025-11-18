# utils.py
# [PERBAIKAN FINAL]: Support Multimodal (Gambar + Teks) di loop utama

import streamlit as st
import json
import google.generativeai as genai

def send_function_response(chat_session, tool_name, result):
    function_response_content = {
        "parts": [{"function_response": {"name": tool_name, "response": {"result": result}}}]
    }
    return chat_session.send_message(function_response_content)

def get_function_call(response):
    if not response.candidates or not response.candidates[0].content.parts: return None
    for part in response.candidates[0].content.parts:
        if part.function_call: return part.function_call
    return None

def run_chat_loop_with_tools(model, chat_session, messages_key, display_func, spinner_text):
    from tools import search_google 

    for i, message in enumerate(st.session_state[messages_key]):
        role = "assistant" if message["role"] == "model" else "user"
        with st.chat_message(role):
            # Jika konten adalah list (multimodal), tampilkan teksnya saja di riwayat agar rapi
            content = message["content"]
            if isinstance(content, list):
                st.markdown(content[0]) # Asumsi elemen pertama adalah teks prompt
                if len(content) > 1:
                    st.caption("➕ [Gambar Referensi Disertakan]")
            else:
                if role == "user": st.markdown(content)
                else: display_func(content, f"chat_{i}")

    if prompt := st.chat_input("Jelaskan kebutuhan Anda..."):
        
        # Siapkan pesan pengguna (Bisa Teks saja, atau Teks + Gambar)
        user_message_content = prompt
        api_message_payload = prompt

        # --- LOGIKA MULTIMODAL (PDF & GAMBAR) ---
        
        # 1. Cek apakah ada Teks Konteks (dari PDF/TXT)
        if "kb_text" in st.session_state and st.session_state.kb_text:
            st.toast("📄 Menggunakan konteks dari PDF/Dokumen...")
            context_text = st.session_state.kb_text
            # Gabungkan ke prompt teks
            prompt_with_context = f"[KONTEKS DOKUMEN REFERENSI]:\n{context_text}\n\n[PERMINTAAN USER]:\n{prompt}"
            api_message_payload = prompt_with_context
            user_message_content = prompt # Di UI tetap tampilkan prompt asli yg pendek

        # 2. Cek apakah ada Gambar Konteks (JPG/PNG)
        if "kb_image" in st.session_state and st.session_state.kb_image:
            st.toast("🖼️ Menggunakan referensi Gambar...")
            # Payload menjadi LIST: [Teks, Gambar]
            api_message_payload = [prompt, st.session_state.kb_image]
            # Simpan ke session state sebagai list juga
            user_message_content = [prompt, "IMAGE_DATA"] 

        # --- AKHIR LOGIKA MULTIMODAL ---

        st.session_state[messages_key].append({"role": "user", "content": user_message_content})
        
        with st.chat_message("user"): 
            st.markdown(prompt)
            if "kb_image" in st.session_state and st.session_state.kb_image:
                st.image(st.session_state.kb_image, width=200)

        with st.chat_message("assistant"):
            with st.spinner(spinner_text):
                try:
                    # Kirim Payload (Teks atau Teks+Gambar)
                    response = chat_session.send_message(api_message_payload)
                    
                    function_call = get_function_call(response)
                    while function_call:
                        query = function_call.args['query']
                        st.info(f"🤖 Mildshift sedang meneliti: '{query}'...")
                        search_result = search_google(query)
                        response = send_function_response(chat_session, "search_google", search_result)
                        function_call = get_function_call(response)
                        
                    response_content = response.text.strip()
                    display_func(response_content, "new") 
                    st.session_state[messages_key].append({"role": "model", "content": response_content})

                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")
                    st.warning("Jika Anda mengirim gambar, pastikan prompt tidak terlalu rumit.")

def create_previewable_html(file_structure: list) -> str | None:
    html_content = ""; css_content = ""; js_content = ""
    for file_data in file_structure:
        if file_data["nama_file"].endswith(".html"): html_content = file_data["isi_kode"]
        elif file_data["nama_file"].endswith(".css"): css_content += file_data["isi_kode"] + "\n"
        elif file_data["nama_file"].endswith(".js"): js_content += file_data["isi_kode"] + "\n"
    if not html_content: return None
    if css_content: html_content = html_content.replace("</head>", f"<style>\n{css_content}\n</style>\n</head>", 1)
    if js_content: html_content = html_content.replace("</body>", f"<script>\n{js_content}\n</script>\n</body>", 1)
    return html_content
import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

from services.chatbot_engine import get_response

# Check for API key
api_key = os.getenv("OPENAI_API_KEY")
api_key_missing = not api_key

# Sidebar for manual API Key input if not found in .env
if api_key_missing:
    st.sidebar.subheader("🔑 OpenAI API Configuration")
    user_provided_key = st.sidebar.text_input("Enter your OpenAI API Key:", type="password", placeholder="sk-...")
    if user_provided_key:
        os.environ["OPENAI_API_KEY"] = user_provided_key
        api_key_missing = False
        st.sidebar.success("API Key applied for this session!")
    else:
        st.sidebar.info("💡 Tip: You can also create a `.env` file in the root folder with `OPENAI_API_KEY=your_key` to avoid entering it every time.")


# ---- Language options shown in the dropdown ----
LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Arabic": "ar",
    "Chinese (Simplified)": "zh-CN",
    "Japanese": "ja",
    "Russian": "ru",
    "Portuguese": "pt",
}

st.set_page_config(page_title="Multilingual AI Chatbot", page_icon="🌍")
st.title("🌍 Multilingual AI Chatbot")
st.caption("Type in ANY language — I'll understand. Then pick the language you want my reply in.")

# ----Session state setup 
if "history" not in st.session_state:
    st.session_state.history=[]
if "messages" not in st.session_state:
    st.session_state.messages=[]   #for display the chat bubble

# --language translator 
selected_language_name = st.selectbox(
    "Select the language you want my reply in:",
    options=list(LANGUAGES.keys()),
    index=0
)
output_lang_code = LANGUAGES[selected_language_name]


#display existing chat---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


#-----Chat input ======

if api_key_missing:
    st.info("👈 Please enter your OpenAI API Key in the sidebar to begin chatting.")
else:
    user_input = st.chat_input("Type your message in any language....")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.spinner("Thinking..."):
            try:
                result = get_response(
                    history=st.session_state.history,
                    user_message=user_input,
                    output_lang_code=output_lang_code
                )
                st.session_state.history = result["history"]
                reply = result["reply"]
                detected = result["input_detected_language"]

                with st.chat_message("assistant"):
                    st.markdown(reply)
                    st.caption(f"🗣️ Detected input language: `{detected}` → Replied in: `{selected_language_name}`")

                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"An error occurred: {e}")





import streamlit as st
from chatbot.chain import build_chain

st.set_page_config(page_title="AI Chatbot with Memory", page_icon="🧠")
st.title("🧠 AI Chatbot with Memory")

# Sidebar: pick provider once per session
provider = st.sidebar.selectbox("LLM Provider", ["groq", "openai"])

# IMPORTANT: Streamlit reruns the whole script on every interaction.
# We must store the chain (and its memory) in session_state so it survives reruns.
if "chain" not in st.session_state or st.session_state.get("provider") != provider:
    st.session_state.chain = build_chain(provider=provider)
    st.session_state.provider = provider
    st.session_state.messages = []

# Render past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("Say something...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chain.predict(input=user_input)
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# Debug helper: see raw memory buffer
with st.sidebar.expander("🔍 Raw memory buffer"):
    st.text(st.session_state.chain.memory.buffer)

    
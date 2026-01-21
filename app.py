
import streamlit as st
from backend import rag_with_history

# -----------------------------------------------------------------------
# Page Config
# -----------------------------------------------------------------------

st.set_page_config(
    page_title="Rust Blockchain Developer Chatbot",
    page_icon="🤖",
    layout="wide"
)

# -----------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------

st.markdown(
    "<h1 style='text-align:center;'>🤖 Rust Blockchain Developer Chatbot</h1>"
    "<p style='text-align:center; font-size:16px;'>"
    "Ask questions about <b>Rust</b>, <b>CosmWasm</b>, "
    "<b>Cosmos SDK</b>, and <b>Blockchain architecture</b>."
    "</p>",
    unsafe_allow_html=True
)

# -----------------------------------------------------------------------
# Session State
# -----------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------------------------------------------------
# Render existing chat history FIRST
# -----------------------------------------------------------------------

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            st.container(height=350).markdown(msg["content"])
        else:
            st.markdown(msg["content"])

# -----------------------------------------------------------------------
# Chat Input
# -----------------------------------------------------------------------

user_input = st.chat_input("Type your question here...")

if user_input:
    # 1️⃣ Render user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2️⃣ Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # 3️⃣ Call backend
    response = rag_with_history.invoke(
        {"input": user_input},
        config={"configurable": {"session_id": "streamlit-session"}}
    )

    # 4️⃣ Render assistant message
    with st.chat_message("assistant"):
        st.container(height=350).markdown(response["answer"])

    # 5️⃣ Save assistant message
    st.session_state.messages.append({
        "role": "assistant",
        "content": response["answer"]
    })

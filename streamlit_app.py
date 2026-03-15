import json
import logging
import os

import requests
import streamlit as st

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("chatbot-ui")

DEFAULT_API_BASE = (
    os.getenv("HOST_API") or os.getenv("HOSTA_API") or "http://localhost:8000"
)

st.set_page_config(page_title="Chatbot", page_icon="💬", layout="wide")
st.title("💬 Chatbot")
st.caption("OpenAI-powered chatbot with conversation history")

if "last_error" not in st.session_state:
    st.session_state.last_error = ""
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

with st.sidebar:
    st.header("API Controls")
    api_base = st.text_input("API Base URL", value=DEFAULT_API_BASE)
    timeout_sec = st.slider("Timeout (seconds)", min_value=1, max_value=60, value=30)

    st.subheader("Health")
    health_button = st.button("Check /api/health")

    if health_button:
        health_url = f"{api_base.rstrip('/')}/api/health"
        logger.info("Checking health endpoint: %s", health_url)
        try:
            res = requests.get(health_url, timeout=timeout_sec)
            if res.ok:
                st.success("API Health: OK")
                st.write(f"Status code: {res.status_code}")
                st.write(res.json())
                st.session_state.last_error = ""
            else:
                st.error("API Health: FAIL")
                st.write(f"Status code: {res.status_code}")
                st.write(res.text)
                st.session_state.last_error = res.text
        except Exception as exc:
            logger.exception("Health check failed")
            st.error("API Health: ERROR")
            st.session_state.last_error = str(exc)

    st.subheader("Error Indicator")
    if st.session_state.last_error:
        st.error("Error sign: ACTIVE")
        st.text_area(
            "Actual error message", value=st.session_state.last_error, height=180
        )
    else:
        st.success("Error sign: CLEAR")

    if st.button("Clear Conversation"):
        st.session_state.conversation_history = []
        st.session_state.last_error = ""
        st.rerun()

st.subheader("Conversation")
st.divider()

# Display conversation history
for msg in st.session_state.conversation_history:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])
    else:
        with st.chat_message("assistant"):
            st.write(msg["content"])

st.divider()

# Input area
user_input = st.chat_input("Type your message here...")

if user_input:
    logger.info("Calling /api/chat", extra={"message_length": len(user_input)})

    with st.chat_message("user"):
        st.write(user_input)

    # Prepare payload
    payload = {
        "message": user_input,
        "conversation_history": st.session_state.conversation_history,
    }

    try:
        resp = requests.post(
            f"{api_base.rstrip('/')}/api/chat",
            json=payload,
            timeout=timeout_sec,
        )

        if resp.ok:
            response_data = resp.json()
            reply = response_data.get("reply", "No reply received")
            st.session_state.conversation_history = response_data.get(
                "conversation_history", []
            )
            st.session_state.last_error = ""

            with st.chat_message("assistant"):
                st.write(reply)

            logger.info(
                "Chat response received",
                extra={"reply_length": len(reply)},
            )
        else:
            error_msg = resp.text
            st.session_state.last_error = error_msg
            st.error(f"API Error {resp.status_code}: {error_msg}")
            logger.error("Chat API returned error", extra={"status": resp.status_code})

    except Exception as exc:
        logger.exception("Chat API call failed")
        st.session_state.last_error = str(exc)
        st.error(f"Connection error: {str(exc)}")

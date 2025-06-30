import streamlit as st
import os
import sys

# Set up system path to import from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.query_handler import handle_query  # Your RAG handler

# --- Page Configuration ---
st.set_page_config(
    page_title="🤖 Company RAG Chatbot",
    page_icon="📄",
    layout="centered"
)

# --- CSS Styling ---
st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: 'Segoe UI', sans-serif;
        }
        .main-title {
            font-size: 2.5rem;
            font-weight: bold;
            text-align: center;
            color: #4A90E2;
            margin-bottom: 5px;
        }
        .subtitle {
            text-align: center;
            font-size: 1.1rem;
            color: #6c757d;
            margin-bottom: 20px;
        }
        .user-msg, .bot-msg {
            padding: 1rem;
            margin-bottom: 1rem;
            border-radius: 12px;
            max-width: 95%;
            word-wrap: break-word;
            font-size: 1rem;
        }
        .user-msg {
            background-color: #e1f5fe;
            align-self: flex-end;
            text-align: right;
        }
        .bot-msg {
            background-color: #f1f2f6;
            align-self: flex-start;
        }
        .chat-box {
            display: flex;
            flex-direction: column;
        }
        .input-container {
            margin-top: 30px;
            text-align: center;
        }
        .stTextInput > div > input {
            padding: 14px;
            border-radius: 10px;
            font-size: 1rem;
            width: 100%;
        }
        .stButton button {
            background-color: #4A90E2;
            color: white;
            font-size: 1rem;
            border-radius: 8px;
            padding: 10px 30px;
            margin-top: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Title & Subtitle ---
st.markdown('<div class="main-title">📄 Company RAG Chatbot</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ask about policies, processes, and internal documents. Powered by AI.</div>', unsafe_allow_html=True)

# --- Session State to Store Chat History ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Chat Display Section ---
chat_container = st.container()
with chat_container:
    for entry in st.session_state.chat_history:
        role, message = entry
        class_name = "user-msg" if role == "user" else "bot-msg"
        st.markdown(f'<div class="chat-box"><div class="{class_name}">{message}</div></div>', unsafe_allow_html=True)

# --- Input Section ---
with st.form("query_form", clear_on_submit=True):
    user_input = st.text_input("💬 Type your question below:", placeholder="e.g., What is the reimbursement policy?")
    submitted = st.form_submit_button("Ask")

if submitted and user_input.strip():
    st.session_state.chat_history.append(("user", user_input))
    with st.spinner("🤖 Thinking..."):
        try:
            response = handle_query(user_input)
        except Exception as e:
            response = f"❌ An error occurred: {str(e)}"
    st.session_state.chat_history.append(("bot", response))
    st.rerun()

import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

st.set_page_config(page_title="Abhay's AI")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)


st.title("Abhay's AI")


client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ---------- PASSWORD PROTECTION ----------

passwords = os.getenv("APP_PASSWORDS", "").split(",")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    pwd = st.text_input("Enter Password", type="password")

    if pwd:
        if pwd in passwords:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Wrong Password")

    st.stop()


# ---------- MESSAGE LIMIT ----------

if "msg_count" not in st.session_state:
    st.session_state.msg_count = 0

if st.session_state.msg_count >= 5:
    st.error("Message limit reached (5 per session).")
    st.stop()

# ---------- CHAT STORAGE ----------

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------- USER INPUT ----------

if prompt := st.chat_input("Ask anything..."):

    st.session_state.msg_count += 1

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=st.session_state.messages,
            temperature=0.7,
            max_tokens=300
        )

        reply = response.choices[0].message.content
        st.markdown(reply)

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

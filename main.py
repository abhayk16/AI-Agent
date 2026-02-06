import os
import streamlit as st
from dotenv import load_dotenv
import anthropic

load_dotenv()

st.set_page_config(page_title="Claude Chat", page_icon="🤖")

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

st.title("Claude Chat")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=800,
            messages=st.session_state.messages
        )

        reply = response.content[0].text
        st.markdown(reply)

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

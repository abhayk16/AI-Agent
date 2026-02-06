import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(page_title="Abhay's AI", page_icon="🤖")

st.title("Abhay's AI")

# Initialize Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Ask anything..."):
    # Store user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
   # Free Groq model
            messages=st.session_state.messages,
            temperature=0.7
        )

        reply = response.choices[0].message.content
        st.markdown(reply)

    # Store assistant reply
    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })

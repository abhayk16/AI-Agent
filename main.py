from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Setup Groq and read secret passwords from .env
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
VALID_PASSWORDS = os.getenv("APP_PASSWORDS", "").split(",")

# Storage for session history and message counts
sessions = {}

class ChatRequest(BaseModel):
    message: str
    password: str
    session_id: str

# 1. VERIFY ENDPOINT: Checks password without exposing the full list
@app.post("/api/verify")
async def verify_password(data: dict = Body(...)):
    password = data.get("password")
    if password in VALID_PASSWORDS:
        return {"status": "ok"}
    # If password is wrong, send 401 Unauthorized
    raise HTTPException(status_code=401, detail="Invalid Password")

# 2. CHAT ENDPOINT: Handles the AI logic
@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    # Double-check password for every message sent
    if req.password not in VALID_PASSWORDS:
        raise HTTPException(status_code=401, detail="Wrong password")

    # Initialize session if it doesn't exist
    if req.session_id not in sessions:
        sessions[req.session_id] = {"count": 0, "history": []}
    
    user_data = sessions[req.session_id]
    
    # Check 5-message limit
    if user_data["count"] >= 5:
        raise HTTPException(status_code=403, detail="Limit reached")

    # Add user message to history
    user_data["history"].append({"role": "user", "content": req.message})
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=user_data["history"],
            max_tokens=300
        )
        reply = completion.choices[0].message.content
        
        # Update history and count
        user_data["count"] += 1
        user_data["history"].append({"role": "assistant", "content": reply})
        
        return {"reply": reply, "count": user_data["count"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3. STATIC MOUNT: Tells FastAPI to show your index.html
app.mount("/", StaticFiles(directory="static", html=True), name="static")
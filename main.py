from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
VALID_PASSWORDS = os.getenv("APP_PASSWORDS", "").split(",")

sessions = {}

class ChatRequest(BaseModel):
    message: str
    password: str
    session_id: str

@app.post("/api/verify")
async def verify_password(data: dict = Body(...)):
    password = data.get("password")
    if password in VALID_PASSWORDS:
        return {"status": "ok"}
    raise HTTPException(status_code=401, detail="Invalid Password")

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    if req.password not in VALID_PASSWORDS:
        raise HTTPException(status_code=401, detail="Wrong password")

    if req.session_id not in sessions:
        # THE CORE IT RULES: Identity updated to InfraSupport
        system_prompt = {
            "role": "system",
            "content": (
                "You are InfraSupport, the official IT Support Assistant for our IT company. "
                "Your ONLY purpose is to help employees troubleshoot technical issues like VPN, "
                "Email, Software, and Hardware. "
                "STRICT RULES: "
                "1. Only answer IT and technical support related questions. "
                "2. If the user asks about non-IT topics (cooking, sports, general chat, etc.), "
                "politely refuse and say you are only authorized for InfraSupport. "
                "3. Be professional, concise, and helpful. "
                "4. If you cannot solve an issue, tell them to email helpdesk@company.com."
            )
        }
        sessions[req.session_id] = {"count": 0, "history": [system_prompt]}
    
    user_data = sessions[req.session_id]
    if user_data["count"] >= 5:
        raise HTTPException(status_code=403, detail="Limit reached")

    user_data["history"].append({"role": "user", "content": req.message})
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=user_data["history"],
            max_tokens=300
        )
        reply = completion.choices[0].message.content
        user_data["count"] += 1
        user_data["history"].append({"role": "assistant", "content": reply})
        return {"reply": reply, "count": user_data["count"]}
    except Exception:
        raise HTTPException(status_code=500, detail="InfraSupport Service Error")

app.mount("/", StaticFiles(directory="static", html=True), name="static")
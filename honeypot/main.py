from fastapi import FastAPI, Header, HTTPException
import re

app = FastAPI()
API_KEY = "innovexa-secret-key"

def detect_scam(message):
    keywords = ["blocked", "upi", "urgent", "verify", "otp", "account"]
    score = sum(1 for k in keywords if k in message.lower())
    return score >= 2, "UPI_FRAUD", min(0.5 + score * 0.1, 0.95)

def agent_reply():
    return "Sir mujhe thoda confuse ho raha hai, payment kaise karna hoga?"

def extract_data(text):
    return {
        "upi_ids": re.findall(r"[a-zA-Z0-9.\-_]+@[a-zA-Z]+", text),
        "bank_accounts": re.findall(r"\b\d{9,18}\b", text),
        "phishing_links": re.findall(r"https?://\S+", text)
    }

@app.post("/honeypot")
def honeypot(payload: dict, x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    message = payload.get("message", "")
    history = payload.get("history", [])

    is_scam, scam_type, confidence = detect_scam(message)

    if not is_scam:
        return {
            "is_scam": False,
            "confidence": confidence,
            "reason": "No scam patterns detected",
            "extracted_data": {},
            "conversation_log": history,
            "metrics": {"engagement_turns": len(history), "agent_active": False}
        }

    ai_msg = agent_reply()
    history.append({"sender": "scammer", "message": message})
    history.append({"sender": "ai_victim", "message": ai_msg})

    extracted = extract_data(message)

    return {
        "is_scam": True,
        "scam_type": scam_type,
        "confidence": confidence,
        "reason": "Multiple scam indicators detected",
        "extracted_data": extracted,
        "conversation_log": history,
        "metrics": {"engagement_turns": len(history), "agent_active": True}
    }

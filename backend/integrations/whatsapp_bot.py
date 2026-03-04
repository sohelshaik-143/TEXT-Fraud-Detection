"""
WhatsApp Bot via Twilio Sandbox (Redefined)
Supports:
- Standard "Body" messages
- Official Twilio Content SID (Templates)
- Real ID Analysis & Multi-signal replies
"""

import os
import logging
import asyncio
from fastapi import APIRouter, Request, Response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook/whatsapp", tags=["whatsapp"])

# ─── Config ────────────────────────────────────────────────
TWILIO_SID   = os.getenv("TWILIO_ACCOUNT_SID", "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM  = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
TWILIO_TO    = os.getenv("TWILIO_WHATSAPP_TO", "")

# Template Config
CONTENT_SID  = os.getenv("TWILIO_CONTENT_SID", "")  # e.g. 'HXb5b62575e6e4ff6129ad7c8efe1f983e'
USE_TEMPLATE = os.getenv("WHATSAPP_USE_TEMPLATE", "false").lower() == "true"

RISK_EMOJIS = {"Safe": "✅", "Suspicious": "⚠️", "High": "🔴", "Critical": "🚨"}

# ─── Send Logic ───────────────────────────────────────────

def send_twilio_whatsapp(to: str, body: str = None, variables: dict = None):
    """
    Send a WhatsApp message.
    If USE_TEMPLATE is true and CONTENT_SID is provided, it uses the Content API.
    Otherwise, it sends a standard body.
    """
    try:
        from twilio.rest import Client
        import json
        
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        to_formatted = to if to.startswith("whatsapp:") else f"whatsapp:{to}"
        
        if USE_TEMPLATE and CONTENT_SID:
            # Using Template (Content API)
            logger.info(f"Sending Template {CONTENT_SID} to {to_formatted}")
            msg = client.messages.create(
                from_=TWILIO_FROM,
                content_sid=CONTENT_SID,
                content_variables=json.dumps(variables) if variables else "{}",
                to=to_formatted
            )
        else:
            # Using Standard Body
            logger.info(f"Sending Body to {to_formatted}")
            msg = client.messages.create(
                from_=TWILIO_FROM,
                body=body,
                to=to_formatted
            )
            
        logger.info(f"Sent successfully. SID: {msg.sid}")
        return msg.sid
    except Exception as e:
        logger.error(f"WhatsApp Send Failure: {e}")
        return None

# ─── Analysis Reply ────────────────────────────────────────

async def process_and_reply(sender: str, text: str):
    """Analyze text and send response back to WhatsApp."""
    try:
        from backend.ai_modules.text_classifier import TextClassifier
        result = TextClassifier().classify(text).to_json()
        
        verdict = result.get("risk_level", "Unknown")
        score   = result.get("risk_score", 0)
        emoji   = RISK_EMOJIS.get(verdict, "❓")
        reasons = result.get("why_fraud", [])[:2]
        action  = result.get("recommended_action", ["Stay safe"])[0]
        
        # Build message string for Body mode
        reasons_str = "".join(f"\n- {r}" for r in reasons)
        body = (
            f"{emoji} *FRAUD VERDICT: {verdict.upper()}*\n"
            f"Risk Score: {score}/100\n"
            f"\n*Analysis Highlights:*{reasons_str}\n"
            f"\n⚡ *Action:* {action}\n"
            f"\n_Protected by FraudGuard AI 2.0_"
        )
        
        # Build variables for Template mode (1: Verdict, 2: Score, 3: Action)
        vars = {
            "1": verdict,
            "2": str(score),
            "3": action
        }
        
        # Run send in executor
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, send_twilio_whatsapp, sender, body, vars)
        
    except Exception as e:
        logger.error(f"Processing Error: {e}")
        error_msg = "❌ Technical error analyzing your message. Please try again."
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, send_twilio_whatsapp, sender, error_msg)

# ─── Webhook ──────────────────────────────────────────────

@router.post("/twilio")
async def handle_incoming(request: Request):
    """Twilio Webhook for incoming WhatsApp messages."""
    form = await request.form()
    sender = form.get("From")
    body = form.get("Body", "").strip()
    
    if not sender or not body:
        return Response(content="<Response></Response>", media_type="application/xml")
    
    logger.info(f"Received WhatsApp from {sender}: {body[:50]}...")
    
    # Process asynchronously to return webhook response immediately
    asyncio.create_task(process_and_reply(sender, body))
    
    return Response(content="<Response></Response>", media_type="application/xml")

# ─── Standalone Test ───────────────────────────────────────

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv("backend/.env")
    
    print("🚀 Running WhatsApp Bot Test Mode...")
    test_num = os.getenv("TWILIO_WHATSAPP_TO", "")
    if not test_num:
        test_num = input("Enter target number (+countrycode): ")
        
    sid = send_twilio_whatsapp(test_num, "🔍 This is a manual test of the FraudGuard AI Redefined system.")
    if sid:
        print(f"✅ Success! Message SID: {sid}")
    else:
        print("❌ Failed. Check your credentials in .env")

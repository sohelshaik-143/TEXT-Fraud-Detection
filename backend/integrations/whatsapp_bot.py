"""
WhatsApp Integration via Twilio WhatsApp Sandbox (Free)
OR Meta WhatsApp Cloud API (Free tier)

Setup Options:
----------------------
OPTION A - Twilio Sandbox (easiest for testing):
1. Go to: https://www.twilio.com/try-twilio (sign up free)
2. In console: Messaging -> Try it out -> Send a WhatsApp message
3. Follow sandbox join instructions (send "join <word>" to Twilio's number)
4. Copy Account SID, Auth Token, and WhatsApp sandbox number
5. Set in .env:
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxx  
   TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

OPTION B - Meta Cloud API (production):
1. Go to: https://developers.facebook.com/apps
2. Create App -> WhatsApp -> Get phone number
3. Set in .env:
   META_WHATSAPP_TOKEN=xxxxxxxxxxxxxxxx
   META_WHATSAPP_PHONE_ID=xxxxxxxxxxxxxxxx

Run webhook receiver:
   Set WHATSAPP_MODE=twilio or meta in .env
"""

import os
import logging
import asyncio
import httpx
from fastapi import APIRouter, Request, Response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook/whatsapp", tags=["whatsapp"])

# ----- Twilio Config -----
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
TWILIO_SMS_URL = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json"

# ----- Meta Cloud API Config -----
META_TOKEN = os.getenv("META_WHATSAPP_TOKEN", "")
META_PHONE_ID = os.getenv("META_WHATSAPP_PHONE_ID", "")
META_API_URL = f"https://graph.facebook.com/v19.0/{META_PHONE_ID}/messages"

WHATSAPP_MODE = os.getenv("WHATSAPP_MODE", "twilio")  # "twilio" or "meta"

RISK_EMOJIS = {"Safe": "✅", "Suspicious": "⚠️", "High": "🔴", "Critical": "🚨"}


# ─── Reply Helpers ──────────────────────────────────────────────

async def send_twilio_reply(to: str, body: str):
    """Send a WhatsApp reply using Twilio."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                TWILIO_SMS_URL,
                data={"From": TWILIO_FROM, "To": f"whatsapp:{to}", "Body": body},
                auth=(TWILIO_SID, TWILIO_TOKEN)
            )
            resp.raise_for_status()
    except Exception as e:
        logger.error(f"Twilio send error: {e}")


async def send_meta_reply(to: str, body: str):
    """Send a WhatsApp reply using Meta Cloud API."""
    try:
        headers = {"Authorization": f"Bearer {META_TOKEN}", "Content-Type": "application/json"}
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": body}
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(META_API_URL, headers=headers, json=payload)
            resp.raise_for_status()
    except Exception as e:
        logger.error(f"Meta WhatsApp send error: {e}")


async def send_whatsapp_reply(to: str, body: str):
    """Route to correct provider."""
    if WHATSAPP_MODE == "meta" and META_TOKEN:
        await send_meta_reply(to, body)
    elif TWILIO_SID and TWILIO_TOKEN:
        await send_twilio_reply(to, body)
    else:
        logger.warning("No WhatsApp credentials configured. Set TWILIO or META keys in .env")


# ─── Analysis ────────────────────────────────────────────────────

def build_verdict_message(text: str, result: dict) -> str:
    """Build a formatted WhatsApp verdict message."""
    verdict = result.get("risk_level", "Unknown")
    score = result.get("risk_score", 0)
    emoji = RISK_EMOJIS.get(verdict, "❓")
    fraud_types = ", ".join(result.get("fraud_type", ["None"])[:3])
    reasons = result.get("why_fraud", [])
    grammar = result.get("text_error_analysis", {})

    reasons_text = ""
    for i, r in enumerate(reasons[:3], 1):
        reasons_text += f"\n  {i}. {r}"

    grammar_score = grammar.get("score", 100)
    author = result.get("author_prediction", "Unknown")

    msg = (
        f"{emoji} *FRAUD ANALYSIS RESULT* {emoji}\n"
        f"{'─' * 28}\n"
        f"*Verdict:* {verdict}\n"
        f"*Risk Score:* {score}/100\n"
        f"*Fraud Type:* {fraud_types}\n"
        f"*Grammar Score:* {grammar_score}/100\n"
        f"*Author:* {author}\n"
    )

    if reasons:
        msg += f"\n*Why suspicious:*{reasons_text}\n"

    actions = result.get("recommended_action", [])
    if actions:
        msg += f"\n*Action:* {actions[0]}\n"

    msg += "\n_Powered by FraudGuard AI_"
    return msg


async def analyze_and_reply(sender: str, text: str):
    """Run fraud analysis and send WhatsApp reply."""
    try:
        from backend.ai_modules.text_classifier import TextClassifier
        from backend.integrations.api_orchestrator import run_full_analysis

        # Quick heuristic
        clf = TextClassifier()
        result = clf.classify(text).to_json()

        # Try real APIs
        try:
            api_report = await run_full_analysis(text)
            api_score = api_report.get("combined_risk_score", 0)
            if api_score > 0:
                blended = int(result["risk_score"] * 0.4 + api_score * 0.6)
                result["risk_score"] = blended
        except Exception:
            pass

        msg = build_verdict_message(text, result)
        await send_whatsapp_reply(sender, msg)

    except Exception as e:
        logger.error(f"WhatsApp analysis error: {e}")
        await send_whatsapp_reply(
            sender,
            "❌ Analysis failed. Please try again or visit our web app."
        )


# ─── Twilio Webhook ─────────────────────────────────────────────

@router.post("/twilio")
async def twilio_webhook(request: Request):
    """Twilio WhatsApp incoming message webhook."""
    form = await request.form()
    sender = str(form.get("From", "")).replace("whatsapp:", "")
    body = str(form.get("Body", "")).strip()

    if not body:
        return Response(content="<Response></Response>", media_type="application/xml")

    if body.lower() in ("/start", "hi", "hello", "help"):
        intro = (
            "👋 *Welcome to FraudGuard!*\n\n"
            "Send me any suspicious SMS, message or text and I will analyze it for:\n"
            "• Scam & Spam Detection\n"
            "• Phishing URLs\n"
            "• Grammar Forensics\n"
            "• AI-Generated Text Detection\n\n"
            "Just paste a suspicious message now! 🔍"
        )
        asyncio.create_task(send_whatsapp_reply(sender, intro))
    else:
        asyncio.create_task(analyze_and_reply(sender, body))

    return Response(content="<Response></Response>", media_type="application/xml")


# ─── Meta Cloud API Webhook ──────────────────────────────────────

META_VERIFY_TOKEN = os.getenv("META_WEBHOOK_VERIFY_TOKEN", "fraudguard_verify_2026")

@router.get("/meta")
async def meta_webhook_verify(request: Request):
    """Meta webhook verification (GET)."""
    params = dict(request.query_params)
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    if mode == "subscribe" and token == META_VERIFY_TOKEN:
        return Response(content=challenge or "OK")
    return Response(status_code=403)


@router.post("/meta")
async def meta_webhook(request: Request):
    """Meta Cloud API incoming message webhook."""
    try:
        data = await request.json()
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                messages = change.get("value", {}).get("messages", [])
                for msg in messages:
                    sender = msg.get("from", "")
                    text = msg.get("text", {}).get("body", "").strip()
                    if sender and text:
                        if text.lower() in ("hi", "hello", "start", "help"):
                            intro = (
                                "👋 *FraudGuard AI is ready!*\n\n"
                                "Send any suspicious message and I'll scan it instantly for scams, phishing & fraud."
                            )
                            asyncio.create_task(send_whatsapp_reply(sender, intro))
                        else:
                            asyncio.create_task(analyze_and_reply(sender, text))
    except Exception as e:
        logger.error(f"Meta webhook error: {e}")

    return {"status": "ok"}

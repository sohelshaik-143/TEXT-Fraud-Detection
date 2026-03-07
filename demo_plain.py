"""
WhatsApp Fraud Detection - DEMO (Plain Terminal Version)
Works in any Windows CMD / PowerShell terminal.

Run:
    python demo_plain.py
"""

import httpx
import asyncio
import time
import sys

BACKEND_URL = "http://localhost:8000"
WEBHOOK_URL = f"{BACKEND_URL}/whatsapp/webhook"

DEMO_MESSAGES = [
    {
        "label": "SCAM: Lottery Fraud",
        "lang":  "English",
        "from":  "whatsapp:+919876543210",
        "body":  (
            "CONGRATULATIONS! You have been selected as the WINNER of Rs 50,00,000 "
            "in the National Lottery. To claim your prize, send your Aadhar, PAN, and "
            "bank account details to claim@nationallotteryindia.xyz IMMEDIATELY. "
            "Offer expires in 24 HOURS! Click: bit.ly/claim-now-lottery"
        ),
    },
    {
        "label": "SCAM: Bank Phishing",
        "lang":  "English",
        "from":  "whatsapp:+918765432109",
        "body":  (
            "URGENT: Your SBI account has been SUSPENDED due to suspicious activity. "
            "Verify your account NOW to avoid permanent closure. "
            "Login here: https://sbi-secure-verify.com/login and enter your Net Banking credentials. "
            "Failure to verify within 2 hours will result in account freeze."
        ),
    },
    {
        "label": "SCAM: Fake Job Offer",
        "lang":  "English",
        "from":  "whatsapp:+917654321098",
        "body":  (
            "Dear Candidate, You are selected for Work From Home job at Amazon India. "
            "Salary: Rs 45,000/month. No experience required. You need to pay Rs 2,500 "
            "registration fee via UPI to activate your account. Pay to: fraud_hr@ybl "
            "Then WhatsApp screenshot to get your joining kit."
        ),
    },
    {
        "label": "SCAM: OTP Theft",
        "lang":  "English",
        "from":  "whatsapp:+916543210987",
        "body":  (
            "Hi, I am calling from TRAI (Telecom Regulatory Authority). "
            "Your mobile number is going to be disconnected due to illegal activities. "
            "Press 1 to connect with our cyber crime department. "
            "Share the OTP you receive to verify your identity immediately."
        ),
    },
    {
        "label": "SCAM: Crypto Scam",
        "lang":  "English",
        "from":  "whatsapp:+919988776655",
        "body":  (
            "GUARANTEED 300% returns in 7 days! Our AI-powered crypto trading bot "
            "has made 10,000+ investors rich. Minimum investment Rs 5,000. "
            "Limited slots available! Join now: t.me/crypto_profit_bot_2025"
        ),
    },
    # ---- Regional Language Scams ----
    {
        "label": "SCAM: Hindi - Lottery Fraud",
        "lang":  "Hindi (Romanised)",
        "from":  "whatsapp:+919811223344",
        "body":  (
            "Badhai ho! Aapka number Lucky Draw mein select hua hai aur aap Rs 25,00,000 "
            "jeete hain. Yeh prize claim karne ke liye turant hamein apni bank details do "
            "aur ek baar otp share karo jo aapke registered number pe aayega. "
            "Offer sirf aaj valid hai — jaldi karo!"
        ),
    },
    {
        "label": "SCAM: Telugu - Bank OTP Phishing",
        "lang":  "Telugu (Romanised)",
        "from":  "whatsapp:+919922334455",
        "body":  (
            "Meeru SBI bank customer care nunchi matladadam. Mee account block avutundi "
            "suspicious transaction valla. Dini fix cheyyataniki otp cheppandi — "
            "oka roju lo mee bank details ivvandi, lekapothe mee account suspend avutundi. "
            "Ippudu response ivvakante mee account delete chestamu."
        ),
    },
    {
        "label": "SCAM: Tamil - Fake Job Offer",
        "lang":  "Tamil (Romanised)",
        "from":  "whatsapp:+919933445566",
        "body":  (
            "Vanakkam! Ungalukku Amazon India-la work from home velai varugiradhu. "
            "Maadam Rs 40,000 salary. Interview illai. Ungal bank details kudunga "
            "matrum registration kattanam Rs 1,500 UPI moolam — otp sollunga "
            "confirm pannunga. Kadaisi vaaippu, innum irandum per mattume!"
        ),
    },
    {
        "label": "SCAM: Marathi - UPI Collect Fraud",
        "lang":  "Marathi (Romanised)",
        "from":  "whatsapp:+919944556677",
        "body":  (
            "Namaskar! Tumcha PhonePe account verify karaycha aahe. Tumcha sim band honar "
            "aahe illegal activity mule. Lagech tumchi bank khate details sanga ani "
            "otp patha jo tumhala milel. Registration shulk Rs 999 UPI var bhara — "
            "inaam milale aahe Rs 10 lakh, turant claim kara!"
        ),
    },
    {
        "label": "SCAM: Bengali - Crypto Investment",
        "lang":  "Bengali (Romanised)",
        "from":  "whatsapp:+919955667788",
        "body":  (
            "Apnar jonno ekta special offer! Amader AI crypto trading bot-e invest korun "
            "minimum Rs 3,000 — 7 dine 200% return guaranteed. Apnar account verify "
            "korte otp pathiye din ebong bank details din. Tara tari korun — "
            "slot shesh hoye jacche! Amader Telegram group-e join korun: t.me/cryptowin_bd"
        ),
    },
    {
        "label": "SCAM: Kannada - TRAI Impersonation",
        "lang":  "Kannada (Romanised)",
        "from":  "whatsapp:+919966778899",
        "body":  (
            "Namaskara! Naavu TRAI department inda maatanaaduttiddeve. Nimma mobile number "
            "illegal activity karana sim close aaguttade. Idu tappisu haagu nimma khata "
            "block aaguttade avoid maadalu, otp heli mattu bank details kodi. "
            "Koodane maadi — kevalav 2 gante baki ide!"
        ),
    },
    {
        "label": "SAFE: Legitimate Message",
        "lang":  "English",
        "from":  "whatsapp:+911234567890",
        "body":  (
            "Hi! Just wanted to remind you about our team meeting tomorrow at 10 AM. "
            "We will be discussing the Q1 project updates. Please bring your progress report. "
            "See you there!"
        ),
    },
]


def line(char="=", n=60):
    print(char * n)


def show_message(idx, total, msg):
    print()
    line("-")
    lang_tag = f"  [{msg['lang']}]" if msg.get("lang") else ""
    print(f"  Message {idx}/{total}  |  {msg['label']}{lang_tag}")
    line("-")
    print(f"  From    : {msg['from']}")
    body = msg['body']
    preview = body[:100] + ("..." if len(body) > 100 else "")
    print(f"  Content : {preview}")
    print("  Analyzing...", end="", flush=True)



def show_result(data, elapsed):
    risk_level  = data.get("risk_level", "Unknown")
    risk_score  = data.get("risk_score", 0)
    is_fraud    = data.get("is_fraud", False)
    fraud_types = data.get("fraud_type", [])
    why_fraud   = data.get("why_fraud", [])
    signals     = data.get("api_signals") or []
    rec_action  = data.get("recommended_action", [])

    print(f"  done ({elapsed:.2f}s)")
    print()

    if risk_level == "Critical":
        verdict_str = f"*** CRITICAL FRAUD DETECTED *** | Score: {risk_score}/100"
    elif risk_level == "High":
        verdict_str = f"[HIGH RISK]  Likely Fraud       | Score: {risk_score}/100"
    elif risk_level == "Suspicious":
        verdict_str = f"[WARNING]    Suspicious          | Score: {risk_score}/100"
    else:
        verdict_str = f"[SAFE]       No Fraud Detected   | Score: {risk_score}/100"

    print(f"  VERDICT  : {verdict_str}")

    if fraud_types:
        print(f"  TYPE     : {', '.join(fraud_types)}")

    if why_fraud:
        print(f"  SIGNALS  :")
        for w in why_fraud[:4]:
            print(f"    >> {w}")

    if signals:
        print(f"  API DATA :")
        for sig in signals:
            flag = "[FRAUD]" if sig.get("flagged") else "[OK]   "
            print(f"    {flag}  {sig.get('api',''):<22}  {sig.get('verdict',''):<18}  {sig.get('detail','')}")

    if rec_action:
        print(f"  ACTION   : {rec_action[0]}")


async def check_backend():
    try:
        async with httpx.AsyncClient(timeout=5) as c:
            r = await c.get(f"{BACKEND_URL}/health")
            return r.status_code == 200
    except Exception:
        return False


async def analyze(client, msg):
    async def _webhook():
        try:
            await client.post(WEBHOOK_URL,
                data={"From": msg["from"], "Body": msg["body"]},
                timeout=20)
        except Exception:
            pass

    _, r = await asyncio.gather(
        _webhook(),
        client.post(f"{BACKEND_URL}/api/v1/analyze/text",
                    json={"text": msg["body"]}, timeout=25),
        return_exceptions=True
    )

    if isinstance(r, Exception):
        return {"error": str(r)}
    try:
        data = r.json()
        if "detail" in data and "is_fraud" not in data:
            return {"error": str(data["detail"])}
        return data
    except Exception as e:
        return {"error": str(e)}


async def main():
    print()
    line("=")
    print("  WhatsApp Fraud Detection - LIVE DEMO")
    print(f"  Backend  : {BACKEND_URL}")
    print(f"  Webhook  : {WEBHOOK_URL}")
    line("=")

    print("\n  Checking backend... ", end="", flush=True)
    alive = await check_backend()
    if not alive:
        print("OFFLINE")
        print("\n  ERROR: Backend is not running!")
        print("  Start it with:")
        print("    python -m uvicorn backend.main:app --reload --port 8000")
        sys.exit(1)
    print("ONLINE - Ready!\n")

    async with httpx.AsyncClient() as client:
        for i, msg in enumerate(DEMO_MESSAGES, 1):
            show_message(i, len(DEMO_MESSAGES), msg)
            t0 = time.time()
            result = await analyze(client, msg)
            elapsed = time.time() - t0

            if "error" not in result:
                show_result(result, elapsed)
            else:
                print(f"\n  ERROR: {result['error']}")

            if i < len(DEMO_MESSAGES):
                print()
                print("  Next message in 2 seconds...")
                await asyncio.sleep(2)

    print()
    line("=")
    print(f"  DEMO COMPLETE - All {len(DEMO_MESSAGES)} messages analyzed!")
    line("=")
    print(f"\n  API Docs  : {BACKEND_URL}/docs")
    print(f"  Webhook   : {WEBHOOK_URL}")
    print(f"  Frontend  : http://localhost:3000")
    print()


if __name__ == "__main__":
    asyncio.run(main())

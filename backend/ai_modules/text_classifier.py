"""
Advanced Text Fraud Classifier
Deep heuristic analysis engine covering all 15 scam signal types.
Provides:
- Accurate risk scoring based on multiple signals
- Detailed fraud reasons ("why_fraud")
- Real grammar & spelling forensics
- Author prediction (AI vs Human)
- UPI / regional fraud patterns
"""

import re
import time
from typing import List, Tuple

class ClassificationResult:
    def __init__(self, data: dict, processing_time: float):
        self.data = data
        self.processing_time = processing_time

    def to_json(self):
        return self.data

class RiskLevel:
    LOW    = "Safe"
    MEDIUM = "Suspicious"
    HIGH   = "High"
    CRITICAL = "Critical"

# ============================================================
# Signal Pattern Definitions
# Each entry: (pattern, weight, fraud_category, reason_string)
# ============================================================

SIGNALS = {
    "urgency": {
        "patterns": [
            r"\burgent(ly)?\b", r"\bact now\b", r"\bimmediate(ly)?\b", r"\bexpires?\s*(in|today|soon)\b",
            r"\blast chance\b", r"\blimited time\b", r"\bwithin\s*\d+\s*(hours?|minutes?|days?)\b",
            r"\bdeadline\b", r"\bresponse required\b", r"\bdo not delay\b", r"\btoday only\b",
            r"\btime.sensitive\b", r"\binstant action\b"
        ],
        "weight": 20,
        "category": "Urgency / Deadline Pressure",
        "reason": "Message creates artificial time pressure to prevent rational thinking"
    },
    "financial_lure": {
        "patterns": [
            r"\b(won|win|winner|winning)\b", r"\blotter(y|ies)\b", r"\bprize\b", r"\bcongratulations?\b",
            r"\bcash\s*(prize|reward|back)\b", r"\bfree\s*(money|gift|reward|iphone|laptop)\b",
            r"\b(₹|rs\.?|inr)\s*[\d,]+\b", r"\$\s*[\d,]+", r"\b\d+\s*(lakh|crore|million|billion)\b",
            r"\bguaranteed\s*(income|profit|returns?)\b", r"\bget\s*rich\b", r"\bdouble\s*your\s*(money|investment)\b",
            r"\bclaim\s*(your)?\s*(prize|reward|cash)\b", r"\bsend\s*money\b"
        ],
        "weight": 22,
        "category": "Financial Lure",
        "reason": "Message promises improbable financial reward to entice victims"
    },
    "impersonation": {
        "patterns": [
            r"\b(rbi|reserve\s*bank|sbi|hdfc|icici|axis|kotak|paytm|npci)\b",
            r"\b(google|microsoft|apple|amazon|facebook|meta|paypal|ebay)\b",
            r"\b(government|ministry|police|court|income\s*tax|it\s*department|irdai|sebi)\b",
            r"\b(official|verified|authorised|authorized)\b.*\b(account|rep|team|notice)\b",
            r"\brepresenting\b", r"\bon\s*behalf\s*of\b", r"\bceo\b|\bcfo\b|\bcto\b",
            r"\byour\s*(bank|provider|network|telecom)\b"
        ],
        "weight": 25,
        "category": "Impersonation / Brand Spoofing",
        "reason": "Message impersonates a trusted authority, brand or government body"
    },
    "credential_theft": {
        "patterns": [
            r"\b(otp|one.time\s*password)\b", r"\bpin\b", r"\bpassword\b", r"\bverif(y|ication)\s*(your)?\s*(account|identity|number)\b",
            r"\bsend\s*(us\s*)?(your\s*)?(otp|pin|cvv|card\s*number|account)\b",
            r"\bbank\s*(details?|account|number|info)\b",
            r"\bkyc\b", r"\bpan\s*(card)?\b", r"\baadhar\b", r"\bsocial\s*security\b",
            r"\bnever\s*share\b.*\b(otp|pin)\b", r"\benter\s*(your\s*)?(details?|credentials?)\b",
            r"\blink\s*(your|the)\s*(account|card)\b"
        ],
        "weight": 30,
        "category": "Credential Theft / OTP Request",
        "reason": "Message requests sensitive credentials, OTP or personal identifiers"
    },
    "suspicious_url": {
        "patterns": [
            r"https?://[^\s]+\.(tk|ml|ga|cf|xyz|top|click|info|biz|link)/",
            r"\bbit\.ly/\S+", r"\btinyurl\.com/\S+", r"\bshort\.link/\S+", r"\bt\.co/\S+",
            r"https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
            r"https?://[^\s]*(login|signin|verify|secure|account)[^\s]*(\.php|\.html)",
            r"\bclick\s*(here|this\s*link)\b", r"\bvisit\s*(this\s*)?(link|site|url)\b",
            r"\bdownload\s*(now|app|apk)\b", r"\.apk\b"
        ],
        "weight": 22,
        "category": "Suspicious URL / Link",
        "reason": "Message contains shortened, suspicious or phishing-style links"
    },
    "ai_generated_tone": {
        "patterns": [
            r"\bi\s*hope\s*this\s*(message|email|letter)\s*finds\s*you\s*well\b",
            r"\bplease\s*be\s*informed\s*that\b", r"\bkindly\s*(note|be\s*advised|revert)\b",
            r"\bdo\s*the\s*needful\b", r"\bwith\s*regards?\s*to\s*the\s*(above|matter)\b",
            r"\bon\s*a\s*priority\s*basis\b", r"\bat\s*the\s*earliest\s*(convenience|opportunity)?\b",
            r"\bplease\s*find\s*(attached|enclosed|herewith)\b"
        ],
        "weight": 12,
        "category": "AI-Generated Tone",
        "reason": "Message contains hyper-formal or robotic phrasing commonly produced by AI tools"
    },
    "social_engineering": {
        "patterns": [
            r"\btrust\s*(me|us)\b", r"\bi\s*(need|require)\s*your\s*(help|assistance|support)\b",
            r"\bstranded\b|\bstuck\b|\bemergency\b", r"\bplease\s*help\b",
            r"\bjust\s*(between\s*us|this\s*once|a\s*small\s*favour)\b",
            r"\bno\s*one\s*(else|can\s*know)\b", r"\bkeep\s*(this\s*)?(secret|confidential|between\s*us)\b",
            r"\bdon.t\s*tell\s*(anyone|your\s*(family|friends|bank))\b",
            r"\bcharity\b|\borphan\b|\bdying\b|\bterminal(ly\s*ill)?\b"
        ],
        "weight": 18,
        "category": "Social Engineering",
        "reason": "Message uses psychological manipulation like guilt, fear or appeals for secrecy"
    },
    "crypto_pitch": {
        "patterns": [
            r"\b(bitcoin|btc|ethereum|eth|usdt|tether|crypto|nft|defi|blockchain)\b",
            r"\b(invest(ment)?\s*(opportunity|plan|scheme))\b",
            r"\b\d{2,4}%\s*(daily|weekly|monthly|annual)?\s*(returns?|profit|roi)\b",
            r"\bpassive\s*income\b", r"\btrading\s*(bot|signal|tip)\b",
            r"\bcrypto\s*(wallet|exchange|mining|miner)\b",
            r"\brisk.free\b", r"\b100%\s*(safe|guaranteed)\b"
        ],
        "weight": 20,
        "category": "Crypto / Investment Scam",
        "reason": "Message promotes unrealistic crypto investment returns or trading schemes"
    },
    "threat_extortion": {
        "patterns": [
            r"\b(arrest|arrested|jail|police|legal\s*action|lawsuit|fir|case\s*filed)\b",
            r"\byour\s*(account|data|info)\s*(has\s*been\s*)?(compromised|hacked|leaked|exposed)\b",
            r"\bblackmail\b", r"\bsextortion\b", r"\bpay\s*(or|else|otherwise)\b",
            r"\bpay\s*(immediately|now|within)\b", r"\bwarrant\b",
            r"\bwe\s*have\s*(your|access\s*to\s*your)\b",
            r"\byour\s*(camera|microphone|device)\s*(has\s*been\s*)?(hacked|accessed)\b"
        ],
        "weight": 28,
        "category": "Threat / Extortion",
        "reason": "Message uses intimidation, threats of arrest or blackmail to coerce the victim"
    },
    "job_scam": {
        "patterns": [
            r"\b(work\s*from\s*home|wfh)\b", r"\bpart.time\s*(job|work|income|earning)\b",
            r"\bearn\s*(₹|rs\.?|\$|upto|up\s*to)?\s*[\d,]+\s*(per\s*(day|week|month))\b",
            r"\b(no\s*(experience|qualification)\s*required|freshers?\s*(welcome|apply))\b",
            r"\bregistration\s*(fee|charge|deposit)\b",
            r"\btask.based\s*(earning|income|job)\b",
            r"\bdata\s*entry\s*job\b", r"\btyping\s*job\b",
            r"\b(apply\s*now|limited\s*seats?)\b"
        ],
        "weight": 20,
        "category": "Job Scam",
        "reason": "Message promotes fake employment requiring upfront payment or personal data"
    },
    "spam_marketing": {
        "patterns": [
            r"\bunsubscribe\b", r"\byou\s*have\s*been\s*selected\b",
            r"\bspecial\s*(offer|deal|discount|deal)\b.*\b(today|limited|exclusive)\b",
            r"\b(buy\s*1\s*get\s*1|bogo)\b", r"\b(sale|off)\s*\d{1,3}%\b",
            r"\bno\s*cost\s*emi\b", r"\bexclusive\s*(member(ship)?|deal)\b",
            r"\bfree\s*(trial|shipping|delivery|gift)\b"
        ],
        "weight": 8,
        "category": "Spam Marketing",
        "reason": "Unsolicited commercial message with aggressive promotional language"
    },
    "regional_upi_fraud": {
        "patterns": [
            r"\b(upi|gpay|phonepe|paytm|bhim|neft|rtgs|imps)\b",
            r"\bsend\s*(money|amount|payment)\s*(to|via)\b",
            r"\bcollect\s*(payment|money|amount)\b", r"\bscanner\b|\bqr\s*code\b",
            r"\benter\s*(your\s*)?(upi|pin|mpin)\b",
            r"\brequest\s*(accepted|declined|pending)\b",
            r"\btransaction\s*(failed|reversed|pending)\b"
        ],
        "weight": 25,
        "category": "UPI / Payment Fraud",
        "reason": "Message exploits local payment systems (UPI, GPay, PhonePe) for fraud"
    },
    "romance_scam": {
        "patterns": [
            r"\bfalling\s*(in\s*love|for\s*you)\b", r"\bsoulmate\b", r"\blife\s*partner\b",
            r"\bmet\s*(you\s*)?(online|on\s*(tinder|bumble|facebook|instagram))\b",
            r"\bi\s*(love|miss|need)\s*you\b",
            r"\bsend\s*(me\s*)?(money|gift|card)\b.*\b(love|relationship|partner)\b",
            r"\bstranded\s*(abroad|overseas)\b",
            r"\bvisit\s*(me|you)\b.*\b(ticket|visa|flight)\b"
        ],
        "weight": 22,
        "category": "Romance Scam",
        "reason": "Message builds a fabricated romantic relationship to solicit money or data"
    },
    "tech_support_refund": {
        "patterns": [
            r"\b(tech\s*support|customer\s*care)\b.*\b(call|contact|number)\b",
            r"\brefund\s*(process(ing)?|initiated|amount)\b",
            r"\byour\s*(computer|device|pc|system)\s*(is\s*)?(infected|hacked|compromised|at\s*risk)\b",
            r"\bcall\s*(us\s*)?(immediately|now|toll.free)\b",
            r"\bremote\s*(access|desktop|control)\b",
            r"\binstall\s*(this\s*)?(app|software|tool)\b",
            r"\boverpayment\s*(refund|return)\b"
        ],
        "weight": 22,
        "category": "Tech Support / Refund Scam",
        "reason": "Message impersonates tech support or offers fake refunds to gain remote access"
    }
}

# Common scam phrases with weights
COMMON_SCAM_PHRASES = [
    (r"\bdo not share\b.*\bwith anyone\b", 10),
    (r"\bsecret\b.*\bcode\b", 15),
    (r"\bno questions\b", 8),
    (r"\byou.?ve been selected\b", 12),
    (r"\bconfidential\b.*\binformation\b", 10),
]

# Grammar/spelling indicators with weights
GRAMMAR_CHECKS = [
    # deliberate obfuscation
    (r"[A-Z]{4,}",                           10, "Excessive capitals (shouting tactic)"),
    (r"!{2,}",                                8,  "Multiple exclamation marks"),
    (r"\?\?+",                                6,  "Multiple question marks"),
    (r"\.{4,}",                               5,  "Excessive ellipsis"),
    # Known scam misspellings
    (r"\b(recieve|recieved|teh\b|acount|pasword|verfiy|beleive|beware|guarentee|neccesary)\b", 12, "Common scam misspelling"),
    (r"\b(loosing|looser|its\s+me|am\s+i)\b", 8, "Lose/loose or grammar confusion"),
    # AI/spam formal markers
    (r"\b(kindly|revert|do\s*the\s*needful)\b", 6, "Outdated bureaucratic phrasing"),
    (r"\b(dear\s+(sir|madam|customer|user|valued))\b", 5, "Generic impersonal salutation"),
    # Structural spam patterns
    (r"\$\s+\d|\d\s+\$",                      5,  "Incorrect currency spacing"),
    (r",{2,}",                                 4,  "Double comma punctuation"),
    (r"\s{2,}",                                3,  "Extra whitespace between words"),
    # Very short message with red flags
]

# Scam misspelling dictionary for typo detection
KNOWN_TYPOS = {
    "recieve": "receive", "recieved": "received", "teh": "the",
    "acount": "account", "pasword": "password", "verfiy": "verify",
    "beleive": "believe", "guarentee": "guarantee", "neccesary": "necessary",
    "occured": "occurred", "seperately": "separately", "accomodation": "accommodation",
    "adress": "address", "begining": "beginning", "harrased": "harassed",
}


def analyze_grammar(text: str):
    """
    Multi-layer grammar analysis:
    1. Heuristic regex patterns (fast, catches scam-specific patterns)
    2. TextBlob spell checking (catches misspellings)
    3. Sentence structure check (run-ons, no punctuation)
    Returns: (typos, grammar_issues, score 0-100)
    """
    issues = []
    typos = []
    deductions = 0

    # --- Layer 1: Regex heuristics ---
    for pattern, penalty, label in GRAMMAR_CHECKS:
        if re.search(pattern, text, re.IGNORECASE):
            issues.append(label)
            deductions += penalty

    # --- Layer 2: Known typo dictionary ---
    words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    for w in words:
        if w in KNOWN_TYPOS:
            typos.append(f'"{w}" should be "{KNOWN_TYPOS[w]}"')
            deductions += 8

    # --- Layer 3: TextBlob spell check (if available) ---
    try:
        from textblob import TextBlob
        blob = TextBlob(text)
        corrections = blob.correct()
        corrected_words = str(corrections).split()
        original_words = text.split()
        changed = 0
        for orig, corr in zip(original_words[:30], corrected_words[:30]):
            if orig.lower() != corr.lower() and orig.isalpha() and corr.isalpha():
                if orig.lower() not in KNOWN_TYPOS:  # avoid double-counting
                    typos.append(f'Possible misspelling: "{orig}"')
                    changed += 1
        deductions += changed * 6
    except Exception:
        pass  # textblob not available, skip

    # --- Layer 4: Sentence structure ---
    text_stripped = text.strip()
    sentences = re.split(r'[.!?]+', text_stripped)
    sentences = [s.strip() for s in sentences if s.strip()]

    if sentences:
        avg_words = sum(len(s.split()) for s in sentences) / len(sentences)
        if avg_words > 35:
            issues.append("Run-on sentences (avg >35 words)")
            deductions += 8
        if len(text_stripped) > 50 and not re.search(r'[.!?]', text_stripped):
            issues.append("No sentence-ending punctuation in long message")
            deductions += 6

    # No punctuation at all
    if len(text) > 30 and not re.search(r'[,;.!?]', text):
        issues.append("Missing punctuation throughout")
        deductions += 5

    score = max(0, 100 - deductions)
    return typos[:5], issues[:5], score


def detect_author(text: str, signals: dict) -> str:
    """Predict whether message is AI-generated or human-typed."""
    ai_score = 0
    ai_patterns = [
        r"\bI hope this (message|email|letter) finds you well\b",
        r"\bKindly (note|be advised|revert)\b",
        r"\bPlease be informed\b",
        r"\bDo the needful\b",
        r"\bAt the earliest( convenience)?\b",
        r"\bWith regards? to\b",
        r"\bIt has come to (our|my) attention\b",
    ]
    for p in ai_patterns:
        if re.search(p, text, re.IGNORECASE):
            ai_score += 25

    if signals.get("ai_generated_tone"):
        ai_score += 30

    if ai_score >= 50:
        return "AI Generated"
    elif ai_score > 0:
        return "Unknown"
    return "Human Typed"


class TextClassifier:
    def __init__(self):
        pass

    def classify(self, text: str) -> ClassificationResult:
        start_time = time.time()
        text_lower = text.lower()

        total_score = 5  # baseline
        detected_signals = {}
        fraud_types = []
        why_fraud = []

        # ─── Run all signal checks ───────────────────────────────
        for signal_key, config in SIGNALS.items():
            matched = False
            matched_phrases = []
            for pattern in config["patterns"]:
                if re.search(pattern, text, re.IGNORECASE):
                    matched = True
                    matched_phrases.append(pattern)

            detected_signals[signal_key] = matched
            if matched:
                total_score += config["weight"]
                fraud_types.append(config["category"])
                why_fraud.append(config["reason"])

        # ─── Common scam boosters ────────────────────────────────
        for pattern, boost in COMMON_SCAM_PHRASES:
            if re.search(pattern, text, re.IGNORECASE):
                total_score += boost

        # ─── Cap score ──────────────────────────────────────────
        risk_score = min(total_score, 100)

        # ─── Determine risk level ───────────────────────────────
        if risk_score >= 75:
            risk_level = RiskLevel.CRITICAL
            is_fraud = True
        elif risk_score >= 55:
            risk_level = RiskLevel.HIGH
            is_fraud = True
        elif risk_score >= 30:
            risk_level = RiskLevel.MEDIUM
            is_fraud = False
        else:
            risk_level = RiskLevel.LOW
            is_fraud = False

        if not fraud_types:
            fraud_types = ["None"]
        if not why_fraud:
            why_fraud = ["No significant fraud patterns detected in the text"]

        # ─── Grammar analysis ───────────────────────────────────
        typos, grammar_issues, grammar_score = analyze_grammar(text)

        # ─── Author prediction ──────────────────────────────────
        author_prediction = detect_author(text, detected_signals)

        # ─── Recommended actions ────────────────────────────────
        if risk_score >= 75:
            actions = [
                "Do NOT click any links in this message",
                "Do NOT share OTPs, PINs or card details",
                "Report this message to CERT-In (cybercrime.gov.in)",
                "Block the sender immediately"
            ]
        elif risk_score >= 55:
            actions = [
                "Verify the sender's identity through official channels",
                "Do not share personal information",
                "Check the sender's phone number or email against official records"
            ]
        elif risk_score >= 30:
            actions = [
                "Proceed with caution",
                "Verify sender identity before responding"
            ]
        else:
            actions = ["Message appears safe. No action required."]

        # ─── Build URL link intelligence if URL found ───────────
        url_match = re.search(r'https?://\S+|bit\.ly/\S+|www\.\S+', text)
        link_intelligence = None
        if url_match:
            url = url_match.group()
            suspicious_tlds = [".tk", ".ml", ".ga", ".cf", ".xyz", ".top", ".click"]
            is_suspicious_tld = any(url.endswith(t) or "/" in url[url.rfind(t):] for t in suspicious_tlds)
            link_intelligence = {
                "domain_age_days": -1,
                "tld_risk": is_suspicious_tld,
                "brand_spoofing": detected_signals.get("impersonation", False),
                "google_presence": "Unknown",
                "reputation_summary": "Suspicious shortened link detected" if detected_signals.get("suspicious_url") else "URL detected — verify before clicking"
            }

        data = {
            "is_fraud": is_fraud,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "fraud_type": fraud_types[:5],  # cap for display
            "why_fraud": why_fraud[:5],      # cap for display
            "detected_signals": detected_signals,
            "link_intelligence": link_intelligence,
            "text_error_analysis": {
                "typos": typos,
                "grammar_issues": grammar_issues,
                "score": grammar_score
            },
            "author_prediction": author_prediction,
            "recommended_action": actions,
            "confidence": round(min(0.95, 0.5 + risk_score / 200), 2)
        }

        processing_time = time.time() - start_time
        return ClassificationResult(data, processing_time)

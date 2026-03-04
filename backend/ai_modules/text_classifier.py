"""
Advanced Text Fraud Classifier 2.0 (Redefined)
Analytic Engine with Trust-Scoring and Linguistic Forensic mapping.
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

# ─── FRAUD SIGNALS (NEGATIVE) ─────────────────────────────
SIGNALS = {
    "urgency": {
        "patterns": [r"\burgent(ly)?\b", r"\bact now\b", r"\bimmediate(ly)?\b", r"\bexpires?\b", r"\blast chance\b"],
        "weight": 20, "category": "Urgency", "reason": "Manipulative time pressure detected."
    },
    "financial_lure": {
        "patterns": [r"\b(won|win|winner|winning)\b", r"\bprize\b", r"\bcash\b", r"\bfree\s*(money|gift)\b"],
        "weight": 22, "category": "Financial Lure", "reason": "Promises improbable financial gain."
    },
    "impersonation": {
        "patterns": [r"\b(sbi|hdfc|icici|axis|rbi|npci)\b", r"\b(google|apple|amazon|meta)\b"],
        "weight": 25, "category": "Brand Spoofing", "reason": "Impersonates trusted brands or banks."
    },
    "credential_theft": {
        "patterns": [r"\b(otp|pin|password|cvv)\b", r"\bverif(y|ication)\b", r"\bkyc\b"],
        "weight": 30, "category": "Credential Theft", "reason": "Direct request for sensitive authenticators."
    },
    "suspicious_url": {
        "patterns": [r"\.tk\b", r"\.ml\b", r"\.xyz\b", r"bit\.ly", r"tinyurl"],
        "weight": 25, "category": "Phishing Link", "reason": "Deceptive or low-reputation URL detected."
    }
}

# ─── TRUST SIGNALS (POSITIVE - REDEFINED) ──────────────────
# These patterns REDUCE the risk score if present
TRUST_SIGNALS = [
    (r"\bvisit\s*our\s*(official\s*)?website\b", -15, "Official Website Reference"),
    (r"\bcontact\s*customer\s*support\s*at\b", -10, "Standard Support Channel"),
    (r"\bview\s*your\s*account\s*statement\b", -8, "Account Transparency"),
    (r"\bstandard\s*rates\s*apply\b", -5, "Regulatory Compliance Text"),
    (r"\bterms\s*and\s*conditions\s*apply\b", -5, "Legitimate Disclaimer"),
    (r"\bregistered\s*office\b", -10, "Corporate Disclosure"),
]

# ─── DEFENSE TIPS MAPPING ──────────────────────────────────
TIPS_MAP = {
    "Urgency": "Take a breath. Scammers use rush tactics. Verify via a known official app.",
    "Financial Lure": "If it sounds too good to be true, it is. Never pay 'customs' or 'processing' fees for prizes.",
    "Brand Spoofing": "Banks never ask for OTPs or login links via SMS. Call the number on the back of your card.",
    "Credential Theft": "NEVER share your OTP or PIN with anyone, including bank staff.",
    "Phishing Link": "Hover over links to see the real destination. Official sites rarely use URL shorteners."
}

def analyze_url_granular(text: str) -> dict:
    """Deep inspection of URLs for subdomain trickery."""
    url_match = re.search(r'https?://[^\s]+', text, re.IGNORECASE)
    if not url_match:
        return {}
    
    url = url_match.group().lower()
    domain_part = url.replace("https://", "").replace("http://", "").split("/")[0]
    
    # Subdomain check: e.g. "sbi-verification.xyz" or "sbi.com.verification.net"
    parts = domain_part.split(".")
    is_deceptive = False
    trusted_brands = ["sbi", "hdfc", "axis", "kotak", "icici", "amazon", "google", "paypal", "apple"]
    
    # Check if brand is in subdomain but not main domain
    if len(parts) > 2:
        main_domain = parts[-2]
        subdomains = ".".join(parts[:-2])
        for brand in trusted_brands:
            if brand in subdomains and brand != main_domain:
                is_deceptive = True
                break
                
    return {
        "domain": domain_part,
        "is_deceptive_subdomain": is_deceptive,
        "tld_risk": any(url.endswith(t) for t in [".tk", ".ml", ".ga", ".cf", ".xyz", ".top"])
    }

def analyze_grammar(text: str):
    """Refined grammar analyzer."""
    score = 100
    deductions = []
    
    if re.search(r"[A-Z]{5,}", text): 
        score -= 15; deductions.append("Excessive Uppercase")
    if re.search(r"!!+", text): 
        score -= 10; deductions.append("Aggressive Punctuation")
    
    # Simple spell check for common scams
    scam_words = {"recieve": "receive", "acount": "account", "pasword": "password", "verfiy": "verify"}
    found_typos = []
    for typo in scam_words:
        if typo in text.lower():
            score -= 12
            found_typos.append(f"{typo} (should be {scam_words[typo]})")
            
    return max(0, score), found_typos, deductions

class TextClassifier:
    def classify(self, text: str) -> ClassificationResult:
        start_time = time.time()
        
        base_score = 10
        raw_score = base_score
        detected_signals = {}
        why_fraud = []
        categories = set()
        
        # 1. Negative Signals
        for key, config in SIGNALS.items():
            hit = any(re.search(p, text, re.IGNORECASE) for p in config["patterns"])
            detected_signals[key] = hit
            if hit:
                raw_score += config["weight"]
                why_fraud.append(config["reason"])
                categories.add(config["category"])
                
        # 2. Positive Trust Signals (REDEFINED)
        trust_matched = []
        for pattern, weight, label in TRUST_SIGNALS:
            if re.search(pattern, text, re.IGNORECASE):
                raw_score += weight
                trust_matched.append(label)

        # 3. URL Granular Analysis
        url_info = analyze_url_granular(text)
        if url_info.get("is_deceptive_subdomain"):
            raw_score += 30
            why_fraud.append("Deceptive subdomain trickery detected (Brand spoofing in URL).")
            categories.add("Phishing Link")

        # 4. Final Scoring Logic
        risk_score = max(0, min(100, int(raw_score)))
        
        if risk_score >= 75: level = RiskLevel.CRITICAL
        elif risk_score >= 55: level = RiskLevel.HIGH
        elif risk_score >= 30: level = RiskLevel.MEDIUM
        else: level = RiskLevel.LOW

        # 5. Grammar & Author
        g_score, typos, g_issues = analyze_grammar(text)
        
        # Build Tips
        tips = [TIPS_MAP[cat] for cat in categories if cat in TIPS_MAP]
        if not tips: tips = ["Always verify unknown senders before engaging."]

        data = {
            "is_fraud": risk_score >= 55,
            "risk_score": risk_score,
            "risk_level": level,
            "fraud_type": list(categories) if categories else ["None"],
            "why_fraud": why_fraud if why_fraud else ["No significant fraud patterns."],
            "trust_indicators": trust_matched,
            "text_error_analysis": {"score": g_score, "typos": typos, "issues": g_issues},
            "author_prediction": "AI Generated" if "kindly" in text.lower() or "be advised" in text.lower() else "Human Typed",
            "recommended_action": tips[:3],
            "explanation": f"Linguistic analysis scored this message at {risk_score}% risk due to {', '.join(categories) if categories else 'clean results'}.",
            "confidence": 0.92 if risk_score > 80 or risk_score < 20 else 0.75,
            "detected_signals": detected_signals
        }
        
        return ClassificationResult(data, time.time() - start_time)

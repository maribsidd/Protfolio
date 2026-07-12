"""
Groq API integration layer for PrahariAI.

All calls are wrapped in try/except with graceful fallbacks so the demo
never hard-crashes on stage if the API key is missing or a model name
has changed upstream.
"""
import os
import json
import base64
from groq import Groq

TEXT_MODEL = "llama-3.3-70b-versatile"
# NOTE: Groq has renamed/deprecated vision-preview models before.
# If this model 404s, check https://console.groq.com/docs/models
# and swap the string below (as of early 2026 Groq's maintained vision
# model has generally been an updated "llama-4-scout" / "llama-4-maverick"
# vision-capable checkpoint â€” verify the exact current id before demo day).
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

_client = None


def get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY not set in environment")
        _client = Groq(api_key=api_key)
    return _client


SCAM_SYSTEM_PROMPT = """You are PrahariAI's Digital Arrest Scam Detection engine, trained on
patterns from Indian 'digital arrest' fraud calls (fake CBI/ED/Customs/Police officers, video-call
hostage-style scams, fake e-warrants, forced fund transfers).

Analyze the given call transcript excerpt and return ONLY valid JSON, no markdown fences, no preamble:
{
  "risk_score": <integer 0-100>,
  "verdict": "<one of: SAFE, SUSPICIOUS, LIKELY_SCAM, CONFIRMED_SCAM_PATTERN>",
  "red_flags": ["<short flag>", "..."],
  "reasoning": "<2-3 sentence plain-language explanation a non-technical citizen or officer can understand>"
}

Score using known digital-arrest / fraud-call markers: claims of law-enforcement authority without
verifiable ID, threats of immediate arrest, instructions to isolate the victim from family, demands to
stay on video call continuously, urgency to transfer money "for verification", references to fake
warrants/parcels/customs seizures, requests for OTP/bank details, discouraging the victim from
contacting real police. Absence of these markers should score low."""

COUNTERFEIT_SYSTEM_PROMPT = """You are PrahariAI's Currency Note Scanner. First identify the currency type shown in the
image, then respond appropriately. Return ONLY valid JSON, no markdown fences:
{
  "currency_type": "<one of: INR, non_INR, unclear>",
  "denomination_guess": "<e.g. Rs 500, Rs 200, USD 20, EUR 50, unknown>",
  "verdict": "<one of: GENUINE, SUSPICIOUS, LIKELY_COUNTERFEIT, NOT_APPLICABLE>",
  "confidence": <integer 0-100>,
  "flagged_features": ["<short feature note>", "..."],
  "reasoning": "<2-3 sentence explanation>"
}

RULES:
- If currency_type is "INR": examine known RBI security features (security thread, latent image,
  microprinting, see-through register, colour-shift ink, serial number font/alignment, Mahatma Gandhi
  watermark clarity) and give a real verdict of GENUINE, SUSPICIOUS, or LIKELY_COUNTERFEIT with
  supporting reasoning referencing the specific features observed.
- If currency_type is "non_INR" (any non-Indian currency: USD, EUR, GBP, etc.): this scanner is
  trained specifically on RBI security features and cannot reliably authenticate other currencies.
  Set verdict to "NOT_APPLICABLE". Do NOT claim it is fake or genuine. In reasoning, simply describe
  what currency/denomination you can identify and note that authentication for this currency is not
  yet supported — recommend the user check with a local bank for verification of non-Indian notes.
- If currency_type is "unclear" (image too blurry/unclear to identify): set verdict to
  "NOT_APPLICABLE" and lower confidence, and say so honestly in reasoning.
- Be conservative: never guess a fake/genuine verdict when you are not looking at Indian currency."""

CITIZEN_SYSTEM_PROMPT = """You are PrahariAI's Citizen Fraud Shield assistant. A citizen describes a
suspicious call, message, or payment request they received. Respond with ONLY valid JSON, no markdown
fences:
{
  "verdict": "<one of: LIKELY_SAFE, BE_CAUTIOUS, LIKELY_SCAM>",
  "reply": "<a warm, plain-language, non-alarmist explanation in 3-5 sentences, plus one concrete next
  action. If it looks like a scam, tell them: real police/CBI/ED never arrest over video call or demand
  money to 'verify' identity, and direct them to call 1930 (national cyber fraud helpline) or report at
  cybercrime.gov.in. Do not use jargon.>"
}"""


def _extract_json(raw_text):
    raw_text = raw_text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.lower().startswith("json"):
            raw_text = raw_text[4:]
    return json.loads(raw_text)


def analyze_scam_transcript(transcript):
    try:
        client = get_client()
        resp = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": SCAM_SYSTEM_PROMPT},
                {"role": "user", "content": transcript},
            ],
            temperature=0.2,
            max_tokens=600,
        )
        return _extract_json(resp.choices[0].message.content)
    except Exception as e:
        return {
            "risk_score": 0,
            "verdict": "ERROR",
            "red_flags": [],
            "reasoning": f"Detection engine unavailable: {str(e)}",
        }


def analyze_currency_image(image_bytes, mime_type="image/jpeg"):
    try:
        client = get_client()
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        resp = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {"role": "system", "content": COUNTERFEIT_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Examine this currency note image for authenticity."},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime_type};base64,{b64}"},
                        },
                    ],
                },
            ],
            temperature=0.2,
            max_tokens=500,
        )
        return _extract_json(resp.choices[0].message.content)
    except Exception as e:
        return {
            "denomination_guess": "unknown",
            "verdict": "ERROR",
            "confidence": 0,
            "flagged_features": [],
            "reasoning": f"Vision model unavailable: {str(e)}. Check VISION_MODEL in groq_service.py "
                         f"against https://console.groq.com/docs/models",
        }


def citizen_chat(user_message):
    try:
        client = get_client()
        resp = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": CITIZEN_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.4,
            max_tokens=500,
        )
        return _extract_json(resp.choices[0].message.content)
    except Exception as e:
        return {
            "verdict": "ERROR",
            "reply": f"Assistant unavailable right now: {str(e)}",
        }


def transcribe_audio(file_bytes, filename="recording.webm"):
    """Speech-to-text via Groq Whisper. Returns plain transcript text."""
    try:
        client = get_client()
        resp = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=(filename, file_bytes),
        )
        return {"transcript": resp.text, "error": None}
    except Exception as e:
        return {"transcript": "", "error": str(e)}


COMPLAINT_SYSTEM_PROMPT = """You are PrahariAI's Complaint Assist drafting engine. Given structured
incident details from a citizen, draft a clear, formal cybercrime complaint narrative in the format
expected by India's National Cyber Crime Reporting Portal (cybercrime.gov.in). Return ONLY valid JSON,
no markdown fences:
{
  "draft_text": "<a formal, factual, first-person complaint narrative, 150-250 words, covering: what
  happened, date/time, how contact was made, what was requested/taken, amount lost if any, and any
  identifying details of the perpetrator (phone, UPI ID, account) provided. Do not add legal
  conclusions or accusations beyond the facts given. End with a line stating the complainant requests
  the matter be registered and investigated.>"
}
This is a DRAFT to help the citizen file faster at the official portal — never claim this constitutes
an actual filed complaint."""


def draft_complaint(incident_type, incident_date, amount_lost, description, perpetrator_details):
    try:
        client = get_client()
        user_content = (
            f"Incident type: {incident_type}\n"
            f"Date: {incident_date or 'not specified'}\n"
            f"Amount lost: {amount_lost or 'not specified'}\n"
            f"Description: {description}\n"
            f"Perpetrator details: {perpetrator_details or 'not specified'}"
        )
        resp = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": COMPLAINT_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0.3,
            max_tokens=600,
        )
        return _extract_json(resp.choices[0].message.content)
    except Exception as e:
        return {"draft_text": f"Draft generation unavailable: {str(e)}"}


REPORT_AGENT_SYSTEM_PROMPT = """You are PrahariAI's Report Generation Agent, the final step in a
three-agent fraud-detection chain (Detection Agent -> Network Correlation Agent -> Report Agent). You
receive the Detection Agent's scam verdict and the Correlation Agent's matched fraud-network entries.
Synthesize a short preliminary incident report. Return ONLY valid JSON, no markdown fences:
{
  "incident_report": "<3-5 sentence preliminary report combining the scam verdict with any matched
  network entities, written for a law enforcement analyst, factual and concise, noting this is a
  preliminary AI-generated summary requiring human review before action>"
}"""


def generate_agent_report(scam_result, matched_nodes):
    try:
        client = get_client()
        user_content = (
            f"Detection Agent verdict: {scam_result.get('verdict')} "
            f"(risk score {scam_result.get('risk_score')}/100)\n"
            f"Red flags: {', '.join(scam_result.get('red_flags', [])) or 'none'}\n"
            f"Correlation Agent matched network entities: "
            f"{', '.join(matched_nodes) if matched_nodes else 'no existing matches found'}"
        )
        resp = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": REPORT_AGENT_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0.3,
            max_tokens=400,
        )
        return _extract_json(resp.choices[0].message.content)
    except Exception as e:
        return {"incident_report": f"Report agent unavailable: {str(e)}"}

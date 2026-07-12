import os
import json
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from models import db, ScamScan, CounterfeitScan, FraudNode, FraudEdge, Hotspot, ChatLog, NewsCard, ComplaintDraft
import groq_service
import seed_data
import re

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "instance", "prahariai.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # 8MB upload cap

db.init_app(app)


def init_db():
    os.makedirs(os.path.join(BASE_DIR, "instance"), exist_ok=True)
    db.create_all()
    seed_data.seed_all()


with app.app_context():
    init_db()


# ---------- Pages ----------

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/scam-detector")
def scam_detector_page():
    return render_template("scam_detector.html")


@app.route("/counterfeit-scanner")
def counterfeit_scanner_page():
    return render_template("counterfeit_scanner.html")


@app.route("/citizen-shield")
def citizen_shield_page():
    return render_template("citizen_shield.html")


@app.route("/voice-shield")
def voice_shield_page():
    return render_template("voice_shield.html")


@app.route("/complaint-assist")
def complaint_assist_page():
    return render_template("complaint_assist.html")


@app.route("/awareness")
def awareness_page():
    return render_template("awareness.html")


# ---------- API: Scam detection ----------

SIMULATED_CALL_SCRIPT = [
    "Officer: This is Inspector Rakesh Sharma from CBI Cyber Cell, Delhi headquarters.",
    "Officer: Your Aadhaar number has been linked to a parcel containing illegal substances, intercepted at Mumbai customs.",
    "Officer: This is a very serious matter. You are under digital arrest until this is resolved.",
    "Officer: Do not disconnect this video call or contact anyone, including your family, until we clear this.",
    "Officer: To verify you are not involved, you must transfer your savings to a secure RBI verification account immediately.",
    "Officer: If you contact local police or a lawyer, your case will escalate to non-bailable arrest.",
    "Officer: Share the OTP sent to your phone right now to complete identity verification.",
]


@app.route("/api/scam-detect", methods=["POST"])
def api_scam_detect():
    data = request.get_json(force=True)
    transcript = (data.get("transcript") or "").strip()
    if not transcript:
        return jsonify({"error": "transcript is required"}), 400

    result = groq_service.analyze_scam_transcript(transcript)

    scan = ScamScan(
        transcript=transcript,
        risk_score=result.get("risk_score", 0),
        verdict=result.get("verdict", "ERROR"),
        red_flags=json.dumps(result.get("red_flags", [])),
        reasoning=result.get("reasoning", ""),
    )
    db.session.add(scan)
    db.session.commit()

    return jsonify(result)


@app.route("/api/scam-demo-script")
def api_scam_demo_script():
    """Returns the canned line-by-line script used for the live simulated
    digital-arrest call demo on stage."""
    return jsonify({"lines": SIMULATED_CALL_SCRIPT})


# ---------- API: Voice Shield (Speech AI) ----------

@app.route("/api/voice-detect", methods=["POST"])
def api_voice_detect():
    if "audio" not in request.files:
        return jsonify({"error": "audio file is required"}), 400
    file = request.files["audio"]
    audio_bytes = file.read()

    transcription = groq_service.transcribe_audio(audio_bytes, filename=file.filename or "recording.webm")
    if transcription.get("error"):
        return jsonify({
            "transcript": "",
            "risk_score": 0,
            "verdict": "ERROR",
            "red_flags": [],
            "reasoning": f"Transcription failed: {transcription['error']}",
        })

    transcript = transcription["transcript"]
    result = groq_service.analyze_scam_transcript(transcript)
    result["transcript"] = transcript

    scan = ScamScan(
        transcript=transcript,
        risk_score=result.get("risk_score", 0),
        verdict=result.get("verdict", "ERROR"),
        red_flags=json.dumps(result.get("red_flags", [])),
        reasoning=result.get("reasoning", ""),
    )
    db.session.add(scan)
    db.session.commit()

    return jsonify(result)


# ---------- API: Agentic multi-source intelligence fusion ----------

def _extract_identifiers(text):
    phones = re.findall(r"(?:\+91[\s-]?)?\d{5}[\s-]?\d{5}|\d{10}", text)
    upi_ids = re.findall(r"[\w.\-]{2,}@[\w]{2,}", text)
    return phones, upi_ids


@app.route("/api/agent-fusion", methods=["POST"])
def api_agent_fusion():
    """Chains: Detection Agent -> Network Correlation Agent -> Report Agent."""
    data = request.get_json(force=True)
    transcript = (data.get("transcript") or "").strip()
    if not transcript:
        return jsonify({"error": "transcript is required"}), 400

    # Step 1: Detection Agent
    scam_result = groq_service.analyze_scam_transcript(transcript)

    # Step 2: Network Correlation Agent - naive identifier extraction + fuzzy match
    phones, upi_ids = _extract_identifiers(transcript)
    candidates = phones + upi_ids
    matched_nodes = []
    if candidates:
        all_nodes = FraudNode.query.all()
        for cand in candidates:
            digits = re.sub(r"\D", "", cand)
            for node in all_nodes:
                node_digits = re.sub(r"\D", "", node.label)
                if digits and node_digits and digits[-4:] == node_digits[-4:]:
                    matched_nodes.append(node.label)
                elif cand.lower() in node.label.lower():
                    matched_nodes.append(node.label)
    matched_nodes = list(dict.fromkeys(matched_nodes))  # dedupe, preserve order

    # Step 3: Report Agent
    report_result = groq_service.generate_agent_report(scam_result, matched_nodes)

    return jsonify({
        "detection": scam_result,
        "correlation": {"extracted_identifiers": candidates, "matched_nodes": matched_nodes},
        "report": report_result,
    })


# ---------- API: Complaint Assist ----------

@app.route("/api/complaint-draft", methods=["POST"])
def api_complaint_draft():
    data = request.get_json(force=True)
    incident_type = (data.get("incident_type") or "").strip()
    incident_date = (data.get("incident_date") or "").strip()
    amount_lost = (data.get("amount_lost") or "").strip()
    description = (data.get("description") or "").strip()
    perpetrator_details = (data.get("perpetrator_details") or "").strip()

    if not incident_type or not description:
        return jsonify({"error": "incident_type and description are required"}), 400

    result = groq_service.draft_complaint(
        incident_type, incident_date, amount_lost, description, perpetrator_details
    )

    draft = ComplaintDraft(
        incident_type=incident_type,
        incident_date=incident_date,
        amount_lost=amount_lost,
        description=description,
        perpetrator_details=perpetrator_details,
        draft_text=result.get("draft_text", ""),
    )
    db.session.add(draft)
    db.session.commit()

    return jsonify(result)


# ---------- API: Awareness news feed ----------

@app.route("/api/news-cards")
def api_news_cards():
    cards = NewsCard.query.order_by(NewsCard.id.desc()).all()
    return jsonify([
        {
            "headline": c.headline, "publisher": c.publisher, "summary": c.summary,
            "url": c.url, "category": c.category, "published_on": c.published_on,
        }
        for c in cards
    ])


# ---------- API: Counterfeit detection ----------

@app.route("/api/counterfeit-detect", methods=["POST"])
def api_counterfeit_detect():
    if "image" not in request.files:
        return jsonify({"error": "image file is required"}), 400
    file = request.files["image"]
    mime_type = file.mimetype or "image/jpeg"
    image_bytes = file.read()

    result = groq_service.analyze_currency_image(image_bytes, mime_type)

    scan = CounterfeitScan(
        denomination_guess=result.get("denomination_guess", "unknown"),
        verdict=result.get("verdict", "ERROR"),
        confidence=result.get("confidence", 0),
        flagged_features=json.dumps(result.get("flagged_features", [])),
        reasoning=result.get("reasoning", ""),
    )
    db.session.add(scan)
    db.session.commit()

    return jsonify(result)


# ---------- API: Citizen chat ----------

@app.route("/api/citizen-chat", methods=["POST"])
def api_citizen_chat():
    data = request.get_json(force=True)
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "message is required"}), 400

    result = groq_service.citizen_chat(message)

    db.session.add(ChatLog(
        user_message=message,
        verdict=result.get("verdict", "ERROR"),
        reply=result.get("reply", ""),
    ))
    db.session.commit()

    return jsonify(result)


# ---------- API: Dashboard data ----------

@app.route("/api/fraud-network")
def api_fraud_network():
    nodes = FraudNode.query.all()
    edges = FraudEdge.query.all()
    return jsonify({
        "nodes": [
            {"id": n.id, "label": n.label, "group": n.node_type, "risk": n.risk_level}
            for n in nodes
        ],
        "edges": [
            {"from": e.source_id, "to": e.target_id, "label": e.relation}
            for e in edges
        ],
    })


@app.route("/api/hotspots")
def api_hotspots():
    hotspots = Hotspot.query.all()
    return jsonify([
        {
            "city": h.city, "lat": h.lat, "lng": h.lng,
            "category": h.category, "severity": h.severity,
            "incidents_30d": h.incident_count_30d,
        }
        for h in hotspots
    ])


@app.route("/api/stats")
def api_stats():
    scam_scans = ScamScan.query.count()
    counterfeit_scans = CounterfeitScan.query.count()
    high_risk_scams = ScamScan.query.filter(ScamScan.risk_score >= 70).count()
    fraud_rings = FraudNode.query.filter_by(node_type="mule_account").count()
    total_incidents_30d = sum(h.incident_count_30d for h in Hotspot.query.all())
    complaint_drafts = ComplaintDraft.query.count()

    return jsonify({
        "scam_scans_total": scam_scans,
        "counterfeit_scans_total": counterfeit_scans,
        "high_risk_scams_flagged": high_risk_scams,
        "active_fraud_rings": fraud_rings,
        "total_incidents_30d": total_incidents_30d,
        "cities_monitored": Hotspot.query.count(),
        "complaint_drafts_total": complaint_drafts,
    })


@app.route("/api/recent-incidents")
def api_recent_incidents():
    scams = ScamScan.query.order_by(ScamScan.created_at.desc()).limit(5).all()
    counterfeits = CounterfeitScan.query.order_by(CounterfeitScan.created_at.desc()).limit(5).all()
    items = []
    for s in scams:
        items.append({
            "type": "Digital Arrest Scam",
            "verdict": s.verdict,
            "score": s.risk_score,
            "time": s.created_at.isoformat() if s.created_at else None,
        })
    for c in counterfeits:
        items.append({
            "type": "Counterfeit Note",
            "verdict": c.verdict,
            "score": c.confidence,
            "time": c.created_at.isoformat() if c.created_at else None,
        })
    items.sort(key=lambda x: x["time"] or "", reverse=True)
    return jsonify(items[:8])


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ScamScan(db.Model):
    __tablename__ = "scam_scans"
    id = db.Column(db.Integer, primary_key=True)
    transcript = db.Column(db.Text, nullable=False)
    risk_score = db.Column(db.Integer, nullable=False)
    verdict = db.Column(db.String(32), nullable=False)
    red_flags = db.Column(db.Text, nullable=False)  # JSON string list
    reasoning = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class CounterfeitScan(db.Model):
    __tablename__ = "counterfeit_scans"
    id = db.Column(db.Integer, primary_key=True)
    denomination_guess = db.Column(db.String(32))
    verdict = db.Column(db.String(32), nullable=False)
    confidence = db.Column(db.Integer, nullable=False)
    flagged_features = db.Column(db.Text, nullable=False)  # JSON string list
    reasoning = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class FraudNode(db.Model):
    __tablename__ = "fraud_nodes"
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(120), nullable=False)
    node_type = db.Column(db.String(32), nullable=False)  # phone, upi, device, victim, mule_account
    risk_level = db.Column(db.String(16), default="medium")  # low, medium, high


class FraudEdge(db.Model):
    __tablename__ = "fraud_edges"
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey("fraud_nodes.id"), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey("fraud_nodes.id"), nullable=False)
    relation = db.Column(db.String(64))  # e.g. "called", "transferred_to", "shared_device"


class Hotspot(db.Model):
    __tablename__ = "hotspots"
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(64), nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(32), nullable=False)  # digital_arrest, counterfeit, phishing, upi_fraud
    severity = db.Column(db.Integer, nullable=False)  # 1-100
    incident_count_30d = db.Column(db.Integer, nullable=False)


class ChatLog(db.Model):
    __tablename__ = "chat_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.Text, nullable=False)
    verdict = db.Column(db.String(32), nullable=False)
    reply = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class NewsCard(db.Model):
    __tablename__ = "news_cards"
    id = db.Column(db.Integer, primary_key=True)
    headline = db.Column(db.String(240), nullable=False)
    publisher = db.Column(db.String(120), nullable=False)
    summary = db.Column(db.Text, nullable=False)  # original paraphrase, not reproduced text
    url = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(32), nullable=False)  # digital_arrest, upi_fraud, counterfeit, policy
    published_on = db.Column(db.String(32), nullable=False)  # display string, e.g. "18 Apr 2026"


class ComplaintDraft(db.Model):
    __tablename__ = "complaint_drafts"
    id = db.Column(db.Integer, primary_key=True)
    incident_type = db.Column(db.String(64), nullable=False)
    incident_date = db.Column(db.String(32))
    amount_lost = db.Column(db.String(32))
    description = db.Column(db.Text, nullable=False)
    perpetrator_details = db.Column(db.Text)
    draft_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

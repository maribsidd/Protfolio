"""
Seeds the database with a realistic-looking (synthetic) fraud network and
hotspot dataset so the dashboard has something to show on first run.
This is demo/illustrative data, clearly not live law-enforcement data.
"""
from models import db, FraudNode, FraudEdge, Hotspot, NewsCard


def seed_news_cards():
    if NewsCard.query.first():
        return

    cards = [
        (
            "CBI cracks Rs 1.6 crore digital arrest scam, bank official among 3 held",
            "Deccan Herald",
            "A CBI investigation traced a digital-arrest scam targeting a senior citizen back to a "
            "network that included a bank insider, with raids across two states uncovering mule "
            "accounts and seized devices used to launder the stolen funds.",
            "https://www.deccanherald.com/india/cbi-busts-rs-16-crore-digital-arrest-scam-bank-official-among-3-held-3972761",
            "digital_arrest",
            "18 Apr 2026",
        ),
        (
            "India's digital wallets face a security stress test in 2026",
            "The420.in",
            "As UPI usage deepens into rural and first-time digital users, experts point to social "
            "engineering — not technical hacking — as the dominant force behind India's rising "
            "digital payment fraud numbers this year.",
            "https://the420.in/india-digital-wallets-upi-cyber-fraud-security-2026/",
            "upi_fraud",
            "4 Jan 2026",
        ),
        (
            "How to spot digital arrest and UPI scams before they cost you",
            "Business Standard",
            "A practical breakdown of how fraudsters impersonate police, CBI, and customs officials "
            "over video calls, plus the newer 'Boss Scam' and UPI collect-request tricks now being "
            "flagged by India's cyber crime coordination centre.",
            "https://www.business-standard.com/technology/tech-news/protect-yourself-cyber-scams-india-digital-arrest-investment-fraud-126062500136_1.html",
            "digital_arrest",
            "25 Jun 2026",
        ),
        (
            "India's fraud epidemic: the ₹22,500 crore toll of a record year",
            "ScamWatchHQ",
            "A full accounting of 2025's cyber fraud losses shows complaint volumes up sharply even as "
            "the amount stolen held flat — with digital arrest scams alone drawing over 30,000 formal "
            "complaints and enforcement agencies freezing more than a million mule accounts in response.",
            "https://scamwatchhq.com/india-scams-2026-digital-arrest-upi-fraud-epidemic/",
            "policy",
            "6 Jun 2026",
        ),
        (
            "UPI-linked frauds cross Rs 805 crore so far this financial year",
            "via PTI / Madhyamam",
            "Government data tabled in the Lok Sabha shows over 10 lakh UPI-related fraud incidents "
            "reported through November of this financial year, as authorities point to device binding "
            "and AI-based transaction monitoring as the main current lines of defence.",
            "https://madhyamamonline.com/india/upi-linked-frauds-amount-to-rs-805-crore-far-fy26-govt-1477281",
            "upi_fraud",
            "15 Dec 2025",
        ),
        (
            "Fake Rs 500 notes rise over 20% in FY26, RBI annual report shows",
            "Outlook Money",
            "The RBI's latest annual report shows counterfeit Rs 500 note detections climbing sharply "
            "even as overall currency in circulation grows, with commercial banks — not the RBI itself "
            "— catching the vast majority of fakes entering the banking system.",
            "https://www.outlookmoney.com/banking/fake-rs-500-notes-rise-over-20-per-cent-in-fy26-rbi-annual-report-shows",
            "counterfeit",
            "31 May 2026",
        ),
        (
            "Why India's trust in authority makes digital arrest scams so effective",
            "Lowy Institute",
            "A policy analysis argues that digital arrest scams succeed by exploiting a deep, "
            "well-documented public trust in state authority — a dynamic serious enough that "
            "commentators are now asking whether the same playbook could be turned toward "
            "disinformation, not just theft.",
            "https://www.lowyinstitute.org/the-interpreter/india-s-digital-arrest-scams",
            "policy",
            "30 Apr 2026",
        ),
        (
            "What the law actually says about digital arrest — and why it doesn't exist",
            "CourtKutchehry",
            "A legal explainer walks through exactly which IPC, IT Act, and BNS provisions apply to "
            "digital arrest scams, and stresses the one fact every citizen should know: there is no "
            "such thing as a 'digital arrest' anywhere in Indian law.",
            "https://www.courtkutchehry.com/pages/blog/digital-arrest-scam-laws-legal-remedies-india-2026/",
            "policy",
            "6 Jan 2026",
        ),
    ]
    for headline, publisher, summary, url, category, published_on in cards:
        db.session.add(NewsCard(
            headline=headline, publisher=publisher, summary=summary,
            url=url, category=category, published_on=published_on,
        ))
    db.session.commit()


def seed_fraud_network():
    if FraudNode.query.first():
        return

    nodes = [
        ("+91 98XXX-11029", "phone", "high"),
        ("+91 70XXX-88213", "phone", "high"),
        ("+91 63XXX-40071", "phone", "medium"),
        ("scammer.upi@fakebank", "upi", "high"),
        ("mule.acct.7734@paytm", "upi", "high"),
        ("relay.acct.2291@ybl", "upi", "medium"),
        ("Device IMEI ...4471", "device", "high"),
        ("Device IMEI ...9902", "device", "medium"),
        ("Victim Report #A1029", "victim", "low"),
        ("Victim Report #A1030", "victim", "low"),
        ("Victim Report #A1044", "victim", "low"),
        ("Shell Account SBI-XX412", "mule_account", "high"),
        ("Shell Account HDFC-XX998", "mule_account", "medium"),
    ]
    node_objs = []
    for label, ntype, risk in nodes:
        n = FraudNode(label=label, node_type=ntype, risk_level=risk)
        db.session.add(n)
        node_objs.append(n)
    db.session.flush()

    def idx(label):
        return next(n.id for n in node_objs if n.label == label)

    edges = [
        ("+91 98XXX-11029", "Victim Report #A1029", "called"),
        ("+91 98XXX-11029", "Victim Report #A1030", "called"),
        ("+91 98XXX-11029", "Device IMEI ...4471", "used_on"),
        ("+91 70XXX-88213", "Victim Report #A1044", "called"),
        ("+91 70XXX-88213", "Device IMEI ...4471", "used_on"),
        ("Victim Report #A1029", "scammer.upi@fakebank", "transferred_to"),
        ("Victim Report #A1030", "scammer.upi@fakebank", "transferred_to"),
        ("Victim Report #A1044", "mule.acct.7734@paytm", "transferred_to"),
        ("scammer.upi@fakebank", "Shell Account SBI-XX412", "routes_to"),
        ("mule.acct.7734@paytm", "Shell Account HDFC-XX998", "routes_to"),
        ("mule.acct.7734@paytm", "relay.acct.2291@ybl", "linked_device"),
        ("+91 63XXX-40071", "Device IMEI ...9902", "used_on"),
        ("relay.acct.2291@ybl", "Device IMEI ...9902", "linked_device"),
    ]
    for src, tgt, rel in edges:
        db.session.add(FraudEdge(source_id=idx(src), target_id=idx(tgt), relation=rel))

    db.session.commit()


def seed_hotspots():
    if Hotspot.query.first():
        return

    hotspots = [
        ("Delhi", 28.6139, 77.2090, "digital_arrest", 88, 214),
        ("Mumbai", 19.0760, 72.8777, "upi_fraud", 76, 189),
        ("Bengaluru", 12.9716, 77.5946, "phishing", 82, 233),
        ("Hyderabad", 17.3850, 78.4867, "digital_arrest", 71, 142),
        ("Kolkata", 22.5726, 88.3639, "counterfeit", 64, 98),
        ("Chennai", 13.0827, 80.2707, "upi_fraud", 58, 87),
        ("Pune", 18.5204, 73.8567, "phishing", 55, 76),
        ("Jaipur", 26.9124, 75.7873, "counterfeit", 61, 91),
        ("Lucknow", 26.8467, 80.9462, "digital_arrest", 69, 118),
        ("Ahmedabad", 23.0225, 72.5714, "upi_fraud", 52, 69),
        ("Patna", 25.5941, 85.1376, "counterfeit", 74, 103),
        ("Surat", 21.1702, 72.8311, "phishing", 47, 54),
    ]
    for city, lat, lng, cat, sev, count in hotspots:
        db.session.add(Hotspot(city=city, lat=lat, lng=lng, category=cat,
                                severity=sev, incident_count_30d=count))
    db.session.commit()


def seed_all():
    seed_fraud_network()
    seed_hotspots()
    seed_news_cards()

# Setup

1. `cd backend`
2. `python3 -m venv venv && source venv/bin/activate` (Windows: `venv\Scripts\activate`)
3. `pip install -r requirements.txt`
4. `cp .env.example .env` and add your `GROQ_API_KEY` (free tier at console.groq.com)
5. `python3 app.py`
6. Open `http://localhost:5000`

## Notes

- SQLite DB auto-creates at `backend/instance/prahariai.db` with seeded demo fraud-network and
  hotspot data on first run.
- `groq_service.py` line ~16: `VISION_MODEL`. If the counterfeit scanner returns a model-not-found
  error, check https://console.groq.com/docs/models for Groq's current vision-capable model id and
  swap it in — Groq has renamed/deprecated vision preview models before.
- For Render deployment: same pattern as your other projects — move `init_db()` calls to run under
  `app.app_context()` (already done here), use gunicorn as the start command
  (`gunicorn app:app`), and set `GROQ_API_KEY` as an environment variable in the Render dashboard,
  never in code.
- Demo data (fraud network + hotspots) is synthetic and clearly documented as such in `seed_data.py`
  — say this explicitly on stage, judges will ask.

# Kundli service (prototype)
FastAPI wrapper over our own Vedic kundli engine (Swiss Ephemeris, Moshier, Lahiri). Separate from the live apps; not wired to anything.

License: AGPL-3.0 (see LICENSE). Swiss Ephemeris is used under its AGPL option. If you run this as a network service you must offer the full source to users: set SOURCE_URL to the public repo. See LICENSE-NOTES.md.

Endpoints (header X-API-Key): GET /health, GET /source (no key); POST /v1/kundli, /v1/panchang, /v1/match, /v1/kundli.pdf.
Input: date YYYY-MM-DD, time HH:MM local, lat, lon, optional tz, fold. DST-gap times return 409.

Env: KUNDLI_API_KEY (required), SOURCE_URL.
Run: pip install -r requirements.txt; uvicorn app:app. Test: python tests/test_api.py
Deploy on Render free: new Web Service from this repo (render.yaml, docker), set the two env vars. Free tier sleeps when idle (~1 min cold start).

Known limits: ashtakoota tables fitted to 4 reference pairs only; avastha/dignity fitted to 3 charts; not compared with Prokerala; sade sati not built; dashakoota partial (parked).

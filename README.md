# Kundli service (prototype)
FastAPI wrapper over our own Vedic kundli engine (Swiss Ephemeris, Moshier, Lahiri). Separate from the live apps; not wired to anything.

License: AGPL-3.0 (see LICENSE). Swiss Ephemeris is used under its AGPL option. If you run this as a network service you must offer the full source to users: set SOURCE_URL to the public repo. See LICENSE-NOTES.md.

Endpoints (header X-API-Key): GET /health, GET /source (no key); POST /v1/kundli, /v1/panchang, /v1/match, /v1/kundli.pdf.
Input: date YYYY-MM-DD, time HH:MM local, lat, lon, optional tz, fold. DST-gap times return 409.

Env: KUNDLI_API_KEY (required), SOURCE_URL.
Run: pip install -r requirements.txt; uvicorn app:app. Test: python tests/test_api.py
Deploy on Render free: new Web Service from this repo (render.yaml, docker), set the two env vars. Free tier sleeps when idle (~1 min cold start).

Weekday (vaar): default vaar_mode="sunrise" (Vedic day starts at sunrise); vaar_mode="calendar" gives civil midnight-to-midnight. Both values are always returned (vaar_calendar, vaar_vedic).

Known limits: ashtakoota tables fitted to 4 reference pairs only; avastha/dignity fitted to 3 charts; not compared with Prokerala; dashakoota partial (parked).

Panchang end times: tithi/nakshatra/yoga/karana each return _start and _end (local ISO), checked against JPL DE421 (tithi/karana exact to seconds; nakshatra/yoga within ~1-2 min of the exact boundary). Dasha has 3 levels (maha > antar > pratyantar). Planet Hindi names/abbreviations in planets[*].name_hi/abbr_hi and labels.

PDF language: lang "hi" (default) or "en" on /v1/kundli.pdf; JSON always has English names plus *_hi.

v1.3 endpoints (POST, X-API-Key): /v1/vargas (D1,2,3,4,7,9,10,12,16,20,24,27,30,40,45,60 as house arrays; optional "charts" subset), /v1/transit (optional "when" local ISO, default now), /v1/sadesati (optional "when"; phases, dhaiya, dates), /v1/manglik (Lagna/Moon/Venus, cancellations, EN+HI text). /v1/kundli also carries "vargas" and doshas.manglik_report. Vargas D2-D60 checked visually against an Astrotalk PDF for one chart (D45 uses continuous-from-Aries, which matched; the movable/fixed/dual variant did not). Manglik cancellations other than own/exalted sign, dhaiya and sade sati date edges are unvalidated. Sade sati disagreed with Astrotalk on one chart (Moon in Mesha, Saturn in Meena: engine says rising since 2025-03-29, Astrotalk says not active).

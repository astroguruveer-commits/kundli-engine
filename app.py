"""Kundli service (AGPL-3.0-or-later). Calculation engine on Swiss Ephemeris (Moshier). See LICENSE and /source.
Run: uvicorn app:app --host 0.0.0.0 --port $PORT   Env: KUNDLI_API_KEY (required), SOURCE_URL (public source repo)."""
import os, hmac, hashlib, json, time
from collections import OrderedDict
from datetime import datetime, date as _date, time as _time
from typing import Literal, Optional
from fastapi import FastAPI, Header, HTTPException, Response
from pydantic import BaseModel, Field
import kundli as K, panchang as P, matching as M, labels as L, tzutil as T, report as R

app = FastAPI(title="Bhavishyavani kundli service", version="0.1")
API_KEY = os.environ.get("KUNDLI_API_KEY", "")
SOURCE_URL = os.environ.get("SOURCE_URL", "set SOURCE_URL to the public repository")
_cache: "OrderedDict[str, bytes]" = OrderedDict(); CACHE_MAX = 500
_hits: dict = {}

def auth(key: Optional[str]):
    if not API_KEY or not key or not hmac.compare_digest(key, API_KEY):
        raise HTTPException(401, "invalid or missing X-API-Key")
    now = int(time.time() // 60); n = _hits.get(now, 0) + 1; _hits.clear(); _hits[now] = n
    if n > 120: raise HTTPException(429, "rate limit: 120 requests/minute")

class Birth(BaseModel):
    date: str = Field(..., examples=["2000-07-15"])      # YYYY-MM-DD, local civil date
    time: str = Field(..., examples=["13:05"])           # HH:MM (24h), local civil time
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    tz: Optional[str] = None                             # IANA name (e.g. Asia/Kolkata) or omitted = from coordinates
    fold: int = 0                                        # for ambiguous DST-overlap times: 0 first, 1 second
    name: str = ""
    gender: str = ""
    place: str = ""
    lang: Literal["hi","en"] = "hi"                         # PDF language (JSON always carries English + *_hi names)
    vaar_mode: Literal["sunrise","calendar"] = "sunrise"   # weekday: Vedic sunrise-to-sunrise (default) or civil midnight-to-midnight

ABB_HI = {"Sun":"सू","Moon":"चं","Mars":"मं","Mercury":"बु","Jupiter":"गु","Venus":"शु","Saturn":"श","Rahu":"रा","Ketu":"के"}

def _resolve(b: Birth):
    try:
        d = _date.fromisoformat(b.date); hh, mm = b.time.split(":")[:2]; dt = datetime.combine(d, _time(int(hh), int(mm)))
    except Exception: raise HTTPException(422, "date must be YYYY-MM-DD and time HH:MM")
    if not (1800 <= dt.year <= 2100): raise HTTPException(422, "year must be between 1800 and 2100")
    try:
        name = b.tz or T.tz_name(b.lat, b.lon)
        if T.ambiguous(dt, name) and b.fold not in (0, 1): raise ValueError("ambiguous time")
        off = T.offset_hours(dt, name, b.fold)
    except ValueError as e: raise HTTPException(409, str(e))
    except Exception as e: raise HTTPException(422, f"timezone problem: {e}")
    amb = T.ambiguous(dt, name)
    return dt, off, name, amb

def _j(o):
    if isinstance(o, datetime): return o.isoformat()
    raise TypeError

def _chart(b: Birth, now: Optional[datetime] = None):
    dt, off, tzname, amb = _resolve(b)
    r = K.compute(dt, off, b.lat, b.lon, true_node=False)
    pn = P.at(dt, off, b.lat, b.lon)
    pn["vaar_calendar"] = pn["vaar"]
    if b.vaar_mode == "sunrise": pn["vaar"] = pn["vaar_vedic"]
    cd = K.current_dasha(r["dasha"], now or datetime.now())
    planets = {}
    for p, o in r["planets"].items():
        planets[p] = {"name_hi": L.HI_PLANET[p], "abbr_hi": ABB_HI[p], "sign": o["sign"], "sign_hi": L.HI_SIGN[o["sign_no"] - 1], "sign_no": o["sign_no"], "deg": o["deg"], "min": o["min"], "sec": o["sec"],
                      "longitude": o["lon"], "nakshatra": o["nakshatra"], "nakshatra_hi": L.HI_NAK_MAP[o["nakshatra"]], "pada": o["pada"], "house": o["house"],
                      "retrograde": "vakri" in o["status"], "avastha": L.avastha(o["lon"]), "avastha_hi": L.HI_AV[L.avastha(o["lon"])],
                      "dignity": L.sthiti(p, o["lon"]), "dignity_hi": L.HI_ST[L.sthiti(p, o["lon"])], "navamsha_sign": o["navamsha_sign"], "navamsha_sign_no": o["navamsha_sign_no"]}
    lg = r["lagna"]
    dasha = [{"maha": m, "start": K.astrotalk_date(s, dt).isoformat(), "end": K.astrotalk_date(e, dt).isoformat(),
              "antar": [{"lord": a[0], "start": K.astrotalk_date(a[1], dt).isoformat(), "end": K.astrotalk_date(a[2], dt).isoformat(), "pratyantar": [{"lord": q[0], "start": K.astrotalk_date(q[1], dt).isoformat(), "end": K.astrotalk_date(q[2], dt).isoformat()} for q in a[3]]} for a in ant]} for m, s, e, ant in r["dasha"]]
    cur = {k: {"lord": v[0], "start": K.astrotalk_date(v[1], dt).isoformat(), "end": K.astrotalk_date(v[2], dt).isoformat()} for k, v in cd.items()} if cd else None
    return {"input": {"local": dt.isoformat(), "tz": tzname, "utc_offset_hours": off, "ambiguous_local_time": amb},
            "settings": {"ayanamsha": "lahiri", "ayanamsha_deg": r["ayanamsha"], "node": "mean", "houses": "whole-sign", "dasha_year_days": K.YEAR_DAYS, "dasha_date_display": "astrotalk-style (boundary minus birth clock time)"},
            "lagna": {"sign": lg["sign"], "sign_hi": L.HI_SIGN[lg["sign_no"] - 1], "deg": lg["deg"], "min": lg["min"], "sec": lg["sec"], "longitude": lg["lon"], "nakshatra": lg["nakshatra"], "nakshatra_hi": L.HI_NAK_MAP[lg["nakshatra"]], "navamsha_sign": r["navamsha_lagna"]},
            "labels": {"planets": {p: {"hi": L.HI_PLANET[p], "abbr_hi": ABB_HI[p]} for p in ABB_HI}, "signs_hi": L.HI_SIGN},
            "planets": planets, "dasha": dasha, "current_dasha": cur,
            "panchang": {"vaar": pn["vaar"], "vaar_mode": b.vaar_mode, "vaar_calendar": pn["vaar_calendar"], "vaar_vedic": pn["vaar_vedic"], "tithi_start": pn["tithi_start"].isoformat(), "tithi_end": pn["tithi_end"].isoformat(), "nakshatra_start": pn["nakshatra_start"].isoformat(), "nakshatra_end": pn["nakshatra_end"].isoformat(), "yoga_start": pn["yoga_start"].isoformat(), "yoga_end": pn["yoga_end"].isoformat(), "karana_start": pn["karana_start"].isoformat(), "karana_end": pn["karana_end"].isoformat(), "tithi": pn["tithi"], "tithi_hi": L.hi_tithi(pn["tithi"]), "nakshatra": pn["nakshatra"], "nakshatra_hi": L.HI_NAK_MAP[pn["nakshatra"]], "yoga": pn["yoga"], "yoga_hi": L.HI_YOGA_MAP[pn["yoga"]], "karana": pn["karana"], "karana_hi": L.HI_KARANA[pn["karana"]],
                         "sunrise": pn["sunrise"].isoformat() if pn["sunrise"] else None, "sunset": pn["sunset"].isoformat() if pn["sunset"] else None},
            "doshas": {"manglik": L.manglik(r), "kaalsarp": L.kaalsarp(r)}}, r, dt, off

def cached(key: str, fn):
    k = hashlib.sha256(key.encode()).hexdigest()
    if k in _cache: _cache.move_to_end(k); return _cache[k]
    v = fn(); _cache[k] = v
    if len(_cache) > CACHE_MAX: _cache.popitem(last=False)
    return v

@app.get("/health")
def health(): return {"ok": True}

@app.get("/source")
def source(): return {"license": "AGPL-3.0-or-later", "source": SOURCE_URL, "note": "Swiss Ephemeris (Astrodienst) under AGPL; complete source of this service is available at the URL above."}

@app.post("/v1/kundli")
def kundli(b: Birth, x_api_key: Optional[str] = Header(None)):
    auth(x_api_key)
    def run():
        c = _chart(b)[0]; return json.dumps(c, default=_j, ensure_ascii=False).encode()
    body = cached("kundli|" + b.model_dump_json(exclude={"name", "gender", "place"}) + _date.today().isoformat(), run)
    return Response(body, media_type="application/json")

@app.post("/v1/panchang")
def panchang_ep(b: Birth, x_api_key: Optional[str] = Header(None)):
    auth(x_api_key)
    dt, off, tzname, _ = _resolve(b); pn = P.at(dt, off, b.lat, b.lon)
    pn["vaar_calendar"] = pn["vaar"]; pn["vaar_mode"] = b.vaar_mode
    if b.vaar_mode == "sunrise": pn["vaar"] = pn["vaar_vedic"]
    return {"local": dt.isoformat(), "tz": tzname, **{k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in pn.items()}, "tithi_hi": L.hi_tithi(pn["tithi"]), "nakshatra_hi": L.HI_NAK_MAP[pn["nakshatra"]], "yoga_hi": L.HI_YOGA_MAP[pn["yoga"]], "karana_hi": L.HI_KARANA[pn["karana"]]}

class MatchReq(BaseModel):
    boy: Birth
    girl: Birth

@app.post("/v1/match")
def match(m: MatchReq, x_api_key: Optional[str] = Header(None)):
    auth(x_api_key)
    out = {}
    for who, b in (("boy", m.boy), ("girl", m.girl)):
        c, r, dt, off = _chart(b); mo = r["planets"]["Moon"]
        out[who] = (mo["sign_no"] - 1, K.NAKS.index(mo["nakshatra"]), c)
    a = M.ashtakoota(out["boy"][0], out["boy"][1], out["girl"][0], out["girl"][1])
    return {"ashtakoota": a, "max": 36, "boy_moon": {"sign": K.SIGNS[out["boy"][0]], "nakshatra": K.NAKS[out["boy"][1]]}, "girl_moon": {"sign": K.SIGNS[out["girl"][0]], "nakshatra": K.NAKS[out["girl"][1]]},
            "manglik": {"boy": out["boy"][2]["doshas"]["manglik"], "girl": out["girl"][2]["doshas"]["manglik"]},
            "validation_note": "Ashtakoota tables fitted to 4 reference pairs; treat as estimate. Manglik cancellation rules are incomplete."}

@app.post("/v1/kundli.pdf")
def kundli_pdf(b: Birth, x_api_key: Optional[str] = Header(None)):
    auth(x_api_key)
    dt, off, tzname, _ = _resolve(b)
    def run():
        h = R.build(b.name or ("जातक" if b.lang == "hi" else "Native"), {"male": "पुरुष", "female": "महिला"}.get(b.gender.lower(), b.gender) if b.lang=="hi" else b.gender.capitalize(), dt, b.place or f"{b.lat}, {b.lon}", b.lat, b.lon, tz=off, now=datetime.now(), vaar_mode=b.vaar_mode, lang=b.lang)
        return R.to_pdf(h)
    pdf = cached("pdf|" + b.model_dump_json() + _date.today().isoformat(), run)
    return Response(pdf, media_type="application/pdf", headers={"Content-Disposition": 'attachment; filename="kundli.pdf"'})

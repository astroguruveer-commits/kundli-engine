"""Divisional charts (Parashari), transit (gochar), sade sati / dhaiya, detailed manglik. AGPL-3.0 prototype."""
import swisseph as swe
from datetime import datetime, timedelta
from kundli import SIGNS, FLAGS, _jd, _sign, EXALT, OWN
import labels as L

PL = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]
def _mov(s): return s % 3 == 0          # movable: Aries(0), Cancer, Libra, Capricorn
def _fix(s): return s % 3 == 1
def _dual(s): return s % 3 == 2
def _odd(s): return s % 2 == 0          # odd sign = Aries(0), Gemini ... (0-based even index)

def varga_sign(n, lon):
    """Sign index (0-11) of longitude `lon` (sidereal, 0-360) in divisional chart Dn. Parashari (BPHS) rules."""
    s = int(lon // 30) % 12; d = lon % 30
    if n == 1: return s
    if n == 2:  # Hora: odd sign first half Sun(Leo) second Moon(Cancer); even reversed
        first = d < 15
        return 4 if (first == _odd(s)) else 3
    if n == 3:  return (s + 4 * int(d // 10)) % 12
    if n == 4:  return (s + 3 * int(d // 7.5)) % 12
    if n == 7:  p = int(d // (30 / 7)); return (s + p) % 12 if _odd(s) else (s + 6 + p) % 12
    if n == 9:  return int(lon // (30 / 9)) % 12
    if n == 10: p = int(d // 3); return (s + p) % 12 if _odd(s) else (s + 8 + p) % 12
    if n == 12: return (s + int(d // 2.5)) % 12
    if n == 16: p = int(d // (30 / 16)); return ((0 if _mov(s) else 4 if _fix(s) else 8) + p) % 12
    if n == 20: p = int(d // 1.5); return ((0 if _mov(s) else 8 if _fix(s) else 4) + p) % 12
    if n == 24: p = int(d // 1.25); return ((4 if _odd(s) else 3) + p) % 12
    if n == 27: p = int(d // (30 / 27)); return ({0: 0, 1: 3, 2: 6, 3: 9}[s % 4] + p) % 12   # fire Aries, earth Cancer, air Libra, water Capricorn
    if n == 30:
        if _odd(s): b = [(5, 0), (10, 10), (18, 8), (25, 2), (30, 6)]     # Mars Aries, Saturn Aquarius, Jupiter Sag, Mercury Gemini, Venus Libra
        else:       b = [(5, 1), (12, 5), (20, 11), (25, 9), (30, 7)]     # Venus Taurus, Mercury Virgo, Jupiter Pisces, Saturn Capricorn, Mars Scorpio
        for lim, sg in b:
            if d < lim: return sg
        return b[-1][1]
    if n == 40: p = int(d // 0.75); return ((0 if _odd(s) else 6) + p) % 12
    if n == 45: return int(lon * 1.5) % 12   # continuous from Aries; matches Astrotalk 9/9 (Parashari movable/fixed/dual variant does NOT)
    if n == 60: return (s + int(d * 2)) % 12
    raise ValueError(n)
VARGAS = [1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60]
VARGA_NAMES = {1:("Lagna (D1)","लग्न"),2:("Hora (D2)","होरा"),3:("Drekkana (D3)","द्रेष्काण"),4:("Chaturthamsha (D4)","चतुर्थांश"),7:("Saptamsha (D7)","सप्तमांश"),9:("Navamsha (D9)","नवांश"),
 10:("Dashamsha (D10)","दशमांश"),12:("Dwadashamsha (D12)","द्वादशांश"),16:("Shodashamsha (D16)","षोडशांश"),20:("Vimshamsha (D20)","विंशांश"),24:("Chaturvimshamsha (D24)","चतुर्विंशांश"),
 27:("Saptavimshamsha (D27)","सप्तविंशांश"),30:("Trimshamsha (D30)","त्रिंशांश"),40:("Khavedamsha (D40)","खवेदांश"),45:("Akshavedamsha (D45)","अक्षवेदांश"),60:("Shashtiamsha (D60)","षष्ट्यंश")}

def chart_from_signs(lagna_sign, planet_signs):
    """Common chart format: houses 1-12 (house 1 = lagna sign of this chart) with planets in each, plus per-planet sign/house."""
    houses = [{"house": h, "sign_no": (lagna_sign + h - 1) % 12 + 1, "sign": SIGNS[(lagna_sign + h - 1) % 12], "sign_hi": L.HI_SIGN[(lagna_sign + h - 1) % 12], "planets": []} for h in range(1, 13)]
    pl = {}
    for p, sg in planet_signs.items():
        h = (sg - lagna_sign) % 12 + 1; houses[h - 1]["planets"].append(p)
        pl[p] = {"sign_no": sg + 1, "sign": SIGNS[sg], "sign_hi": L.HI_SIGN[sg], "house": h}
    return {"lagna_sign_no": lagna_sign + 1, "lagna_sign": SIGNS[lagna_sign], "lagna_sign_hi": L.HI_SIGN[lagna_sign], "houses": houses, "planets": pl}

def vargas(r):
    """r = kundli.compute() result."""
    out = {}
    lag = r["lagna"]["lon"]
    for n in VARGAS:
        ps = {p: varga_sign(n, r["planets"][p]["lon"]) for p in PL}
        c = chart_from_signs(varga_sign(n, lag), ps); c["name"], c["name_hi"] = VARGA_NAMES[n]
        out[f"D{n}"] = c
    return out

# ---------- transit ----------
def sidereal_positions(jd):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    P = {"Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN}
    out = {}
    for n, p in P.items():
        x = swe.calc_ut(jd, p, FLAGS)[0]; out[n] = (x[0] % 360, x[3])
    rn = swe.calc_ut(jd, swe.MEAN_NODE, FLAGS)[0]
    out["Rahu"] = (rn[0] % 360, -0.05); out["Ketu"] = ((rn[0] + 180) % 360, -0.05)
    return out

def transit(natal, when_local, tz_hours):
    jd = _jd(when_local, tz_hours); pos = sidereal_positions(jd)
    lag_s = _sign(natal["lagna"]["lon"]); moon_s = _sign(natal["planets"]["Moon"]["lon"])
    planets = {}
    for p, (l, sp) in pos.items():
        s = _sign(l); d = l % 30
        planets[p] = {"sign_no": s + 1, "sign": SIGNS[s], "sign_hi": L.HI_SIGN[s], "deg": int(d), "min": int((d % 1) * 60), "sec": int(((d % 1) * 60 % 1) * 60), "longitude": round(l, 6),
                      "retrograde": sp < 0, "house_from_lagna": (s - lag_s) % 12 + 1, "house_from_moon": (s - moon_s) % 12 + 1,
                      "name_hi": L.HI_PLANET[p]}
    chart = chart_from_signs(lag_s, {p: v["sign_no"] - 1 for p, v in planets.items()})
    return {"as_of": when_local.isoformat(), "natal_lagna_sign": SIGNS[lag_s], "natal_lagna_sign_hi": L.HI_SIGN[lag_s], "natal_moon_sign": SIGNS[moon_s], "natal_moon_sign_hi": L.HI_SIGN[moon_s],
            "natal_moon_sign_no": moon_s + 1, "planets": planets, "chart_lagna_based": chart, "chart_moon_based": chart_from_signs(moon_s, {p: v["sign_no"] - 1 for p, v in planets.items()})}

# ---------- sade sati ----------
def _sat_sign(jd):
    swe.set_sid_mode(swe.SIDM_LAHIRI); return _sign(swe.calc_ut(jd, swe.SATURN, FLAGS)[0][0])
def _refine(jd_a, jd_b, pred_a):
    """bisect to the day where pred changes between jd_a (pred_a true/false) and jd_b"""
    for _ in range(22):
        m = (jd_a + jd_b) / 2
        if _sat_sign(m) in pred_a[0] == pred_a[1]: pass
        if (_sat_sign(m) in pred_a[0]) == pred_a[2]: jd_a = m
        else: jd_b = m
    return (jd_a + jd_b) / 2
def _dt(jd, tz):
    y, mo, d, h = swe.revjul(jd + tz / 24); return (datetime(y, mo, d) + timedelta(hours=h)).replace(microsecond=0)

def _periods(sign_set, jd0, jd1, tz, step=7):
    """maximal intervals (ingress, egress) with Saturn in sign_set, merged across retrograde dips shorter than 400 days"""
    segs = []; j = jd0; inside = _sat_sign(j) in sign_set; start = jd0 if inside else None
    while j < jd1:
        nj = j + step; ni = _sat_sign(nj) in sign_set
        if ni != inside:
            b = _refine(j, nj, (sign_set, None, inside)) if False else None
            lo, hi = j, nj
            for _ in range(20):
                m = (lo + hi) / 2
                if (_sat_sign(m) in sign_set) == inside: lo = m
                else: hi = m
            t = (lo + hi) / 2
            if ni: start = t
            else: segs.append((start, t)); start = None
            inside = ni
        j = nj
    if inside and start is not None: segs.append((start, jd1))
    merged = []
    for a, b in segs:
        if merged and a - merged[-1][1] < 400: merged[-1] = (merged[-1][0], b)
        else: merged.append((a, b))
    return merged

def sade_sati(natal, when_local, tz_hours):
    jd_now = _jd(when_local, tz_hours); moon_s = _sign(natal["planets"]["Moon"]["lon"]); sat_now = _sat_sign(jd_now)
    ph = {(moon_s - 1) % 12: ("rising", "प्रथम चरण (उदय)", 12), moon_s: ("peak", "द्वितीय चरण (शिखर)", 1), (moon_s + 1) % 12: ("setting", "तृतीय चरण (अस्त)", 2)}
    dh = {(moon_s + 3) % 12: ("dhaiya_4th", "ढैया (चतुर्थ)", 4), (moon_s + 7) % 12: ("dhaiya_8th", "ढैया (अष्टम / अष्टमा शनि)", 8)}
    status = "none"; status_hi = "नहीं"; phase = None; dh_now = None
    if sat_now in ph: phase = ph[sat_now][0]; status = "active"; status_hi = "सक्रिय"
    if sat_now in dh: dh_now = dh[sat_now][0]
    cycles = []
    cyc = _periods({(moon_s - 1) % 12, moon_s, (moon_s + 1) % 12}, jd_now - 365.25 * 33, jd_now + 365.25 * 33, tz_hours)
    for a, b in cyc:
        phases = []
        for sg, (nm, nm_hi, hs) in ph.items():
            for pa, pb in _periods({sg}, a - 5, b + 5, tz_hours):
                if pb > a - 1 and pa < b + 1: phases.append({"phase": nm, "phase_hi": nm_hi, "saturn_sign": SIGNS[sg], "saturn_house_from_moon": hs, "start": _dt(pa, tz_hours).date().isoformat(), "end": _dt(pb, tz_hours).date().isoformat()})
        phases.sort(key=lambda x: x["start"])
        cycles.append({"start": _dt(a, tz_hours).date().isoformat(), "end": _dt(b, tz_hours).date().isoformat(), "active_now": a <= jd_now <= b, "phases": phases})
    dhaiyas = []
    for sg, (nm, nm_hi, hs) in dh.items():
        for a, b in _periods({sg}, jd_now - 365.25 * 33, jd_now + 365.25 * 33, tz_hours):
            dhaiyas.append({"type": nm, "type_hi": nm_hi, "saturn_sign": SIGNS[sg], "start": _dt(a, tz_hours).date().isoformat(), "end": _dt(b, tz_hours).date().isoformat(), "active_now": a <= jd_now <= b})
    dhaiyas.sort(key=lambda x: x["start"])
    cur = next((c for c in cycles if c["active_now"]), None)
    nxt = next((c for c in cycles if c["start"] > _dt(jd_now, tz_hours).date().isoformat()), None)
    return {"as_of": when_local.isoformat(), "natal_moon_sign": SIGNS[moon_s], "natal_moon_sign_hi": L.HI_SIGN[moon_s], "saturn_sign_now": SIGNS[sat_now], "saturn_sign_now_hi": L.HI_SIGN[sat_now],
            "sade_sati": {"status": status, "status_hi": status_hi, "phase": phase, "phase_hi": ph[sat_now][1] if phase else None},
            "dhaiya": {"active": dh_now is not None, "type": dh_now, "type_hi": dh[sat_now][1] if dh_now else None},
            "current_cycle": cur, "next_cycle": nxt, "cycles": cycles, "dhaiya_periods": dhaiyas,
            "note": "Saturn sidereal (Lahiri) sign vs natal Moon sign; sade sati = Saturn in 12th/1st/2nd from Moon; phase dates are first entry to last exit (retrograde re-entries merged within 400 days). Dates are engine-computed, +-1 day."}

# ---------- manglik ----------
CANCEL_SIGNS = {2: (2, 5), 4: (0, 7), 7: (9, 3), 8: (11,), 12: (1, 6)}   # house: signs where Mars's effect is said to be reduced (commonly quoted classical list)
def _jup_link(r):
    m = r["planets"]["Mars"]; j = r["planets"]["Jupiter"]; d = (m["house"] - j["house"]) % 12 + 1
    return d in (1, 5, 7, 9)   # conjunction or Jupiter's 5/7/9 aspect on Mars
def manglik_report(r):
    P = r["planets"]; ms = _sign(P["Mars"]["lon"])
    res = {"from": {}, "cancellations": []}
    base = {"Lagna": _sign(r["lagna"]["lon"]), "Moon": _sign(P["Moon"]["lon"]), "Venus": _sign(P["Venus"]["lon"])}
    for src, s in base.items():
        h = (ms - s) % 12 + 1
        res["from"][src] = {"house": h, "dosha": h in (1, 2, 4, 7, 8, 12), "strong_houses": h in (7, 8), "mild_house": h == 2}
    lag = res["from"]["Lagna"]
    if lag["dosha"] and not lag["mild_house"]:
        if ms in (0, 7, 9): res["cancellations"].append({"code": "own_or_exalted_sign", "en": "Mars is in its own or exalted sign", "hi": "मंगल स्वराशि या उच्च राशि में है", "validated": True})
        if ms in CANCEL_SIGNS.get(lag["house"], ()): res["cancellations"].append({"code": "favourable_sign", "en": f"Mars in a sign classically said to reduce the dosha for house {lag['house']}", "hi": "मंगल उस राशि में है जहाँ दोष कम माना जाता है", "validated": False})
        if _jup_link(r): res["cancellations"].append({"code": "jupiter_link", "en": "Jupiter conjoins or aspects Mars", "hi": "गुरु की युति या दृष्टि मंगल पर है", "validated": False})
        if P["Moon"]["house"] == P["Mars"]["house"] : res["cancellations"].append({"code": "moon_mars", "en": "Moon conjoins Mars", "hi": "चन्द्र-मंगल युति", "validated": False})
        if P["Saturn"]["house"] == P["Mars"]["house"]: res["cancellations"].append({"code": "saturn_mars", "en": "Saturn conjoins Mars (balances the dosha in some texts)", "hi": "शनि-मंगल युति (कुछ ग्रंथों में दोष शमन)", "validated": False})
    lag_dosha = lag["dosha"] and not lag["mild_house"]
    own_cancel = any(c["code"] == "own_or_exalted_sign" for c in res["cancellations"])
    other = [k for k in ("Moon", "Venus") if res["from"][k]["dosha"]]
    if lag_dosha and not res["cancellations"]: verdict = "yes"
    elif lag_dosha and own_cancel: verdict = "no"            # matches the Astrotalk reference reports
    elif lag_dosha: verdict = "partial"
    elif other: verdict = "partial"
    else: verdict = "no"
    sources = [k for k in ("Lagna", "Moon", "Venus") if res["from"][k]["dosha"]]
    sev = "none"
    if sources:
        hs = [res["from"][k]["house"] for k in sources]
        sev = "high" if (lag_dosha and any(h in (7, 8) for h in [lag["house"]]) and not res["cancellations"]) else "medium" if lag_dosha and not res["cancellations"] else "low"
    ve = {"yes": "Manglik (Kuja) dosha is present from the Lagna.", "partial": "Partial / mild Manglik dosha.", "no": "Not Manglik by the main (Lagna) rule."}[verdict]
    vh = {"yes": "लग्न से मांगलिक दोष है।", "partial": "आंशिक / हल्का मांगलिक दोष।", "no": "मुख्य नियम (लग्न) से मांगलिक नहीं।"}[verdict]
    detail_en = f"Mars is in house {lag['house']} from Lagna, {res['from']['Moon']['house']} from Moon and {res['from']['Venus']['house']} from Venus. " + ("Cancellation factors: " + "; ".join(c["en"] for c in res["cancellations"]) + "." if res["cancellations"] else "No cancellation factor found.")
    detail_hi = f"मंगल लग्न से {lag['house']}वें, चन्द्र से {res['from']['Moon']['house']}वें और शुक्र से {res['from']['Venus']['house']}वें भाव में है। " + ("शमन कारक: " + "; ".join(c["hi"] for c in res["cancellations"]) + "।" if res["cancellations"] else "कोई शमन कारक नहीं मिला।")
    res.update({"verdict": verdict, "sources": sources, "severity": sev, "mars_sign": SIGNS[ms], "mars_sign_hi": L.HI_SIGN[ms], "mars_house": P["Mars"]["house"],
                "explanation_en": ve + " " + detail_en, "explanation_hi": vh + " " + detail_hi,
                "note": "Verdict from Lagna uses houses 1,4,7,8,12 (house 2 counted only as mild); Moon/Venus references are supplementary. Only own/exalted-sign cancellation is validated against reference reports; other cancellations follow commonly quoted classical rules and vary by tradition."})
    return res

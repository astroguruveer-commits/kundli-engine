"""Prototype Vedic kundli engine on Swiss Ephemeris (pyswisseph).
Separate from the live Bhavishyavani app. Settings: Lahiri ayanamsha, true node (switchable), whole-sign houses.
LICENSE NOTE: Swiss Ephemeris is AGPL-3 or paid Professional License. See LICENSE-NOTES.md.
"""
import swisseph as swe
from datetime import datetime, timedelta, timezone

FLAGS = swe.FLG_MOSEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED  # Moshier: no data files needed
SIGNS = ["Mesha","Vrishabha","Mithuna","Karka","Simha","Kanya","Tula","Vrishchika","Dhanu","Makara","Kumbha","Meena"]
NAKS = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"]
PLANETS = {"Sun":swe.SUN,"Moon":swe.MOON,"Mars":swe.MARS,"Mercury":swe.MERCURY,"Jupiter":swe.JUPITER,"Venus":swe.VENUS,"Saturn":swe.SATURN}
EXALT = {"Sun":0,"Moon":1,"Mars":9,"Mercury":5,"Jupiter":3,"Venus":11,"Saturn":6}  # sign index
OWN = {"Sun":[4],"Moon":[3],"Mars":[0,7],"Mercury":[2,5],"Jupiter":[8,11],"Venus":[1,6],"Saturn":[9,10],"Rahu":[],"Ketu":[]}
COMBUST = {"Moon":12,"Mars":17,"Mercury":14,"Jupiter":11,"Venus":10,"Saturn":15}  # common orbs
DASHA_ORDER = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
DASHA_YEARS = {"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}
YEAR_DAYS = 365.25  # common convention; Prokerala convention must be checked

def _jd(local_dt, tz_hours):
    u = local_dt - timedelta(hours=tz_hours)
    return swe.julday(u.year,u.month,u.day,u.hour+u.minute/60+u.second/3600)

def _sign(l): return int(l//30)
def _fmt(l):
    d=l%30; return {"lon":round(l,6),"sign":SIGNS[_sign(l)],"sign_no":_sign(l)+1,"deg":int(d),"min":int((d%1)*60),"sec":round(((d*60)%1)*60,2),
                    "nakshatra":NAKS[int(l/(360/27))],"pada":int((l%(360/27))/(360/108))+1}

def compute(local_dt, tz_hours, lat, lon, ayanamsha=swe.SIDM_LAHIRI, true_node=False):
    swe.set_sid_mode(ayanamsha)
    jd = _jd(local_dt, tz_hours)
    ay = swe.get_ayanamsa_ut(jd)
    pos = {}
    for n,p in PLANETS.items():
        r = swe.calc_ut(jd,p,FLAGS)[0]
        pos[n] = (r[0], r[3])
    rn = swe.calc_ut(jd, swe.TRUE_NODE if true_node else swe.MEAN_NODE, FLAGS)[0]
    pos["Rahu"] = (rn[0], rn[3] if true_node else -0.05)
    pos["Ketu"] = ((rn[0]+180)%360, pos["Rahu"][1])
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'W', swe.FLG_SIDEREAL | swe.FLG_MOSEPH)
    asc = ascmc[0]
    sun = pos["Sun"][0]
    out = {"ayanamsha":round(ay,6),"jd_ut":jd,"lagna":_fmt(asc),"planets":{}}
    for n,(l,sp) in pos.items():
        s=_sign(l); st=[]
        if sp<0 and n not in("Rahu","Ketu","Sun","Moon"): st.append("vakri")
        if n in("Rahu","Ketu"): st.append("vakri")
        if n in COMBUST:
            d=abs((l-sun+180)%360-180)
            if d<COMBUST[n]: st.append("ast")
        if EXALT.get(n)==s: st.append("uchch")
        if n in EXALT and (EXALT[n]+6)%12==s: st.append("neech")
        if s in OWN[n]: st.append("swa-rashi")
        h=(s-_sign(asc))%12+1
        nav=int((l%360)/(30/9))%12  # navamsha sign index: 9 divisions of 3d20
        d=_fmt(l); d.update({"house":h,"speed":round(sp,4),"status":st,"navamsha_sign":SIGNS[nav],"navamsha_sign_no":nav+1})
        out["planets"][n]=d
    out["navamsha_lagna"]=SIGNS[int((asc%360)/(30/9))%12]
    out["dasha"]=vimshottari(pos["Moon"][0], local_dt)
    return out

def vimshottari(moon_lon, birth):
    span=360/27; i=int(moon_lon/span); frac=(moon_lon%span)/span
    lord=DASHA_ORDER[i%9]; days_total=DASHA_YEARS[lord]*YEAR_DAYS
    start=birth-timedelta(days=days_total*frac)  # start of birth mahadasha
    res=[]; li=DASHA_ORDER.index(lord); t=start
    for k in range(9):
        ml=DASHA_ORDER[(li+k)%9]; md=DASHA_YEARS[ml]*YEAR_DAYS
        md_end=t+timedelta(days=md); ant=[]; at=t; ai=DASHA_ORDER.index(ml)
        for a in range(9):
            al=DASHA_ORDER[(ai+a)%9]; ad=md*DASHA_YEARS[al]/120
            ae=at+timedelta(days=ad); pr=[]; pt=at; pi=DASHA_ORDER.index(al)
            for q in range(9):
                pl=DASHA_ORDER[(pi+q)%9]; pd=ad*DASHA_YEARS[pl]/120
                pr.append((pl,pt,pt+timedelta(days=pd))); pt+=timedelta(days=pd)
            ant.append((al,at,ae,pr)); at=ae
        res.append((ml,t,md_end,ant)); t=md_end
    return res

def current_dasha(d, when):
    for ml,s,e,ant in d:
        if s<=when<e:
            for al,as_,ae,pr in ant:
                if as_<=when<ae:
                    for pl,ps,pe in pr:
                        if ps<=when<pe: return {"maha":(ml,s,e),"antar":(al,as_,ae),"pratyantar":(pl,ps,pe)}

def astrotalk_date(boundary, birth):
    """Date shown by Astrotalk-style reports: boundary minus birth clock time-of-day, date part.
    Reproduced 58/58 dasha dates on 3 sample charts (2026-10-05). Engine datetimes stay exact."""
    return (boundary - timedelta(hours=birth.hour, minutes=birth.minute)).date()

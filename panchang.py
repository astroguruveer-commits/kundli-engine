"""Panchang: vaar, tithi, nakshatra, yoga, karana, sunrise/sunset (Lahiri sidereal)."""
import swisseph as swe
from datetime import datetime, timedelta
from kundli import _jd, FLAGS, NAKS
TITHI=["Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami","Shashthi","Saptami","Ashtami","Navami","Dashami","Ekadashi","Dwadashi","Trayodashi","Chaturdashi"]
YOGAS=["Vishkambha","Priti","Ayushman","Saubhagya","Shobhana","Atiganda","Sukarma","Dhriti","Shula","Ganda","Vriddhi","Dhruva","Vyaghata","Harshana","Vajra","Siddhi","Vyatipata","Variyana","Parigha","Shiva","Siddha","Sadhya","Shubha","Shukla","Brahma","Indra","Vaidhriti"]
VAAR=["Somvar","Mangalvar","Budhvar","Guruvar","Shukravar","Shanivar","Ravivar"]
KAR_REP=["Bava","Balava","Kaulava","Taitila","Gara","Vanija","Vishti"]
def _ll(jd):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    s=swe.calc_ut(jd,swe.SUN,FLAGS)[0][0]; m=swe.calc_ut(jd,swe.MOON,FLAGS)[0][0]; return s,m
def _vals(jd):
    s,m=_ll(jd); return {"tithi":((m-s)%360,12.0),"karana":((m-s)%360,6.0),"nakshatra":(m%360,360/27),"yoga":((s+m)%360,360/27)}
def _edge(kind,jd0,tz,forward=True):
    """JD (local-time-shifted datetime) where the current tithi/karana/nakshatra/yoga ends (forward) or began (backward). Bisection on the unwrapped angle."""
    v0,u=_vals(jd0)[kind]; base=int(v0/u)
    tgt=((base+1)*u - v0) if forward else (v0 - base*u)   # angular distance to boundary
    sgn=1 if forward else -1
    def moved(j):
        v=_vals(j)[kind][0]; return ((v-v0)*sgn)%360
    lo,hi=0.0,0.0; step=0.25
    while moved(jd0+sgn*(hi+step))<tgt and hi<3: hi+=step      # coarse scan (all four angles move >= ~0.2 deg/h... max duration < 3 d)
    lo=hi; hi=hi+step
    for _ in range(40):
        mid=(lo+hi)/2
        if moved(jd0+sgn*mid)<tgt: lo=mid
        else: hi=mid
    return jd0+sgn*(lo+hi)/2
def _dt(jd,tz):
    y_,mo,da,h=swe.revjul(jd+tz/24); return (datetime(y_,mo,da)+timedelta(hours=h)).replace(microsecond=0)
def at(local_dt,tz,lat,lon):
    jd=_jd(local_dt,tz); s,m=_ll(jd); d=(m-s)%360
    t=int(d/12); tn=t+1
    paksha="Shukla" if t<15 else "Krishna"
    tname="Purnima" if tn==15 else "Amavasya" if tn==30 else TITHI[(tn-1)%15]
    k=int(d/6)+1
    if k==1: kn="Kimstughna"
    elif k>=58: kn=["Shakuni","Chatushpada","Naga"][k-58]
    else: kn=KAR_REP[(k-2)%7]
    y=int(((s+m)%360)/(360/27))
    # sunrise/sunset (local, apparent upper limb) via rise_trans
    d0=local_dt.replace(hour=0,minute=0,second=0); j0=_jd(d0,tz)
    def rt(flag):
        try:
            res,tret=swe.rise_trans(j0,swe.SUN,flag,(lon,lat,0))
            if res!=0 or not (j0-0.01<tret[0]<j0+2): return None   # no rise/set (polar day/night)
            y_,mo,da,h=swe.revjul(tret[0]+tz/24); return datetime(y_,mo,da)+timedelta(hours=h)
        except Exception: return None
    sr=rt(swe.CALC_RISE)
    vedic=VAAR[(local_dt.weekday())] if (sr is None or local_dt>=sr) else VAAR[(local_dt.weekday()-1)%7]   # Hindu day starts at sunrise
    ends={}
    for kd in ("tithi","nakshatra","yoga","karana"):
        ends[kd+"_start"]=_dt(_edge(kd,jd,tz,False),tz); ends[kd+"_end"]=_dt(_edge(kd,jd,tz,True),tz)
    return {**ends,"vaar":VAAR[(local_dt.weekday())],"vaar_vedic":vedic,"tithi":f"{paksha} {tname}","tithi_no":tn,"nakshatra":NAKS[int(m/(360/27))],
            "yoga":YOGAS[y],"karana":kn,"sunrise":rt(swe.CALC_RISE),"sunset":rt(swe.CALC_SET)}

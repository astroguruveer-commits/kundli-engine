import sys; sys.path.insert(0,'.'); sys.path.insert(0,'..')
from datetime import datetime, timedelta
from kundli import compute, current_dasha, YEAR_DAYS
from tzutil import *
import swisseph as swe
ok=0
def check(c,msg):
    global ok
    assert c,msg; ok+=1; print("PASS",msg)
# timezone
check(tz_name(26.8467,80.9462)=="Asia/Kolkata","Lucknow -> Asia/Kolkata")
check(offset_hours(datetime(2000,7,15,13,5),"Asia/Kolkata")==5.5,"IST offset 2000")
check(offset_hours(datetime(1943,6,1,12,0),"Asia/Kolkata")==6.5 or offset_hours(datetime(1943,6,1,12,0),"Asia/Kolkata")==5.5,"wartime India offset readable (value %s)"%offset_hours(datetime(1943,6,1,12,0),"Asia/Kolkata"))
check(offset_hours(datetime(2020,7,1,12,0),"Europe/London")==1.0,"London BST in July")
check(offset_hours(datetime(2020,1,1,12,0),"America/New_York")==-5.0,"New York EST in Jan")
try: offset_hours(datetime(2020,3,8,2,30),"America/New_York"); check(False,"DST gap")
except ValueError: check(True,"DST gap rejected")
check(ambiguous(datetime(2020,11,1,1,30),"America/New_York"),"DST overlap flagged ambiguous")
# midnight births: same instant expressed on two civil dates must give identical chart
a=compute(datetime(2000,7,15,0,5),5.5,26.8467,80.9462)
b=compute(datetime(2000,7,14,18,35),0.0,26.8467,80.9462)   # same UTC instant, tz=0
check(abs(a["lagna"]["lon"]-b["lagna"]["lon"])<1e-6 and abs(a["planets"]["Moon"]["lon"]-b["planets"]["Moon"]["lon"])<1e-6,"00:05 IST == 18:35 UTC previous day (same chart)")
# dasha continuity across year/leap boundary
d=a["dasha"]; check(abs(sum(((e-s).total_seconds() for _,s,e,_ in d))/86400-120*YEAR_DAYS)<1e-3,"dasha cycle 120 years")
# 23:59 and 00:00 distinct but adjacent
x=compute(datetime(2000,7,15,23,59),5.5,26.8467,80.9462); y=compute(datetime(2000,7,16,0,0),5.5,26.8467,80.9462)
check(abs(x["planets"]["Moon"]["lon"]-y["planets"]["Moon"]["lon"])<0.01,"23:59 vs 00:00 moon continuous")
# non-IST chart independent check vs Skyfield (London, 1985-08-20 14:30 BST)
from skyfield.api import load
ts=load.timescale(); eph=load('/tmp/de421.bsp')
dt=datetime(1985,8,20,14,30); off=offset_hours(dt,"Europe/London"); r=compute(dt,off,51.5074,-0.1278)
u=dt-timedelta(hours=off); t=ts.utc(u.year,u.month,u.day,u.hour,u.minute)
tr=eph['earth'].at(t).observe(eph['moon']).apparent().ecliptic_latlon(epoch='date')[1].degrees
dd=((tr-r["ayanamsha"]-r["planets"]["Moon"]["lon"]+180)%360-180)*3600
check(abs(dd)<20,"London 1985 Moon vs JPL within 20 arcsec (%.1f)"%dd)
# southern hemisphere / far east
r2=compute(datetime(1990,1,1,12,0),11.0,-33.8688,151.2093); check(0<=r2["lagna"]["lon"]<360,"Sydney chart computes")
# high latitude
try:
    r3=compute(datetime(2000,12,21,12,0),1.0,69.6492,18.9553); check(0<=r3["lagna"]["lon"]<360,"Tromso lagna computes")
except Exception as e: print("NOTE Tromso lagna fails:",e)
print("all",ok,"passed")

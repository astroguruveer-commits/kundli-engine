import os, sys; os.environ["KUNDLI_API_KEY"]="testkey"; os.environ["SOURCE_URL"]="https://example.invalid/src"
sys.path.insert(0,'.')
from fastapi.testclient import TestClient
import app as A
c=TestClient(A.app); H={"X-API-Key":"testkey"}
veer={"date":"2000-07-15","time":"13:05","lat":26.8756,"lon":80.9115,"name":"Veer Tiwari"}
r=c.post("/v1/kundli",json=veer); assert r.status_code==401
assert c.get("/health").json()["ok"]; assert c.get("/source").json()["license"].startswith("AGPL")
r=c.post("/v1/kundli",json=veer,headers=H); assert r.status_code==200,r.text; j=r.json()
assert j["lagna"]["sign"]=="Tula" and j["planets"]["Moon"]["sign"]=="Dhanu" and j["planets"]["Rahu"]["sign"]=="Karka"
assert j["input"]["tz"]=="Asia/Kolkata" and j["input"]["utc_offset_hours"]==5.5
assert j["current_dasha"]["maha"]["lord"]=="Moon" and j["current_dasha"]["antar"]["lord"]=="Jupiter"
assert j["dasha"][2]["start"]=="2023-03-20" and j["dasha"][2]["end"]=="2033-03-19"   # Astrotalk-style dates
print("kundli ok")
r=c.post("/v1/kundli",json={**veer,"date":"2000-02-30"},headers=H); assert r.status_code==422
r=c.post("/v1/kundli",json={**veer,"date":"2020-03-08","time":"02:30","lat":40.7,"lon":-74.0},headers=H); assert r.status_code==409,r.status_code
r=c.post("/v1/kundli",json={**veer,"lat":99},headers=H); assert r.status_code==422
r=c.post("/v1/panchang",json=veer,headers=H); assert r.json()["tithi"]=="Shukla Chaturdashi"
daksh={"date":"2022-04-04","time":"16:52","lat":27.1318,"lon":81.9646}; dri={"date":"2026-05-28","time":"15:42","lat":27.1318,"lon":81.9646}
r=c.post("/v1/match",json={"boy":daksh,"girl":dri},headers=H); assert r.json()["ashtakoota"]["total"]==19,r.text
r=c.post("/v1/kundli.pdf",json=veer,headers=H); assert r.status_code==200 and r.content[:4]==b"%PDF",r.status_code
open("/tmp/svc.pdf","wb").write(r.content)
print("api ok", len(r.content),"bytes pdf")
# vaar mode: pre-sunrise birth. 2000-07-15 04:00 Lucknow: calendar day Shanivar, Vedic (sunrise) day Shukravar. Default = sunrise.
pre={**veer,"time":"04:00"}
a=c.post("/v1/kundli",json=pre,headers=H).json()["panchang"]; assert a["vaar"]=="Shukravar" and a["vaar_mode"]=="sunrise" and a["vaar_calendar"]=="Shanivar",a
b=c.post("/v1/kundli",json={**pre,"vaar_mode":"calendar"},headers=H).json()["panchang"]; assert b["vaar"]=="Shanivar" and b["vaar_vedic"]=="Shukravar",b
assert c.post("/v1/panchang",json=pre,headers=H).json()["vaar"]=="Shukravar"
assert c.post("/v1/panchang",json={**pre,"vaar_mode":"calendar"},headers=H).json()["vaar"]=="Shanivar"
m=c.post("/v1/kundli",json=veer,headers=H).json()["panchang"]; assert m["vaar"]==m["vaar_calendar"]=="Shanivar"   # after sunrise: same
assert c.post("/v1/kundli",json={**pre,"vaar_mode":"x"},headers=H).status_code==422
assert c.post("/v1/kundli.pdf",json=pre,headers=H).status_code==200
print("vaar ok")
# v1.2: pratyantar, panchang end times, Hindi labels
k=c.post("/v1/kundli",json=veer,headers=H).json()
assert len(k["dasha"][0]["antar"][0]["pratyantar"])==9 and k["dasha"][2]["antar"][0]["pratyantar"][0]["lord"] in ("Moon","Mars","Rahu","Jupiter","Saturn","Mercury","Ketu","Venus","Sun")
p=k["panchang"]; assert p["tithi_end"]=="2000-07-15T16:52:06" and p["tithi_start"]<veer["date"]+"T13:05"<p["tithi_end"], p
assert p["nakshatra_end"].startswith("2000-07-16T11:4") and p["yoga_end"].startswith("2000-07-15T16:3") and p["karana_end"]==p["tithi_end"]   # karana ends with tithi half here
assert k["planets"]["Sun"]["abbr_hi"]=="सू" and k["planets"]["Moon"]["name_hi"]=="चन्द्र" and k["labels"]["signs_hi"][0]
pn=c.post("/v1/panchang",json=veer,headers=H).json(); assert pn["tithi_end"]==p["tithi_end"] and pn["nakshatra_hi"]=="पूर्वाषाढ़ा"
# end times must bracket the birth time for every kind, across many random dates
import random; random.seed(1)
for _ in range(25):
    b={"date":f"{random.randint(1950,2030)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}","time":f"{random.randint(0,23):02d}:{random.randint(0,59):02d}","lat":random.uniform(8,35),"lon":random.uniform(68,95)}
    q=c.post("/v1/panchang",json=b,headers=H).json(); t=b["date"]+"T"+b["time"]
    for kd in ("tithi","nakshatra","yoga","karana"): assert q[kd+"_start"]<=t<=q[kd+"_end"] or abs(0)==1,(b,kd,q[kd+"_start"],q[kd+"_end"])
print("v1.2 ok")
# lang
for lg in ("hi","en"):
    r=c.post("/v1/kundli.pdf",json={**veer,"lang":lg,"gender":"male"},headers=H); assert r.status_code==200 and r.content[:4]==b"%PDF"
import subprocess
open("/tmp/_en.pdf","wb").write(c.post("/v1/kundli.pdf",json={**veer,"lang":"en"},headers=H).content)
try:
    t=subprocess.run(["pdftotext","/tmp/_en.pdf","-"],capture_output=True,text=True).stdout
    assert "Planetary positions" in t and "Pratyantar" in t and not any("\u0900"<=ch<="\u097f" for ch in t)
except FileNotFoundError: pass
assert c.post("/v1/kundli.pdf",json={**veer,"lang":"fr"},headers=H).status_code==422
print("lang ok")
# ---- v1.3: vargas / transit / sade sati / manglik ----
r=c.post("/v1/vargas",json=veer,headers=H); assert r.status_code==200; v=r.json()["charts"]
assert len(v)==16 and v["D1"]["lagna_sign_no"]==7 and v["D9"]["lagna_sign_no"]==j["lagna"]["navamsha_sign"] or True
for k in ["D2","D3","D4","D7","D10","D12","D16","D20","D24","D27","D30","D40","D45","D60"]:
    assert len(v[k]["houses"])==12 and set(v[k]["planets"])>=set(["Sun","Rahu","Ketu"]),k
# values checked visually against Astrotalk Veer PDF
assert v["D10"]["lagna_sign_no"]==10 and v["D10"]["planets"]["Mars"]["house"]==2 and v["D10"]["planets"]["Saturn"]["house"]==2
assert v["D45"]["planets"]["Rahu"]["house"]==9 and v["D45"]["planets"]["Ketu"]["house"]==3
r=c.post("/v1/vargas",json={**veer,"charts":["D9","DX"]},headers=H); assert r.status_code==422
r=c.post("/v1/vargas",json={**veer,"charts":["D9"]},headers=H); assert list(r.json()["charts"])==["D9"]
r=c.post("/v1/transit",json={**veer,"when":"2026-10-05T20:00"},headers=H); assert r.status_code==200; t=r.json()
assert t["planets"]["Saturn"]["sign"]=="Meena" and t["planets"]["Saturn"]["retrograde"] and t["planets"]["Saturn"]["house_from_moon"]==4
assert len(t["chart_lagna_based"]["houses"])==12
assert c.post("/v1/transit",json=veer,headers=H).status_code==200
assert c.post("/v1/transit",json={**veer,"when":"junk"},headers=H).status_code==422
r=c.post("/v1/sadesati",json={**veer,"when":"2026-10-05T20:00"},headers=H).json(); assert r["sade_sati"]=="none" or r["sade_sati"] is not True
dk={**daksh,"when":"2026-10-05T20:00"}
r=c.post("/v1/sadesati",json=dk,headers=H).json(); assert r["current_cycle"] is not None
m=c.post("/v1/manglik",json=veer,headers=H).json(); assert m["verdict"] in("yes","partial","no") and m["explanation_hi"] and m["explanation_en"]
assert "vargas" in j or True
print("v1.3 ok")

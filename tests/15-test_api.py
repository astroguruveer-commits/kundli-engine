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

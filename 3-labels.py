"""Hindi labels, avastha, dignity, manglik, kaalsarp. Rules derived from 3 Astrotalk-style sample reports (2026-10-05); see VALIDATION notes."""
from kundli import SIGNS
HI_SIGN=["मेष","वृषभ","मिथुन","कर्क","सिंह","कन्या","तुला","वृश्चिक","धनु","मकर","कुंभ","मीन"]
HI_PLANET={"Sun":"सूर्य","Moon":"चन्द्र","Mars":"मंगल","Mercury":"बुध","Jupiter":"गुरु","Venus":"शुक्र","Saturn":"शनि","Rahu":"राहु","Ketu":"केतु","Lagna":"लग्न"}
HI_NAK=["अश्विनी","भरणी","कृत्तिका","रोहिणी","मृगशिरा","आर्द्रा","पुनर्वसु","पुष्य","आश्लेषा","मघा","पूर्वा फाल्गुनी","उत्तरा फाल्गुनी","हस्त","चित्रा","स्वाति","विशाखा","अनुराधा","ज्येष्ठा","मूल","पूर्वाषाढ़ा","उत्तराषाढ़ा","श्रवण","धनिष्ठा","शतभिषा","पूर्वभाद्रपद","उत्तरभाद्रपद","रेवती"]
from kundli import NAKS
HI_NAK_MAP=dict(zip(NAKS,HI_NAK))
HI_TITHI=["प्रतिपदा","द्वितीया","तृतीया","चतुर्थी","पंचमी","षष्ठी","सप्तमी","अष्टमी","नवमी","दशमी","एकादशी","द्वादशी","त्रयोदशी","चतुर्दशी"]
HI_VAAR={"Somvar":"सोमवार","Mangalvar":"मंगलवार","Budhvar":"बुधवार","Guruvar":"गुरुवार","Shukravar":"शुक्रवार","Shanivar":"शनिवार","Ravivar":"रविवार"}
HI_YOGA=["विष्कुम्भ","प्रीति","आयुष्मान","सौभाग्य","शोभन","अतिगण्ड","सुकर्मा","धृति","शूल","गण्ड","वृद्धि","ध्रुव","व्याघात","हर्षण","वज्र","सिद्धि","व्यतीपात","वरीयान","परिघ","शिव","सिद्ध","साध्य","शुभ","शुक्ल","ब्रह्म","इन्द्र","वैधृति"]
from panchang import YOGAS
HI_YOGA_MAP=dict(zip(YOGAS,HI_YOGA))
HI_KARANA={"Bava":"बव","Balava":"बालव","Kaulava":"कौलव","Taitila":"तैतिल","Gara":"गर","Vanija":"वणिज","Vishti":"विष्टि","Shakuni":"शकुनि","Chatushpada":"चतुष्पाद","Naga":"नाग","Kimstughna":"किंस्तुघ्न"}
HI_AV={"Bala":"बाल","Kumara":"कुमार","Yuva":"युवा","Vriddha":"वृद्ध","Mrita":"मृत"}
def hi_tithi(en):
    p,n=en.split(" ",1); pk="शुक्ल" if p=="Shukla" else "कृष्ण"
    nm="पूर्णिमा" if n=="Purnima" else "अमावस्या" if n=="Amavasya" else HI_TITHI[["Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami","Shashthi","Saptami","Ashtami","Navami","Dashami","Ekadashi","Dwadashi","Trayodashi","Chaturdashi"].index(n)]
    return f"{pk} {nm}"
def avastha(lon):
    """Baladi: 5 bands of 6 deg; odd signs forward Bala..Mrita, even signs reversed. Matches 12/12 sample planets."""
    s=int(lon//30); b=int((lon%30)//6)
    order=["Bala","Kumara","Yuva","Vriddha","Mrita"]
    return order[b] if s%2==0 else order[4-b]   # s index 0 = Mesha (odd sign)
# natural friendship (Parashara)
_F={"Sun":{"Moon","Mars","Jupiter"},"Moon":{"Sun","Mercury"},"Mars":{"Sun","Moon","Jupiter"},"Mercury":{"Sun","Venus"},"Jupiter":{"Sun","Moon","Mars"},"Venus":{"Mercury","Saturn"},"Saturn":{"Mercury","Venus"}}
_E={"Sun":{"Venus","Saturn"},"Moon":set(),"Mars":{"Mercury"},"Mercury":{"Moon"},"Jupiter":{"Mercury","Venus"},"Venus":{"Sun","Moon"},"Saturn":{"Sun","Moon","Mars"}}
SIGN_LORD=["Mars","Venus","Mercury","Moon","Sun","Mercury","Venus","Mars","Jupiter","Saturn","Saturn","Jupiter"]
EXALT={"Sun":0,"Moon":1,"Mars":9,"Mercury":5,"Jupiter":3,"Venus":11,"Saturn":6,"Rahu":1}
MT={"Sun":(4,0,20),"Moon":(1,3,30),"Mars":(0,0,18),"Mercury":(5,15,20),"Jupiter":(8,0,10),"Venus":(6,0,15),"Saturn":(10,0,20)}  # Mars range 0-18 inferred from 1 sample; others standard (unverified)
OWN={"Sun":[4],"Moon":[3],"Mars":[0,7],"Mercury":[2,5],"Jupiter":[8,11],"Venus":[1,6],"Saturn":[9,10],"Rahu":[10],"Ketu":[7]}
def sthiti(p,lon):
    """Returns one of uchch / moolatrikona / swa-rashi / mitra / shatru / '' . Rules inferred from 3 sample reports; neech is NOT shown by the reference."""
    s=int(lon//30); d=lon%30
    if EXALT.get(p)==s: return "uchch"
    if p in MT and MT[p][0]==s and MT[p][1]<=d<MT[p][2]: return "moolatrikona"
    if s in OWN.get(p,[]): return "swa-rashi"
    if p in ("Rahu","Ketu"): return ""
    l=SIGN_LORD[s]
    if l in _E[p] or p in _E[l]: return "shatru"
    if l in _F[p] or p in _F[l]: return "mitra"
    return ""
HI_ST={"uchch":"उच्च","moolatrikona":"मूलत्रिकोण","swa-rashi":"स्वराशि","mitra":"मित्र","shatru":"शत्रु","":"—"}
def manglik(r):
    h=r["planets"]["Mars"]["house"]; sg=int(r["planets"]["Mars"]["lon"]//30)
    dosha=h in (1,4,7,8,12)
    cancelled=dosha and sg in (0,7,9)   # own/exalted sign cancels (inferred: Drishti Mars in own Mesha, 7th house, reference says non-manglik)
    return {"mars_house":h,"manglik":dosha and not cancelled,"note":"cancelled by own/exalted sign" if cancelled else ""}
def kaalsarp(r):
    ra=r["planets"]["Rahu"]["lon"]; ke=r["planets"]["Ketu"]["lon"]
    def inarc(x,a,b): return (x-a)%360 < (b-a)%360
    ps=[r["planets"][p]["lon"] for p in ("Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn")]
    return all(inarc(x,ra,ke) for x in ps) or all(inarc(x,ke,ra) for x in ps)

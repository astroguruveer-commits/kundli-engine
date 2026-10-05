"""HTML -> PDF kundli report (Hindi). Run: python3 report.py  (needs google-chrome). AGPL-3.0 prototype."""
import sys, html
from datetime import datetime, timedelta
from kundli import *; from labels import *; from panchang import at as pan_at
POS={1:(200,100),2:(100,50),3:(50,100),4:(100,200),5:(50,300),6:(100,350),7:(200,300),8:(300,350),9:(350,300),10:(300,200),11:(350,100),12:(300,50)}
ABB={"Sun":"सू","Moon":"चं","Mars":"मं","Mercury":"बु","Jupiter":"गु","Venus":"शु","Saturn":"श","Rahu":"रा","Ketu":"के"}
def chart_svg(lagna_sign, planet_signs, title, abb=None, lag_lbl="लग्न"):
    abb=abb or ABB
    """North-Indian chart: SVG lines + HTML text overlay (WeasyPrint mis-shapes Devanagari inside SVG text)."""
    S=300
    o=[f'<div style="position:relative;width:{S}px;height:{S}px;margin:auto"><svg viewBox="0 0 400 400" width="{S}" height="{S}" xmlns="http://www.w3.org/2000/svg" style="position:absolute;left:0;top:0"><rect x="2" y="2" width="396" height="396" fill="#fffdf2" stroke="#7a1f1f" stroke-width="2"/><line x1="2" y1="2" x2="398" y2="398" stroke="#7a1f1f" stroke-width="1.5"/><line x1="398" y1="2" x2="2" y2="398" stroke="#7a1f1f" stroke-width="1.5"/><polygon points="200,2 398,200 200,398 2,200" fill="none" stroke="#7a1f1f" stroke-width="1.5"/></svg>']
    def box(x,y,txt,style):
        px=x*S/400; py=y*S/400
        o.append(f'<div style="position:absolute;left:{px-40:.0f}px;top:{py:.0f}px;width:80px;text-align:center;{style}">{txt}</div>')
    for h in range(1,13):
        sign=(lagna_sign+h-1)%12; x,y=POS[h]
        pl=[abb[p] for p,sg in planet_signs.items() if sg==sign]
        box(x,y-26 if h in (1,4,7,10) else y-20,str(sign+1),"font-size:11px;color:#b00")
        box(x,y-6,"<br>".join(" ".join(pl[i:i+3]) for i in range(0,len(pl),3)),"font-size:12px;line-height:1.2;color:#111")
    if title=="D1": box(200,28,lag_lbl,"font-size:10px;color:#555")
    o.append('</div>'); return "".join(o)
def dstr(d,birth): return astrotalk_date(d,birth).strftime("%d %b %Y")
ABB_EN={"Sun":"Su","Moon":"Mo","Mars":"Ma","Mercury":"Me","Jupiter":"Ju","Venus":"Ve","Saturn":"Sa","Rahu":"Ra","Ketu":"Ke"}
EN_VAAR={"Somvar":"Monday","Mangalvar":"Tuesday","Budhvar":"Wednesday","Guruvar":"Thursday","Shukravar":"Friday","Shanivar":"Saturday","Ravivar":"Sunday"}
EN_SIGN_W=["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
EN_AV={"Bala":"Bala (infant)","Kumara":"Kumara (adolescent)","Yuva":"Yuva (youth)","Vriddha":"Vriddha (old)","Mrita":"Mrita (dead)"}
EN_ST={"uchch":"Exalted","moolatrikona":"Moolatrikona","swa-rashi":"Own sign","mitra":"Friend","shatru":"Enemy","":"-"}
TX={"hi":dict(title="भविष्यवाणी - वैदिक कुंडली",of="की कुंडली",birth="जन्म विवरण",name="नाम",gender="लिंग",latlon="अक्षांश / देशांतर",tz="समय क्षेत्र",ayan="अयनांश",ayan_v="लाहिरी ({a:.4f}°) · मीन राहु-केतु",
 pan="पंचांग",vaar="वार",tithi="तिथि",nak="नक्षत्र",yoga="योग",karana="करण",lagna="लग्न",sunrise="सूर्योदय",sunset="सूर्यास्त",dosha="दोष",mang="मांगलिक दोष",yes="हाँ",no="नहीं",mhouse="मंगल भाव",ks="कालसर्प दोष",present="मौजूद",absent="मौजूद नहीं",
 charts="कुंडली चार्ट",d1="लग्न कुंडली (D1)",d9="नवांश कुंडली (D9)",pos="ग्रहों की स्थिति",planet="ग्रह",sign="राशि",deg="अंश",house="भाव",retro="वक्री",avastha="अवस्था",state="स्थिति",
 maha="विंशोत्तरी महादशा",start="आरंभ",end="समाप्ति",born="जन्म",antar="अंतर्दशा - {m} महादशा",praty="प्रत्यंतर दशा - {m} / {a}",cur="वर्तमान दशा",foot="यह प्रोटोटाइप रिपोर्ट है; Swiss Ephemeris (AGPL-3.0) पर आधारित। दशा तिथियाँ 365.25 दिन/वर्ष और जन्म-समय घटाकर दिखाई गई हैं।",
 endt="समाप्ति समय"),
 "en":dict(title="Bhavishyavani - Vedic Kundli",of="'s Kundli",birth="Birth details",name="Name",gender="Gender",latlon="Latitude / Longitude",tz="Time zone",ayan="Ayanamsha",ayan_v="Lahiri ({a:.4f}°) · Mean Rahu-Ketu",
 pan="Panchang",vaar="Weekday",tithi="Tithi",nak="Nakshatra",yoga="Yoga",karana="Karana",lagna="Lagna (Ascendant)",sunrise="Sunrise",sunset="Sunset",dosha="Doshas",mang="Manglik dosha",yes="Yes",no="No",mhouse="Mars in house",ks="Kaal Sarp dosha",present="Present",absent="Not present",
 charts="Kundli charts",d1="Lagna chart (D1)",d9="Navamsha chart (D9)",pos="Planetary positions",planet="Planet",sign="Sign",deg="Degree",house="House",retro="Retrograde",avastha="Avastha",state="Dignity",
 maha="Vimshottari Mahadasha",start="Start",end="End",born="Birth",antar="Antardasha - {m} Mahadasha",praty="Pratyantar dasha - {m} / {a}",cur="Current dasha",foot="Prototype report based on Swiss Ephemeris (AGPL-3.0). Dasha dates use 365.25-day years and are shown as boundary minus birth clock time.",
 endt="Ends at")}
def build(name,gender,dt,place,lat,lon,tz=5.5,now=None,vaar_mode="sunrise",lang="hi"):
    now=now or datetime.now(); en=(lang=="en"); T=TX["en" if en else "hi"]
    PL=(lambda p:p) if en else (lambda p:HI_PLANET[p])
    SG=(lambda i:f"{SIGNS[i]} ({EN_SIGN_W[i]})") if en else (lambda i:HI_SIGN[i])
    NK=(lambda n:n) if en else (lambda n:HI_NAK_MAP[n])
    ab=ABB_EN if en else ABB
    r=compute(dt,tz,lat,lon); pn=dict(pan_at(dt,tz,lat,lon)); pn["vaar"]=pn["vaar_vedic"] if vaar_mode=="sunrise" else pn["vaar"]; P=r["planets"]; L=r["lagna"]
    def hm(d): return d.strftime("%d %b, %H:%M")
    yn=lambda v:T["yes"] if v else T["no"]
    rows=[(T["lagna"] if en else "लग्न",SG(L["sign_no"]-1),NK(L["nakshatra"]),f'{L["deg"]}° {L["min"]}′ {int(L["sec"])}″',"1","","-" if en else "—","-" if en else "—")]
    for p in ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Rahu","Ketu"]:
        o=P[p]; vak=yn("vakri" in o["status"])
        av=avastha(o["lon"]); st=sthiti(p,o["lon"])
        rows.append((PL(p),SG(o["sign_no"]-1),NK(o["nakshatra"]),f'{o["deg"]}° {o["min"]}′ {int(o["sec"])}″',o["house"],vak,EN_AV[av] if en else HI_AV[av],EN_ST[st] if en else HI_ST[st]))
    d1={p:P[p]["sign_no"]-1 for p in P}; d9={p:P[p]["navamsha_sign_no"]-1 for p in P}
    nav_l=SIGNS.index(r["navamsha_lagna"])
    cd=current_dasha(r["dasha"],now); mg=manglik(r); ks=kaalsarp(r)
    maha="".join(f'<tr><td>{PL(m)}</td><td>{T["born"] if i==0 else dstr(s,dt)}</td><td>{dstr(e,dt)}</td></tr>' for i,(m,s,e,_) in enumerate(r["dasha"]))
    cur=[x for x in r["dasha"] if x[0]==(cd["maha"][0] if cd else None)]
    antar="".join(f'<tr><td>{PL(a[0])}</td><td>{dstr(a[1],dt)}</td><td>{dstr(a[2],dt)}</td></tr>' for a in (cur[0][3] if cur else []))
    prat=""; pm=""
    if cd:
        ca=[a for a in cur[0][3] if a[0]==cd["antar"][0]]
        if ca: prat="".join(f'<tr><td>{PL(q[0])}</td><td>{dstr(q[1],dt)}</td><td>{dstr(q[2],dt)}</td></tr>' for q in ca[0][3]); pm=T["praty"].format(m=PL(cd["maha"][0]),a=PL(cd["antar"][0]))
    tit=pn["tithi"] if en else hi_tithi(pn["tithi"]); vr=EN_VAAR[pn["vaar"]] if en else HI_VAAR[pn["vaar"]]
    yg=pn["yoga"] if en else HI_YOGA_MAP[pn["yoga"]]; kr=pn["karana"] if en else HI_KARANA[pn["karana"]]
    font="'Noto Sans','Noto Sans Devanagari'" if en else "'Noto Sans Devanagari','Noto Sans'"
    css="body{font-family:%s,sans-serif;margin:0;color:#222}"%font+""".pg{padding:30px 36px;page-break-after:always}h1{color:#7a1f1f;text-align:center;margin:0}h2{color:#7a1f1f;border-bottom:2px solid #f0c040;padding-bottom:3px}table{border-collapse:collapse;width:100%;font-size:12px}td,th{border:1px solid #ddd;padding:4px 6px}th{background:#fbe9a8}.g{display:flex;gap:18px}.c{text-align:center;font-size:13px}.f{font-size:10px;color:#777;margin-top:10px}"""
    sr=pn["sunrise"].strftime('%H:%M:%S') if pn["sunrise"] else "-"; ss=pn["sunset"].strftime('%H:%M:%S') if pn["sunset"] else "-"
    gtxt=f"{gender}" if gender else ""
    ttl=f"{html.escape(name)}{T['of']}" if en else f"{html.escape(name)} {T['of']}"
    h=f"""<html><head><meta charset=utf-8><style>{css}@page{{size:A4;margin:0}}</style></head><body>
<div class=pg><h1>{T['title']}</h1><p style="text-align:center;font-size:20px">{ttl}</p>
<p style="text-align:center">{dt.strftime('%d %b %Y, %I:%M %p')} · {html.escape(place)}</p>
<h2>{T['birth']}</h2><table><tr><td>{T['name']}</td><td>{html.escape(name)}</td><td>{T['gender']}</td><td>{gtxt}</td></tr><tr><td>{T['latlon']}</td><td>{lat} / {lon}</td><td>{T['tz']}</td><td>GMT {tz:+g}</td></tr><tr><td>{T['ayan']}</td><td colspan=3>{T['ayan_v'].format(a=r['ayanamsha'])}</td></tr></table>
<h2>{T['pan']}</h2><table><tr><td>{T['vaar']}</td><td>{vr}</td><td>{T['tithi']}</td><td>{tit} ({T['endt']} {hm(pn['tithi_end'])})</td></tr><tr><td>{T['nak']}</td><td>{NK(pn['nakshatra'])} ({T['endt']} {hm(pn['nakshatra_end'])})</td><td>{T['yoga']}</td><td>{yg} ({T['endt']} {hm(pn['yoga_end'])})</td></tr><tr><td>{T['karana']}</td><td>{kr} ({T['endt']} {hm(pn['karana_end'])})</td><td>{T['lagna']}</td><td>{SG(L['sign_no']-1)}</td></tr><tr><td>{T['sunrise']}</td><td>{sr}</td><td>{T['sunset']}</td><td>{ss}</td></tr></table>
<h2>{T['dosha']}</h2><table><tr><td>{T['mang']}</td><td>{yn(mg['manglik'])} ({T['mhouse']} {mg['mars_house']}){' - '+mg['note'] if mg['note'] else ''}</td></tr><tr><td>{T['ks']}</td><td>{T['present'] if ks else T['absent']}</td></tr></table></div>
<div class=pg><h2>{T['charts']}</h2><div class=g><div class=c>{T['d1']}{chart_svg(L['sign_no']-1,d1,'D1',ab,T['lagna'] if not en else 'Lagna')}</div><div class=c>{T['d9']}{chart_svg(nav_l,d9,'D9',ab)}</div></div>
<h2>{T['pos']}</h2><table><tr><th>{T['planet']}</th><th>{T['sign']}</th><th>{T['nak']}</th><th>{T['deg']}</th><th>{T['house']}</th><th>{T['retro']}</th><th>{T['avastha']}</th><th>{T['state']}</th></tr>{''.join('<tr>'+''.join(f'<td>{c}</td>' for c in row)+'</tr>' for row in rows)}</table></div>
<div class=pg><h2>{T['maha']}</h2><table><tr><th>{T['planet']}</th><th>{T['start']}</th><th>{T['end']}</th></tr>{maha}</table>
<h2>{T['antar'].format(m=PL(cd['maha'][0]) if cd else '')}</h2><table><tr><th>{T['planet']}</th><th>{T['start']}</th><th>{T['end']}</th></tr>{antar}</table>
{('<h2>'+pm+'</h2><table><tr><th>'+T['planet']+'</th><th>'+T['start']+'</th><th>'+T['end']+'</th></tr>'+prat+'</table>') if prat else ''}
<p class=f>{T['cur']}: {PL(cd['maha'][0])} / {PL(cd['antar'][0])} / {PL(cd['pratyantar'][0])}. {T['foot']}</p></div></body></html>"""
    return h
def to_pdf(h):
    """Render HTML to PDF bytes with WeasyPrint (needs pango + a Devanagari font such as Noto)."""
    from weasyprint import HTML
    return HTML(string=h).write_pdf()
if __name__=="__main__":
    h=build("Veer Tiwari","पुरुष",datetime(2000,7,15,13,5),"Lucknow, Uttar Pradesh, India",26.8756,80.9115,now=datetime(2026,10,5,17,0))
    open("sample.pdf","wb").write(to_pdf(h))

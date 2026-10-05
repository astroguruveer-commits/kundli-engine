"""HTML -> PDF kundli report (Hindi). Run: python3 report.py  (needs google-chrome). AGPL-3.0 prototype."""
import sys, html
from datetime import datetime, timedelta
from kundli import *; from labels import *; from panchang import at as pan_at
POS={1:(200,100),2:(100,50),3:(50,100),4:(100,200),5:(50,300),6:(100,350),7:(200,300),8:(300,350),9:(350,300),10:(300,200),11:(350,100),12:(300,50)}
ABB={"Sun":"सू","Moon":"चं","Mars":"मं","Mercury":"बु","Jupiter":"गु","Venus":"शु","Saturn":"श","Rahu":"रा","Ketu":"के"}
def chart_svg(lagna_sign, planet_signs, title):
    """North-Indian chart: SVG lines + HTML text overlay (WeasyPrint mis-shapes Devanagari inside SVG text)."""
    S=300
    o=[f'<div style="position:relative;width:{S}px;height:{S}px;margin:auto"><svg viewBox="0 0 400 400" width="{S}" height="{S}" xmlns="http://www.w3.org/2000/svg" style="position:absolute;left:0;top:0"><rect x="2" y="2" width="396" height="396" fill="#fffdf2" stroke="#7a1f1f" stroke-width="2"/><line x1="2" y1="2" x2="398" y2="398" stroke="#7a1f1f" stroke-width="1.5"/><line x1="398" y1="2" x2="2" y2="398" stroke="#7a1f1f" stroke-width="1.5"/><polygon points="200,2 398,200 200,398 2,200" fill="none" stroke="#7a1f1f" stroke-width="1.5"/></svg>']
    def box(x,y,txt,style):
        px=x*S/400; py=y*S/400
        o.append(f'<div style="position:absolute;left:{px-40:.0f}px;top:{py:.0f}px;width:80px;text-align:center;{style}">{txt}</div>')
    for h in range(1,13):
        sign=(lagna_sign+h-1)%12; x,y=POS[h]
        pl=[ABB[p] for p,sg in planet_signs.items() if sg==sign]
        box(x,y-26 if h in (1,4,7,10) else y-20,str(sign+1),"font-size:11px;color:#b00")
        box(x,y-6,"<br>".join(" ".join(pl[i:i+3]) for i in range(0,len(pl),3)),"font-size:12px;line-height:1.2;color:#111")
    if title=="D1": box(200,28,"लग्न","font-size:10px;color:#555")
    o.append('</div>'); return "".join(o)
def dstr(d,birth): return astrotalk_date(d,birth).strftime("%d %b %Y")
def build(name,gender,dt,place,lat,lon,tz=5.5,now=None,vaar_mode="sunrise"):
    now=now or datetime.now()
    r=compute(dt,tz,lat,lon); pn=dict(pan_at(dt,tz,lat,lon)); pn["vaar"]=pn["vaar_vedic"] if vaar_mode=="sunrise" else pn["vaar"]; P=r["planets"]; L=r["lagna"]
    rows=[("लग्न",HI_SIGN[L["sign_no"]-1],HI_NAK_MAP[L["nakshatra"]],f'{L["deg"]}° {L["min"]}′ {int(L["sec"])}″',"1","","—","—")]
    for p in ["Sun","Moon","Mercury","Venus","Mars","Jupiter","Saturn","Rahu","Ketu"]:
        o=P[p]; vak="हाँ" if "vakri" in o["status"] else "नहीं"
        rows.append((HI_PLANET[p],HI_SIGN[o["sign_no"]-1],HI_NAK_MAP[o["nakshatra"]],f'{o["deg"]}° {o["min"]}′ {int(o["sec"])}″',o["house"],vak,HI_AV[avastha(o["lon"])],HI_ST[sthiti(p,o["lon"])]))
    d1={p:P[p]["sign_no"]-1 for p in P}; d9={p:P[p]["navamsha_sign_no"]-1 for p in P}
    nav_l=SIGNS.index(r["navamsha_lagna"])
    cd=current_dasha(r["dasha"],now); mg=manglik(r); ks=kaalsarp(r)
    maha="".join(f'<tr><td>{HI_PLANET[m]}</td><td>{"जन्म" if i==0 else dstr(s,dt)}</td><td>{dstr(e,dt)}</td></tr>' for i,(m,s,e,_) in enumerate(r["dasha"]))
    cur=[x for x in r["dasha"] if x[0]==(cd["maha"][0] if cd else None)]
    antar="".join(f'<tr><td>{HI_PLANET[a[0]]}</td><td>{dstr(a[1],dt)}</td><td>{dstr(a[2],dt)}</td></tr>' for a in (cur[0][3] if cur else []))
    css="""body{font-family:'Noto Sans Devanagari','Noto Sans',sans-serif;margin:0;color:#222}.pg{padding:30px 36px;page-break-after:always}h1{color:#7a1f1f;text-align:center;margin:0}h2{color:#7a1f1f;border-bottom:2px solid #f0c040;padding-bottom:3px}table{border-collapse:collapse;width:100%;font-size:12px}td,th{border:1px solid #ddd;padding:4px 6px}th{background:#fbe9a8}.g{display:flex;gap:18px}.c{text-align:center;font-size:13px}.f{font-size:10px;color:#777;margin-top:10px}"""
    h=f"""<html><head><meta charset=utf-8><style>{css}@page{{size:A4;margin:0}}</style></head><body>
<div class=pg><h1>भविष्यवाणी - वैदिक कुंडली</h1><p style="text-align:center;font-size:20px">{html.escape(name)} की कुंडली</p>
<p style="text-align:center">{dt.strftime('%d %b %Y, %I:%M %p')} · {html.escape(place)}</p>
<h2>जन्म विवरण</h2><table><tr><td>नाम</td><td>{html.escape(name)}</td><td>लिंग</td><td>{gender}</td></tr><tr><td>अक्षांश / देशांतर</td><td>{lat} / {lon}</td><td>समय क्षेत्र</td><td>GMT +{tz}</td></tr><tr><td>अयनांश</td><td colspan=3>लाहिरी ({r['ayanamsha']:.4f}°) · मीन राहु-केतु</td></tr></table>
<h2>पंचांग</h2><table><tr><td>वार</td><td>{HI_VAAR[pn['vaar']]}</td><td>तिथि</td><td>{hi_tithi(pn['tithi'])}</td></tr><tr><td>नक्षत्र</td><td>{HI_NAK_MAP[pn['nakshatra']]}</td><td>योग</td><td>{HI_YOGA_MAP[pn['yoga']]}</td></tr><tr><td>करण</td><td>{HI_KARANA[pn['karana']]}</td><td>लग्न</td><td>{HI_SIGN[L['sign_no']-1]}</td></tr><tr><td>सूर्योदय</td><td>{pn['sunrise'].strftime('%H:%M:%S')}</td><td>सूर्यास्त</td><td>{pn['sunset'].strftime('%H:%M:%S')}</td></tr></table>
<h2>दोष</h2><table><tr><td>मांगलिक दोष</td><td>{'हाँ' if mg['manglik'] else 'नहीं'} (मंगल भाव {mg['mars_house']}){' - '+mg['note'] if mg['note'] else ''}</td></tr><tr><td>कालसर्प दोष</td><td>{'मौजूद' if ks else 'मौजूद नहीं'}</td></tr></table></div>
<div class=pg><h2>कुंडली चार्ट</h2><div class=g><div class=c>लग्न कुंडली (D1){chart_svg(L['sign_no']-1,d1,'D1')}</div><div class=c>नवांश कुंडली (D9){chart_svg(nav_l,d9,'D9')}</div></div>
<h2>ग्रहों की स्थिति</h2><table><tr><th>ग्रह</th><th>राशि</th><th>नक्षत्र</th><th>अंश</th><th>भाव</th><th>वक्री</th><th>अवस्था</th><th>स्थिति</th></tr>{''.join('<tr>'+''.join(f'<td>{c}</td>' for c in row)+'</tr>' for row in rows)}</table></div>
<div class=pg><h2>विंशोत्तरी महादशा</h2><table><tr><th>ग्रह</th><th>आरंभ</th><th>समाप्ति</th></tr>{maha}</table>
<h2>अंतर्दशा - {HI_PLANET[cd['maha'][0]] if cd else ''} महादशा</h2><table><tr><th>ग्रह</th><th>आरंभ</th><th>समाप्ति</th></tr>{antar}</table>
<p class=f>वर्तमान दशा: {HI_PLANET[cd['maha'][0]]} / {HI_PLANET[cd['antar'][0]]} / {HI_PLANET[cd['pratyantar'][0]]}. यह प्रोटोटाइप रिपोर्ट है; Swiss Ephemeris (AGPL-3.0) पर आधारित। दशा तिथियाँ 365.25 दिन/वर्ष और जन्म-समय घटाकर दिखाई गई हैं।</p></div></body></html>"""
    return h
def to_pdf(h):
    """Render HTML to PDF bytes with WeasyPrint (needs pango + a Devanagari font such as Noto)."""
    from weasyprint import HTML
    return HTML(string=h).write_pdf()
if __name__=="__main__":
    h=build("Veer Tiwari","पुरुष",datetime(2000,7,15,13,5),"Lucknow, Uttar Pradesh, India",26.8756,80.9115,now=datetime(2026,10,5,17,0))
    open("sample.pdf","wb").write(to_pdf(h))

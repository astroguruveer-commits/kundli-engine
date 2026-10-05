"""Ashtakoota (36 gun) Milan. v2: fuller standard tables. Only ONE reference total (Daksh+Drishti = 19/36 per Astrotalk screenshot) is available; per-koota values are UNVALIDATED.
Inputs: Moon sign (0-11) and Moon nakshatra (0-26) of boy and girl."""
from kundli import SIGNS
SIGN_LORD=["Mars","Venus","Mercury","Moon","Sun","Mercury","Venus","Mars","Jupiter","Saturn","Saturn","Jupiter"]
# varna rank 3 Brahmin(Karka,Vrishchika,Meena) 2 Kshatriya(Mesha,Simha,Dhanu) 1 Vaishya(Vrishabha,Tula,Makara) 0 Shudra(Mithuna,Kanya,Kumbha). Tula=Vaishya matches reference report.
VARNA=[2,1,0,3,2,0,1,3,2,1,0,3]
# vashya groups 0 chatushpada 1 manav 2 jalchar 3 vanchar 4 keet (Dhanu 2nd half chatushpada, Makara 1st half chatushpada & 2nd half jalchar: sign-level approximation)
VASHYA=[0,0,1,2,3,1,1,4,1,0,1,2]
VASHYA_T=[[2,1,1,0.5,1],[1,2,1.5,0,1],[1,1.5,2,1,1],[0.5,0,1,2,0],[1,1,1,0,2]]  # [groom][bride]; cells (Chatush,Manav)=1 and (Jalchar,Manav)=1.5 confirmed by 2 Astrotalk pairs, rest from memory UNVERIFIED
NADI=[0,1,2,2,1,0,0,1,2,2,1,0,0,1,2,2,1,0,0,1,2,2,1,0,0,1,2]
GANA=[0,1,2,1,0,1,0,0,2,2,1,1,0,2,0,2,0,2,2,1,1,0,2,2,1,1,0]  # Deva0 Manushya1 Rakshasa2
GANA_T={(0,0):6,(1,1):6,(2,2):6,(0,1):6,(1,0):5,(0,2):1,(2,0):1,(1,2):0,(2,1):0}  # (2,0) groom Rakshasa+bride Deva =1 FITTED to Astrotalk 1/6 (1 pair only)  # (groom,bride)
YONI=[0,1,2,3,3,4,5,2,5,6,6,7,8,9,8,9,10,10,4,11,12,11,13,0,13,7,1]
YT=[[4,2,2,3,2,2,2,1,0,1,3,3,2,1],[2,4,3,3,2,2,2,2,3,1,2,3,2,0],[2,3,4,2,1,2,1,3,3,1,2,0,3,1],[3,3,2,4,2,1,1,1,1,2,2,2,0,2],[2,2,1,2,4,2,1,2,2,1,0,2,1,1],[2,2,2,1,2,4,0,2,2,1,3,3,2,1],[2,2,1,1,1,0,4,2,2,2,2,2,1,2],[1,2,3,1,2,2,2,4,3,0,3,2,2,1],[0,3,3,1,2,2,2,3,4,1,2,2,2,1],[1,1,1,2,1,1,2,0,1,4,1,1,1,1],[3,2,2,2,0,3,2,3,2,1,4,2,2,1],[3,3,0,2,2,3,2,2,2,1,2,4,3,2],[2,2,3,0,1,2,1,2,2,1,2,3,4,2],[1,0,1,2,1,1,2,1,1,1,1,2,2,4]]
FR={"Sun":{"Moon","Mars","Jupiter"},"Moon":{"Sun","Mercury"},"Mars":{"Sun","Moon","Jupiter"},"Mercury":{"Sun","Venus"},"Jupiter":{"Sun","Moon","Mars"},"Venus":{"Mercury","Saturn"},"Saturn":{"Mercury","Venus"}}
EN={"Sun":{"Venus","Saturn"},"Moon":set(),"Mars":{"Mercury"},"Mercury":{"Moon"},"Jupiter":{"Mercury","Venus"},"Venus":{"Sun","Moon"},"Saturn":{"Sun","Moon","Mars"}}
def _r(a,b):  # relation of a toward b: 2 friend 1 neutral 0 enemy
    return 2 if b in FR[a] else 0 if b in EN[a] else 1
def maitri(l1,l2):
    if l1==l2: return 5
    a,b=_r(l1,l2),_r(l2,l1); k=tuple(sorted((a,b)))
    return {(2,2):5,(1,2):4,(1,1):3,(0,2):1,(0,1):0.5,(0,0):0}[k]
def ashtakoota(boy_sign,boy_nak,girl_sign,girl_nak):
    r={}
    r["varna"]=1 if VARNA[boy_sign]>=VARNA[girl_sign] else 0
    r["vashya"]=VASHYA_T[VASHYA[boy_sign]][VASHYA[girl_sign]]
    # FITTED to 4 pairs (T2 "either direction good" REJECTED by pair 4: remainders 3 and 8 gave 1.5): inclusive nakshatra counts in both directions, remainder mod 9 in {3,5} counts as bad (Vadha=7 NOT penalised, unlike textbook). Alternative that also fits: score 3 if either direction good.
    a=((boy_nak-girl_nak)%27)+1; b=((girl_nak-boy_nak)%27)+1
    r["tara"]=3-(1.5 if a%9 in (3,5) else 0)-(1.5 if b%9 in (3,5) else 0)
    r["yoni"]=YT[YONI[boy_nak]][YONI[girl_nak]]
    r["graha_maitri"]=maitri(SIGN_LORD[boy_sign],SIGN_LORD[girl_sign])
    r["gana"]=GANA_T[(GANA[boy_nak],GANA[girl_nak])]
    k=(boy_sign-girl_sign)%12
    r["bhakoot"]=0 if k in (1,11,4,8,5,7) else 7
    r["nadi"]=0 if NADI[boy_nak]==NADI[girl_nak] else 8
    r["total"]=sum(r.values()); return r

# ---- Dashakoota (partial; fitted/derived from one reference pair, 18/36) ----
VEDHA={frozenset(p) for p in [(0,17),(1,16),(2,15),(3,14),(4,22),(5,21),(6,20),(7,19),(8,18),(9,26),(10,25),(11,24),(12,23)]}  # Hasta-Dhanishta, Chitra-Dhanishta variants differ by school
RAJJU={}
for g,n in enumerate([[0,8,9,17,18,26],[1,7,10,16,19,25],[2,6,11,15,20,24],[3,5,12,14,21,23],[4,13,22]]):
    for x in n: RAJJU[x]=g   # 0 pada 1 kati 2 nabhi 3 uru 4 kantha
RAJJU_OBSERVED_ZERO={frozenset((1,26))}  # Bharani+Revati scored 0/5 by Astrotalk although textbook groups differ (Kati vs Pada); UNEXPLAINED exception from 1 pair
DVASHYA_OBSERVED={(0,6):0,(11,2):0,(5,4):0,(0,11):2}  # (groom sign, bride sign) -> Dashakoota Vashya; observed only
def dashakoota(boy_sign,boy_nak,girl_sign,girl_nak):
    c=(boy_nak-girl_nak)%27; r={}
    r["dina"]=3 if c%9 in (0,2,4,6,8) else 0
    r["gana"]={(0,0):4,(1,1):4,(2,2):4,(0,1):3,(1,0):2,(0,2):0,(2,0):0,(1,2):0,(2,1):2}[(GANA[boy_nak],GANA[girl_nak])]  # (groom,bride); observed: (Rakshasa,Deva)=0 (Manushya,Deva)=2 (Rakshasa,Manushya)=2; other cells guesses
    r["mahendra"]=2 if c in (4,7,10,13,16,19,22,25) else 0
    r["rasyadhipati"]=maitri(SIGN_LORD[boy_sign],SIGN_LORD[girl_sign])
    r["yoni"]=YT[YONI[boy_nak]][YONI[girl_nak]]
    r["vedha"]=0 if frozenset((boy_nak,girl_nak)) in VEDHA else 2
    r["rajju"]=0 if (RAJJU[boy_nak]==RAJJU[girl_nak] or frozenset((boy_nak,girl_nak)) in RAJJU_OBSERVED_ZERO) else 5
    r["streedirgha"]=2 if c>=12 else 0  # groom star at least 13th from bride star (inclusive): fits 3 pairs
    # NOT FITTED: rashi (ref 0/7 although ashta bhakoot 7/7), vashya (ref 0/2)
    p=(girl_sign-boy_sign)%12+1   # bride rashi position counted from groom rashi
    r["rashi"]={7:0,4:7,12:0}.get(p)   # ONLY observed points (3 pairs); None = unknown
    r["vashya"]=DVASHYA_OBSERVED.get((boy_sign,girl_sign))   # observed points only (4 pairs); None = unknown
    return r

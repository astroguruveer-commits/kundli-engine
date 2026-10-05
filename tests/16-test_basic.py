import sys; sys.path.insert(0,'..'); sys.path.insert(0,'.')
from kundli import *
from datetime import datetime
r=compute(datetime(1990,5,15,10,30),5.5,26.7606,82.0)
p=r["planets"]
assert abs(((p["Rahu"]["lon"]-p["Ketu"]["lon"])%360)-180)<1e-6
assert 23.6<r["ayanamsha"]<23.8   # Lahiri 1990 ~23.72
tot=sum(((e-s).total_seconds() for _,s,e,_ in r["dasha"]))/86400
assert abs(tot-120*YEAR_DAYS)<1e-3
print("ok")

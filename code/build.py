import json,numpy as np,pandas as pd
import os
f=pd.read_csv('data/features_wd2.csv' if os.path.exists('data/features_wd2.csv') else 'data/features_wd.csv',dtype={'atlas':str})
A=json.load(open('raw/hillforts-attn.json'));P=A['P'];CI=A['CI']
if os.path.exists('raw/hillforts-pv-gs.json'):
    G=json.load(open('raw/hillforts-pv-gs.json')); P.update(G['P']); CI.update(G['CI'])
ops={};
for i,p,o in A['OPS']: ops.setdefault(str(int(i)),set()).add(o)
months=sorted({m for v in P.values() for m,_ in v})
def tot(r,langs=('en','cy','ga','gd')):
    s=0;n=0
    for l in langs:
        t=r[l]
        if isinstance(t,str) and t and (l+':'+t) in P: s+=sum(v for _,v in P[l+':'+t]); n+=1
    return s
f['pv_all']=f.apply(tot,axis=1); f['pv_en']=f.apply(lambda r: tot(r,('en',)),axis=1)
f['has_en']=(f.en.fillna('')!='').astype(int)
f['has_any']=((f[['en','cy','ga','gd']].fillna('')!='').any(axis=1)).astype(int)
f['commons']=f.cc.map(lambda c: CI.get(c,0) if isinstance(c,str) and c else 0).clip(lower=0)
f['img']=pd.to_numeric(f.img,errors='coerce').fillna(0).astype(int); f['sl']=pd.to_numeric(f.sl,errors='coerce').fillna(0).astype(int)
H=['National Trust','English Heritage','Cadw','Historic Environment Scotland']
f['heritage_op']=f.atlas.map(lambda a: int(bool(ops.get(a,set())&set(H))))
f['pv_yr']=f.pv_all/10
# monthly series for en
ms={}
for _,r in f[f.has_en==1].iterrows():
    k='en:'+r.en
    if k in P: ms[r.atlas]=dict(P[k])
json.dump({'months':months,'series':ms},open('data/monthly.json','w'))
f.to_csv('data/analysis.csv',index=False)
print(len(months),months[:2],months[-2:])
print(f[['pv_all','pv_en','has_en','has_any','commons','img','sl','heritage_op']].describe().T)
print(f.sort_values('pv_all',ascending=False)[['name','area_ha','pv_yr','country']].head(25).to_string())

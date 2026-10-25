import json,re,numpy as np,pandas as pd
from scipy.spatial import cKDTree
d=json.load(open('raw/hillforts-wikidata.json'));f=pd.read_csv('data/features.csv',dtype={'atlas':str})
c=pd.DataFrame(d['cand']);xy=c['c'].str.extract(r'Point\(([-\d.]+) ([-\d.]+)\)').astype(float);c['lon'],c['lat']=xy[0],xy[1]
wd={str(int(k)):v for k,v in d['wd'].items()}
for k in ['en','cy','ga','gd','sl','img','cc']: f[k]=f.atlas.map(lambda a: wd.get(a,{}).get(k,''))
def xyz(la,lo):
  la,lo=np.radians(la),np.radians(lo);return np.c_[np.cos(la)*np.cos(lo),np.cos(la)*np.sin(lo),np.sin(la)]
t=cKDTree(xyz(c.lat.values,c.lon.values));dist,idx=t.query(xyz(f.lat.values,f.lon.values));km=dist*6371
stop={'camp','castle','hill','fort','hillfort','the','of','ring','rings','wood','and','iron','age'}
def toks(s): return set(re.findall(r'[a-z]{3,}',str(s).lower().replace('_',' ')))
f['en_src']=np.where(f.en!='','wd','')
used=set(f.en[f.en!=''])
for i in np.where(f.en=='')[0]:
    ce=c.en.values[idx[i]]
    if km[i]>0.5 or ce in used or re.search(r'barrow|cairn|stone|priory|abbey|mead|church',ce,re.I): continue
    a=toks(f.name.iloc[i])-stop; b=toks(ce)-stop
    if (a&b) or (km[i]<0.08):
        f.loc[f.index[i],'en']=ce; f.loc[f.index[i],'en_src']='geo'; used.add(ce)
print(f.en_src.value_counts())
print(f[f.en_src=='geo'][['name','en']].to_string()[:3000])
f.to_csv('data/features_wd.csv',index=False)
T=[]
for _,r in f.iterrows():
    for l in ['en','cy','ga','gd']:
        if isinstance(r[l],str) and r[l]: T.append(l+':'+r[l])
T=sorted(set(T));print(len(T))
json.dump(T,open('data/titles.json','w'),ensure_ascii=False)

C=sorted(set(x for x in f.cc if isinstance(x,str) and x))
print('cats',len(C));json.dump(C,open('data/cats.json','w'),ensure_ascii=False)

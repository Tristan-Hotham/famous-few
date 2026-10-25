import re,json,numpy as np,pandas as pd
f=pd.read_csv('data/features_wd.csv',dtype={'atlas':str})
cols=['id','name','ascii','alt','lat','lon','fc','fcode','cc','cc2','a1','a2','a3','a4','pop','elev','dem','tz','mod']
g=pd.read_csv('/home/claude/brig/raw/cities1000.txt',sep='\t',header=None,names=cols,usecols=['name','cc'],quoting=3)
towns=set(g[g.cc.isin(['GB','IE','IM'])].name.str.lower())
BL=re.compile(r'hospital|f\.c\.|escalator|sports centre|gardens|cup and ring|mine$|roman villa|electoral ward|range$|courtaulds|manor|estate$|peninsula|^port of|margam castle',re.I)
c=[x.split('|') for x in open('raw/gs_cands.txt').read().strip().split(';')]
idx={a:i for i,a in enumerate(f.atlas)}
used=set(f.en.dropna()); acc=[]; rej=[]
for a,t,d in c:
    a=str(int(a)); d=int(d); i=idx.get(a)
    if i is None or isinstance(f.en.iloc[i],str): continue
    r=f.iloc[i]; rad=300+(np.sqrt(r.area_ha*1e4/np.pi) if r.area_ha==r.area_ha else 0)
    base=re.sub(r'\s*\(.*\)$','',t).lower()
    why=None
    if d>rad: why='far'
    elif BL.search(t): why='bl'
    elif base in towns or (re.search(r'bury$',base) and ' ' not in base): why='town'
    elif t.replace(' ','_') in used: why='used'
    if why: rej.append((a,r['name'][:40],t,d,why)); continue
    f.loc[f.index[i],'en']=t.replace(' ','_'); f.loc[f.index[i],'en_src']='gs'; used.add(t.replace(' ','_')); acc.append((a,r['name'][:45],t,d))
print(len(acc)); [print(x) for x in acc]
print('--rejected',len(rej)); [print(x) for x in rej if x[4]!='far'][:0]
f.to_csv('data/features_wd2.csv',index=False)
T=sorted(set('en:'+x for x in f[f.en_src=='gs'].en)); json.dump(T,open('data/titles_gs.json','w'),ensure_ascii=False); print(len(T))

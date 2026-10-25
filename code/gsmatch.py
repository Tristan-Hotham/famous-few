"""Second matching pass: English Wikipedia geosearch around each atlas site; accept nearby articles whose title shares a distinctive word with the atlas site name."""
import json,re,sys,numpy as np,pandas as pd
f=pd.read_csv('data/features_wd.csv',dtype={'atlas':str})
GS={}
for p in sys.argv[1:]: GS.update(json.load(open(p))['GS'])
cols=['id','name','ascii','alt','lat','lon','fc','fcode','cc','cc2','a1','a2','a3','a4','pop','elev','dem','tz','mod']
g=pd.read_csv('/home/claude/brig/raw/cities1000.txt',sep='\t',header=None,names=cols,usecols=['name','cc'],quoting=3)
towns=set(g[g.cc.isin(['GB','IE','IM'])].name.str.lower())
d=json.load(open('raw/hillforts-wikidata.json'))['wd']
stop=set('camp castle hill fort hillfort hillforts the of ring rings wood and iron age settlement enclosure earthwork earthworks banks bank head farm house park common down moor point island isle north south east west upper lower little great old new st saint broch dun promontory near'.split())
def toks(s): return set(w for w in re.findall(r"[a-zà-ÿ']{3,}",str(s).lower().replace('_',' ').replace("'s",'')) if w not in stop)
used=set(f.en.dropna()); acc=[]
for i,r in f.iterrows():
    if isinstance(r.en,str) and r.en: continue
    hits=GS.get(r.atlas)
    if not hits: continue
    rad=300+ (np.sqrt(r.area_ha*1e4/np.pi) if r.area_ha==r.area_ha else 0)
    nm=toks(r['name'])-toks(r['county'])-toks(r['country'])
    for t,dist in hits:
        if dist>rad: continue
        tl=t.lower(); base=re.sub(r',.*$|\s*\(.*\)$','',tl)
        if base in towns: continue
        if re.search(r'church|chapel|school|station|railway|road|street|parish|village|reservoir|quarry|golf|battle|siege|club|pentre|abbey|priory|hall|mill|bridge|lighthouse|airfield|rspb|sssi|nature reserve',tl): continue
        if toks(t)&nm or re.search(r'hill ?fort|camp\b|rings?\b|\bdun|\bcaer|\bgaer|broch',tl) and dist<250:
            if t.replace(' ','_') in used: continue
            acc.append((r.atlas,r['name'][:50],t,dist)); f.loc[i,'en']=t.replace(' ','_'); f.loc[i,'en_src']='gs'; used.add(t.replace(' ','_')); break
print(len(acc))
for a in acc[:80]: print(a)
f.to_csv('data/features_wd2.csv',index=False)
T=sorted(set('en:'+x for x in f[f.en_src=='gs'].en))
json.dump(T,open('data/titles_gs.json','w'),ensure_ascii=False)

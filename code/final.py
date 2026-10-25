import json,numpy as np,pandas as pd,statsmodels.formula.api as smf,warnings; warnings.filterwarnings('ignore')
f=pd.read_csv('data/analysis.csv',dtype={'atlas':str}); M=json.load(open('data/monthly.json')); MAP=json.load(open('data/map.json'))
S={}
def gini(x):
    x=np.sort(np.asarray(x,float));n=len(x);return float((2*np.arange(1,n+1)-n-1).dot(x)/(n*x.sum()))
v=f.pv_yr.values; s=np.sort(v)[::-1]; T=s.sum()
S.update(N=len(f),n_any=int(f.has_any.sum()),n_en=int(f.has_en.sum()),n_cy=int((f.cy.fillna('')!='').sum()),
  gini=gini(v),gini_art=gini(v[f.has_en==1]),top1=s[0]/T,top4=s[:4].sum()/T,top10=s[:10].sum()/T,top41=s[:41].sum()/T,
  total=T,med_art=float(np.median(v[f.has_en==1])),n_under100=int(((f.has_en==1)&(f.pv_yr<100)).sum()))
# sites taking half of all views
c=np.cumsum(s)/T; S['n_half']=int(np.searchsorted(c,.5)+1); S['n_90']=int(np.searchsorted(c,.9)+1)
lor=[[0,0]]+[[ (i+1)/len(s), float(c[i])] for i in np.unique(np.r_[np.arange(0,60),np.geomspace(60,len(s)-1,140).astype(int)])]
later=(f.castle_name==1)|(f.medieval==1); f['later']=later.astype(int)
S['later_sites']=later.mean(); S['later_views']=f.pv_yr[later].sum()/T; S['n_later']=int(later.sum())
f['larea']=np.log2(f.area_ha.clip(lower=0.01)); f['lexc']=np.log2(1+f.n_excav); f['ltown']=np.log2(1+f.town_km); f['lpop']=np.log2(1+f.pop25k/1000)
f['lpv']=np.log(1+f.pv_yr); f['multiv']=(f.ramparts>=2).astype(int)
d=f.dropna(subset=['area_ha']).copy()
d['dec']=pd.qcut(d.area_ha.rank(method='first'),10,labels=False)
dec=d.groupby('dec').agg(lo=('area_ha','min'),hi=('area_ha','max'),med=('area_ha','median'),art=('has_en','mean'),pv=('pv_yr','mean'),n=('atlas','size')).reset_index()
S['dec_top']=float(dec.art.iloc[-1]); S['dec_bot']=float(dec.art.iloc[0])
X='larea + multiv + scheduled + lexc + dated + medieval + roman + story_name + castle_name + coastal + ltown + lpop'
lab={'larea':'Twice the enclosed area','multiv':'Multiple ramparts','scheduled':'Legally scheduled','lexc':'Twice the excavations','dated':'Has a date','medieval':'Reused after AD 400','roman':'Roman-period activity','story_name':'Storied name (Arthur, Caesar, giant...)','castle_name':'"Castle" in the name','coastal':'Coastal','ltown':'Twice as far from a town','lpop':'Twice the nearby population'}
grp={'larea':'importance','multiv':'importance','scheduled':'importance','lexc':'importance','dated':'importance','medieval':'fame','roman':'fame','story_name':'fame','castle_name':'fame','coastal':'access','ltown':'access','lpop':'access'}
d['country2']=d.country.replace({'Isle of Man':'England','Northern Ireland':'Republic of Ireland'})
m1=smf.logit('has_en ~ '+X+' + C(country2)',data=d).fit(disp=0,cov_type='HC1')
a=d[(d.has_en==1)&(d.pv_yr>0)]
m2=smf.ols('lpv ~ '+X+' + C(country2)',data=a).fit(cov_type='HC1')
m3=smf.ols('lpv ~ '+X+' + C(country2)',data=d).fit(cov_type='HC1')
coef=[]
for k in lab:
    ci1=m1.conf_int().loc[k]; ci2=m2.conf_int().loc[k]
    coef.append(dict(k=k,label=lab[k],g=grp[k],or_=float(np.exp(m1.params[k])),or_lo=float(np.exp(ci1[0])),or_hi=float(np.exp(ci1[1])),p1=float(m1.pvalues[k]),
       pct=float(np.exp(m2.params[k])-1),pct_lo=float(np.exp(ci2[0])-1),pct_hi=float(np.exp(ci2[1])-1),p2=float(m2.pvalues[k]),b3=float(m3.params[k]),p3=float(m3.pvalues[k])))
S['m1']=dict(n=int(m1.nobs),pr2=float(m1.prsquared)); S['m2']=dict(n=int(m2.nobs),r2=float(m2.rsquared)); S['m3']=dict(n=int(m3.nobs),r2=float(m3.rsquared))
G={}
for nm,xx in [('importance','larea + multiv + scheduled + lexc + dated'),('fame','medieval + roman + story_name + castle_name'),('access','coastal + ltown + lpop')]:
    G[nm]=dict(art=float(smf.logit('has_en ~ '+xx,data=d).fit(disp=0).prsquared),views=float(smf.ols('lpv ~ '+xx,data=a).fit().rsquared))
S['groups']=G
# country / language coverage
ct=f.assign(cyx=(f.cy.fillna('')!=''),gax=(f.ga.fillna('')!='')|(f.gd.fillna('')!='')).groupby('country').agg(n=('atlas','size'),en=('has_en','mean'),cy=('cyx','mean'),ga=('gax','mean'),any=('has_any','mean'),views=('pv_yr','sum')).reset_index()
# seasonality: median over sites of month share (pure hillfort articles with >=1000 views/yr)
mon=M['months']; SE=pd.DataFrame({k:pd.Series(v) for k,v in M['series'].items()}).reindex(mon).fillna(0)
pure=[c for c in SE.columns if c in set(f[(f.later==0)&(f.pv_yr>=300)].atlas)]
sh=SE[pure].copy(); sh.index=[int(m[2:]) for m in mon]
sh=sh.groupby(level=0).sum(); sh=sh/sh.sum()*12
seas=sh.median(axis=1).round(3).tolist(); S['seas_n']=len(pure)
# yearly totals (all en)
yr=SE.copy(); yr.index=[2000+int(m[:2]) for m in mon]; yt=yr.groupby(level=0).sum().sum(axis=1).astype(int).tolist()
# spikes
nm=f.set_index('atlas')['name'].map(lambda x: x.split(' (')[0])
SP=[('1213','Cefnllys Castle','Wikipedia front page, 24 Dec 2020'),('3555','The Trundle','Wikipedia front page, 15 Jan 2022'),('2788','Tap o\' Noth','News: largest Pictish settlement, May 2020'),('4046','Stanwick','News: the Melsonby hoard, March 2025')]
ids={}
for atl in SE.columns:
    n=nm[atl]
    for key in ['Cefnllys','Trundle','Tap o','Stanwick']:
        if n.startswith(key) or (key in n and key!='Tap o'): ids.setdefault(key,atl)
spk=[]
for key,(a_,t,note) in zip(['Cefnllys','Trundle','Tap o','Stanwick'],SP):
    atl=ids[key]; spk.append(dict(name=t,note=note,atlas=atl,series=SE[atl].astype(int).tolist()))
# forgotten giants & top list
gi=f[f.has_any==0].sort_values('area_ha',ascending=False).head(12)
giants=[dict(name=r['name'].split(' (')[0],area=r.area_ha,ramparts=None if r.ramparts!=r.ramparts else int(r.ramparts),country=r.country,sched=int(r.scheduled),excav=int(r.n_excav)) for _,r in gi.iterrows()]
top=f.sort_values('pv_yr',ascending=False).head(25)
topl=[dict(name=r['name'].split(' (')[0],en=r.en,pv=round(r.pv_yr),area=None if r.area_ha!=r.area_ha else r.area_ha,later=int(r.later),country=r.country) for _,r in top.iterrows()]
S['top_named']=[t['name'] for t in topl[:6]]
# sites for map
cidx={c:i for i,c in enumerate(sorted(f.country.unique()))}
sites=[]
for i,r in f.iterrows():
    xy=MAP['xy'][i]
    if not xy: continue
    lang=(1 if r.has_en else 0)|(2 if isinstance(r.cy,str) and r.cy else 0)|(4 if (isinstance(r.ga,str) and r.ga) or (isinstance(r.gd,str) and r.gd) else 0)
    sites.append([xy[0],xy[1],round(r.pv_yr),lang,None if r.area_ha!=r.area_ha else r.area_ha,None if r.ramparts!=r.ramparts else int(r.ramparts),int(r.n_excav),r['name'].split(' (')[0],r.en if isinstance(r.en,str) else '',cidx[r.country],int(r.later),int(r.scheduled),r.atlas,int(r.story_name)])
OUT=dict(S=S,lor=lor,dec=dec.to_dict('records'),coef=coef,ct=ct.to_dict('records'),seas=seas,years=yt,spikes=spk,giants=giants,top=topl,sites=sites,countries=list(cidx),land=MAP['land'],borders=MAP['borders'],W=MAP['W'],H=MAP['H'])
json.dump(OUT,open('data/page.json','w'),separators=(',',':'),default=float)
print(json.dumps(S,indent=0,default=float)); print(dec.round(3).to_string()); print(ct.round(3).to_string()); print(seas); print(yt)
for c in coef: print(f"{c['label'][:28]:28s} OR {c['or_']:.2f} [{c['or_lo']:.2f},{c['or_hi']:.2f}] p={c['p1']:.3f} | views {c['pct']*100:+.0f}% p={c['p2']:.3f}")
print(giants[:5]); print([ (t['name'],t['pv']) for t in topl[:12]])

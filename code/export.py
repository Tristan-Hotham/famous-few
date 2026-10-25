import json,pandas as pd,os,shutil
R='release'; os.makedirs(R+'/data',exist_ok=True); os.makedirs(R+'/code',exist_ok=True)
f=pd.read_csv('data/analysis.csv',dtype={'atlas':str})
cols=['atlas','name','country','county','lat','lon','qid','area_ha','ramparts','scheduled','n_invest','n_excav','dated','roman','medieval','castle_name','story_name','coastal','town','town_km','pop25k','en','en_src','cy','ga','gd','has_en','has_any','pv_en','pv_all','pv_yr','commons','img','sl','heritage_op']
f[cols].rename(columns={'atlas':'atlas_id','en':'en_article','en_src':'en_match','cy':'cy_article','ga':'ga_article','gd':'gd_article','pv_en':'pageviews_en_2016_2025','pv_all':'pageviews_all_2016_2025','pv_yr':'pageviews_per_year','commons':'commons_category_files','img':'wikidata_has_image','sl':'wikidata_sitelinks','heritage_op':'heritage_body_owner_operator'}).to_csv(R+'/data/hillforts_attention.csv',index=False)
M=json.load(open('data/monthly.json'))
m=pd.DataFrame({k:pd.Series(v) for k,v in M['series'].items()}).reindex(M['months']).fillna(0).astype(int)
m.index=['20'+x[:2]+'-'+x[2:] for x in m.index]; m.index.name='month'; m.T.rename_axis('atlas_id').to_csv(R+'/data/monthly_pageviews_en.csv')
for s in ['features.py','match.py','gsmatch.py','build.py','final.py','paper.py','assemble.py']: shutil.copy(s,R+'/code/')
print(os.listdir(R+'/data'), m.shape)

import json,re,sys
D=json.load(open('data/page.json')); S=D['S']
pc=lambda x,d=0: f"{x*100:.{d}f}%"
co={c['k']:c for c in D['coef']}
ct={r['country']:r for r in D['ct']}
area_n=sum(r['n'] for r in D['dec'])
W={1:'one',2:'two',3:'three',4:'four',5:'five',6:'six',7:'seven',8:'eight',9:'nine',10:'ten',11:'eleven',12:'twelve',13:'thirteen',14:'fourteen',15:'fifteen'}
R={'__N__':f"{S['N']:,}",'__PCT_NONE__':pc(1-S['n_en']/S['N']),'__N_HALF__':str(S['n_half']),'__GINI__':f"{S['gini']:.2f}",'__GINI_ART__':f"{S['gini_art']:.2f}",
'__TOTAL10__':f"{S['total']*10/1e6:.1f} million",'__TOP1__':pc(S['top1']),'__TOP4__':pc(S['top4']),'__N_90__':str(S['n_90']),'__REST90__':f"{S['N']-S['n_90']:,}",
'__N_EN__':f"{S['n_en']:,}",'__DEC_TOP__':pc(S['dec_top']),'__DEC_BOT__':pc(S['dec_bot']),'__N_AREA__':f"{area_n:,}",'__N_LATER__':f"{S['n_later']:,}",
'__LATER_SITES__':pc(S['later_sites']),'__LATER_VIEWS__':pc(S['later_views']),'__M1N__':f"{S['m1']['n']:,}",
'__OR_EXC__':pc(co['lexc']['or_']-1),'__PCT_EXC__':pc(co['lexc']['pct']),
'__EN_ENG__':pc(ct['England']['en']),'__EN_WAL__':pc(ct['Wales']['en']),'__EN_SCO__':pc(ct['Scotland']['en']),'__EN_IRL__':pc(ct['Republic of Ireland']['en'],1),'__CY_WAL__':pc(ct['Wales']['cy']),
'__N_HALF_W__':W[S['n_half']].capitalize(),'__N_HALF_WL__':W[S['n_half']],'__DEC_TOP_NONE__':pc(1-S['dec_top']),'__PCT_CASTLE__':pc(co['castle_name']['pct']),'__GIANT1__':f"{D['giants'][0]['area']:.0f}",'__DATE__':'October 2026',
'__PAPER__':sys.argv[1] if len(sys.argv)>1 else '#','__BLOG__':sys.argv[2] if len(sys.argv)>2 else '#','__REPO__':'famous-few','__OGIMG__':'https://tristan-hotham.github.io/famous-few/header.png'}
s=open('page_template.html').read()
for k,v in R.items(): s=s.replace(k,v)
s=s.replace('__DATA__',json.dumps(D,separators=(',',':'),ensure_ascii=False))
left=re.findall(r'__[A-Z0-9_]+__',s); print('left',set(left))
open('famous-few.html','w').write(s); print(len(s))
json.dump(R,open('data/repl.json','w'),indent=0)

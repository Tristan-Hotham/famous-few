import json,re,subprocess,shutil,os
D=json.load(open('data/page.json')); S=D['S']; R=json.load(open('data/repl.json'))
pc=lambda x,d=0: f"{x*100:.{d}f}\\%"
co={c['k']:c for c in D['coef']}; ct={r['country']:r for r in D['ct']}
esc=lambda s: s.replace('&','\\&').replace('%','\\%').replace('_','\\_').replace('#','\\#')
V={k.strip('_'):v for k,v in R.items()}
for k in list(V): V[k]=V[k].replace('%','\\%')
V.update(PCT_EN=pc(S['n_en']/S['N'],1),N_ANY=f"{S['n_any']:,}",PCT_ANY=pc(S['n_any']/S['N'],1),N_ENG=f"{ct['England']['n']:,}",N_SCO=f"{ct['Scotland']['n']:,}",N_WAL=f"{ct['Wales']['n']:,}",N_IRL=f"{ct['Republic of Ireland']['n']:,}",
 M2N=f"{S['m2']['n']:,}",MED_ART=f"{S['med_art']:,.0f}",SEAS_N=str(S['seas_n']),SEAS_RANGE=pc(max(abs(x-1) for x in D['seas'][:10]),0),
 OR_AREA=f"{co['larea']['or_']:.2f}",OR_SCHED=f"{co['scheduled']['or_']:.2f}",OR_EXC2=f"{co['lexc']['or_']:.2f}",OR_MED=f"{co['medieval']['or_']:.2f}",OR_CASTLE=f"{co['castle_name']['or_']:.2f}",OR_ROMAN=f"{co['roman']['or_']:.2f}",
 PCT_EXC2=('+' if co['lexc']['pct']>0 else '')+pc(co['lexc']['pct']),PCT_CASTLE=('+' if co['castle_name']['pct']>0 else '')+pc(co['castle_name']['pct']),PCT_AREA=('+' if co['larea']['pct']>0 else '')+pc(co['larea']['pct']),
 G_IMP_ART=f"{S['groups']['importance']['art']:.2f}",G_IMP_VIEWS=f"{S['groups']['importance']['views']:.2f}",G_FAME_ART=f"{S['groups']['fame']['art']:.2f}",G_FAME_VIEWS=f"{S['groups']['fame']['views']:.2f}",G_ACC_ART=f"{S['groups']['access']['art']:.2f}",G_ACC_VIEWS=f"{S['groups']['access']['views']:.2f}")
# tables
rows=''.join(f"{esc(r['country'])} & {r['n']:,} & {pc(r['en'],1)} & {pc(r['cy'],1)} & {pc(r['ga'],1)} & {pc(r['any'],1)} & {r['views']:,.0f}\\\\\n" for r in D['ct'])
V['TABLE_NATIONS']="\\begin{table}[H]\\centering\\small\\caption{Article coverage and reading by nation.}\\label{tab:nations}\\begin{tabular}{lrrrrrr}\\toprule Nation & Sites & English & Welsh & Irish/Gaelic & Any & Reads per year\\\\\\midrule\n"+rows+"\\bottomrule\\end{tabular}\\end{table}"
star=lambda p: '***' if p<.001 else '**' if p<.01 else '*' if p<.05 else ''
mr=''.join(f"{esc(c['label'])} & {c['or_']:.2f}{star(c['p1'])} & [{c['or_lo']:.2f}, {c['or_hi']:.2f}] & {c['pct']*100:+.0f}\\%{star(c['p2'])} & [{c['pct_lo']*100:+.0f}, {c['pct_hi']*100:+.0f}] & {c['b3']:+.2f}{star(c['p3'])}\\\\\n" for c in D['coef'])
V['TABLE_MODELS']="\\begin{table}[H]\\centering\\small\\caption{Models of attention. (1) Logistic regression of having an English article, odds ratios. (2) OLS of log yearly reading for sites with an English article, shown as percentage change. (3) OLS of log(1 + yearly reading), all sites, coefficients. Area, excavations, distance and population are base-2 logs. All models include nation controls; robust standard errors. * $p<0.05$, ** $p<0.01$, *** $p<0.001$.}\\label{tab:models}\\resizebox{\\textwidth}{!}{\\begin{tabular}{lrrrrr}\\toprule & (1) OR & 95\\% CI & (2) Change & 95\\% CI & (3) $b$\\\\\\midrule\n"+mr+f"\\midrule Observations & {S['m1']['n']:,} & & {S['m2']['n']:,} & & {S['m3']['n']:,}\\\\ Pseudo-$R^2$ / $R^2$ & {S['m1']['pr2']:.2f} & & {S['m2']['r2']:.2f} & & {S['m3']['r2']:.2f}\\\\\\bottomrule\\end{{tabular}}}}\\end{{table}}"
tr=''.join(f"{i+1} & {esc(t['name'])} & {esc(t['country'].replace('Republic of ',''))} & {'' if t['area'] is None else t['area']} & {'yes' if t['later'] else ''} & {t['pv']:,}\\\\\n" for i,t in enumerate(D['top'][:15]))
V['TABLE_TOP']="\\begin{table}[H]\\centering\\small\\caption{The fifteen most-read hillforts. Reuse = activity after AD 400 or a castle name.}\\label{tab:top}\\begin{tabular}{rllrcr}\\toprule & Site & Nation & Area (ha) & Reuse & Reads per year\\\\\\midrule\n"+tr+"\\bottomrule\\end{tabular}\\end{table}"
gr=''.join(f"{esc(g['name'])} & {esc(g['country'].replace('Republic of ',''))} & {g['area']} & {'' if g['ramparts'] is None else g['ramparts']} & {'yes' if g['sched'] else ''} & {g['excav']}\\\\\n" for g in D['giants'])
V['TABLE_GIANTS']="\\begin{table}[H]\\centering\\small\\caption{The largest hillforts with no Wikipedia article in English, Welsh, Irish or Scottish Gaelic.}\\label{tab:giants}\\begin{tabular}{llrrcr}\\toprule Site & Nation & Area (ha) & Ramparts & Scheduled & Excavations\\\\\\midrule\n"+gr+"\\bottomrule\\end{tabular}\\end{table}"
s=open('paper/paper_template.tex').read()
for k,v in V.items(): s=s.replace('{{'+k+'}}',v)
left=re.findall(r'\{\{[A-Z0-9_]+\}\}',s); print('left',left)
open('paper/Hotham_Famous_Few_Hillforts_Attention.tex','w').write(s)
# figures
from PIL import Image
a=Image.open('figs/f_map_views.png');b=Image.open('figs/f_map_area.png');g=24
c=Image.new('RGB',(a.width+b.width+g,max(a.height,b.height)),'white');c.paste(a,(0,0));c.paste(b,(a.width+g,0));c.save('paper/f_map.png')
for f in ['f_lorenz','f_deciles','f_scatter','f_coef_or','f_spikes','f_lang']: shutil.copy(f'figs/{f}.png','paper/')
os.chdir('paper')
for _ in range(2): r=subprocess.run(['xelatex','-interaction=nonstopmode','Hotham_Famous_Few_Hillforts_Attention.tex'],capture_output=True,text=True)
print(r.stdout[-600:])

import json, os
import numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.colors import LinearSegmentedColormap
from shapely.geometry import shape
from shapely.ops import unary_union
from shapely.affinity import scale as sscale

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, '..', 'data')
F = '/tmp/claude-0/-home-claude/c232619d-81e0-53f3-9de6-41e973630753/scratchpad/fonts/'
for f in ['FrauncesVar.ttf', 'IBMPlexMono-Regular.ttf', 'IBMPlexMono-Medium.ttf', 'SourceSerif4-Regular.ttf', 'SourceSerif4-Semibold.ttf', 'SourceSerif4-It.ttf']:
    fm.fontManager.addfont(F + f)
DISP = fm.FontProperties(fname=F + 'FrauncesVar.ttf', weight=900)
SER = 'Source Serif 4'; MONO = 'IBM Plex Mono'

BG = '#F3EEE2'; LAND = '#DCD3C0'; EDGE = '#C4B9A2'
FG = '#1D1A15'; MUT = '#6B6457'; FIRE = '#C2410C'; HOT = '#8E1B10'; EMBER = '#9C9586'; PLUM = '#8A4A96'; DARKEDGE = '#4A140A'
fire = LinearSegmentedColormap.from_list('fire', ['#F5B26B', '#EE7A2C', '#C93A12', '#8E1B10'])

d = pd.read_csv(os.path.join(D, 'hillforts_attention.csv'))
v = d.pageviews_all_2016_2025.values.astype(float)
TOT = v.sum()
vs = np.sort(v)[::-1]; cum = vs.cumsum() / TOT
n_half = int((cum < 0.5).sum() + 1); n_90 = int((cum < 0.9).sum() + 1)
x = np.sort(v); n = len(x); gini = (2 * np.arange(1, n + 1) - n - 1).dot(x) / (n * x.sum())
no_en = 1 - d.has_en.mean()
reuse = (d.medieval == 1) | (d.castle_name == 1)
re_sites, re_read = reuse.mean(), v[reuse.values].sum() / TOT
print(n_half, n_90, round(gini, 3), round(no_en, 3), reuse.sum(), round(re_sites, 3), round(re_read, 3), round(cum[0], 3), round(cum[3], 3))

K = np.cos(np.radians(55.0))
d['X'] = d.lon * K; d['Y'] = d.lat
land = unary_union([shape(g) for g in json.load(open(os.path.join(HERE, 'ne10m_land.json')))])
land = sscale(land, xfact=K, yfact=1.0, origin=(0, 0))

fig = plt.figure(figsize=(12, 15), dpi=200, facecolor=BG)

# ---------------- title
fig.text(0.04, 0.968, 'Who reads about hillforts?', fontproperties=DISP, fontsize=50, color=FG, va='top')
fig.text(0.04, 0.913, f'Britain and Ireland have {len(d):,} hillforts. Ten years of Wikipedia reading, 2016 to 2025,\n'
         f'about {TOT/1e6:.1f} million page views, lands on a famous few. Most forts get no readers at all.',
         family=SER, fontsize=15, color=FG, va='top', linespacing=1.35)

# ---------------- hero map
ax = fig.add_axes([0.0, 0.305, 0.64, 0.56]); ax.set_facecolor(BG)
geoms = land.geoms if hasattr(land, 'geoms') else [land]
for g in geoms:
    if g.area < 0.002 or g.centroid.y < 50.0: continue
    xx, yy = g.exterior.xy
    ax.fill(xx, yy, color=LAND, ec=EDGE, lw=0.6, zorder=1)
none = d[d.has_any == 0]
ax.scatter(none.X, none.Y, s=2.4, c=EMBER, lw=0, alpha=0.9, zorder=2, rasterized=True)
lit = d[d.pageviews_all_2016_2025 > 0].sort_values('pageviews_per_year')
r = (lit.pageviews_per_year / lit.pageviews_per_year.max()).values
col = fire(np.clip(np.log10(lit.pageviews_per_year.values) / np.log10(lit.pageviews_per_year.max()), 0, 1))
core = 2.5 + 1100 * r ** 0.8
ax.scatter(lit.X, lit.Y, s=core, c=col, edgecolors=DARKEDGE, lw=0.35, alpha=0.95, zorder=4, rasterized=True)
ax.set_aspect('equal'); ax.axis('off')
ax.set_xlim(-10.8 * K, 2.1 * K); ax.set_ylim(49.55, 60.95)

LAB = {3519: ('Edinburgh Castle', (3.3, 0.45)), 3948: ('Bamburgh Castle', (2.4, -0.15)),
       4012: ('Stirling Castle', (-3.6, 0.2)), 3578: ('Dover Castle', (0.2, 0.95)),
       2936: ('Dunnottar Castle', (2.6, 0.8)), 2709: ('Urquhart Castle', (-2.7, 0.55)),
       390: ('Old Sarum', (1.3, -0.85)), 2797: ('Mam Tor', (2.3, 0.15)),
       3406: ('Maiden Castle', (-1.3, -0.92)), 3758: ('Solsbury Hill', (-3.7, -0.47)),
       711: ('Dún Aonghasa', (0.47, 2.55))}
for i, (name, (dx, dy)) in LAB.items():
    row = d.loc[i]
    tx, ty = row.X + dx * K, row.Y + dy
    ax.annotate(f'{name}\n{row.pageviews_per_year/1000:,.0f}k a year', xy=(row.X, row.Y), xytext=(tx, ty),
                family=MONO, fontsize=10, color=FG, ha='center', va='center', zorder=6, linespacing=1.15,
                arrowprops=dict(arrowstyle='-', color=MUT, lw=0.7, shrinkA=2, shrinkB=5))

# legend
lx = fig.add_axes([0.04, 0.262, 0.6, 0.045]); lx.axis('off'); lx.set_xlim(0, 10); lx.set_ylim(0, 2)
lx.scatter([0.2], [1.5], s=12, c=EMBER); lx.text(0.5, 1.5, f'no article in any language ({(d.has_any==0).sum():,})', family=MONO, fontsize=10, color=MUT, va='center')
for xx, val in [(0.2, 1000), (0.8, 10000), (1.6, 100000)]:
    s = 2.5 + 1100 * (val / lit.pageviews_per_year.max()) ** 0.8
    c = fire(np.log10(val) / np.log10(lit.pageviews_per_year.max()))
    lx.scatter([xx], [0.45], s=s, c=[c], edgecolors=DARKEDGE, lw=0.35)
lx.text(2.3, 0.45, 'English, Welsh, Irish, Gaelic Wikipedia readers a year: 1k, 10k, 100k', family=MONO, fontsize=10, color=MUT, va='center')

# ---------------- right column numbers
tx = fig.add_axes([0.655, 0.32, 0.33, 0.54]); tx.axis('off')
notes = [(f'{n_half}', f'sites take half of all reading.\nEdinburgh Castle alone takes {cum[0]*100:.0f}%.'),
         (f'{gini:.2f}', 'Gini coefficient of attention.\n1 would mean one fort got everything.'),
         (f'{no_en*100:.0f}%', 'of hillforts have no English\nWikipedia article to read.'),
         (f'{re_read*100:.0f}%', f'of reading goes to forts reused\nafter AD 400 or named as castles,\njust {re_sites*100:.0f}% of all sites.')]
for (b, s), y in zip(notes, [1.0, 0.75, 0.50, 0.25]):
    tx.text(0, y, b, fontproperties=DISP, fontsize=44, color=FIRE, va='top', transform=tx.transAxes)
    tx.text(0, y - 0.105, s, family=SER, fontsize=13, color=FG, va='top', transform=tx.transAxes, linespacing=1.3)

# ---------------- bottom: cumulative curve
def style(a):
    a.set_facecolor(BG)
    for s in ['top', 'right']: a.spines[s].set_visible(False)
    for s in ['left', 'bottom']: a.spines[s].set_color(EDGE)
    a.tick_params(colors=MUT, labelsize=10)
    for t in a.get_xticklabels() + a.get_yticklabels(): t.set_family(MONO)

a1 = fig.add_axes([0.075, 0.095, 0.5, 0.13]); style(a1)
rk = np.arange(1, n + 1)
a1.fill_between(rk, 0, cum * 100, color=FIRE, alpha=0.10, lw=0)
a1.plot(rk, cum * 100, color=FIRE, lw=2.6)
a1.set_xscale('log'); a1.set_xlim(1, n); a1.set_ylim(0, 104)
a1.set_xticks([1, 10, 100, 1000, n]); a1.set_xticklabels(['1', '10', '100', '1,000', f'{n:,}'], family=MONO)
a1.set_yticks([0, 50, 100]); a1.set_yticklabels(['0%', '50%', '100%'], family=MONO)
for k, txt, off in [(1, f'top 1: {cum[0]*100:.0f}%', (10, -12)), (4, f'top 4: {cum[3]*100:.0f}%', (10, -16)),
                    (n_half, f'top {n_half}: 50%', (-105, 10)), (n_90, f'top {n_90}: 90%', (8, -16))]:
    a1.scatter([k], [cum[k - 1] * 100], s=30, c=HOT, zorder=5, lw=0)
    a1.annotate(txt, (k, cum[k - 1] * 100), xytext=off, textcoords='offset points', family=MONO, fontsize=10, color=FG)
a1.set_xlabel('hillforts ranked from most to least read (log scale)', family=MONO, fontsize=10, color=MUT)
fig.text(0.04, 0.236, 'THE STAIRCASE  cumulative share of all reading', family=MONO, fontsize=11, color=MUT)

# ---------------- bottom: castle effect
a2 = fig.add_axes([0.66, 0.085, 0.31, 0.125]); a2.axis('off'); a2.set_xlim(0, 100); a2.set_ylim(-0.6, 1.9)
for y, lab, val, c in [(1.25, 'share of sites', re_sites * 100, PLUM), (0.15, 'share of reading', re_read * 100, PLUM)]:
    a2.barh(y, 100, height=0.42, color='#E2DACA')
    a2.barh(y, val, height=0.42, color=c)
    a2.text(0, y + 0.36, lab, family=MONO, fontsize=10.5, color=MUT, va='bottom')
    a2.text(val + 2, y, f'{val:.0f}%', family=MONO, fontsize=12, color=FG, va='center')
fig.text(0.66, 0.222, f'THE CASTLE ON TOP  {reuse.sum()} forts reused\nafter AD 400 or named as a castle', family=MONO, fontsize=11, color=MUT, va='bottom', linespacing=1.3)
a2.text(0, -0.55, 'Readers mostly come for the castle.', family=SER, fontsize=12, color=FG, style='italic')

# ---------------- footer
fig.text(0.04, 0.016, 'Data: Lock and Ralston 2017, Atlas of Hillforts of Britain and Ireland (CC BY-SA 4.0), via Middleton 2024 Hillforts Primer.\n'
         'Wikipedia human pageviews 2016 to 2025 (Wikimedia REST API), en, cy, ga and gd Wikipedias; Wikidata (CC0).\n'
         'Base map: Natural Earth. Analysis and chart: Tristan Hotham, with Python and matplotlib.',
         family=MONO, fontsize=9, color=MUT, linespacing=1.45)
fig.savefig(os.path.join(HERE, 'famous_few.png'), facecolor=BG, dpi=200)
print('ok')

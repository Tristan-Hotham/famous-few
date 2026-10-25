"""Site-level importance and context features from the Atlas of Hillforts (CC BY-SA 4.0) plus GeoNames towns."""
import pandas as pd, numpy as np, re
from scipy.spatial import cKDTree
src = '/home/claude/mikedairsie/hillforts-primer/hillforts-atlas-source-data-csv/'
d = pd.read_csv(src + 'hillforts.csv', low_memory=False)
inv = pd.read_csv(src + 'hillforts-investigations-table.csv', low_memory=False)
yes = lambda c: (d[c].astype(str).str.lower() == 'yes').astype(int)

f = pd.DataFrame({
    'atlas': d['Main_Atlas_Number'].astype(str),
    'name': d['Main_Display_Name'],
    'site': d['Main_Site_Name'],
    'country': d['Main_Country'],
    'county': d['Location_Current_County'],
    'lat': pd.to_numeric(d['Location_Latitude'], errors='coerce'),
    'lon': pd.to_numeric(d['Location_Longitude'], errors='coerce'),
    'qid': d['URL_Wiki'].str.extract(r'(Q\d+)')[0],
    'area_ha': pd.to_numeric(d['Enclosing_Enclosed_Area'], errors='coerce'),
    'ramparts': pd.to_numeric(d['Enclosing_Max_Ramparts'], errors='coerce'),
    'altitude': pd.to_numeric(d['Landscape_Altitude'], errors='coerce'),
    'scheduled': d['Main_SM'].notna().astype(int),
    'extant': yes('Management_Condition_Extant'),
    'cropmark': yes('Management_Condition_Cropmark'),
    'destroyed': yes('Management_Condition_Destroyed'),
    'confirmed': (d['Status_Interpretation_Reliability'] == 'Confirmed').astype(int),
    'coastal': yes('Landscape_Topography_Coastal'),
    'promontory': yes('Landscape_Type_Promontory'),
    'hilltop': yes('Landscape_Topography_Hilltop'),
    'woodland': yes('Management_Land_Use_Woodland') | yes('Management_Land_Use_Plantation'),
    'urban': yes('Management_Land_Use_Urban'),
    'summary': d['Main_Summary'].fillna(''),
})
f['medieval'] = (yes('Dating_Date_Post_AD800') | yes('Dating_Date_AD400_AD800')).clip(0,1)
f['roman'] = yes('Dating_Date_AD50_AD400')
f['dated'] = (1 - yes('Dating_Date_Unknown')).clip(0, 1)
# investigations: number of excavations and of all recorded investigations
inv['atlas'] = inv['Atlas_Number'].astype(str)
f['n_invest'] = f['atlas'].map(inv.groupby('atlas').size()).fillna(0).astype(int)
f['n_excav'] = f['atlas'].map(inv[inv['Investigations_Type'] == 'Excavation'].groupby('atlas').size()).fillna(0).astype(int)
# legend / famous-name cues in the atlas summary and name
txt = (f['name'].fillna('') + ' ' + f['summary']).str.lower()
f['legend'] = txt.str.contains(r'\barthur|camelot|legend|folklore|\bmyth').astype(int)
f['story_name'] = f['site'].fillna('').str.contains(r"\b(?:arthur|caesar|giant|devil|king|queen|maiden|fairy|druid|merlin|dane|danes|roman|romans|vespasian|alfred|robin)\b", case=False).astype(int)
f['castle_name'] = f['site'].fillna('').str.contains(r'castle', case=False).astype(int)

# distance to nearest town of 10,000+ (GeoNames cities1000)
cols = ['id', 'name', 'ascii', 'alt', 'lat', 'lon', 'fc', 'fcode', 'cc', 'cc2', 'a1', 'a2', 'a3', 'a4', 'pop', 'elev', 'dem', 'tz', 'mod']
g = pd.read_csv('/home/claude/brig/raw/cities1000.txt', sep='\t', header=None, names=cols, usecols=['name', 'lat', 'lon', 'cc', 'pop'], quoting=3, low_memory=False)
g = g[g['cc'].isin(['GB', 'IE', 'IM']) & (g['pop'] >= 10000)]
def xyz(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    return np.c_[np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)]
t = cKDTree(xyz(g['lat'].values, g['lon'].values))
ok = f['lat'].notna()
dist, idx = t.query(xyz(f.loc[ok, 'lat'].values, f.loc[ok, 'lon'].values))
f.loc[ok, 'town_km'] = 6371 * 2 * np.arcsin(dist / 2)
f.loc[ok, 'town'] = g['name'].values[idx]
# population within 25 km (sum of towns of 1,000+)
g1 = pd.read_csv('/home/claude/brig/raw/cities1000.txt', sep='\t', header=None, names=cols, usecols=['lat', 'lon', 'cc', 'pop'], quoting=3, low_memory=False)
g1 = g1[g1['cc'].isin(['GB', 'IE', 'IM'])]
t1 = cKDTree(xyz(g1['lat'].values, g1['lon'].values))
P = g1['pop'].values
nb = t1.query_ball_point(xyz(f.loc[ok, 'lat'].values, f.loc[ok, 'lon'].values), r=2 * np.sin(25 / 6371 / 2))
f.loc[ok, 'pop25k'] = [P[i].sum() for i in nb]
f.drop(columns=['summary']).to_csv('data/features.csv', index=False)
print(f.describe().T[['count', 'mean', '50%', 'max']])
print(f['legend'].sum(), f['castle_name'].sum())

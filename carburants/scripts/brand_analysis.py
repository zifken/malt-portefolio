"""
Fuel station brand detection and price-premium analysis.
Reads raw/stations.csv and raw/prices.csv, writes brand outputs.
"""
import re
import pandas as pd
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent

def detect_brand(text):
    if pd.isna(text):
        return 'Independant/Other'
    text = str(text).lower()
    patterns = [
        ('Total/TotalEnergies', r'\btotal\b|total energies|totalenergies|total access'),
        ('E.Leclerc', r'\be\.?leclerc\b|\bleclerc\b'),
        ('Intermarché', r'\bintermarche\b|\bintermarch[eé]\b'),
        ('Carrefour', r'\bcarrefour\b'),
        ('Auchan', r'\bauchan\b'),
        ('Casino', r'\bcasino\b'),
        ('Super U', r'\bsuper\s+u\b|\bsysteme\s+u\b'),
        ('Esso', r'\besso\b'),
        ('Shell', r'\bshell\b'),
        ('BP', r'\bbp\b'),
        ('Avia', r'\bavia\b'),
        ('Dyneff', r'\bdyneff\b'),
    ]
    for brand, pat in patterns:
        if re.search(pat, text):
            return brand
    return 'Independant/Other'

if __name__ == '__main__':
    stations = pd.read_csv(PROJECT / 'raw' / 'stations.csv')
    prices = pd.read_csv(PROJECT / 'raw' / 'prices.csv')
    stations['brand'] = (stations['adresse'].fillna('') + ' ' + stations['ville'].fillna('')).apply(detect_brand)
    df = prices.merge(stations, on='id_station', how='left')
    (PROJECT / 'outputs').mkdir(exist_ok=True)
    stations.to_csv(PROJECT / 'outputs' / 'stations_brand.csv', index=False)
    results = []
    for fuel in ['Gazole', 'SP98']:
        sub = df[(df['carburant'] == fuel) & df['prix_euros'].notna()].copy()
        median_price = sub['prix_euros'].median()
        group = sub.groupby('brand')['prix_euros'].agg(['mean', 'median', 'count']).reset_index()
        group['premium_vs_median'] = group['mean'] - median_price
        group['fuel'] = fuel
        group['market_median'] = median_price
        results.append(group)
        route = sub.groupby(['brand', 'type_route'])['prix_euros'].agg(['mean', 'count']).reset_index()
        route['premium_vs_median'] = route['mean'] - median_price
        route['fuel'] = fuel
        results.append(route)
    out = pd.concat(results, ignore_index=True)
    out.to_csv(PROJECT / 'outputs' / 'brand_premium.csv', index=False)
    print('Brand counts:', stations['brand'].value_counts().to_dict())
    print('Saved outputs/stations_brand.csv and outputs/brand_premium.csv')

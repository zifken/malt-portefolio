"""
Parse French fuel prices XML from data.gouv.fr into clean CSV files.

Source: https://donnees.roulez-eco.fr/opendata/instantane
Dataset: https://www.data.gouv.fr/datasets/prix-des-carburants-en-france-flux-instantane-v2-amelioree
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "raw"
RAW_DIR.mkdir(exist_ok=True)

XML_PATH = PROJECT_DIR / "PrixCarburants_instantane.xml"


def extract_department(postal_code: str) -> str:
    """Extract French department from 5-digit postal code."""
    if not postal_code:
        return None
    if postal_code.startswith(("97", "98")):
        return postal_code[:3]
    return postal_code[:2]


def parse_fuel_data(xml_path: Path = XML_PATH) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Parse XML and return (stations_df, prices_df)."""
    print(f"Parsing {xml_path} ...")
    tree = ET.parse(xml_path)
    root = tree.getroot()

    stations = []
    fuel_prices = []

    for pdv in root.findall("pdv"):
        station_id = pdv.get("id")
        try:
            lat = float(pdv.get("latitude")) / 100_000.0
        except (TypeError, ValueError):
            lat = None
        try:
            lon = float(pdv.get("longitude")) / 100_000.0
        except (TypeError, ValueError):
            lon = None

        cp = pdv.get("cp")
        pop = pdv.get("pop")
        adresse = (pdv.findtext("adresse") or "").strip()
        ville = (pdv.findtext("ville") or "").strip()
        automate_24_24 = pdv.find("horaires").get("automate-24-24") if pdv.find("horaires") is not None else None
        services = [s.text for s in pdv.find("services")] if pdv.find("services") is not None else []

        stations.append({
            "id_station": station_id,
            "latitude": lat,
            "longitude": lon,
            "code_postal": cp,
            "departement": extract_department(cp),
            "type_route": pop,
            "adresse": adresse,
            "ville": ville,
            "automate_24_24": automate_24_24,
            "services": " | ".join(services),
        })

        for prix in pdv.findall("prix"):
            try:
                value = float(prix.get("valeur"))
            except (TypeError, ValueError):
                value = None
            fuel_prices.append({
                "id_station": station_id,
                "carburant": prix.get("nom"),
                "date_maj": prix.get("maj"),
                "prix_euros": value,
                "rupture": prix.get("rupture"),
            })

    stations_df = pd.DataFrame(stations)
    prices_df = pd.DataFrame(fuel_prices)

    return stations_df, prices_df


if __name__ == "__main__":
    stations_df, prices_df = parse_fuel_data()

    stations_csv = RAW_DIR / "stations.csv"
    prices_csv = RAW_DIR / "prices.csv"

    stations_df.to_csv(stations_csv, index=False)
    prices_df.to_csv(prices_csv, index=False)

    print(f"Stations: {len(stations_df):,} → {stations_csv}")
    print(f"Prices:   {len(prices_df):,} → {prices_csv}")
    print("\nFuel types:")
    print(prices_df["carburant"].value_counts())
    print("\nPrice stats:")
    print(prices_df["prix_euros"].describe())

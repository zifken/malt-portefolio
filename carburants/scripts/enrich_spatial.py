"""
Enrich fuel stations with spatial features for pricing analysis.

Creates:
- raw/stations_enriched.csv
- outputs/spatial_enrichment_report.txt
"""

from pathlib import Path
import pandas as pd
import numpy as np


PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "raw"
OUTPUTS_DIR = PROJECT_DIR / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)


# Service categories of interest
SERVICE_MAP = {
    "24/7": "Automate CB 24/24",
    "car_wash_auto": "Lavage automatique",
    "car_wash_manual": "Lavage manuel",
    "shop_food": "Boutique alimentaire",
    "shop_non_food": "Boutique non alimentaire",
    "restaurant_takeaway": "Restauration à emporter",
    "restaurant_on_site": "Restauration sur place",
    "tire_inflation": "Station de gonflage",
    "truck_lane": "Piste poids lourds",
    "atm": "DAB (Distributeur automatique de billets)",
    "ev_charging": "Bornes électriques",
    "lpg": "Vente de gaz domestique (Butane, Propane)",
    "wifi": "Wifi",
    "toilets": "Toilettes publiques",
    "repair": "Services réparation / entretien",
    "camper_area": "Aire de camping-cars",
    "bar": "Bar",
}


# Urban departments (top 15 by population density, approx.)
URBAN_DEPTS = {
    "75", "92", "93", "94",  # Paris + petite couronne
    "69", "13", "31", "33", "59", "67", "44", "6", "34", "76",
}


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    stations = pd.read_csv(RAW_DIR / "stations.csv")
    prices = pd.read_csv(RAW_DIR / "prices.csv")
    pop = pd.read_csv(RAW_DIR / "department_population.csv")
    return stations, prices, pop


def add_service_dummies(stations: pd.DataFrame) -> pd.DataFrame:
    """Create one-hot columns for key services."""
    out = stations.copy()
    out["services"] = out["services"].fillna("")
    for col, pattern in SERVICE_MAP.items():
        out[f"has_{col}"] = out["services"].str.contains(pattern, case=False, regex=False).astype(int)
    out["n_services"] = out[[c for c in out.columns if c.startswith("has_")]].sum(axis=1)
    return out


def add_route_segment(stations: pd.DataFrame) -> pd.DataFrame:
    """Categorize route type."""
    out = stations.copy()
    out["route_segment"] = out["type_route"].map({
        "A": "motorway",
        "R": "road",
        "M": "other",
    }).fillna("unknown")
    return out


def add_urban_flag(stations: pd.DataFrame) -> pd.DataFrame:
    """Flag urban vs rural departments."""
    out = stations.copy()
    out["departement"] = out["departement"].astype(str)
    out["is_urban_dept"] = out["departement"].isin(URBAN_DEPTS).astype(int)
    return out


def compute_station_features(stations: pd.DataFrame, prices: pd.DataFrame, pop: pd.DataFrame) -> pd.DataFrame:
    """Merge station features with price stats and population."""
    # Latest price per station for each fuel
    latest = prices.sort_values("date_maj").groupby(["id_station", "carburant"]).last().reset_index()
    price_pivot = latest.pivot(index="id_station", columns="carburant", values="prix_euros")
    price_pivot.columns = [f"price_{c}" for c in price_pivot.columns]

    # Keep last update date per station
    last_update = prices.groupby("id_station")["date_maj"].max().rename("last_update")
    price_pivot = price_pivot.join(last_update)

    out = stations.merge(price_pivot, left_on="id_station", right_index=True, how="left")
    out["departement"] = out["departement"].astype(str)
    # Fix Corsica: keep 2A/2B as-is; map 20 -> 2A/2B if needed
    out.loc[out["departement"] == "20", "departement"] = "2A"
    pop["departement"] = pop["departement"].astype(str)
    # Add Corsica population split if missing
    if "2A" not in pop["departement"].values:
        corsica = pd.DataFrame({
            "departement": ["2A", "2B"],
            "population_2023": [160000, 190000],  # approx. split
        })
        pop = pd.concat([pop, corsica], ignore_index=True)
    out = out.merge(pop, on="departement", how="left")

    return out


def generate_report(df: pd.DataFrame) -> str:
    lines = []
    lines.append("=" * 70)
    lines.append("SPATIAL ENRICHMENT REPORT")
    lines.append("=" * 70)
    lines.append(f"Total stations: {len(df):,}")
    lines.append(f"Stations with coordinates: {df['latitude'].notna().sum():,}")
    lines.append(f"Stations with at least one price: {df.filter(like='price_').notna().any(axis=1).sum():,}")

    lines.append("\n--- Route segment distribution ---")
    lines.append(df["route_segment"].value_counts().to_string())

    lines.append("\n--- Urban vs rural ---")
    lines.append(df["is_urban_dept"].value_counts().rename({0: "rural", 1: "urban"}).to_string())

    lines.append("\n--- Service availability ---")
    svc_cols = [c for c in df.columns if c.startswith("has_")]
    for c in sorted(svc_cols):
        lines.append(f"{c.replace('has_', ''):20s}: {df[c].sum():4d} ({100*df[c].mean():.1f}%)")

    lines.append("\n--- Gazole price by route segment ---")
    gazole = df[df["price_Gazole"].notna()]
    lines.append(gazole.groupby("route_segment")["price_Gazole"].describe().to_string())

    lines.append("\n--- Gazole price: urban vs rural ---")
    lines.append(gazole.groupby("is_urban_dept")["price_Gazole"].agg(["mean", "median", "std", "count"]).to_string())

    # Pricing desert: departments with few stations per capita
    lines.append("\n--- Pricing desert metric (Gazole stations per 100k inhabitants) ---")
    dept_stats = gazole.groupby("departement").agg(
        stations=("id_station", "nunique"),
        population=("population_2023", "first"),
        avg_price=("price_Gazole", "mean"),
    ).reset_index()
    dept_stats["stations_per_100k"] = (dept_stats["stations"] / dept_stats["population"]) * 100_000
    dept_stats = dept_stats[dept_stats["population"].notna()]
    dept_stats = dept_stats.sort_values("stations_per_100k")
    lines.append("Bottom 15 (most scarce):")
    lines.append(dept_stats.head(15).to_string(index=False))
    lines.append("\nTop 15 (most dense):")
    lines.append(dept_stats.tail(15).to_string(index=False))

    return "\n".join(lines)


if __name__ == "__main__":
    stations, prices, pop = load_data()
    print(f"Loaded {len(stations):,} stations and {len(prices):,} price records")

    enriched = add_service_dummies(stations)
    enriched = add_route_segment(enriched)
    enriched = add_urban_flag(enriched)
    enriched = compute_station_features(enriched, prices, pop)

    out_path = RAW_DIR / "stations_enriched.csv"
    enriched.to_csv(out_path, index=False)
    print(f"Saved enriched stations → {out_path}")

    report = generate_report(enriched)
    report_path = OUTPUTS_DIR / "spatial_enrichment_report.txt"
    report_path.write_text(report, encoding="utf-8")
    print(f"Saved report → {report_path}")
    print("\n" + report)

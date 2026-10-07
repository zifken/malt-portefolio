"""
Quick exploratory analysis of French fuel prices.

Outputs:
- outputs/fuel_summary.txt
- outputs/prices_boxplot.png
- outputs/gazole_dept_top10.png
- outputs/stations_map.html
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px


PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "raw"
OUTPUTS_DIR = PROJECT_DIR / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)


def load_data() -> pd.DataFrame:
    """Merge stations and prices into a single DataFrame."""
    stations = pd.read_csv(RAW_DIR / "stations.csv")
    prices = pd.read_csv(RAW_DIR / "prices.csv")
    return prices.merge(stations, on="id_station", how="left")


def summary_report(df: pd.DataFrame) -> str:
    """Generate a human-readable summary of the dataset."""
    lines = []
    lines.append("=" * 60)
    lines.append("FRENCH FUEL PRICES — DATASET SNAPSHOT")
    lines.append("=" * 60)
    lines.append(f"Download date:   {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"Stations:        {df['id_station'].nunique():,}")
    lines.append(f"Price records:   {len(df):,}")
    lines.append("\n--- Average price per fuel type ---")

    avg = df.groupby("carburant")["prix_euros"].agg(["mean", "min", "max", "count"])
    lines.append(avg.sort_values("mean").to_string())

    lines.append("\n--- Top 10 cheapest Gazole stations ---")
    gazole = df[df["carburant"] == "Gazole"].copy()
    cheap = gazole.nsmallest(10, "prix_euros")[[
        "ville", "departement", "code_postal", "adresse", "prix_euros", "date_maj"
    ]]
    lines.append(cheap.to_string(index=False))

    lines.append("\n--- Top 10 most expensive Gazole stations ---")
    expensive = gazole.nlargest(10, "prix_euros")[[
        "ville", "departement", "code_postal", "adresse", "prix_euros", "date_maj"
    ]]
    lines.append(expensive.to_string(index=False))

    lines.append("\n--- Top 10 most expensive departments (Gazole, min 20 stations) ---")
    dept = gazole.groupby("departement")["prix_euros"].agg(["mean", "count"])
    dept = dept[dept["count"] >= 20].sort_values("mean", ascending=False).head(10)
    lines.append(dept.to_string())

    lines.append("\n--- Top 10 cheapest departments (Gazole, min 20 stations) ---")
    dept_all = gazole.groupby("departement")["prix_euros"].agg(["mean", "count"])
    dept_all = dept_all[dept_all["count"] >= 20].sort_values("mean", ascending=True).head(10)
    lines.append(dept_all.to_string())

    return "\n".join(lines)


def price_boxplot(df: pd.DataFrame) -> Path:
    """Save a boxplot of fuel prices by type."""
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x="carburant", y="prix_euros", order=sorted(df["carburant"].unique()))
    plt.title("Fuel price distribution by type (€/L)")
    plt.ylabel("Price (€)")
    plt.xlabel("Fuel type")
    plt.tight_layout()
    path = OUTPUTS_DIR / "prices_boxplot.png"
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def top_departments_chart(gazole: pd.DataFrame) -> Path:
    """Save a bar chart of average Gazole price by department."""
    dept = gazole.groupby("departement")["prix_euros"].agg(["mean", "count"])
    dept = dept[dept["count"] >= 20].sort_values("mean").head(15)
    dept.index = dept.index.astype(str)
    colors = sns.color_palette("RdYlGn_r", n_colors=len(dept))

    plt.figure(figsize=(10, 8))
    bars = plt.barh(dept.index, dept["mean"], color=colors)
    plt.title("15 cheapest departments for Gazole (min. 20 stations)")
    plt.xlabel("Average price (€/L)")
    plt.ylabel("Department")
    plt.gca().invert_yaxis()  # cheapest at top
    for bar, mean in zip(bars, dept["mean"]):
        plt.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height()/2,
                 f"{mean:.3f}", va="center", fontsize=9)
    plt.xlim(dept["mean"].min() - 0.02, dept["mean"].max() + 0.05)
    plt.tight_layout()
    path = OUTPUTS_DIR / "gazole_dept_top15.png"
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def create_map(gazole: pd.DataFrame) -> Path:
    """Create an interactivefolium map with the cheapest Gazole stations."""
    # Keep stations with known coordinates
    map_data = gazole.dropna(subset=["latitude", "longitude", "prix_euros"])
    # Sample for map readability
    sample = map_data.nsmallest(500, "prix_euros")

    fig = px.scatter_map(
        sample,
        lat="latitude",
        lon="longitude",
        color="prix_euros",
        hover_name="ville",
        hover_data={"prix_euros": ":.3f", "adresse": True, "departement": True},
        color_continuous_scale="RdYlGn_r",
        zoom=5,
        height=700,
        title="500 cheapest Gazole stations in France",
    )
    fig.update_layout(mapbox_style="carto-positron")
    path = OUTPUTS_DIR / "stations_map.html"
    fig.write_html(path)
    return path


if __name__ == "__main__":
    df = load_data()
    print(f"Loaded {len(df):,} price records from {df['id_station'].nunique():,} stations")

    report = summary_report(df)
    report_path = OUTPUTS_DIR / "fuel_summary.txt"
    report_path.write_text(report, encoding="utf-8")
    print(f"\nSaved summary → {report_path}")

    p1 = price_boxplot(df)
    print(f"Saved plot   → {p1}")

    gazole = df[df["carburant"] == "Gazole"].copy()
    p2 = top_departments_chart(gazole)
    print(f"Saved plot   → {p2}")

    p3 = create_map(gazole)
    print(f"Saved map    → {p3}")

    print("\n" + "=" * 60)
    print(report)
    print("=" * 60)

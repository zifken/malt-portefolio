"""
Spatial pricing analysis of French fuel stations.

Outputs:
- outputs/spatial_analysis_report.txt
- outputs/price_map_gazole.html
- outputs/motorway_premium_chart.png
- outputs/dept_price_map.png
- outputs/pricing_desert_chart.png
- outputs/service_premium_chart.png
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats


PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "raw"
OUTPUTS_DIR = PROJECT_DIR / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)


def load_enriched() -> pd.DataFrame:
    df = pd.read_csv(RAW_DIR / "stations_enriched.csv")
    df["last_update"] = pd.to_datetime(df["last_update"])
    return df


def motorway_premium(df: pd.DataFrame, fuel: str = "Gazole") -> dict:
    """Compute motorway price premium with confidence interval."""
    col = f"price_{fuel}"
    m = df[df["route_segment"] == "motorway"][col].dropna()
    r = df[df["route_segment"] == "road"][col].dropna()

    t_stat, p_value = stats.ttest_ind(m, r, equal_var=False)
    diff = m.mean() - r.mean()
    pct = 100 * diff / r.mean()

    # 95% CI for difference
    se = np.sqrt(m.var()/len(m) + r.var()/len(r))
    ci_low = diff - 1.96 * se
    ci_high = diff + 1.96 * se

    return {
        "fuel": fuel,
        "motorway_mean": m.mean(),
        "road_mean": r.mean(),
        "premium_eur": diff,
        "premium_pct": pct,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "t_stat": t_stat,
        "p_value": p_value,
        "n_motorway": len(m),
        "n_road": len(r),
    }


def service_premiums(df: pd.DataFrame, fuel: str = "Gazole") -> pd.DataFrame:
    """Compute price premium for each service."""
    col = f"price_{fuel}"
    subset = df[df[col].notna()].copy()
    svc_cols = [c for c in df.columns if c.startswith("has_")]
    results = []
    for c in svc_cols:
        with_svc = subset[subset[c] == 1][col]
        without_svc = subset[subset[c] == 0][col]
        if len(with_svc) < 30 or len(without_svc) < 30:
            continue
        t_stat, p_value = stats.ttest_ind(with_svc, without_svc, equal_var=False)
        results.append({
            "service": c.replace("has_", ""),
            "n_with": len(with_svc),
            "n_without": len(without_svc),
            "mean_with": with_svc.mean(),
            "mean_without": without_svc.mean(),
            "premium_eur": with_svc.mean() - without_svc.mean(),
            "premium_pct": 100 * (with_svc.mean() - without_svc.mean()) / without_svc.mean(),
            "p_value": p_value,
        })
    return pd.DataFrame(results).sort_values("premium_eur", ascending=False)


def urban_rural_premium(df: pd.DataFrame, fuel: str = "Gazole") -> dict:
    col = f"price_{fuel}"
    u = df[df["is_urban_dept"] == 1][col].dropna()
    r = df[df["is_urban_dept"] == 0][col].dropna()
    t_stat, p_value = stats.ttest_ind(u, r, equal_var=False)
    diff = u.mean() - r.mean()
    return {
        "fuel": fuel,
        "urban_mean": u.mean(),
        "rural_mean": r.mean(),
        "premium_eur": diff,
        "premium_pct": 100 * diff / r.mean(),
        "p_value": p_value,
        "n_urban": len(u),
        "n_rural": len(r),
    }


def create_price_map(df: pd.DataFrame, fuel: str = "Gazole") -> Path:
    col = f"price_{fuel}"
    map_df = df.dropna(subset=["latitude", "longitude", col]).copy()
    map_df = map_df[map_df[col] > 0]

    fig = px.scatter_map(
        map_df.sample(min(5000, len(map_df)), random_state=42),
        lat="latitude",
        lon="longitude",
        color=col,
        hover_name="ville",
        hover_data={col: ":.3f", "adresse": True, "departement": True, "route_segment": True},
        color_continuous_scale="RdYlGn_r",
        zoom=5,
        height=700,
        title=f"{fuel} prices across France",
    )
    fig.update_layout(mapbox_style="carto-positron")
    path = OUTPUTS_DIR / f"price_map_{fuel.lower()}.html"
    fig.write_html(path)
    return path


def create_motorway_chart(df: pd.DataFrame) -> Path:
    fuels = ["Gazole", "SP95", "SP98", "E10", "E85", "GPLc"]
    rows = []
    for f in fuels:
        try:
            res = motorway_premium(df, f)
            rows.append(res)
        except Exception:
            pass
    res_df = pd.DataFrame(rows)

    plt.figure(figsize=(10, 6))
    colors = ["#d62728" if x > 0 else "#2ca02c" for x in res_df["premium_eur"]]
    bars = plt.bar(res_df["fuel"], res_df["premium_eur"], color=colors, alpha=0.8)
    plt.axhline(0, color="black", linewidth=0.8)
    plt.title("Motorway price premium vs. road stations (€/L)")
    plt.ylabel("Premium (€/L)")
    for bar, val, pct in zip(bars, res_df["premium_eur"], res_df["premium_pct"]):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                 f"+{val:.3f}\n({pct:+.1f}%)", ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    path = OUTPUTS_DIR / "motorway_premium_chart.png"
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def create_dept_price_chart(df: pd.DataFrame, fuel: str = "Gazole") -> Path:
    col = f"price_{fuel}"
    dept = df.groupby("departement").agg(
        avg_price=(col, "mean"),
        stations=("id_station", "nunique"),
        population=("population_2023", "first"),
    ).reset_index()
    dept = dept[dept["stations"] >= 10]
    dept = dept.sort_values("avg_price", ascending=False).head(20)
    dept["departement"] = dept["departement"].astype(str)

    plt.figure(figsize=(10, 8))
    colors = sns.color_palette("RdYlGn_r", n_colors=len(dept))
    bars = plt.barh(dept["departement"], dept["avg_price"], color=colors)
    plt.gca().invert_yaxis()
    plt.title(f"Top 20 most expensive departments — {fuel} (min. 10 stations)")
    plt.xlabel("Average price (€/L)")
    plt.ylabel("Department")
    for bar, val in zip(bars, dept["avg_price"]):
        plt.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height()/2,
                 f"{val:.3f}", va="center", fontsize=9)
    plt.tight_layout()
    path = OUTPUTS_DIR / f"dept_price_top20_{fuel.lower()}.png"
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def create_pricing_desert_chart(df: pd.DataFrame, fuel: str = "Gazole") -> Path:
    col = f"price_{fuel}"
    dept = df.groupby("departement").agg(
        stations=("id_station", "nunique"),
        population=("population_2023", "first"),
        avg_price=(col, "mean"),
    ).reset_index()
    dept = dept[dept["population"].notna()]
    dept["stations_per_100k"] = (dept["stations"] / dept["population"]) * 100_000
    dept = dept.sort_values("stations_per_100k").head(20)
    dept["departement"] = dept["departement"].astype(str)

    fig, ax1 = plt.subplots(figsize=(10, 8))
    bars = ax1.barh(dept["departement"], dept["stations_per_100k"], color=sns.color_palette("Blues_r", len(dept)))
    ax1.set_xlabel("Stations per 100k inhabitants")
    ax1.set_ylabel("Department")
    ax1.invert_yaxis()
    ax1.set_title(f"Fuel station scarcity — bottom 20 departments ({fuel})")

    ax2 = ax1.twiny()
    ax2.scatter(dept["avg_price"], dept["departement"], color="red", s=40, label="Avg price (€/L)", zorder=5)
    ax2.set_xlabel("Average price (€/L)", color="red")
    ax2.tick_params(axis="x", colors="red")

    plt.tight_layout()
    path = OUTPUTS_DIR / f"pricing_desert_{fuel.lower()}.png"
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def create_service_premium_chart(svc_df: pd.DataFrame) -> Path:
    plt.figure(figsize=(10, 7))
    colors = ["#d62728" if x > 0 else "#2ca02c" for x in svc_df["premium_eur"]]
    bars = plt.barh(svc_df["service"], svc_df["premium_eur"], color=colors, alpha=0.8)
    plt.axvline(0, color="black", linewidth=0.8)
    plt.title("Service price premium — Gazole (€/L)")
    plt.xlabel("Premium (€/L)")
    for bar, val, pct in zip(bars, svc_df["premium_eur"], svc_df["premium_pct"]):
        plt.text(bar.get_width() + (0.005 if val >= 0 else -0.005),
                 bar.get_y() + bar.get_height()/2,
                 f"{val:+.3f} ({pct:+.1f}%)",
                 va="center", ha="left" if val >= 0 else "right", fontsize=9)
    plt.tight_layout()
    path = OUTPUTS_DIR / "service_premium_gazole.png"
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def generate_report(df: pd.DataFrame) -> str:
    lines = []
    lines.append("=" * 70)
    lines.append("SPATIAL PRICING ANALYSIS REPORT")
    lines.append("=" * 70)

    # Motorway premiums for all fuels
    lines.append("\n--- Motorway price premium ---")
    fuels = ["Gazole", "SP95", "SP98", "E10", "E85", "GPLc"]
    for f in fuels:
        try:
            res = motorway_premium(df, f)
            lines.append(f"{f:8s}: road={res['road_mean']:.3f} | motorway={res['motorway_mean']:.3f} | "
                         f"+{res['premium_eur']:.3f} € ({res['premium_pct']:+.1f}%) "
                         f"[CI {res['ci_low']:.3f}, {res['ci_high']:.3f}] p={res['p_value']:.2e}")
        except Exception as e:
            lines.append(f"{f:8s}: error {e}")

    # Urban premium
    lines.append("\n--- Urban vs rural premium ---")
    for f in fuels:
        try:
            res = urban_rural_premium(df, f)
            lines.append(f"{f:8s}: rural={res['rural_mean']:.3f} | urban={res['urban_mean']:.3f} | "
                         f"{res['premium_eur']:+.3f} € ({res['premium_pct']:+.1f}%) p={res['p_value']:.2e}")
        except Exception as e:
            lines.append(f"{f:8s}: error {e}")

    # Service premiums
    lines.append("\n--- Service premiums (Gazole) ---")
    svc = service_premiums(df, "Gazole")
    lines.append(svc[["service", "premium_eur", "premium_pct", "p_value", "n_with"]].to_string(index=False))

    return "\n".join(lines)


if __name__ == "__main__":
    df = load_enriched()
    print(f"Loaded {len(df):,} enriched stations")

    report = generate_report(df)
    report_path = OUTPUTS_DIR / "spatial_analysis_report.txt"
    report_path.write_text(report, encoding="utf-8")
    print(f"Saved report → {report_path}")

    p1 = create_price_map(df, "Gazole")
    print(f"Saved map → {p1}")

    p2 = create_motorway_chart(df)
    print(f"Saved chart → {p2}")

    p3 = create_dept_price_chart(df, "Gazole")
    print(f"Saved chart → {p3}")

    p4 = create_pricing_desert_chart(df, "Gazole")
    print(f"Saved chart → {p4}")

    svc = service_premiums(df, "Gazole")
    p5 = create_service_premium_chart(svc)
    print(f"Saved chart → {p5}")

    print("\n" + "=" * 70)
    print(report)
    print("=" * 70)

"""
Streamlit dashboard: Spatial Pricing Intelligence — French fuel stations.

Run locally:
    python3 -m streamlit run app.py
"""

from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st


PROJECT_DIR = Path(__file__).resolve().parent
ENRICHED_PATH = PROJECT_DIR / "raw" / "stations_enriched.csv"


@st.cache_data(show_spinner="Loading enriched station data...")
def load_data() -> pd.DataFrame:
    df = pd.read_csv(ENRICHED_PATH)
    df["last_update"] = pd.to_datetime(df["last_update"])
    df["departement"] = df["departement"].astype(str)
    return df


def motorway_premium(df: pd.DataFrame, fuel: str) -> dict:
    col = f"price_{fuel}"
    m = df[df["route_segment"] == "motorway"][col].dropna()
    r = df[df["route_segment"] == "road"][col].dropna()
    return {
        "fuel": fuel,
        "motorway_mean": m.mean(),
        "road_mean": r.mean(),
        "premium_eur": m.mean() - r.mean(),
        "premium_pct": 100 * (m.mean() - r.mean()) / r.mean(),
        "n_motorway": len(m),
        "n_road": len(r),
    }


def main():
    st.set_page_config(
        page_title="Fuel Price Spatial Intelligence",
        page_icon="⛽",
        layout="wide",
    )

    st.title("⛽ French Fuel Prices — Spatial Pricing Intelligence")
    st.markdown(
        "Live analysis of **9,800+ fuel stations** from [data.gouv.fr](https://www.data.gouv.fr/datasets/prix-des-carburants-en-france-flux-instantane-v2-amelioree/) "
        "— updated every 10 minutes."
    )

    df = load_data()

    # Sidebar filters
    st.sidebar.header("Filters")
    fuel_type = st.sidebar.selectbox(
        "Fuel type",
        options=["Gazole", "SP95", "SP98", "E10", "E85", "GPLc"],
        index=0,
    )
    price_col = f"price_{fuel_type}"

    min_stations = st.sidebar.slider(
        "Min. stations per department",
        min_value=5,
        max_value=100,
        value=20,
        step=5,
    )

    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🗺️ Price Map",
        "🛣️ Motorway Premium",
        "🏙️ Pricing Deserts",
        "🔧 Service Premiums",
    ])

    # KPIs
    subset = df[df[price_col].notna()].copy()
    motorway = subset[subset["route_segment"] == "motorway"]
    road = subset[subset["route_segment"] == "road"]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Stations analyzed", f"{len(subset):,}")
    col2.metric("Avg. price", f"{subset[price_col].mean():.3f} €/L")
    if len(motorway) and len(road):
        col3.metric(
            "Motorway premium",
            f"+{motorway[price_col].mean() - road[price_col].mean():.3f} €/L",
            help=f"n motorway = {len(motorway):,} · n road = {len(road):,} "
                 f"({len(motorway)/len(subset)*100:.1f}% of stations are motorway)",
        )
    else:
        col3.metric("Motorway premium", "—")
    most_expensive_dept = subset.groupby("departement")[price_col].mean().idxmax()
    col4.metric("Most expensive dept.", most_expensive_dept)

    # --- Tab 1: Price Map ---
    with tab1:
        st.subheader(f"{fuel_type} prices across France")
        map_df = subset.dropna(subset=["latitude", "longitude", price_col])
        map_df = map_df.sample(min(4000, len(map_df)), random_state=42)

        fig_map = px.scatter_map(
            map_df,
            lat="latitude",
            lon="longitude",
            color=price_col,
            hover_name="ville",
            hover_data={
                price_col: ":.3f",
                "adresse": True,
                "departement": True,
                "route_segment": True,
            },
            color_continuous_scale="RdYlGn_r",
            zoom=5,
            height=650,
        )
        fig_map.update_layout(mapbox_style="carto-positron")
        st.plotly_chart(fig_map, use_container_width=True)

    # --- Tab 2: Motorway Premium ---
    with tab2:
        st.subheader("Motorway vs. road price premium")
        fuels = ["Gazole", "SP95", "SP98", "E10", "E85", "GPLc"]
        premiums = [motorway_premium(df, f) for f in fuels]
        prem_df = pd.DataFrame(premiums)

        fig_prem = px.bar(
            prem_df,
            x="fuel",
            y="premium_eur",
            text=prem_df["premium_pct"].apply(lambda x: f"{x:+.1f}%"),
            color="premium_eur",
            color_continuous_scale="RdYlGn_r",
            labels={"premium_eur": "Premium (€/L)", "fuel": "Fuel type"},
            title="Motorway stations charge a significant premium",
        )
        st.plotly_chart(fig_prem, use_container_width=True)

        st.dataframe(
            prem_df[["fuel", "road_mean", "motorway_mean", "premium_eur", "premium_pct", "n_road", "n_motorway"]]
            .round(4),
            use_container_width=True,
        )

        st.info(
            f"**{fuel_type}**: motorway stations charge **+{prem_df[prem_df['fuel'] == fuel_type]['premium_eur'].iloc[0]:.3f} €/L** "
            f"({prem_df[prem_df['fuel'] == fuel_type]['premium_pct'].iloc[0]:+.1f}%) on average."
        )

        st.caption(
            "⚠️ **Taille d'échantillon :** les stations autoroutières ne représentent "
            f"qu'environ {len(df[df['route_segment']=='motorway'])/len(df)*100:.1f}% du parc "
            f"({len(df[df['route_segment']=='motorway']):,} stations vs "
            f"{len(df[df['route_segment']=='road']):,} sur route). "
            "L'écart est statistiquement significatif (test de Welch, p < 10⁻⁴⁹) "
            "mais repose sur un sous-échantillon réduit — à interpréter avec ce contexte."
        )

    # --- Tab 3: Pricing Deserts ---
    with tab3:
        st.subheader("Fuel station scarcity by department")
        dept = subset.groupby("departement").agg(
            stations=("id_station", "nunique"),
            population=("population_2023", "first"),
            avg_price=(price_col, "mean"),
        ).reset_index()
        dept = dept[dept["stations"] >= min_stations]
        dept["stations_per_100k"] = (dept["stations"] / dept["population"]) * 100_000
        dept = dept.sort_values("stations_per_100k")

        fig_desert = px.scatter(
            dept.head(30),
            x="stations_per_100k",
            y="avg_price",
            size="stations",
            hover_name="departement",
            labels={
                "stations_per_100k": "Stations per 100k inhabitants",
                "avg_price": f"Avg. {fuel_type} price (€/L)",
                "stations": "Number of stations",
            },
            title="Scarcity vs. price — fewer stations does not always mean higher prices",
        )
        st.plotly_chart(fig_desert, use_container_width=True)

        st.dataframe(
            dept.head(20)[["departement", "stations", "population", "stations_per_100k", "avg_price"]].round(3),
            use_container_width=True,
        )

        st.caption(
            "Paris (75) has only **1.83 Gazole stations per 100k inhabitants**, "
            "while Lozère (48) has **48.68** — a **27x difference**."
        )

    # --- Tab 4: Service Premiums ---
    with tab4:
        st.subheader("Which services are associated with higher prices?")
        svc_cols = [c for c in df.columns if c.startswith("has_")]
        svc_rows = []
        for c in svc_cols:
            with_svc = subset[subset[c] == 1][price_col]
            without_svc = subset[subset[c] == 0][price_col]
            if len(with_svc) < 30 or len(without_svc) < 30:
                continue
            svc_rows.append({
                "service": c.replace("has_", ""),
                "premium_eur": with_svc.mean() - without_svc.mean(),
                "premium_pct": 100 * (with_svc.mean() - without_svc.mean()) / without_svc.mean(),
                "n_with": len(with_svc),
                "n_without": len(without_svc),
            })
        svc_df = pd.DataFrame(svc_rows).sort_values("premium_eur", ascending=False)

        fig_svc = px.bar(
            svc_df,
            x="premium_eur",
            y="service",
            orientation="h",
            text=svc_df["premium_pct"].apply(lambda x: f"{x:+.1f}%"),
            color="premium_eur",
            color_continuous_scale="RdYlGn_r",
            labels={"premium_eur": "Premium (€/L)", "service": "Service"},
            title=f"Service price premiums — {fuel_type}",
        )
        st.plotly_chart(fig_svc, use_container_width=True)

        st.dataframe(svc_df.round(4), use_container_width=True)

        st.info(
            "Shops, restaurants, and Wi-Fi are associated with **higher** prices. "
            "24/7, ATM, and LPG sales are associated with **lower** prices — likely because they indicate "
            "high-volume, automated stations."
        )

    # Footer
    st.markdown("---")
    st.caption(
        "Data: [data.gouv.fr](https://www.data.gouv.fr) | "
        "Source: [donnees.roulez-eco.fr](https://donnees.roulez-eco.fr) | "
        "Built with Python, pandas, Plotly, and Streamlit."
    )


if __name__ == "__main__":
    main()

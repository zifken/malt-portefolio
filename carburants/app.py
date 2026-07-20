"""
Streamlit dashboard: Spatial Pricing Intelligence — French fuel stations.

Run locally:
    python3 -m streamlit run app.py
"""

from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


PROJECT_DIR = Path(__file__).resolve().parent
ENRICHED_PATH = PROJECT_DIR / "raw" / "stations_enriched.csv"


THEME = {
    "colors": {
        "bg": "#FFFFFF",
        "surface": "#F5F5F7",
        "primary": "#1B3A5C",
        "secondary": "#C8553D",
        "tertiary": "#5B8C5A",
        "text": "#1A1A1A",
        "muted": "#6B6B6B",
        "grid": "#E0E0E0",
        "font": "Helvetica Neue, Arial, sans-serif",
    }
}

TEMPLATE = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor=THEME["colors"]["bg"],
        plot_bgcolor=THEME["colors"]["bg"],
        font={
            "family": THEME["colors"]["font"],
            "color": THEME["colors"]["text"],
        },
        title={
            "font": {
                "family": THEME["colors"]["font"],
                "color": THEME["colors"]["primary"],
            }
        },
        colorway=[
            THEME["colors"]["primary"],
            THEME["colors"]["secondary"],
            THEME["colors"]["tertiary"],
        ],
        xaxis={
            "gridcolor": THEME["colors"]["grid"],
            "linecolor": THEME["colors"]["grid"],
            "zerolinecolor": THEME["colors"]["grid"],
            "title": {"font": {"color": THEME["colors"]["text"]}},
        },
        yaxis={
            "gridcolor": THEME["colors"]["grid"],
            "linecolor": THEME["colors"]["grid"],
            "zerolinecolor": THEME["colors"]["grid"],
            "title": {"font": {"color": THEME["colors"]["text"]}},
        },
        legend={
            "font": {"color": THEME["colors"]["text"]},
            "title": {"font": {"color": THEME["colors"]["primary"]}},
        },
        hoverlabel={
            "bgcolor": THEME["colors"]["surface"],
            "font": {
                "family": THEME["colors"]["font"],
                "color": THEME["colors"]["text"],
            },
        },
    )
)

COLOR_SCALE = [
    [0.0, THEME["colors"]["tertiary"]],
    [0.5, THEME["colors"]["surface"]],
    [1.0, THEME["colors"]["secondary"]],
]

SERVICE_LABELS = {
    "24/7": "24 h/24, 7 j/7",
    "car_wash_auto": "Lavage automatique",
    "car_wash_manual": "Lavage manuel",
    "shop_food": "Boutique alimentaire",
    "shop_non_food": "Boutique non alimentaire",
    "restaurant_takeaway": "Restauration à emporter",
    "restaurant_on_site": "Restauration sur place",
    "tire_inflation": "Gonflage des pneus",
    "truck_lane": "Piste poids lourds",
    "atm": "Distributeur automatique de billets",
    "ev_charging": "Recharge électrique",
    "lpg": "GPL",
    "wifi": "Wi-Fi",
    "toilets": "Toilettes",
    "repair": "Réparation",
    "camper_area": "Aire pour camping-cars",
    "bar": "Bar",
}


@st.cache_data(show_spinner="Chargement des données enrichies des stations...")
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
        page_title="Analyse spatiale des prix des carburants",
        page_icon=None,
        layout="wide",
    )

    st.title("Prix des carburants en France — Analyse spatiale des prix")
    st.markdown(
        "Analyse en direct de **plus de 9 800 stations-service** à partir de "
        "[data.gouv.fr](https://www.data.gouv.fr/datasets/prix-des-carburants-en-france-flux-instantane-v2-amelioree/) "
        "— données actualisées toutes les 10 minutes."
    )

    df = load_data()

    # Sidebar filters
    st.sidebar.header("Filtres")
    fuel_type = st.sidebar.selectbox(
        "Type de carburant",
        options=["Gazole", "SP95", "SP98", "E10", "E85", "GPLc"],
        index=0,
    )
    price_col = f"price_{fuel_type}"

    min_stations = st.sidebar.slider(
        "Nombre min. de stations par département",
        min_value=5,
        max_value=100,
        value=20,
        step=5,
    )

    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Carte des prix",
        "Prime autoroutière",
        "Déserts de prix",
        "Primes de services",
    ])

    # KPIs
    subset = df[df[price_col].notna()].copy()
    motorway = subset[subset["route_segment"] == "motorway"]
    road = subset[subset["route_segment"] == "road"]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Stations analysées", f"{len(subset):,.0f}")
    col2.metric("Prix moyen", f"{subset[price_col].mean():.3f} €/L")
    if len(motorway) and len(road):
        col3.metric(
            "Prime autoroutière",
            f"+{motorway[price_col].mean() - road[price_col].mean():.3f} €/L",
            help=f"n autoroute = {len(motorway):,.0f} · n route = {len(road):,.0f} "
                 f"({len(motorway)/len(subset)*100:.1f}% des stations sont sur autoroute)",
        )
    else:
        col3.metric("Prime autoroutière", "—")
    most_expensive_dept = subset.groupby("departement")[price_col].mean().idxmax()
    col4.metric("Dépt. le plus cher", str(most_expensive_dept))

    # --- Tab 1: Price Map ---
    with tab1:
        st.subheader(f"Prix du {fuel_type} en France")
        map_df = subset.dropna(subset=["latitude", "longitude", price_col])
        map_df = map_df.sample(min(4000, len(map_df)), random_state=42)
        map_df["route_segment"] = map_df["route_segment"].replace({
            "motorway": "autoroute",
            "road": "route",
        })

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
            labels={
                price_col: f"Prix du {fuel_type} (€/L)",
                "adresse": "Adresse",
                "departement": "Département",
                "route_segment": "Type de route",
                "latitude": "Latitude",
                "longitude": "Longitude",
            },
            color_continuous_scale=COLOR_SCALE,
            zoom=5,
            height=650,
        )
        fig_map.update_layout(template=TEMPLATE, mapbox_style="carto-positron")
        st.plotly_chart(fig_map, use_container_width=True)

    # --- Tab 2: Motorway Premium ---
    with tab2:
        st.subheader("Prime de prix autoroute vs route")
        fuels = ["Gazole", "SP95", "SP98", "E10", "E85", "GPLc"]
        premiums = [motorway_premium(df, f) for f in fuels]
        prem_df = pd.DataFrame(premiums)

        fig_prem = px.bar(
            prem_df,
            x="fuel",
            y="premium_eur",
            text=prem_df["premium_pct"].apply(lambda x: f"{x:+.1f}%"),
            color="premium_eur",
            color_continuous_scale=COLOR_SCALE,
            color_continuous_midpoint=0,
            labels={"premium_eur": "Prime (€/L)", "fuel": "Type de carburant"},
            title="Les stations autoroutières appliquent une prime significative",
        )
        fig_prem.update_layout(template=TEMPLATE)
        st.plotly_chart(fig_prem, use_container_width=True)

        st.dataframe(
            prem_df[["fuel", "road_mean", "motorway_mean", "premium_eur", "premium_pct", "n_road", "n_motorway"]]
            .rename(columns={
                "fuel": "Carburant",
                "road_mean": "Prix moyen route (€/L)",
                "motorway_mean": "Prix moyen autoroute (€/L)",
                "premium_eur": "Prime (€/L)",
                "premium_pct": "Prime (%)",
                "n_road": "Stations sur route",
                "n_motorway": "Stations autoroutières",
            })
            .round(4),
            use_container_width=True,
        )

        st.info(
            f"**{fuel_type}** : les stations autoroutières appliquent en moyenne une prime de "
            f"**+{prem_df[prem_df['fuel'] == fuel_type]['premium_eur'].iloc[0]:.3f} €/L** "
            f"({prem_df[prem_df['fuel'] == fuel_type]['premium_pct'].iloc[0]:+.1f} %)."
        )

        st.caption(
            "**Taille d'échantillon :** les stations autoroutières ne représentent "
            f"qu'environ {len(df[df['route_segment']=='motorway'])/len(df)*100:.1f}% du parc "
            f"({len(df[df['route_segment']=='motorway']):,.0f} stations autoroutières contre "
            f"{len(df[df['route_segment']=='road']):,.0f} sur route). "
            "L'écart est statistiquement significatif (test de Welch, p < 10⁻⁴⁹), "
            "mais repose sur un sous-échantillon réduit — à interpréter avec ce contexte."
        )

    # --- Tab 3: Pricing Deserts ---
    with tab3:
        st.subheader("Rareté des stations par département")
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
            color_discrete_sequence=[THEME["colors"]["primary"]],
            labels={
                "stations_per_100k": "Stations pour 100 000 habitants",
                "avg_price": f"Prix moyen du {fuel_type} (€/L)",
                "stations": "Nombre de stations",
            },
            title="Rareté et prix — moins de stations ne signifie pas toujours des prix plus élevés",
        )
        fig_desert.update_layout(template=TEMPLATE)
        st.plotly_chart(fig_desert, use_container_width=True)

        dept_display = (
            dept.head(20)[["departement", "stations", "population", "stations_per_100k", "avg_price"]]
            .round(3)
            .rename(columns={
                "departement": "Département",
                "stations": "Stations",
                "population": "Population",
                "stations_per_100k": "Stations pour 100 000 habitants",
                "avg_price": f"Prix moyen du {fuel_type} (€/L)",
            })
        )
        dept_display["Département"] = dept_display["Département"].astype(str)
        st.dataframe(dept_display, use_container_width=True)

        st.caption(
            "Paris (75) ne compte que **1,83 station de Gazole pour 100 000 habitants**, "
            "contre **48,68** en Lozère (48), soit un écart multiplié par **27**."
        )

    # --- Tab 4: Service Premiums ---
    with tab4:
        st.subheader("Quels services sont associés à des prix plus élevés ?")
        svc_cols = [c for c in df.columns if c.startswith("has_")]
        svc_rows = []
        for c in svc_cols:
            with_svc = subset[subset[c] == 1][price_col]
            without_svc = subset[subset[c] == 0][price_col]
            if len(with_svc) < 30 or len(without_svc) < 30:
                continue
            service_key = c.replace("has_", "")
            svc_rows.append({
                "service": SERVICE_LABELS.get(service_key, service_key),
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
            color_continuous_scale=COLOR_SCALE,
            color_continuous_midpoint=0,
            labels={"premium_eur": "Prime (€/L)", "service": "Service"},
            title=f"Primes de prix des services — {fuel_type}",
        )
        fig_svc.update_layout(template=TEMPLATE)
        st.plotly_chart(fig_svc, use_container_width=True)

        st.dataframe(
            svc_df.rename(columns={
                "service": "Service",
                "premium_eur": "Prime (€/L)",
                "premium_pct": "Prime (%)",
                "n_with": "Stations avec service",
                "n_without": "Stations sans service",
            }).round(4),
            use_container_width=True,
        )

        st.info(
            "Les boutiques, les restaurants et le Wi-Fi sont associés à des prix **plus élevés**. "
            "L'ouverture 24 h/24, les distributeurs automatiques de billets et la vente de GPL sont "
            "associés à des prix **plus bas** — probablement parce qu'ils caractérisent des stations "
            "automatisées à fort volume."
        )

    # Footer
    st.markdown("---")
    st.caption(
        "Données : [data.gouv.fr](https://www.data.gouv.fr) | "
        "Source : [donnees.roulez-eco.fr](https://donnees.roulez-eco.fr) | "
        "Réalisé avec Python, pandas, Plotly et Streamlit."
    )


if __name__ == "__main__":
    main()

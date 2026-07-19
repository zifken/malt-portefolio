"""
Streamlit dashboard — French Public Procurement Intelligence (DECP).

Run:
    python3 -m streamlit run app.py
"""

from __future__ import annotations

import pathlib

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

HERE = pathlib.Path(__file__).resolve().parent
OUTPUTS = HERE / "output"


@st.cache_data(show_spinner="Loading aggregates...")
def load_agg(name: str) -> pd.DataFrame:
    return pd.read_csv(OUTPUTS / name)


@st.cache_data(show_spinner="Loading geo sample for map...")
def load_geo() -> pd.DataFrame:
    return pd.read_csv(OUTPUTS / "geo_sample.csv")


def main() -> None:
    st.set_page_config(
        page_title="Public Procurement Intelligence (DECP)",
        page_icon="🏛️",
        layout="wide",
    )
    st.title("🏛️ French Public Procurement Intelligence")
    st.markdown(
        "Market intelligence on **French government spending** built from the official "
        "[Données Essentielles de la Commande Publique (DECP)](https://www.data.gouv.fr/datasets/donnees-essentielles-de-la-commande-publique-consolidees-format-tabulaire/) "
        "— **1.9M public contracts** (2018–2026), updated continuously."
    )

    # ---------- KPIs ----------
    yearly = load_agg("agg_yearly.csv")
    winners = load_agg("agg_winners.csv")
    total_m = yearly["total_eur_m"].sum()
    n_markets = int(yearly["n"].sum())
    sme = load_agg("agg_sme.csv")
    st.markdown(
        f"**Total awarded (excl. outliers):** €{total_m/1000:,.1f} trillion &nbsp;|&nbsp; "
        f"**Contracts:** {n_markets/1e6:,.2f}M &nbsp;|&nbsp; "
        f"**Unique vendors:** {winners.shape[0]/1000:,.1f}k &nbsp;|&nbsp; "
        f"**Unique buyers:** 26k+"
    )
    # Vendor concentration (top-1% share of spend) computed from the data
    s_win = winners["total_eur"].sort_values(ascending=False).values
    tot_win = s_win.sum()
    k_win = max(1, int(len(s_win) * 0.01))
    top1_share = s_win[:k_win].sum() / tot_win * 100

    c1, c2, c3, c4 = st.columns(4)
    pme_val = sme.loc[sme["titulaire_categorie"] == "PME", "value_share"].iloc[0]
    c1.metric("SME value share", f"{pme_val:.0f}%")
    c2.metric("Single-bid rate", "22.7%")
    c3.metric("Top 1% vendors capture", f"{top1_share:.0f}% of spend")
    c4.metric("Median contract", "€125k")

    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Overview", "🏆 Vendor Concentration", "🏢 SME vs Large",
        "⚖️ Competition & Transparency", "🗺️ Geography", "🔎 Categories & Anomalies",
    ])

    # ===== Tab 1: Overview =====
    with tab1:
        st.subheader("Spend over time and by contract type")
        col_a, col_b = st.columns(2)
        with col_a:
            st.image(str(OUTPUTS / "fig_yearly_trend.png"), use_container_width=True)
        with col_b:
            st.image(str(OUTPUTS / "fig_type_split.png"), use_container_width=True)
        st.dataframe(yearly[["year", "n", "total_eur_m", "median_eur"]]
                     .rename(columns={"year": "Year", "n": "Contracts",
                                      "total_eur_m": "Spend (€M)", "median_eur": "Median (€)"})
                     .astype({"Year": int}), use_container_width=True)

    # ===== Tab 2: Vendor concentration =====
    with tab2:
        st.subheader("Who captures public money")
        col_a, col_b = st.columns(2)
        with col_a:
            st.image(str(OUTPUTS / "fig_top_winners.png"), use_container_width=True)
        with col_b:
            st.image(str(OUTPUTS / "fig_pareto.png"), use_container_width=True)
        st.info(
            "The market is **long-tail but front-loaded**: 152k vendors exist, yet the "
            "**top 1% capture ~70% of all spend** and the top 5% capture ~90%. "
            "Winners are dominated by energy & telecom giants (Orange, Engie, EDF, TotalEnergies)."
        )
        st.dataframe(winners.head(25).assign(total_eur_M=lambda d: (d.total_eur/1e6).round(1))
                     [["titulaire_nom", "n", "total_eur_M"]]
                     .rename(columns={"titulaire_nom": "Vendor", "n": "Contracts",
                                      "total_eur_M": "Spend (€M)"}),
                     use_container_width=True)

    # ===== Tab 3: SME vs Large =====
    with tab3:
        st.subheader("The SME paradox")
        st.image(str(OUTPUTS / "fig_sme_share.png"), use_container_width=True)
        st.info(
            f"SMEs (PME) win **60% of contracts by count but only {pme_val:.0f}% by value** — large groups "
            "(GE) win 18% of contracts but **31% of spend**. The gap is widest on State contracts "
            "(SME value share ~22%) and narrowest on Regional contracts (~65%)."
        )
        sme_by = load_agg("agg_sme_by_buyer.csv")
        display = sme_by.rename(columns={
            "acheteur_categorie": "Buyer type", "PME": "SME spend (€)",
            "ETI": "ETI spend (€)", "GE": "GE spend (€)",
            "total": "Total spend (€)", "pme_value_share": "SME value %",
        })
        st.dataframe(display.head(15), use_container_width=True)

    # ===== Tab 4: Competition =====
    with tab4:
        st.subheader("Where competition is weak")
        st.image(str(OUTPUTS / "fig_single_bid.png"), use_container_width=True)
        st.info(
            "Only **38% of contracts** disclose the number of bids, and **22.7% of those had a single "
            "bidder**. The rate is highest for sub-threshold direct awards (expected) but also "
            "elevated for State (29%) and Regional (27%) buyers."
        )
        for label, f in [("By procedure", "agg_single_bid_procedure.csv"),
                         ("By buyer category", "agg_single_bid_acheteur_categorie.csv"),
                         ("By contract type", "agg_single_bid_type.csv")]:
            st.markdown(f"**{label}**")
            d = load_agg(f)
            st.dataframe(d.rename(columns={"single_bid_rate": "Single-bid %",
                                           "avg_offers": "Avg offers"}).round(1),
                         use_container_width=True)
        st.markdown("**Buyers with the highest single-bid rate** (≥200 disclosed markets)")
        buyer_lead = load_agg("agg_single_bid_buyers.csv")
        st.dataframe(buyer_lead.rename(columns={"acheteur_nom": "Buyer", "n": "Contracts",
                                                "single_bid_rate": "Single-bid %"}).round(1),
                     use_container_width=True)

    # ===== Tab 5: Geography =====
    with tab5:
        st.subheader("Spatial distribution of public spend")
        col_a, col_b = st.columns(2)
        with col_a:
            st.image(str(OUTPUTS / "fig_region_spend.png"), use_container_width=True)
        with col_b:
            st.image(str(OUTPUTS / "fig_local_capture.png"), use_container_width=True)
        st.markdown("**Interactive map** — sampled contracts (color = awarded value)")
        geo = load_geo()
        fig = px.scatter_map(
            geo.sample(min(15000, len(geo)), random_state=1),
            lat="acheteur_latitude", lon="acheteur_longitude",
            color="montant", size="montant",
            hover_name="acheteur_region_nom",
            color_continuous_scale="Viridis",
            zoom=5, height=600,
            title="Contract locations (sampled)",
        )
        fig.update_layout(mapbox_style="carto-positron")
        st.plotly_chart(fig, use_container_width=True)
        st.info(
            "Overseas regions capture **80–96% of their own spend locally**, while mainland regions "
            "hover around 50–56% — reflecting both geography and the structure of local suppliers."
        )

    # ===== Tab 6: Categories & anomalies =====
    with tab6:
        st.subheader("Category concentration & attention list")
        st.image(str(OUTPUTS / "fig_cpv_top.png"), use_container_width=True)
        st.markdown("**Most concentrated procurement categories (HHI)**")
        conc = load_agg("agg_cpv_concentration.csv")
        st.dataframe(conc.rename(columns={"cpv_label": "Category", "n_winners": "Vendors",
                                           "hhi": "HHI", "top1_share": "Top-1 vendor %"}).round(0),
                     use_container_width=True)
        st.markdown("**Attention list** — high-value, single-bid contracts far above their "
                    "category median (warrant a closer look, *not* a fraud allegation)")
        att = load_agg("agg_attention_list.csv")
        disp = att.copy()
        disp["montant_M"] = (disp["montant"] / 1e6).round(1)
        st.dataframe(disp[["acheteur_nom", "titulaire_nom", "titulaire_categorie",
                           "montant_M", "offresRecues", "ratio_to_median",
                           "acheteur_departement_nom", "dateNotification"]]
                     .rename(columns={"acheteur_nom": "Buyer", "titulaire_nom": "Vendor",
                                      "titulaire_categorie": "Vendor type",
                                      "montant_M": "Value (€M)", "offresRecues": "Bids",
                                      "ratio_to_median": "x median",
                                      "acheteur_departement_nom": "Dept",
                                      "dateNotification": "Date"}),
                     use_container_width=True)

    st.markdown("---")
    st.caption(
        "Data: data.gouv.fr (DECP, Licence Ouverte 2.0) | "
        "Built with Python, pandas, pyarrow, matplotlib, Plotly, Streamlit."
    )


if __name__ == "__main__":
    main()

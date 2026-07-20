"""
Streamlit dashboard — Intelligence sur la commande publique française (DECP).

Exécuter :
    python3 -m streamlit run app.py
"""

from __future__ import annotations

import pathlib

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

HERE = pathlib.Path(__file__).resolve().parent
OUTPUTS = HERE / "output"


# Thème unifié — appliqué à chaque graphique Plotly.
THEME = {
    "colors": {
        "bg": "#FFFFFF",
        "surface": "#F5F5F7",
        "primary": "#1B3A5C",      # bleu marine profond
        "secondary": "#C8553D",     # terre cuite
        "tertiary": "#5B8C5A",      # vert sauge
        "text": "#1A1A1A",
        "muted": "#6B6B6B",
        "grid": "#E0E0E0",
        "font": "Helvetica Neue, Arial, sans-serif",
    }
}


def build_theme_template() -> go.layout.Template:
    """Construit un go.layout.Template à partir de THEME."""
    c = THEME["colors"]
    axis_common = dict(
        gridcolor=c["grid"],
        zerolinecolor=c["grid"],
        linecolor=c["grid"],
        tickfont=dict(family=c["font"], color=c["muted"], size=12),
        title_font=dict(family=c["font"], color=c["text"], size=13),
    )
    return go.layout.Template(
        layout=go.Layout(
            paper_bgcolor=c["bg"],
            plot_bgcolor=c["bg"],
            font=dict(family=c["font"], color=c["text"], size=13),
            title=dict(
                font=dict(family=c["font"], color=c["text"], size=18),
                x=0.02, xanchor="left",
            ),
            xaxis=dict(**axis_common),
            yaxis=dict(**axis_common),
            legend=dict(
                font=dict(family=c["font"], color=c["text"], size=12),
                bgcolor=c["bg"],
                bordercolor=c["grid"],
                borderwidth=1,
            ),
            colorway=[c["primary"], c["secondary"], c["tertiary"]],
            margin=dict(l=60, r=30, t=60, b=50),
        )
    )


THEME_TEMPLATE = build_theme_template()


@st.cache_data(show_spinner="Chargement des agrégats...")
def load_agg(name: str) -> pd.DataFrame:
    return pd.read_csv(OUTPUTS / name)


@st.cache_data(show_spinner="Chargement de l'échantillon géographique pour la carte...")
def load_geo() -> pd.DataFrame:
    return pd.read_csv(OUTPUTS / "geo_sample.csv")


def main() -> None:
    st.set_page_config(
        page_title="Intelligence sur la commande publique (DECP)",
        page_icon="",
        layout="wide",
    )
    st.title("Intelligence sur la commande publique française")
    st.markdown(
        "Analyse de la **dépense publique française** issue des données officielles "
        "[Données Essentielles de la Commande Publique (DECP)](https://www.data.gouv.fr/datasets/donnees-essentielles-de-la-commande-publique-consolidees-format-tabulaire/) "
        "— **1,9 M de marchés publics** (2018–2026), mis à jour en continu."
    )

    # ---------- KPI ----------
    yearly = load_agg("agg_yearly.csv")
    winners = load_agg("agg_winners.csv")
    total_m = yearly["total_eur_m"].sum()
    n_markets = int(yearly["n"].sum())
    sme = load_agg("agg_sme.csv")
    st.markdown(
        f"**Montant total attribué (hors valeurs aberrantes) :** {total_m/1000:,.2f} Md€ &nbsp;|&nbsp; "
        f"**Contrats :** {n_markets/1e6:,.2f} M &nbsp;|&nbsp; "
        f"**Titulaires uniques :** {winners.shape[0]:,} &nbsp;|&nbsp; "
        f"**Acheteurs uniques :** 26 000+"
    )
    # Concentration des titulaires (part du top 1 % de la dépense)
    s_win = winners["total_eur"].sort_values(ascending=False).values
    tot_win = s_win.sum()
    k_win = max(1, int(len(s_win) * 0.01))
    top1_share = s_win[:k_win].sum() / tot_win * 100

    c1, c2, c3, c4 = st.columns(4)
    pme_val = sme.loc[sme["titulaire_categorie"] == "PME", "value_share"].iloc[0]
    c1.metric("Part de valeur PME", f"{pme_val:.0f} %")
    c2.metric("Taux d'offre unique", "22,7 %")
    c3.metric("Top 1 % des titulaires captent", f"{top1_share:.0f} % de la dépense")
    c4.metric("Contrat médian", "125 k€")

    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Vue d'ensemble", "Concentration des titulaires", "PME vs Grands groupes",
        "Concurrence et transparence", "Géographie", "Catégories et anomalies",
    ])

    # ===== Onglet 1 : Vue d'ensemble =====
    with tab1:
        st.subheader("Dépenses dans le temps et par type de contrat")
        col_a, col_b = st.columns(2)
        with col_a:
            st.image(str(OUTPUTS / "fig_yearly_trend.png"), use_container_width=True)
        with col_b:
            st.image(str(OUTPUTS / "fig_type_split.png"), use_container_width=True)
        st.dataframe(yearly[["year", "n", "total_eur_m", "median_eur"]]
                     .rename(columns={"year": "Année", "n": "Contrats",
                                      "total_eur_m": "Dépense (M€)", "median_eur": "Médiane (€)"})
                     .astype({"Année": int}), use_container_width=True)

    # ===== Onglet 2 : Concentration des titulaires =====
    with tab2:
        st.subheader("Qui capte l'argent public")
        col_a, col_b = st.columns(2)
        with col_a:
            st.image(str(OUTPUTS / "fig_top_winners.png"), use_container_width=True)
        with col_b:
            st.image(str(OUTPUTS / "fig_pareto.png"), use_container_width=True)
        st.info(
            "Le marché est **à longue traîne mais concentré en tête** : 152 000 titulaires existent, "
            "pourtant le **top 1 % capte environ 70 % de la dépense totale** et le top 5 % environ 90 %. "
            "Les titulaires sont dominés par les géants de l'énergie et des télécoms "
            "(Orange, Engie, EDF, TotalEnergies)."
        )
        st.dataframe(winners.head(25).assign(total_eur_M=lambda d: (d.total_eur/1e6).round(1))
                     [["titulaire_nom", "n", "total_eur_M"]]
                     .rename(columns={"titulaire_nom": "Titulaire", "n": "Contrats",
                                      "total_eur_M": "Dépense (M€)"}),
                     use_container_width=True)

    # ===== Onglet 3 : PME vs Grands groupes =====
    with tab3:
        st.subheader("Le paradoxe des PME")
        st.image(str(OUTPUTS / "fig_sme_share.png"), use_container_width=True)
        st.info(
            f"Les PME remportent **60 % des contrats en nombre mais seulement {pme_val:.0f} % en valeur** — "
            "les grands groupes (GE) remportent 18 % des contrats mais **31 % de la dépense**. "
            "L'écart est le plus marqué pour les contrats de l'État (part PME ~22 %) et le plus "
            "faible pour les contrats régionaux (~65 %)."
        )
        sme_by = load_agg("agg_sme_by_buyer.csv")
        display = sme_by.rename(columns={
            "acheteur_categorie": "Type d'acheteur", "PME": "Dépense PME (€)",
            "ETI": "Dépense ETI (€)", "GE": "Dépense GE (€)",
            "total": "Dépense totale (€)", "pme_value_share": "Valeur PME %",
        })
        st.dataframe(display.head(15), use_container_width=True)

    # ===== Onglet 4 : Concurrence =====
    with tab4:
        st.subheader("Où la concurrence est faible")
        st.image(str(OUTPUTS / "fig_single_bid.png"), use_container_width=True)
        st.info(
            "Seuls **38 % des contrats** mentionnent le nombre d'offres reçues, et **22,7 % d'entre "
            "eux n'ont reçu qu'une seule offre**. Le taux est le plus élevé pour les marchés de gré "
            "à gré sous les seuils (attendu) mais aussi élevé pour les acheteurs de l'État (29 %) "
            "et régionaux (27 %)."
        )
        for label, f in [("Par procédure", "agg_single_bid_procedure.csv"),
                         ("Par catégorie d'acheteur", "agg_single_bid_acheteur_categorie.csv"),
                         ("Par type de contrat", "agg_single_bid_type.csv")]:
            st.markdown(f"**{label}**")
            d = load_agg(f)
            st.dataframe(d.rename(columns={"single_bid_rate": "Taux d'offre unique (%)",
                                           "avg_offers": "Offres moyennes"}).round(1),
                         use_container_width=True)
        st.markdown("**Acheteurs présentant le taux d'offre unique le plus élevé** "
                    "(≥ 200 marchés divulgués)")
        buyer_lead = load_agg("agg_single_bid_buyers.csv")
        st.dataframe(buyer_lead.rename(columns={"acheteur_nom": "Acheteur", "n": "Contrats",
                                                "single_bid_rate": "Taux d'offre unique (%)"}).round(1),
                     use_container_width=True)

    # ===== Onglet 5 : Géographie =====
    with tab5:
        st.subheader("Répartition spatiale de la dépense publique")
        col_a, col_b = st.columns(2)
        with col_a:
            st.image(str(OUTPUTS / "fig_region_spend.png"), use_container_width=True)
        with col_b:
            st.image(str(OUTPUTS / "fig_local_capture.png"), use_container_width=True)
        st.markdown("**Carte interactive** — échantillon de contrats (couleur = montant attribué)")
        geo = load_geo()
        fig = px.scatter_map(
            geo.sample(min(15000, len(geo)), random_state=1),
            lat="acheteur_latitude", lon="acheteur_longitude",
            color="montant", size="montant",
            hover_name="acheteur_region_nom",
            color_continuous_scale=[[0, THEME["colors"]["primary"]],
                                    [0.5, THEME["colors"]["secondary"]],
                                    [1, THEME["colors"]["tertiary"]]],
            zoom=5, height=600,
            title="Localisation des contrats (échantillon)",
        )
        fig.update_layout(template=THEME_TEMPLATE)
        fig.update_layout(mapbox_style="carto-positron")
        st.plotly_chart(fig, use_container_width=True)
        st.info(
            "Les régions d'outre-mer captent **80 à 96 % de leur propre dépense localement**, tandis "
            "que les régions métropolitaines se situent autour de 50 à 56 % — reflétant à la fois la "
            "géographie et la structure des fournisseurs locaux."
        )

    # ===== Onglet 6 : Catégories et anomalies =====
    with tab6:
        st.subheader("Concentration par catégorie et liste d'attention")
        st.image(str(OUTPUTS / "fig_cpv_top.png"), use_container_width=True)
        st.markdown("**Catégories de marchés les plus concentrées (HHI)**")
        conc = load_agg("agg_cpv_concentration.csv")
        st.dataframe(conc.rename(columns={"cpv_label": "Catégorie", "n_winners": "Titulaires",
                                           "hhi": "HHI", "top1_share": "Top 1 titulaire (%)"}).round(0),
                     use_container_width=True)
        st.markdown("**Liste d'attention** — contrats à offre unique et de montant élevé, bien au-dessus "
                    "de la médiane de leur catégorie (méritent un examen approfondi, "
                    "*sans* présumer de fraude)")
        att = load_agg("agg_attention_list.csv")
        disp = att.copy()
        disp["montant_M"] = (disp["montant"] / 1e6).round(1)
        st.dataframe(disp[["acheteur_nom", "titulaire_nom", "titulaire_categorie",
                           "montant_M", "offresRecues", "ratio_to_median",
                           "acheteur_departement_nom", "dateNotification"]]
                     .rename(columns={"acheteur_nom": "Acheteur", "titulaire_nom": "Titulaire",
                                      "titulaire_categorie": "Type de titulaire",
                                      "montant_M": "Montant (M€)", "offresRecues": "Offres",
                                      "ratio_to_median": "x médiane",
                                      "acheteur_departement_nom": "Département",
                                      "dateNotification": "Date"}),
                     use_container_width=True)

    st.markdown("---")
    st.caption(
        "Données : data.gouv.fr (DECP, Licence Ouverte 2.0) | "
        "Construit avec Python, pandas, pyarrow, matplotlib, Plotly, Streamlit."
    )


if __name__ == "__main__":
    main()
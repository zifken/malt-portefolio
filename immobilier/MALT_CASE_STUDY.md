# Case Study: French Real Estate Market Intelligence (DVF)

**Role:** Data Analyst
**Client type:** Real-estate investor, property platform, urban planner, or market-study consultancy
**Duration:** 1 week
**Stack:** Python, pandas, numpy, matplotlib, seaborn, plotly, folium, Streamlit

---

## The problem

French property prices are highly local and seasonal, but the raw transaction data is messy, multi-lot, and full of outliers. An investor, a property platform, or a market-study consultancy needs the same thing: **clean price/m² trends across cities and time, with honest seasonality and segmentation.**

## The data

- **Source:** [data.gouv.fr — Demandes de Valeurs Foncières (geo-dvf latest)](https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres)
- **Coverage:** 5 départements — 75 Paris, 13 Bouches-du-Rhône (Marseille), 69 Rhône (Lyon), 31 Haute-Garonne (Toulouse), 44 Loire-Atlantique (Nantes)
- **Period:** 2021-2024
- **Volume:** 1.79M raw transactions → **557,135 cleaned** (31% retention)
- **Fields used:** date_mutation, valeur_fonciere, surface_reelle_bati, type_local, code_departement, nom_commune, latitude/longitude

## Methodology

1. **Ingestion** — downloaded 20 department-year files (5 depts × 4 years) from the geo-dvf latest endpoint; concatenated.
2. **Cleaning** — kept sales (Vente) only; apartments + houses; surface 9-500m²; price €10k-€10M; computed prix_m²; removed 3σ outliers per commune (13,479 outliers, 2.4%).
3. **Price trends** — yearly median €/m² per department and city; year-over-year growth.
4. **Geographic analysis** — commune-level price heatmap, top/bottom communes per metro.
5. **Property-type analysis** — apartments vs houses: price/m², surface, count share.
6. **Seasonality** — monthly transaction volume and median price by month (2021-2024 pooled).
7. **Market segmentation** — budget / mid-range / premium / luxury / ultra-luxury by €/m² bands.

## Results

| Lever | Finding | Why it matters |
|---|---|---|
| Paris dominance | Paris 15e/16e/18e arrondissements among top-5 communes by volume | Paris drives national trends — must be segmented, not averaged |
| Apartment premium | Apartments reach 94.6% of ultra-luxury (>€8k/m²) transactions | Product mix differs sharply by price band |
| Seasonality | Monthly volume + median price patterns visible across 4 years | Timing advice for buyers/sellers (with 4-year caveat) |
| Metro spread | 5 metros span ~€3.9k (median) to €5.2k (mean) /m² | Local benchmarking, not a single "France" number |

## Deliverables

- ✅ Reproducible pipeline (`01_download → 02_exploration → 03_cleaning → 04_analysis → 05_visualization → 06_dashboard`)
- ✅ Interactive Streamlit dashboard (price evolution, geography, property type, seasonality, segments)
- ✅ Statistical analysis report + cleaning report
- ✅ Geographic heatmaps (matplotlib + plotly)

## Business value

- **Investors:** where prices grow, which arrondissements/communes to target, when to transact.
- **Property platforms:** clean benchmark feeds and city-level price/m² widgets.
- **Urban planners / local government:** affordability and market-segment monitoring.
- **Market-study consultancies:** ready-made, reproducible DVF pipeline as a client deliverable.

## Skills demonstrated

Open-data ingestion · multi-file ETL · outlier handling per group · time-series + seasonal analysis · geospatial aggregation · market segmentation · Streamlit/Plotly dashboards · reproducible analytics engineering.

---

**Interested in a tailored real-estate market study?** I build data products that turn open data into board-ready insight.
Contact me on [Malt.fr](https://www.malt.fr).

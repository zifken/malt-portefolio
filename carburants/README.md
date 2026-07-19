# ⛽ Spatial Pricing Intelligence — French Fuel Stations

A **data analyst portfolio project** built from live French government open data.

- **Dataset:** [Prix des carburants en France — Flux instantané v2](https://www.data.gouv.fr/datasets/prix-des-carburants-en-france-flux-instantane-v2-amelioree/)
- **Coverage:** ~9,800 stations, ~33,000 price records, updated every 10 minutes
- **Focus:** How location, services, and station density affect fuel prices


---

## 🇫🇷 Présentation française

**Projet portfolio** pour profil Malt.fr — Data Analyst / Data Scientist.

### Objectif métier

> *Combien les automobilistes paient-ils de plus sur autoroute, et quelles caractéristiques des stations influencent les prix ?*

### Données multi-sources

Ce projet combine **3 sources de données** :

| Source | Données | Utilité |
|---|---|---|
| **Prix des carburants** (data.gouv.fr) | ~9 800 stations, ~33 000 prix, flux temps réel | Prix par type, localisation GPS |
| **INSEE** (population) | Population par département | Densité de stations / 100k hab. |
| **Services stations** (extrait XML) | 18 types de services encodés | Impact des services sur les prix |

### Résultats clés

| Indicateur | Valeur |
|---|---|
| Prime autoroute (gazole) | **+0,14 €/L** (+6,8 %) |
| Prime autoroute (E85) | **+0,14 €/L** (+17,2 %) |
| Écart densité Paris / Lozère | **27×** plus de stations/hab. en Lozère |
| Significativité | **p < 10⁻⁴⁹** (test de Welch) |

### Compétences démontrées
- Parsing XML → CSV structuré
- Enrichissement géospatial et démographique (jointure multi-source)
- Tests d'hypothèse statistiques
- Dashboard Streamlit interactif avec cartes Plotly
- Pipeline reproductible
---

## 🎯 Business question

> *How much more do consumers pay for fuel on motorways versus local roads, and which station characteristics are associated with higher prices?*

This project answers that question using spatial analysis, statistical testing, and interactive visualization.

---

## 📊 Key findings

| Insight | Result |
|---|---|
| **Motorway premium (Gazole)** | **+€0.141/L** (+6.8%) vs. road stations |
| **Motorway premium (E85)** | **+€0.144/L** (+17.2%) — highest percentage premium |
| **Urban vs. rural premium** | +€0.025/L (+1.2%) — small but significant |
| **Fuel station scarcity** | Paris: **1.83** vs. Lozère: **48.68** Gazole stations per 100k inhabitants (**27x difference**) |
| **Service premium (food shop)** | +€0.036/L (+1.7%) for stations with food shops |
| **Service premium (restaurant)** | +€0.019/L (+0.9%) for stations with restaurants |
| **Service discount (24/7)** | −€0.013/L (−0.6%) — automated stations are cheaper |

---

## 🗂️ Project structure

```
fuel-prices-project/
│
├── scripts/
│   ├── download_data.py      # fetch live XML from data.gouv.fr
│   ├── parse_data.py         # XML → CSV
│   ├── enrich_spatial.py     # add spatial features, services, population
│   └── spatial_analysis.py   # statistics + charts
│
├── raw/
│   ├── stations.csv                    # parsed station data
│   ├── prices.csv                      # parsed price data
│   ├── stations_enriched.csv           # enriched with spatial features
│   └── department_population.csv       # INSEE population by department
│
├── outputs/
│   ├── spatial_enrichment_report.txt
│   ├── spatial_analysis_report.txt
│   ├── price_map_gazole.html
│   ├── motorway_premium_chart.png
│   ├── pricing_desert_gazole.png
│   ├── service_premium_gazole.png
│   └── ...
│
├── app.py                    # Streamlit dashboard
├── requirements.txt
├── MALT_CASE_STUDY.md        # portfolio-ready case study
└── README.md
```

---

## 🚀 Quickstart

### 1. Install dependencies

```bash
pip3 install -r requirements.txt
```

### 2. Download the latest data

```bash
python3 scripts/download_data.py
```

### 3. Parse XML to CSV

```bash
python3 scripts/parse_data.py
```

### 4. Enrich with spatial features

```bash
python3 scripts/enrich_spatial.py
```

### 5. Run the analysis

```bash
python3 scripts/spatial_analysis.py
```

### 6. Launch the dashboard

```bash
python3 -m streamlit run app.py
```

Open `http://localhost:8501`.

---

## 📈 What the dashboard shows

1. **Price Map** — interactive map of fuel prices across France
2. **Motorway Premium** — how much more you pay on motorways
3. **Pricing Deserts** — departments with few stations per capita
4. **Service Premiums** — which services correlate with higher/lower prices

---

## 🛠️ Tech stack

- **Python 3.9+**
- **pandas** — data wrangling
- **scipy** — statistical testing (Welch's t-test)
- **matplotlib / seaborn** — static charts
- **Plotly** — interactive maps and dashboards
- **Streamlit** — web app
- **XML parsing** — `xml.etree.ElementTree`
- **requests** (via `urllib`) — data download

---

## 🔄 Reproducibility

The pipeline is fully automated:

```bash
# Refresh everything
python3 scripts/download_data.py && \
python3 scripts/parse_data.py && \
python3 scripts/enrich_spatial.py && \
python3 scripts/spatial_analysis.py
```

---

## 📜 Data license

Source data from the French Ministry of Economy under the **Licence Ouverte 2.0**.

---

## 👤 Author

*[Your Name]* — Data Analyst on [Malt.fr](https://www.malt.fr)

---

**Next steps:** Collect daily snapshots for 30 days to enable time-series analysis and price forecasting.

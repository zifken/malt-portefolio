# 🏠 French Real Estate Market Analysis
## Portfolio Project for Malt.fr Data Analyst Profile

### Project Overview
This project analyzes **French real estate transaction data** (DVF - Demandes de Valeurs Foncières) across the 5 largest French metropolitan areas to uncover market trends, price patterns, and seasonal dynamics.

**Dataset:** DVF — 5 départements (75 Paris, 13 Marseille, 69 Lyon, 31 Toulouse, 44 Nantes), 2021-2024
**Source:** data.gouv.fr - Demandes de Valeurs Foncières (geo-dvf latest)
**Volume:** 557,135 transactions nettoyées (sur 1,79M brutes)
**License:** Licence Ouverte 2.0 (Etalab)


---

## 🇫🇷 Présentation française

**Projet portfolio** pour profil Malt.fr — Data Analyst / Data Scientist.

### Objectif métier

> *Comment les prix de l'immobilier évoluent-ils en France, et où se trouvent les meilleures opportunités d'investissement ?*

### Analyse multi-dimensionnelle

Bien qu'exploitant un dataset unique (DVF), ce projet démontre une **analyse croisée sur 4 dimensions** :

| Dimension | Analyse |
|---|---|
| **Temporelle** | Évolution des prix 2021-2024, saisonnalité mensuelle |
| **Géographique** | Par département, commune, quartier |
| **Typologique** | Appartements vs maisons, surfaces |
| **Financière** | Segmentation budget, luxe, prix/m² |

### Résultats produits
- Dashboard interactif Streamlit (filtres temps, zone, type de bien)
- Cartes de chaleur géographiques
- Analyses statistiques (médianes, percentiles, tendances)
- Recommandations business (meilleur mois pour acheter/vendre)

### Compétences démontrées
- Pipeline complet ETL (téléchargement → nettoyage → analyse → visualisation)
- Traitement de 557k transactions (5 métropoles, 4 années)
- Visualisations professionnelles (matplotlib, plotly, folium)
- Dashboard interactif Streamlit
---

## 🎯 Business Questions We'll Answer

1. **Price Trends:** How have real estate prices evolved in major French cities?
2. **Market Segmentation:** What are the price differences between apartments vs houses?
3. **Geographic Analysis:** Which regions offer the best value for money?
4. **Investment Insights:** Where are prices growing fastest?
5. **Seasonal Patterns:** Are there better times to buy/sell?

---

## 🛠️ Technical Skills Demonstrated

- **Data Acquisition:** Downloading from official APIs
- **Data Cleaning:** Handling 557k+ transactions across 5 départements
- **Statistical Analysis:** Median calculations, outlier detection
- **Time Series Analysis:** Trend identification
- **Geospatial Analysis:** Location-based insights
- **Data Visualization:** Charts and interactive maps
- **Business Intelligence:** Actionable insights

---

## 📁 Project Structure

```
french-real-estate-project/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── 01_data_download.py       # Download DVF data
├── 02_data_exploration.py    # Initial data exploration
├── 03_data_cleaning.py       # Clean and preprocess
├── 04_analysis.py            # Statistical analysis
├── 05_visualization.py       # Create charts
├── 06_dashboard.py           # Interactive Streamlit dashboard
├── data/                     # Data files (not in git)
├── output/                   # Generated charts and reports
└── notebooks/                # Jupyter notebooks for exploration
```

---

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Download Data
```bash
# Download data for Rhône department (Lyon area)
python 01_data_download.py
```

### 3. Run Analysis
```bash
# Complete analysis pipeline
python 04_analysis.py

# Launch interactive dashboard
streamlit run 06_dashboard.py
```

---

## 📊 Sample Outputs

### Price Evolution Chart
![Price Evolution](output/price_evolution.png)

### Geographic Heat Map
![Price Map](output/price_heatmap.html)

### Interactive Dashboard
![Dashboard](output/dashboard_screenshot.png)

---

## 🎓 Learning Outcomes

By completing this project, you'll demonstrate:

1. **Data Engineering:** Handling real-world messy data
2. **Statistical Thinking:** Proper use of medians vs means
3. **Business Acumen:** Translating data into actionable insights
4. **Technical Proficiency:** Python, pandas, visualization libraries
5. **Communication:** Clear documentation and presentation

---

## 📈 Business Impact

This analysis can help:
- **Home Buyers:** Find optimal timing and locations
- **Investors:** Identify growth opportunities
- **Real Estate Agents:** Understand market dynamics
- **Policy Makers:** Monitor housing affordability
- **Urban Planners:** Track development patterns

---

## 🔗 Resources

- **Dataset:** https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres
- **Documentation:** https://www.data.gouv.fr/api/
- **Guide:** https://intentanalytics.fr/guides/python-dvf-pandas

---

## 👤 About This Project

Created as a portfolio piece for Malt.fr data analyst profile, demonstrating:
- Real-world data analysis skills
- Business problem-solving ability
- Technical Python proficiency
- Data storytelling capabilities

**Next Steps:** Deploy to Streamlit Cloud and add to your Malt.fr portfolio!

# 🏛️ French Public Procurement Intelligence (DECP)

A **data-analyst portfolio project** that turns France's official open procurement
data into market intelligence. Built for a **Malt.fr** freelance profile.

- **Dataset:** [Données Essentielles de la Commande Publique (DECP)](https://www.data.gouv.fr/datasets/donnees-essentielles-de-la-commande-publique-consolidees-format-tabulaire/) — consolidated tabular file
- **Coverage:** ~1.92M current public contracts (2018–2026), €3.2 trillion awarded
- **Focus:** vendor concentration, SME vs large-group dynamics, competition/transparency, geography, category anomalies


---

## 🇫🇷 Présentation française

**Projet portfolio** pour profil Malt.fr — Data Analyst / Data Scientist.

### Objectif métier

> *Qui capte l'argent public français, où la concurrence est-elle la plus faible, et quels contrats méritent un examen approfondi ?*

### Données multi-sources

Ce projet combine **3 sources de données** :

| Source | Données | Utilité |
|---|---|---|
| **DECP** (data.gouv.fr) | 1,92 M contrats, 3 200 Md€ | Montants, titulaires, acheteurs, procédures |
| **CPV** | Classification des catégories d'achats | Analyse par secteur économique |
| **Géographique** | Régions acheteurs et titulaires | Capture locale, carte interactive |

### Résultats clés

| Indicateur | Valeur |
|---|---|
| Top 1 % des titulaires | **67 %** de la dépense |
| Part des PME en valeur | **41 %** (60 % en nombre) |
| Taux d'offre unique | **22,7 %** |
| Capture locale Outre-mer | **80-96 %** |
| Contrats « attention » | **200** signalés |

### Compétences démontrées
- Import et parsing Parquet (204 Mo)
- Nettoyage de données gouvernementales complexes
- Jointures multi-niveaux (année, région, catégorie, type de titulaire)
- Analyse de concentration (HHI, Pareto)
- Dashboard Streamlit 6 onglets
- Détection d'anomalies avec cadrage éthique
---

## 🎯 Business question

> *Who captures French public money, how concentrated is that spending, where is
> competition weakest, and which high-value single-bid contracts warrant a closer look?*

## 📊 Headline findings

| Insight | Result |
|---|---|
| **Top 1% of vendors** capture | **~67% of all public spend** |
| **Top 5% of vendors** capture | **~88%** |
| **SME paradox** | SMEs win 60% of contracts by count but only **41% by value** |
| **Large groups (GE)** | 18% of contracts → **31% of spend** |
| **Single-bid rate** | **22.7%** of disclosed contracts (38% disclose bids) |
| **Weakest competition** | State buyers 29%, Regional 27% single-bid |
| **Local capture (overseas)** | **80–96%** of spend won by same-region vendors |
| **Local capture (mainland)** | ~50–56% |

---

## 🗂️ Project structure

```
public-procurement-project/
├── scripts/
│   ├── 01_download_data.py   # fetch consolidated DECP parquet from data.gouv.fr
│   ├── 02_explore_data.py    # data profiling
│   ├── 03_clean.py           # filter current + valid rows, derive year/flags
│   └── 04_analysis.py        # concentration, SME, competition, geography, anomalies
├── raw/
│   ├── decp.parquet          # raw consolidated (git-ignored)
│   ├── decp_clean.parquet   # analysis-ready (git-ignored)
│   └── schema.json           # data dictionary
├── output/
│   ├── analysis_report.txt   # full numbers
│   ├── agg_*.csv             # precomputed aggregates
│   ├── fig_*.png             # charts
│   └── geo_sample.csv        # map sample
├── app.py                    # Streamlit dashboard
├── requirements.txt
├── README.md
└── MALT_CASE_STUDY.md
```

## 🚀 Quickstart

```bash
pip3 install -r requirements.txt
python3 scripts/01_download_data.py     # download consolidated parquet
python3 scripts/03_clean.py             # clean -> decp_clean.parquet
python3 scripts/04_analysis.py          # compute aggregates + charts
python3 -m streamlit run app.py         # launch dashboard
```

Open http://localhost:8501

## 📈 Dashboard tabs

1. **Overview** — spend trend & contract-type split
2. **Vendor Concentration** — top vendors, Pareto curve, HHI
3. **SME vs Large** — value vs count share, by buyer type
4. **Competition & Transparency** — single-bid rates by segment + buyer leaderboard
5. **Geography** — regional spend, local capture, interactive map
6. **Categories & Anomalies** — CPV concentration + attention list

## 🧹 Data-quality notes

- Kept only `donneesActuelles == True` to avoid counting modification duplicates.
- Excluded ~1,600 records (0.08%) with implausible amounts ≥ €900M (sentinel/placeholder values).
- `offresRecues` (number of bids) is disclosed for ~38% of contracts only; competition
  metrics are computed on that subset and labelled as such.
- The "attention list" flags high-value, single-bid contracts far above their category
  median — framed as *transparency signals*, **not** fraud allegations.

## 🛠️ Tech stack

Python (pandas, pyarrow, numpy), matplotlib/seaborn, scipy, Plotly, Streamlit.

## 📜 License

Source data: French government, **Licence Ouverte 2.0**.

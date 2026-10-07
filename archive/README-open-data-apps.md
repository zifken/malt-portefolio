# Portfolio Data Science — Projets Open Data France

3 projets d'analyse de données publiques françaises (data.gouv.fr), avec dashboards interactifs Streamlit.

| Projet | Dossier | Dashboard | Données |
|---|---|---|---|
| 🏠 Marché immobilier (DVF) | `immobilier/` | `app.py` | 557k transactions, 5 métropoles, 2021-2024 |
| ⛔ Prix des carburants | `carburants/` | `app.py` | 9 800 stations, 3 sources combinées |
| 🏛️ Marchés publics (DECP) | `marches-publics/` | `app.py` | 1,92M contrats, 3,2T€ |

## Déploiement Streamlit Cloud

Chaque app se déploie individuellement sur [Streamlit Community Cloud](https://share.streamlit.io) :

1. Fork/clone ce repo sur GitHub (public)
2. Sur share.streamlit.io → "New app"
3. Repo → ce repo; Branch → `main`
4. Main file path → `immobilier/app.py` (ou `carburants/app.py`, `marches-publics/app.py`)
5. Requirements → `immobilier/requirements.txt` (etc.)
6. Deploy → URL `*.streamlit.app`

## Licence

Données : Licence Ouverte 2.0 (Etalab). Code : libre de réutilisation.

---

*Projet portfolio pour profil Malt.fr — Data Analyst / Data Scientist Freelance*

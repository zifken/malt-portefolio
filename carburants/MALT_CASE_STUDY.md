# Case Study: Spatial Pricing Intelligence for French Fuel Stations

**Role:** Data Analyst  
**Client type:** Consumer app, mobility platform, or retail strategy consultancy  
**Duration:** 1 week  
**Stack:** Python, pandas, scipy, Plotly, Streamlit

---

## The problem

Fuel is one of the most visible and emotionally charged consumer expenses in France. Drivers know prices vary, but they rarely know **where, when, and why** they vary. A mobility app or consumer platform wanted to quantify the real price differences between motorway and local stations, and understand which station features drive pricing power.

---

## The data

I used the official French government open dataset:

- **Source:** [data.gouv.fr — Prix des carburants en France](https://www.data.gouv.fr/datasets/prix-des-carburants-en-france-flux-instantane-v2-amelioree/)
- **Update frequency:** every 10 minutes (source); snapshot used for this analysis
- **Coverage:** ~9,800 stations, ~33,000 price records
- **Fields:** GPS coordinates, address, services, fuel types, prices, last update timestamp

I enriched this with department-level population data to compute station scarcity metrics.

---

## Methodology

### 1. Data pipeline
- Downloaded and parsed the live XML feed
- Cleaned and normalized station metadata
- One-hot encoded 18 service types (car wash, 24/7, shop, restaurant, etc.)
- Classified stations by route type: **motorway** (`pop=A`) vs. **road** (`pop=R`)

### 2. Spatial analysis
- Computed **Welch's t-tests** for price differences between segments
- Built **pricing desert** metrics: stations per 100k inhabitants by department
- Analyzed service price premiums with confidence intervals
- Corrected for multiple comparisons in interpretation

### 3. Visualization
- Interactive price map (Plotly + OpenStreetMap)
- Motorway premium comparison across all fuel types
- Scarcity vs. price scatter plot
- Service premium ranking

### 4. Dashboard
- Built a **Streamlit** web app with four tabs: map, motorway premium, pricing deserts, and service premiums
- Fully reproducible pipeline: one command refreshes all data and charts

---

## Results

### Motorway stations charge a significant premium

| Fuel | Road avg. | Motorway avg. | Premium | % |
|---|---:|---:|---:|---:|
| Gazole | €2.089 | €2.230 | **+€0.141** | **+6.8%** |
| SP98 | €2.074 | €2.233 | **+€0.158** | **+7.6%** |
| E10 | €1.990 | €2.141 | **+€0.152** | **+7.6%** |
| E85 | €0.838 | €0.982 | **+€0.144** | **+17.2%** |

All differences are statistically significant (p < 10⁻⁴⁹).

### Urban vs. rural gap is small but real
- Gazole: **+€0.025/L** (+1.2%) in urban departments
- The much bigger driver is **motorway access**, not urbanization

### Pricing deserts are extreme
- **Paris (75):** 1.83 Gazole stations per 100k inhabitants
- **Lozère (48):** 48.68 stations per 100k inhabitants
- **27x difference** in station density between the most and least served departments

### Services tell a story
- **Food shops:** +€0.036/L — full-service stations charge more
- **Restaurants:** +€0.019/L — convenience comes at a price
- **24/7 and ATM:** −€0.01–0.02/L — automated, high-volume stations are cheaper
- **Manual car wash:** −€0.012/L — possibly a loss-leader service

---

## Business value

For a **consumer app**, this analysis powers:
- "Avoid motorways and save €0.14/L" alerts
- Personalized savings estimates based on user routes
- Station recommendations that balance price, services, and detour cost

For a **retail strategy consultancy**, it reveals:
- Where pricing power is concentrated (motorways, urban centers)
- Which services justify premium pricing
- Underserved markets ("pricing deserts") that could support new stations

For **public policy**, it highlights:
- Regional inequalities in fuel access
- The true cost of motorway monopolies

---

## Deliverables

- ✅ Reproducible Python pipeline (download → parse → analyze → visualize)
- ✅ Interactive Streamlit dashboard
- ✅ Statistical report with confidence intervals
- ✅ Portfolio-ready documentation

---

## Skills demonstrated

- Open data ingestion and XML parsing
- Geospatial feature engineering
- Statistical hypothesis testing (Welch's t-test)
- Interactive visualization (Plotly, Streamlit)
- Business storytelling with data
- Reproducible analytics engineering

---

**Interested in similar analysis for your business?**  
I build data products that turn open data into actionable insights. Contact me on [Malt.fr](https://www.malt.fr).

# Case Study: Public Procurement Market Intelligence (DECP)

**Role:** Data Analyst  
**Client type:** B2B consultancy, SMEs hunting public tenders, local government / audit, anti-corruption / transparency  
**Duration:** 1 week  
**Stack:** Python, pandas, pyarrow, scipy, matplotlib, Plotly, Streamlit

---

## The problem

France publishes every public contract above €40k as open data (DECP). That is a
goldmine — but it is raw, messy, and 1.9M rows deep. A consultancy, an SME tender
team, or a local auditor all need the same thing: **who wins public money, where
competition is weak, and which contracts deserve scrutiny.**

## The data

- **Source:** [data.gouv.fr — DECP consolidated tabular file](https://www.data.gouv.fr/datasets/donnees-essentielles-de-la-commande-publique-consolidees-format-tabulaire/)
- **Size:** ~204 MB parquet, 3.1M rows → 1.92M current, valid contracts
- **Coverage:** 2018–2026, €3.2 trillion awarded
- **Fields used:** awarded amount, vendor (name + PME/ETI/GE size class), buyer
  (category, region, department), CPV category, procedure type, number of bids,
  buyer–vendor distance

## Methodology

1. **Ingestion** — resolved the latest consolidated parquet URL from the data.gouv.fr
   API and streamed it locally (script is reproducible on each new publish).
2. **Cleaning** — kept only current-state rows, valid positive amounts; excluded
   ~1,600 sentinel records (≥ €900M placeholders); derived notification year and
   single-bid flag.
3. **Concentration analysis** — winner Pareto curve, top-1%/5%/10% spend capture,
   HHI; SME vs large-group value-vs-count share.
4. **Competition / transparency** — single-bid rates by procedure, buyer type, and
   contract type; buyer leaderboard of weak-competition contracts.
5. **Geography** — regional spend, "local capture" (share of spend won by
   same-region vendors), interactive contract map.
6. **Anomaly screening** — high-value, single-bid contracts >20× their category
   median (a *transparency attention list*, explicitly **not** a fraud claim).

## Results

| Lever | Finding | Why it matters |
|---|---|---|
| Vendor concentration | Top 1% of vendors = **67% of spend** | Tender strategy should target the long tail, not chase giants |
| SME paradox | SMEs = 60% of contracts but **41% of value** | SMEs under-penetrate high-value State contracts (22% value share) |
| Weak competition | **22.7%** single-bid; State 29%, Regional 27% | Highlight markets with no real contest |
| Local capture | Overseas **80–96%**, mainland ~50–56% | Maps where local suppliers dominate vs. where they don't |
| Attention list | 200 high-value single-bid outliers | A starting point for auditor / journalist scrutiny |

## Deliverables

- ✅ Reproducible pipeline (`download → clean → analyze`)
- ✅ Six-tab Streamlit dashboard (overview, concentration, SME/GE, competition, geography, anomalies)
- ✅ Statistical report with defensible data-quality caveats
- ✅ Portfolio-ready case study

## Business value

- **SMEs / tender teams:** where to compete, which buyer types favour SMEs, how to
  size their realistic value-share.
- **Consultancies:** market-sizing and vendor-landscape briefs for public-sector
  clients.
- **Local government / auditors:** where competition is weakest and which contracts
  warrant a closer look.

## Skills demonstrated

Open-data ingestion via API · large-file parquet processing · concentration metrics
(HHI, Pareto) · segmentation (SME/GE) · competition/transparency analysis ·
geospatial "local capture" · anomaly screening with careful, non-defamatory framing ·
interactive Streamlit/Plotly dashboards · reproducible analytics engineering.

---

**Interested in a tailored procurement-intelligence study?** I build data products that
turn open data into board-ready insight. Contact me on [Malt.fr](https://www.malt.fr).

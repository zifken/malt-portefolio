# DECP Radar — analytics and weekly digest on French public procurement

**Stack:** Python (stdlib + pandas), Streamlit, Parquet, plotnine, cron. Data: open data (data.gouv.fr, Licence Ouverte / Etalab 2.0). Status: running weekly on a home server.

## The problem

Every public contract awarded in France must be published as a DECP notice (*données essentielles de la commande publique*). The data is open, but it is split into two awkward sources: daily delta files (for fresh notices) and yearly consolidated files (for history), with duplicated records, inconsistent identifiers, and amounts that mean different things depending on contract type. Any business question — "which contracts expire soon and will be re-tendered?", "who won what this week?" — requires a pipeline before it requires analysis.

I built one.

## What was built

Two repos that work as one product:

**decp-digest** — the ingestion and weekly-digest pipeline. Written in stdlib-only Python: it fetches the daily delta files from the DECP API, watermarks on the last processed file so re-runs are cheap, dedupes on `(acheteur.id, id)` (~3% of records repeat across consecutive files), and produces a weekly digest of new award notices. Measured over a full validation week: 729 records, ~750 notices/week, and every field the digest needs ≥ 99.7% filled. The README documents what the data can and cannot support — e.g. publication lags notification by a median of 6 days, so the digest groups by publication date, not notification date.

**decp-analytics** — the forecast and analytics layer on top. It rebuilds from the consolidated files (2019–2026), deduplicates superseded records (311,002 dropped, 1,355,661 usable contracts), estimates each contract's expiry as `dateNotification + dureeMois`, and outputs:

- the re-tender window: **55,957 contracts expiring in the next 12 months**, filterable by CPV family, département and buyer — delivered as CSV plus a curated IT-sector report;
- a **Streamlit dashboard** (CPV / département / period filters, KPIs, buyer and supplier views);
- a free public sample (60 rows) used for the landing page.

A weekly refresh cron (Monday 07:30) keeps both layers current; the full rebuild is the only heavy step and fits comfortably in the < 2 h/week budget.

## From the real data

![](images/marches_par_annee.png)
![](images/montants_par_annee.png)
![](images/echeances_cpv.png)

*Chart 3 legend — top CPV divisions: 45 Travaux de construction (19 916), 71 Ingénierie (5 848), 79 Conseil (2 658), Environnement (2 374), 33 (2 323), 50 Réparation (1 880), 34 (1 580), Transports (1 530), 44 (1 473), 39 (1 443). Division names come from the open dataset as published; a few arrive unmapped ("33?", "34?") and are shown as-is.*

All charts are generated with plotnine from the pipeline's own parquet outputs, French labels, and are checked programmatically (text bounding boxes) before publication.

## What I learned

- **Measure data quality before building on it.** The fill-rate table in the digest README is what makes the product trustworthy; it also caught the trap of grouping by notification date.
- **Contract identity is not the published `id`.** The consolidated files merge publication channels, so the same contract arrives more than once; deduplication needs a content key, not the raw key.
- **Amounts are ceilings, not spending.** Accord-cadre amounts are the maximum over the agreement — a chart of "total notified volume" is honest only if it says so.
- **Two sources, two cadences.** Daily deltas and yearly consolidations answer different questions; stitching them (supersession handling) was most of the work.

## Repos

Private (zifken/decp-analytics, zifken/decp-digest) — sanitized extracts and the sample dataset are published separately.

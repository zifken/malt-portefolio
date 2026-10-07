"""
Core analysis for the DECP public-procurement intelligence project.

Computes, saves to outputs/agg_*.csv, and plots to outputs/fig_*.png:
  1. Market overview & yearly/type trends
  2. Vendor concentration (HHI, top shares, Pareto)
  3. SME vs GE value/count share
  4. Competition & transparency (single-bid rates by segment)
  5. Geography (region spend, local capture, distance)
  6. Category concentration (CPV divisions) + anomaly/attention list

Writes a plain-text analysis_report.txt with the headline numbers.
"""

from __future__ import annotations

import pathlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
PROJECT = HERE.parent
RAW = PROJECT / "raw"
OUTPUTS = PROJECT / "output"
OUTPUTS.mkdir(parents=True, exist_ok=True)

CLEAN = RAW / "decp_clean.parquet"

# CPV division -> label (first 2 digits of the 8-digit CPV code)
CPV_DIVISIONS = {
    "03": "Agriculture & forêt", "09": "Énergie & carburants", "14": "Métallurgie",
    "15": "Alimentation", "16": "Matériel agricole", "18": "Textile & habillement",
    "19": "Bureautique & papier", "21": "Armes & munitions", "22": "Imprimés",
    "24": "Produits chimiques", "30": "Matériel informatique",
    "31": "Matériel électrique", "32": "Télécom & radio",
    "33": "Médical & pharmacie", "34": "Transport & véhicules",
    "35": "Sécurité & défense", "37": "Sport & loisirs",
    "38": "Laboratoire & optique", "39": "Mobilier & électroménager",
    "41": "Déchets & assainissement", "42": "Machines spécialisées",
    "43": "Matériel BTP", "44": "Travaux de construction",
    "45": "Travaux", "48": "Logiciels & SI", "50": "Réparation & maintenance",
    "51": "Installation (hors logiciel)", "55": "Hôtels & restauration",
    "60": "Transport", "63": "Auxiliaire transport", "64": "Poste & télécom",
    "66": "Finance & assurance", "70": "Immobilier", "71": "Architecture & ingénierie",
    "72": "Services informatiques", "73": "R&D & conseil",
    "75": "Administration publique", "76": "Publicité & marketing",
    "77": "Conseil & RH", "79": "Éducation & formation", "80": "Action sociale",
    "85": "Santé & social", "90": "Environnement", "91": "Ordre public",
    "92": "Culture & sport", "93": "Restauration collective",
    "94": "Assainissement", "95": "Services supports", "96": "Organisations internat.",
    "98": "Autres services",
}

plt.rcParams.update({"figure.autolayout": True, "axes.grid": True, "grid.alpha": 0.3})


def hhi(shares: np.ndarray) -> float:
    """Herfindahl-Hirschman Index on a vector of market shares (0-1)."""
    s = shares[shares > 0]
    return float((s ** 2).sum() * 10000)


def cpv_label(div: str) -> str:
    return CPV_DIVISIONS.get(div, f"CPV {div}")


def load() -> pd.DataFrame:
    df = pd.read_parquet(CLEAN)
    # Analysis amount excludes sentinel/outlier values (>= 1e9 € ~ round-number placeholders).
    # Only ~0.05% of rows are affected; totals are reported excluding them.
    df["montant_analyse"] = df["montant"].where(df["montant"] < 9e8)
    # Keep 2018+ only: DECP consolidation is reliable from 2018 onward.
    # Pre-2018 records (2000-2017) are sparse (5-739 rows/yr) and distort trend charts.
    df = df[df["year"] >= 2018].copy()
    return df


def overview(df: pd.DataFrame, rep: list[str]) -> None:
    val = df["montant_analyse"].dropna()
    rep.append("=== MARKET OVERVIEW ===")
    rep.append(f"Total markets (current, valid amount): {len(df):,}")
    rep.append(f"Total awarded (€M, excl. outliers): {val.sum()/1e6:,.0f}")
    rep.append(f"Unique winners (named): {df['titulaire_nom'].nunique():,}")
    rep.append(f"Unique buyers (named): {df['acheteur_nom'].nunique():,}")
    rep.append(f"Median market value (€): {val.median():,.0f}")
    rep.append("")

    # Yearly trend
    yr = df.dropna(subset=["year"]).groupby("year").agg(
        n=("uid", "size"), total_eur=("montant_analyse", "sum"),
        median_eur=("montant_analyse", "median")).reset_index()
    yr["total_eur_m"] = yr["total_eur"] / 1e6
    yr.to_csv(OUTPUTS / "agg_yearly.csv", index=False)
    rep.append("Yearly trend (2018-2026):")
    rep.append(yr.round(0).to_string(index=False))
    rep.append("")

    # By type
    ty = df.groupby("type").agg(n=("uid", "size"), total_eur=("montant_analyse", "sum"),
                                median_eur=("montant_analyse", "median")).reset_index()
    ty.to_csv(OUTPUTS / "agg_type.csv", index=False)
    rep.append("By contract type:")
    rep.append(ty.round(0).to_string(index=False))
    rep.append("")

    # Charts
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(yr["year"].astype(int).astype(str), yr["total_eur_m"], color="#2c7fb8")
    ax.set_title("Public procurement spend by notification year (€M)")
    ax.set_ylabel("€M")
    fig.savefig(OUTPUTS / "fig_yearly_trend.png", dpi=110)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    ty2 = ty.sort_values("total_eur")
    ax.barh(ty2["type"], ty2["total_eur"] / 1e6, color="#41b6c4")
    ax.set_title("Spend by contract type (€M)")
    ax.set_xlabel("€M")
    fig.savefig(OUTPUTS / "fig_type_split.png", dpi=110)
    plt.close(fig)


def concentration(df: pd.DataFrame, rep: list[str]) -> None:
    rep.append("=== VENDOR CONCENTRATION ===")
    w = df.dropna(subset=["montant_analyse"]).groupby("titulaire_nom").agg(
        n=("uid", "size"), total_eur=("montant_analyse", "sum")).reset_index()
    w = w.sort_values("total_eur", ascending=False)
    w.to_csv(OUTPUTS / "agg_winners.csv", index=False)

    total = w["total_eur"].sum()
    shares = (w["total_eur"] / total).values
    rep.append(f"Winners total: {len(w):,}")
    rep.append(f"HHI (winner concentration): {hhi(shares):,.0f}  (>2500 = highly concentrated)")
    for pct in (0.01, 0.05, 0.10):
        k = max(1, int(len(w) * pct))
        rep.append(f"Top {pct*100:.0f}% winners capture "
                   f"{w['total_eur'].head(k).sum()/total*100:.1f}% of spend")
    rep.append("")

    # Pareto curve
    cum = np.cumsum(w["total_eur"].values) / total
    xs = np.arange(1, len(w) + 1) / len(w)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(xs * 100, cum * 100, color="#d95f0e", lw=2)
    ax.plot([0, 100], [0, 100], "--", color="grey", lw=1)
    ax.set_xlabel("Cumulative % of winners")
    ax.set_ylabel("Cumulative % of spend")
    ax.set_title("Vendor Pareto curve — spend concentration")
    ax.set_xlim(0, 100); ax.set_ylim(0, 100)
    fig.savefig(OUTPUTS / "fig_pareto.png", dpi=110)
    plt.close(fig)

    # Top 15 winners
    top = w.head(15).sort_values("total_eur")
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(top["titulaire_nom"].str.slice(0, 40), top["total_eur"] / 1e6,
            color="#253494")
    ax.set_title("Top 15 vendors by awarded value (€M)")
    ax.set_xlabel("€M")
    fig.savefig(OUTPUTS / "fig_top_winners.png", dpi=110)
    plt.close(fig)
    rep.append("Top 10 vendors by value:")
    rep.append(w.head(10)[["titulaire_nom", "n", "total_eur"]]
               .assign(total_eur=lambda d: (d.total_eur / 1e6).round(1))
               .to_string(index=False))
    rep.append("")


def sme(df: pd.DataFrame, rep: list[str]) -> None:
    rep.append("=== SME vs LARGE (titulaire_categorie) ===")
    g = df.dropna(subset=["montant_analyse"]).groupby("titulaire_categorie").agg(
        n=("uid", "size"), total_eur=("montant_analyse", "sum")).reset_index()
    g["count_share"] = g["n"] / g["n"].sum() * 100
    g["value_share"] = g["total_eur"] / g["total_eur"].sum() * 100
    g.to_csv(OUTPUTS / "agg_sme.csv", index=False)
    rep.append(g.round(1).to_string(index=False))
    rep.append("")

    fig, ax = plt.subplots(figsize=(8, 4.5))
    cats = g["titulaire_categorie"].fillna("Inconnu")
    x = np.arange(len(cats)); wbar = 0.4
    ax.bar(x - wbar/2, g["count_share"], wbar, label="% of markets (count)", color="#66c2a5")
    ax.bar(x + wbar/2, g["value_share"], wbar, label="% of spend (value)", color="#e34a33")
    ax.set_xticks(x); ax.set_xticklabels(cats, rotation=0)
    ax.set_title("SME / ETI / GE: share of markets vs share of spend")
    ax.set_ylabel("%"); ax.legend()
    fig.savefig(OUTPUTS / "fig_sme_share.png", dpi=110)
    plt.close(fig)

    # PME value share by buyer category
    bc = (df.dropna(subset=["montant_analyse", "titulaire_categorie"])
          .pivot_table(index="acheteur_categorie", columns="titulaire_categorie",
                       values="montant_analyse", aggfunc="sum", fill_value=0))
    if "PME" in bc.columns:
        bc["total"] = bc.sum(axis=1)
        bc["pme_value_share"] = bc["PME"] / bc["total"] * 100
        bc = bc.sort_values("pme_value_share", ascending=False)
        bc.reset_index().to_csv(OUTPUTS / "agg_sme_by_buyer.csv", index=False)
        rep.append("\nPME value-share by buyer category (top/bottom):")
        rep.append(bc[["pme_value_share"]].head(6).round(1).to_string())
        rep.append(bc[["pme_value_share"]].tail(6).round(1).to_string())
    rep.append("")


def competition(df: pd.DataFrame, rep: list[str]) -> None:
    rep.append("=== COMPETITION & TRANSPARENCY ===")
    known = df[df["offresRecues"].notna()].copy()
    known["single_bid"] = (known["offresRecues"] == 1)
    overall = known["single_bid"].mean() * 100
    rep.append(f"Markets with known #offers: {len(known):,} "
               f"({len(known)/len(df)*100:.1f}% of all)")
    rep.append(f"Single-bid (exactly 1 offer) share: {overall:.1f}%")
    rep.append("")

    def sb_rate(frame: pd.DataFrame, by: str) -> pd.DataFrame:
        out = frame.groupby(by).agg(
            n=("uid", "size"), single_bid_rate=("single_bid", "mean"),
            avg_offers=("offresRecues", "mean")).reset_index()
        out["single_bid_rate"] = out["single_bid_rate"] * 100
        return out.sort_values("single_bid_rate", ascending=False)

    for by, name in [("procedure", "procedure"), ("acheteur_categorie", "buyer category"),
                     ("type", "contract type")]:
        r = sb_rate(known, by)
        r.to_csv(OUTPUTS / f"agg_single_bid_{by}.csv", index=False)
        rep.append(f"Single-bid rate by {name}:")
        rep.append(r.round(1).head(8).to_string(index=False))
        rep.append("")

    # Buyers with high single-bid rate (min 200 known markets)
    b = sb_rate(known, "acheteur_nom")
    b = b[b["n"] >= 200].sort_values("single_bid_rate", ascending=False)
    b.head(20).to_csv(OUTPUTS / "agg_single_bid_buyers.csv", index=False)
    rep.append(f"Buyers (>=200 known markets) with highest single-bid rate (top 10):")
    rep.append(b.head(10)[["acheteur_nom", "n", "single_bid_rate"]].round(1).to_string(index=False))
    rep.append("")

    fig, ax = plt.subplots(figsize=(9, 4.5))
    r = pd.read_csv(OUTPUTS / "agg_single_bid_procedure.csv")
    r = r[r["procedure"].notna()].sort_values("single_bid_rate")
    ax.barh(r["procedure"].str.slice(0, 35), r["single_bid_rate"], color="#756bb1")
    ax.set_title("Single-bid rate by procurement procedure (%)")
    ax.set_xlabel("% single-bid")
    fig.savefig(OUTPUTS / "fig_single_bid.png", dpi=110)
    plt.close(fig)


def geography(df: pd.DataFrame, rep: list[str]) -> None:
    rep.append("=== GEOGRAPHY ===")
    reg = df.dropna(subset=["montant_analyse"]).groupby("acheteur_region_nom").agg(
        n=("uid", "size"), total_eur=("montant_analyse", "sum")).reset_index()
    reg = reg.sort_values("total_eur", ascending=False)
    reg.to_csv(OUTPUTS / "agg_region_spend.csv", index=False)
    rep.append("Spend by buyer region:")
    rep.append(reg.assign(total_eur=lambda d: (d.total_eur/1e6).round(0))
               .to_string(index=False))
    rep.append("")

    # Local capture: same region as buyer
    both = df.dropna(subset=["montant_analyse", "acheteur_region_nom", "titulaire_region_nom"])
    both = both.copy()
    both["same_region"] = both["acheteur_region_nom"] == both["titulaire_region_nom"]
    cap = both.groupby("acheteur_region_nom").apply(
        lambda g: g.loc[g["same_region"], "montant_analyse"].sum() / g["montant_analyse"].sum() * 100,
        include_groups=False)
    cap = cap.sort_values(ascending=False)
    cap.to_csv(OUTPUTS / "agg_local_capture.csv")
    rep.append("Local capture (share of spend won by same-region vendors) by region:")
    rep.append(cap.round(1).to_string())
    rep.append("")

    # Distance distribution (known)
    dist = df["titulaire_distance"].dropna()
    rep.append(f"Buyer-winner distance: median {dist.median():.0f} km, "
               f"90th pct {dist.quantile(.9):.0f} km, mean {dist.mean():.0f} km")
    rep.append("")

    fig, ax = plt.subplots(figsize=(9, 4.5))
    r2 = reg.sort_values("total_eur")
    ax.barh(r2["acheteur_region_nom"], r2["total_eur"] / 1e6, color="#2b8cbe")
    ax.set_title("Public spend by region (€M, buyer location)")
    ax.set_xlabel("€M")
    fig.savefig(OUTPUTS / "fig_region_spend.png", dpi=110)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    cap2 = cap.sort_values()
    ax.barh(cap2.index, cap2.values, color="#31a354")
    ax.set_title("Local capture by region (% spend won by same-region vendors)")
    ax.set_xlabel("%")
    fig.savefig(OUTPUTS / "fig_local_capture.png", dpi=110)
    plt.close(fig)


def categories(df: pd.DataFrame, rep: list[str]) -> None:
    rep.append("=== CATEGORY CONCENTRATION (CPV divisions) ===")
    d = df.dropna(subset=["montant_analyse", "codeCPV"]).copy()
    d["cpv_div"] = d["codeCPV"].astype(str).str[:2]
    d["cpv_label"] = d["cpv_div"].map(cpv_label)
    grp = d.groupby(["cpv_div", "cpv_label"]).agg(
        n=("uid", "size"), total_eur=("montant_analyse", "sum")).reset_index()
    grp = grp.sort_values("total_eur", ascending=False)
    grp.to_csv(OUTPUTS / "agg_cpv.csv", index=False)
    rep.append("Top CPV divisions by spend:")
    rep.append(grp.head(12).assign(total_eur=lambda x: (x.total_eur/1e6).round(0))
               .to_string(index=False))
    rep.append("")

    # Concentration per CPV division (HHI among winners within division)
    rows = []
    for div, sub in d.groupby("cpv_div"):
        sub2 = sub.groupby("titulaire_nom")["montant_analyse"].sum()
        if len(sub2) >= 20:
            rows.append({
                "cpv_div": div,
                "cpv_label": cpv_label(div),
                "n_winners": len(sub2),
                "total_eur": sub2.sum(),
                "hhi": hhi((sub2 / sub2.sum()).values),
                "top1_share": sub2.sort_values(ascending=False).head(1).sum() / sub2.sum() * 100,
            })
    conc = pd.DataFrame(rows).sort_values("hhi", ascending=False)
    conc.to_csv(OUTPUTS / "agg_cpv_concentration.csv", index=False)
    rep.append("Most concentrated CPV divisions (HHI, min 20 winners):")
    rep.append(conc.head(10)[["cpv_label", "n_winners", "hhi", "top1_share"]].round(0).to_string(index=False))
    rep.append("")

    fig, ax = plt.subplots(figsize=(9, 5))
    top = grp.head(12).sort_values("total_eur")
    ax.barh(top["cpv_label"].str.slice(0, 30), top["total_eur"] / 1e6, color="#8856a7")
    ax.set_title("Top CPV divisions by spend (€M)")
    ax.set_xlabel("€M")
    fig.savefig(OUTPUTS / "fig_cpv_top.png", dpi=110)
    plt.close(fig)


def anomalies(df: pd.DataFrame, rep: list[str]) -> None:
    rep.append("=== ANOMALY / ATTENTION LIST ===")
    rep.append("Definition: high-value markets that are also single-bid and sit far above")
    rep.append("their category median. These warrant a closer look (not a fraud allegation).")
    rep.append("")
    d = df.dropna(subset=["montant_analyse", "codeCPV"]).copy()
    d["cpv_div"] = d["codeCPV"].astype(str).str[:2]
    med = d.groupby("cpv_div")["montant_analyse"].transform("median")
    d["ratio_to_median"] = d["montant_analyse"] / med
    d["single_bid"] = (d["offresRecues"] == 1)
    flagged = d[(d["ratio_to_median"] > 20) & (d["single_bid"] == True)
                & (d["montant_analyse"] > 1e6)].copy()
    flagged = flagged.sort_values("montant_analyse", ascending=False)
    cols = ["acheteur_nom", "titulaire_nom", "titulaire_categorie", "cpv_div",
            "montant", "offresRecues", "ratio_to_median", "titulaire_distance",
            "acheteur_departement_nom", "dateNotification"]
    flagged = (flagged[cols]
                .drop_duplicates(subset=["acheteur_nom", "montant", "dateNotification", "cpv_div"])
                .head(200))
    flagged.to_csv(OUTPUTS / "agg_attention_list.csv", index=False)
    disp = flagged.head(15).copy()
    disp["montant_M"] = (disp["montant"] / 1e6).round(1)
    disp["x_median"] = disp["ratio_to_median"].round(0)
    rep.append(f"Flagged markets: {len(flagged):,} (high value + single-bid + >20x category median)")
    rep.append("Top 15 by value (€M, multiple of category median):")
    rep.append(disp[["acheteur_nom", "titulaire_nom", "titulaire_categorie",
                     "montant_M", "offresRecues", "x_median"]].to_string(index=False))
    rep.append("")


def main() -> None:
    df = load()
    rep: list[str] = []
    rep.append("=" * 70)
    rep.append("DECP PUBLIC PROCUREMENT — ANALYSIS REPORT")
    rep.append("=" * 70)
    overview(df, rep)
    concentration(df, rep)
    sme(df, rep)
    competition(df, rep)
    geography(df, rep)
    categories(df, rep)
    anomalies(df, rep)

    report = "\n".join(rep)
    (OUTPUTS / "analysis_report.txt").write_text(report, encoding="utf-8")
    print(report)
    print(f"\nSaved analysis_report.txt and {len(list(OUTPUTS.glob('agg_*.*')))} aggregate files.")


if __name__ == "__main__":
    main()

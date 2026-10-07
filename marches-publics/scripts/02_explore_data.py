"""
Explore the consolidated DECP parquet file.

Profiles: size, year coverage, key null rates, categorical distributions,
amount statistics, and competition signal (offresRecues).

Writes a human-readable report to outputs/exploration_report.txt.
"""

from __future__ import annotations

import datetime as dt
import pathlib

import pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
PROJECT = HERE.parent
RAW = PROJECT / "raw"
OUTPUTS = PROJECT / "output"
OUTPUTS.mkdir(parents=True, exist_ok=True)

PARQUET = RAW / "decp.parquet"


def main() -> None:
    print(f"Loading {PARQUET} ...")
    df = pd.read_parquet(PARQUET)
    n = len(df)
    print(f"Rows: {n:,}  Cols: {len(df.columns)}")

    lines = []
    lines.append("=" * 70)
    lines.append("DECP CONSOLIDATED DATA — EXPLORATION REPORT")
    lines.append(f"Generated: {dt.datetime.now():%Y-%m-%d %H:%M}")
    lines.append(f"Rows: {n:,} | Cols: {len(df.columns)}")
    lines.append("=" * 70)

    # --- Current-data flag ---
    lines.append("\n--- donneesActuelles (de-dup to current state) ---")
    da = df["donneesActuelles"].value_counts(dropna=False)
    lines.append(da.to_string())

    # --- Year coverage ---
    lines.append("\n--- Year coverage (dateNotification) ---")
    dn = pd.to_datetime(df["dateNotification"], errors="coerce")
    yr = dn.dt.year
    lines.append(yr.value_counts(dropna=False).sort_index().to_string())

    # --- Key column null rates ---
    lines.append("\n--- Null rates for analytical key columns ---")
    key_cols = [
        "montant", "titulaire_categorie", "offresRecues", "type", "procedure",
        "codeCPV", "acheteur_categorie", "acheteur_region_nom",
        "titulaire_region_nom", "titulaire_distance", "donneesActuelles",
    ]
    nulls = {c: df[c].isna().mean() * 100 for c in key_cols if c in df.columns}
    for c, v in nulls.items():
        lines.append(f"  {c:28s} {v:6.2f}% null")

    # --- Categorical distributions ---
    for col, top in [("titulaire_categorie", 10), ("type", 10),
                     ("procedure", 10), ("acheteur_categorie", 12)]:
        if col in df.columns:
            lines.append(f"\n--- {col} ---")
            vc = df[col].value_counts(dropna=False)
            lines.append(vc.head(top).to_string())

    # --- montant stats (current data only) ---
    cur = df[df["donneesActuelles"] == True] if "donneesActuelles" in df.columns else df
    lines.append(f"\n--- montant stats (donneesActuelles=True, n={len(cur):,}) ---")
    m = pd.to_numeric(cur["montant"], errors="coerce")
    m = m[m > 0]
    lines.append(m.describe(percentiles=[.5, .9, .99]).to_string())
    lines.append(f"  total awarded (€): {m.sum():,.0f}")
    lines.append(f"  total awarded (€M): {m.sum()/1e6:,.1f}")

    # --- Competition signal ---
    lines.append("\n--- Competition (offresRecues) ---")
    off = pd.to_numeric(cur["offresRecues"], errors="coerce")
    off_known = off.dropna()
    lines.append(f"  rows with known offresRecues: {len(off_known):,} ({len(off_known)/len(cur)*100:.1f}%)")
    single = (off_known <= 1).mean() * 100
    lines.append(f"  single-bid (<=1 offer) share among known: {single:.1f}%")
    lines.append(off_known.value_counts().sort_index().head(10).to_string())

    # --- Distance ---
    lines.append("\n--- titulaire_distance (km, current data) ---")
    dist = pd.to_numeric(cur["titulaire_distance"], errors="coerce")
    lines.append(dist.dropna().describe(percentiles=[.5, .9, .99]).to_string())

    report = "\n".join(lines)
    out = OUTPUTS / "exploration_report.txt"
    out.write_text(report, encoding="utf-8")
    print(report)
    print(f"\nSaved -> {out}")


if __name__ == "__main__":
    main()

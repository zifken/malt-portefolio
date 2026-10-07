"""
Clean the consolidated DECP data into an analysis-ready parquet.

Steps:
- keep only current-state rows (donneesActuelles == True) to avoid counting
  modification duplicates
- parse dates and derive notification year
- keep valid, positive amounts; flag extreme outliers (> 1e9 €) but keep them
  out of distribution-sensitive computations
- sanitize offresRecues (negative -> NaN)
- select the analytical columns and write raw/decp_clean.parquet
"""

from __future__ import annotations

import pathlib

import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
PROJECT = HERE.parent
RAW = PROJECT / "raw"
OUTPUTS = PROJECT / "output"

PARQUET_IN = RAW / "decp.parquet"
PARQUET_OUT = RAW / "decp_clean.parquet"

KEEP = [
    "uid", "id", "acheteur_id", "acheteur_nom", "acheteur_categorie",
    "acheteur_region_code", "acheteur_region_nom", "acheteur_departement_code",
    "acheteur_departement_nom", "acheteur_commune_nom",
    "acheteur_latitude", "acheteur_longitude",
    "titulaire_id", "titulaire_nom", "titulaire_categorie",
    "titulaire_region_code", "titulaire_region_nom", "titulaire_departement_code",
    "titulaire_departement_nom", "titulaire_commune_nom",
    "titulaire_distance", "titulaire_latitude", "titulaire_longitude",
    "montant", "type", "procedure", "codeCPV", "objet",
    "offresRecues", "dureeMois", "dateNotification", "datePublicationDonnees",
    "donneesActuelles", "nature",
]


def main() -> None:
    print(f"Loading {PARQUET_IN} ...")
    df = pd.read_parquet(PARQUET_IN, columns=None)
    df = df[[c for c in KEEP if c in df.columns]]

    # Current-state only
    df = df[df["donneesActuelles"] == True].copy()
    print(f"After donneesActuelles==True: {len(df):,} rows")

    # Dates
    dn = pd.to_datetime(df["dateNotification"], errors="coerce")
    df["year"] = dn.dt.year
    df["dateNotification"] = dn

    # Amounts
    df["montant"] = pd.to_numeric(df["montant"], errors="coerce")
    df = df[df["montant"] > 0]
    # Outlier flag (> 1 billion €) — keep but mark
    df["is_outlier_amount"] = df["montant"] > 1e9
    print(f"Valid positive amounts: {len(df):,} rows; "
          f"outliers(>1e9 €): {df['is_outlier_amount'].sum():,}")

    # Competition
    off = pd.to_numeric(df["offresRecues"], errors="coerce")
    off = off.where(off >= 0)
    df["offresRecues"] = off
    df["single_bid"] = (off == 1)

    # Drop implausible notification years outside 2000-2026
    df = df[df["year"].between(2000, 2026)]

    df.to_parquet(PARQUET_OUT, index=False)
    print(f"Wrote {PARQUET_OUT} ({PARQUET_OUT.stat().st_size >> 20} MB), "
          f"{len(df):,} rows, {df.shape[1]} cols")


if __name__ == "__main__":
    main()

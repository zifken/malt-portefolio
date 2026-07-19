"""
Step 1: Download French Real Estate Data (DVF)
==============================================

Downloads DVF (Demandes de Valeurs Foncières) transactions from data.gouv.fr
for the 5 largest French metropolitan areas, 2021-2024.

Coverage (5 départements × 4 years = 20 files):
    75 — Paris (Île-de-France)
    13 — Bouches-du-Rhône (Marseille)
    69 — Rhône (Lyon)
    31 — Haute-Garonne (Toulouse)
    44 — Loire-Atlantique (Nantes)

Source : https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres
Licence: Licence Ouverte 2.0 (Etalab)
"""

from __future__ import annotations

import sys
from pathlib import Path
import requests
from tqdm import tqdm

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# 5 largest French metros — each département is one file per year.
DEPARTMENTS = ["75", "13", "69", "31", "44"]
YEARS = [2021, 2022, 2023, 2024]

BASE_URL = "https://files.data.gouv.fr/geo-dvf/latest/csv"


def download_file(url: str, dest_path: Path, desc: str = "") -> Path:
    """Stream-download `url` to `dest_path` with a progress bar; skip if present."""
    if dest_path.exists() and dest_path.stat().st_size > 0:
        print(f"✅ Already present: {dest_path.name}")
        return dest_path

    print(f"📥 Downloading: {desc or url}")
    try:
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            with open(dest_path, "wb") as f, tqdm(
                total=total or None,
                unit="B", unit_scale=True, unit_divisor=1024,
                desc=dest_path.name,
            ) as bar:
                for chunk in r.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
                        bar.update(len(chunk))
        return dest_path
    except requests.RequestException as e:
        print(f"❌ Download failed for {url}: {e}")
        raise


def download_dvf_department(department_code: str, year: int) -> Path:
    """Download DVF for one department-year."""
    url = f"{BASE_URL}/{year}/departements/{department_code}.csv.gz"
    dest_path = DATA_DIR / f"dvf_{year}_dept{department_code}.csv.gz"
    return download_file(url, dest_path, f"DVF {year} - dept {department_code}")


def main() -> None:
    print("🏠 DVF Downloader — 5 métropoles × 5 années (2020-2024)")
    print("=" * 60)
    print(f"Départements : {', '.join(DEPARTMENTS)} (Paris, Marseille, Lyon, Toulouse, Nantes)")
    print(f"Années        : {YEARS[0]}–{YEARS[-1]}")
    print()

    files = []
    for year in YEARS:
        for dept in DEPARTMENTS:
            files.append(download_dvf_department(dept, year))

    print("\n" + "=" * 60)
    total_mb = sum(f.stat().st_size for f in files) / 1e6
    print(f"✅ Download complete: {len(files)} fichiers, {total_mb:.1f} MB total")
    print(f"📁 Data saved to: {DATA_DIR.resolve()}")
    print("\nNext steps:")
    print("  1. python 02_data_exploration.py")
    print("  2. python 03_data_cleaning.py")


if __name__ == "__main__":
    main()

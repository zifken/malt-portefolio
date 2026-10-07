"""
Download the consolidated DECP (Données Essentielles de la Commande Publique)
tabular file from data.gouv.fr.

The dataset is large; we pull the consolidated `decp.parquet` resource, resolving
the latest URL dynamically from the data.gouv.fr API so the script stays robust to
new publishes.

Usage:
    python3 scripts/01_download_data.py
"""

from __future__ import annotations

import json
import pathlib
import sys
import urllib.request

import requests

HERE = pathlib.Path(__file__).resolve().parent
PROJECT = HERE.parent
RAW = PROJECT / "raw"
RAW.mkdir(parents=True, exist_ok=True)

DATASET_SLUG = "donnees-essentielles-de-la-commande-publique-consolidees-format-tabulaire"


def find_decp_parquet_url() -> str:
    """Resolve the latest consolidated decp.parquet resource URL via the API."""
    url = f"https://www.data.gouv.fr/api/2/datasets/{DATASET_SLUG}/"
    print(f"Querying dataset metadata: {url}")
    with urllib.request.urlopen(url, timeout=30) as r:
        meta = json.load(r)
    resources_href = meta["resources"]["href"]
    with urllib.request.urlopen(resources_href, timeout=30) as r:
        res = json.load(r)
    candidates = [
        x for x in res.get("data", [])
        if x.get("format") == "parquet" and x.get("title", "").startswith("decp")
    ]
    if not candidates:
        raise SystemExit("Could not find a decp*.parquet resource.")
    # Prefer "decp.parquet" exactly, else first
    chosen = next((c for c in candidates if c.get("title") == "decp.parquet"), candidates[0])
    dl = chosen.get("url") or chosen.get("latest_url")
    print(f"Selected resource: {chosen.get('title')} ({chosen.get('format')})")
    return dl


def download(url: str, dest: pathlib.Path) -> None:
    print(f"Downloading -> {dest}")
    with requests.get(url, stream=True, timeout=300) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        downloaded = 0
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                if not chunk:
                    continue
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = 100 * downloaded / total
                    sys.stdout.write(f"\r  {pct:6.2f}%  ({downloaded >> 20}/{total >> 20} MB)")
                    sys.stdout.flush()
    print("\nDownload complete.")


def main() -> None:
    dest = RAW / "decp.parquet"
    if dest.exists():
        print(f"{dest} already exists ({dest.stat().st_size >> 20} MB). Skipping.")
        return
    url = find_decp_parquet_url()
    download(url, dest)


if __name__ == "__main__":
    main()

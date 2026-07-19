"""
Download the latest French fuel prices XML from data.gouv.fr / Roulez-eco.
"""

import zipfile
from pathlib import Path
from urllib.request import urlopen


PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_URL = "https://donnees.roulez-eco.fr/opendata/instantane"
ZIP_PATH = PROJECT_DIR / "fuel_prices.zip"
XML_NAME = "PrixCarburants_instantane.xml"


def download_latest() -> Path:
    print(f"Downloading {DATA_URL} ...")
    with urlopen(DATA_URL) as response, open(ZIP_PATH, "wb") as f:
        f.write(response.read())
    print(f"Saved {ZIP_PATH} ({ZIP_PATH.stat().st_size / 1024:.1f} KB)")

    print("Extracting XML...")
    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        z.extract(XML_NAME, path=PROJECT_DIR)
    xml_path = PROJECT_DIR / XML_NAME
    print(f"Extracted → {xml_path} ({xml_path.stat().st_size / 1024 / 1024:.1f} MB)")
    return xml_path


if __name__ == "__main__":
    download_latest()

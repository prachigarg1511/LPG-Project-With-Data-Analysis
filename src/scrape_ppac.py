from __future__ import annotations

import os
import hashlib
import requests
import pandas as pd

def _hash_url(url: str) -> str:
    return hashlib.md5(url.encode("utf-8")).hexdigest()[:10]

def fetch_tables(url: str, raw_dir: str = "data/raw") -> list[pd.DataFrame]:
    os.makedirs(raw_dir, exist_ok=True)

    r = requests.get(url, timeout=40, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()

    # Save raw html for reproducibility
    fp = os.path.join(raw_dir, f"ppac_{_hash_url(url)}.html")
    with open(fp, "wb") as f:
        f.write(r.content)

    # Parse all tables on the page
    tables = pd.read_html(r.text)
    return tables
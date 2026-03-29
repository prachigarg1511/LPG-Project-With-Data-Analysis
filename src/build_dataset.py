from __future__ import annotations

import pandas as pd
from src.utils import coerce_price, coerce_date, normalize_state_name

def _guess_col(cols, keywords):
    cols_l = [c.lower() for c in cols]
    for i, c in enumerate(cols_l):
        if any(k in c for k in keywords):
            return cols[i]
    return None

def normalize_ppac_tables(tables: list[pd.DataFrame], source_url: str) -> pd.DataFrame:
    out_rows = []

    for t in tables:
        if t.shape[1] < 2:
            continue

        cols = list(t.columns)

        # Guess likely columns
        date_col = _guess_col(cols, ["date", "effective", "w.e.f", "wef", "month"])
        state_col = _guess_col(cols, ["state", "ut", "location", "city", "metro"])
        price_col = _guess_col(cols, ["lpg", "domestic", "rsp", "price"])

        # If cannot find a price column, skip
        if price_col is None:
            continue

        df = t.copy()

        # Create working columns
        df_work = pd.DataFrame()
        df_work["source_url"] = source_url

        if date_col is not None:
            df_work["date"] = coerce_date(df[date_col])
        else:
            df_work["date"] = pd.NaT

        if state_col is not None:
            df_work["location"] = df[state_col].astype(str).map(normalize_state_name)
        else:
            df_work["location"] = "Unknown"

        df_work["price"] = coerce_price(df[price_col])

        df_work = df_work.dropna(subset=["price"])
        # keep only rows that look like real prices
        df_work = df_work[(df_work["price"] > 100) & (df_work["price"] < 5000)]

        out_rows.append(df_work)

    if not out_rows:
        return pd.DataFrame(columns=["date", "location", "price", "source_url"])

    result = pd.concat(out_rows, ignore_index=True)

    # If no date in table, still keep for mapping (cross-section)
    return result
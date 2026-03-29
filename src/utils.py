import re
import pandas as pd

def normalize_state_name(x: str) -> str:
    if pd.isna(x):
        return x
    x = str(x).strip()
    x = x.replace("&", "and")
    x = re.sub(r"\s+", " ", x)
    return x

def coerce_price(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.replace("₹", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.extract(r"([-+]?\d*\.?\d+)", expand=False)
        .astype(float)
    )

def coerce_date(series: pd.Series) -> pd.Series:
    # handles many formats; add dayfirst if your table uses dd-mm-yyyy
    return pd.to_datetime(series, errors="coerce", dayfirst=True)
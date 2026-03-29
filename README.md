# LPG Project With Data Analysis (World Bank / PPAC) — Streamlit + ITS

This repository contains a Streamlit app and supporting scripts to analyze LPG (Liquefied Petroleum Gas) price time series and run **Interrupted Time Series (ITS)** analysis around major events.

It supports two data sources:
1. **World Bank Global Fuel Prices Database (Excel/XLSX)** — recommended for country-level LPG analysis.
2. **PPAC scraping workflow** — for India-focused pages (only if URLs and table structure still match).

> Note: The World Bank LPG sheet is typically **country-level**. If your dataset does not contain India State/UT rows, an India state choropleth map is not meaningful. This repo is configured to focus on **ITS + dataset debugging** (maps removed/disabled).

---

## Features

- Load an existing dataset from `data/processed/lpg_ppac_prices.csv`
- (Optional) Scrape PPAC tables and normalize them into a dataset
- Clean and standardize the dataset (`date` parsing, `price` numeric conversion)
- Build **monthly** series via resampling
- Run **Interrupted Time Series (ITS)** regression with configurable event dates
- Export:
  - monthly series CSV
  - fitted ITS results CSV

---

## Project structure (typical)

- `app/main.py` — Streamlit UI
- `src/scrape_ppac.py` — PPAC page table extraction
- `src/build_dataset.py` — dataset normalization
- `src/its.py` — ITS model fitting
- `src/config.py` — PPAC URLs + event dates
- `data/raw/` — raw scraped outputs (usually not committed)
- `data/processed/` — processed datasets (usually not committed)

---

## Setup

### 1) Create and activate a virtual environment (Windows)
```bat
py -3.12 -m venv .venv
.venv\Scripts\activate
```

### 2) Install dependencies
```bat
py -3.12 -m pip install -U pip
py -3.12 -m pip install -r requirements.txt
```

If you load `.xlsx` files with pandas, make sure you have:
```bat
py -3.12 -m pip install openpyxl
```

---

## Data: World Bank XLSX → app CSV

The Streamlit app expects a long-format CSV at:

`data/processed/lpg_ppac_prices.csv`

### If your World Bank `LPG` sheet is wide-format (dates are columns)
Use this command to convert it to long format:

```bat
py -3.12 -c "import pandas as pd; x='data/processed/Global_Fuel_Prices_Database.xlsx'; df=pd.read_excel(x, sheet_name='LPG'); id_col=df.columns[0]; units_col='Units'; date_cols=[c for c in df.columns if c not in [id_col, units_col]]; out=df.melt(id_vars=[id_col, units_col], value_vars=date_cols, var_name='date', value_name='price'); out=out.rename(columns={id_col:'series'}); out['date']=pd.to_datetime(out['date'], errors='coerce'); out['price']=pd.to_numeric(out['price'].astype(str).str.replace(',','', regex=False).str.strip(), errors='coerce'); out=out.dropna(subset=['date','price']); out.to_csv('data/processed/lpg_ppac_prices.csv', index=False); print('Saved', len(out), 'rows')"
```

Output columns will be:
- `series` (e.g., `India (LPG)` or country label)
- `Units`
- `date`
- `price`

---

## Run the Streamlit app

```bat
py -3.12 -m streamlit run app\main.py
```

Then use the sidebar:
- **Load Existing CSV (skip scrape)** to load `data/processed/lpg_ppac_prices.csv`
- Choose an **Event** and **Event date**
- Run ITS and download outputs

---

## Optional: PPAC scraping

If you want to scrape PPAC pages instead of using the World Bank dataset:

1. Open `src/config.py`
2. Add working PPAC URL(s) to `PPAC_URLS`
3. Run the app and click:
   **1) Scrape PPAC + Build Dataset**

**Warning:** Web page structures change. If PPAC tables change, you may need to adjust detection logic in `src/build_dataset.py`.

---

## .gitignore recommendation (avoid committing data)

Do not commit large datasets / raw scraped files. Add a `.gitignore` like:

```gitignore
data/raw/
data/processed/
*.csv
*.xlsx
__pycache__/
*.pyc
.venv/
venv/
```

---

## License
Add a license if you plan to share publicly (MIT is common for student projects).

# India LPG War Analytics (2026-capable)

This project creates a dataset for LPG prices by scraping PPAC pages, then shows:
- India map (choropleth) when data contains State/UT rows
- Interrupted Time Series (ITS) statistics for war shock dates

## Setup
```bash
pip install -r requirements.txt
```

## Configure PPAC URLs
Edit `src/config.py` and paste working PPAC URLs into `PPAC_URLS`.

## Run
```bash
streamlit run app/app.py
```

## Files
- Output dataset: `data/processed/lpg_ppac_prices.csv`
- You must provide: `assets/india_states.geojson`
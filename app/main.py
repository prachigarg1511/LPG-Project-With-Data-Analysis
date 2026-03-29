import os
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.ui_styles import CUSTOM_CSS
from src.config import PPAC_URLS, EVENTS
from src.scrape_ppac import fetch_tables
from src.build_dataset import normalize_ppac_tables
from src.its import fit_its

DATA_PROCESSED = "data/processed"
RAW_DIR = "data/raw"
DEFAULT_OUT = os.path.join(DATA_PROCESSED, "lpg_ppac_prices.csv")

st.set_page_config(page_title="India LPG War Analytics (PPAC 2026)", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.title("India LPG Prices (2026-capable): Dataset + ITS Statistics")

st.warning(
    "If using PPAC scraping: paste working PPAC URL(s) in src/config.py (PPAC_URLS). "
    "If using World Bank XLSX: convert it to data/processed/lpg_ppac_prices.csv first."
)

# Sidebar
st.sidebar.header("Controls")

st.sidebar.markdown("---")
event_name = st.sidebar.selectbox("Event", list(EVENTS.keys()))
event_date = st.sidebar.text_input("Event date", value=EVENTS[event_name])

st.sidebar.markdown("---")
run_scrape = st.sidebar.button("1) Scrape PPAC + Build Dataset")
load_existing = st.sidebar.button("2) Load Existing CSV (skip scrape)")

tab_its, tab_debug = st.tabs(["ITS Stats", "Dataset / Debug"])


def build_or_load_dataset():
    os.makedirs(DATA_PROCESSED, exist_ok=True)
    os.makedirs(RAW_DIR, exist_ok=True)

    if run_scrape:
        if not PPAC_URLS or all((u.strip() == "" for u in PPAC_URLS)):
            st.error("No PPAC_URLS found. Edit src/config.py and paste PPAC URLs.")
            return None

        all_parts = []
        for url in PPAC_URLS:
            url = url.strip()
            if not url:
                continue
            try:
                tables = fetch_tables(url, raw_dir=RAW_DIR)
                norm = normalize_ppac_tables(tables, source_url=url)
                if len(norm):
                    all_parts.append(norm)
            except Exception as e:
                st.error(f"Failed scraping {url}: {e}")

        if not all_parts:
            st.error("No usable tables found on the provided PPAC pages.")
            return None

        df = pd.concat(all_parts, ignore_index=True)

        df.to_csv(DEFAULT_OUT, index=False)
        st.success(f"Saved dataset: {DEFAULT_OUT} (rows={len(df)})")
        return df

    if load_existing:
        if not os.path.exists(DEFAULT_OUT):
            st.error(f"File not found: {DEFAULT_OUT}. Create it first (scrape or convert from XLSX).")
            return None
        return pd.read_csv(DEFAULT_OUT)

    # auto-load if exists
    if os.path.exists(DEFAULT_OUT):
        return pd.read_csv(DEFAULT_OUT)

    return None


df = build_or_load_dataset()

# Normalize/clean if present
if df is not None:
    # date
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # price
    if "price" in df.columns:
        df["price"] = pd.to_numeric(
            df["price"].astype(str).str.replace(",", "", regex=False).str.strip(),
            errors="coerce",
        )

    # drop invalid
    drop_cols = [c for c in ["date", "price"] if c in df.columns]
    if drop_cols:
        df = df.dropna(subset=drop_cols)


with tab_debug:
    st.subheader("Dataset / Debug")
    st.markdown(f"Expected output CSV: `{DEFAULT_OUT}`")

    if df is None:
        st.info("No dataset loaded yet. Use 'Scrape' or 'Load Existing CSV'.")
    else:
        st.dataframe(df.head(50), use_container_width=True)
        st.write("Columns:", list(df.columns))
        st.write("Rows:", len(df))
        if "date" in df.columns:
            st.write("Date coverage:", df["date"].min(), "→", df["date"].max())


with tab_its:
    st.subheader("Interrupted Time Series (ITS) on monthly series")

    if df is None:
        st.info("Load/build dataset first.")
    elif "date" not in df.columns or "price" not in df.columns:
        st.error("Dataset must contain columns named 'date' and 'price' for ITS.")
    else:
        ts = df.dropna(subset=["date", "price"]).copy()
        if ts.empty:
            st.error("No usable (date, price) rows found.")
        else:
            # If multiple series exist (World Bank), allow selecting one
            series_col = None
            if "series" in ts.columns:
                series_col = "series"

            if series_col:
                mode = st.radio("Time series mode", ["Single series", "Aggregate (mean)"], horizontal=True)
                if mode == "Single series":
                    series_vals = sorted(ts[series_col].dropna().unique().tolist())
                    s = st.selectbox("Choose series", series_vals)
                    ts2 = ts[ts[series_col] == s].copy()
                    st.caption(f"ITS on series: {s}")
                else:
                    ts2 = ts.copy()
                    st.caption("ITS on aggregated series (mean across all series per date)")
            else:
                ts2 = ts.copy()

            ts2 = ts2.set_index("date").sort_index()
            monthly = ts2["price"].resample("MS").mean().dropna().reset_index()
            monthly.columns = ["date", "price"]

            fitted, model = fit_its(monthly, date_col="date", y_col="price", event_date=event_date)

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=fitted["date"], y=fitted["price"], name="Observed", mode="lines+markers"))
            fig.add_trace(go.Scatter(x=fitted["date"], y=fitted["yhat"], name="ITS fitted", mode="lines"))
            fig.add_vline(x=pd.to_datetime(event_date), line_width=2, line_dash="dash", line_color="red")
            fig.update_layout(height=520, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

            st.text(model.summary().as_text())
            st.download_button(
                "Download monthly series (CSV)",
                data=monthly.to_csv(index=False).encode("utf-8"),
                file_name="monthly_series.csv",
                mime="text/csv",
            )
            st.download_button(
                "Download ITS fitted (CSV)",
                data=fitted.to_csv(index=False).encode("utf-8"),
                file_name="its_fitted.csv",
                mime="text/csv",
            )
# src/config.py
# Paste PPAC page URLs that contain Domestic LPG (14.2 kg) RSP tables.
# Start with these PPAC RSP section pages (updated in 2026).
# If your scrape produces 0 rows, open these pages in a browser,
# find the exact subpage/PDF that contains the LPG table, and add that URL here.

PPAC_URLS = [
    # PPAC RSP section page (updated 2026; entry point)
    "https://ppac.gov.in/retail-selling-price-rsp-of-petrol-diesel-and-domestic-lpg/price-build-up-of-petrol-and-diesel",

    # PPAC metro cities price page (same RSP section; updated 2026)
    "https://ppac.gov.in/retail-selling-price-rsp-of-petrol-diesel-and-domestic-lpg/rsp-of-petrol-and-diesel-in-metro-cities-since-16-6-2017",
]

# Event dates for Interrupted Time Series analysis
EVENTS = {
    "Russia–Ukraine war start": "2022-02-24",
    "Iran escalation (choose & justify)": "2024-04-01",
}
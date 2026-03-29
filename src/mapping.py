import geopandas as gpd
from src.utils import normalize_state_name

def load_india_geojson(path: str, name_field: str):
    gdf = gpd.read_file(path)
    gdf["state"] = gdf[name_field].astype(str).map(normalize_state_name)
    return gdf
"""
Land Use & Zoning Map — Sealy City + ETJ.
Embeds the self-contained Leaflet map (Sealy_Interactive_Map.html):
  - Aerial / street basemap toggle
  - Three zoning layers: Existing land use, Adopted 2012-2035 FLU, Rebalanced scenario
  - Optional live overlays: FEMA flood zones (NFHL) and Texas RRC pipelines
The map file is fully self-contained (parcel data inlined); only the basemap and
the FEMA / pipeline overlays stream from public services at view time.
"""
import os
import streamlit as st
import _brand
import streamlit.components.v1 as components

st.set_page_config(page_title="Sealy — Land Use & Zoning", page_icon="🗺️", layout="wide")
_brand.hide_chrome(); _brand.disclaimer()

st.title("Sealy — Land Use & Zoning Map")
st.caption(
    "Existing land use, the adopted Future Land Use plan, and a rebalanced zoning "
    "scenario over aerial imagery. Use the panel (top-right of the map) to switch the "
    "basemap, pick a zoning layer, and toggle FEMA flood zones and Texas RRC pipelines. "
    "Click any parcel for owner, acreage, and all three designations."
)

HTML_PATH = os.path.join(os.path.dirname(__file__), "..", "gis_data", "Sealy_Interactive_Map.html")

try:
    with open(HTML_PATH, encoding="utf-8") as f:
        html = f.read()
    components.html(html, height=760, scrolling=False)
except FileNotFoundError:
    st.error("Map file not found: gis_data/Sealy_Interactive_Map.html")

st.caption(
    "Rebalanced scenario reallocates only developable land (vacant / underutilized / "
    "redevelopable) toward a Brenham-like business mix; built neighborhoods are unchanged. "
    "Flood and pipeline layers are informational and stream live from FEMA and the Texas "
    "Railroad Commission."
)

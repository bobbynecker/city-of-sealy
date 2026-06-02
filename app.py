"""
Sealy / Austin County — Fiscal & Land-Use Analysis  (landing hub)
Independent analysis by Councilmember Bobby Necker, Place 1.
"""
import streamlit as st
import _brand

st.set_page_config(page_title="Sealy — Necker Analysis", page_icon="🏛️", layout="wide")
_brand.hide_chrome()

st.title("Sealy / Austin County — Fiscal & Land-Use Analysis")
_brand.disclaimer()
st.markdown(
    "A working hub for the **ESD #2 sales-tax Interlocal Agreement** and Sealy growth questions. "
    "Pick a tool below or from the sidebar. Every fiscal number is computed by the City fiscal-model "
    "workbook itself, so the web results match the spreadsheet exactly."
)
st.markdown("---")

c1, c2, c3 = st.columns(3)
with c1:
    st.subheader("📊 Fiscal Impact Model")
    st.write("Scenario builder for the 1.5% sales-tax pool, the City / ESD split, property tax, "
             "impact fees, infrastructure capital, and the 30-year net fiscal position.")
    st.page_link("pages/0_Fiscal_Model.py", label="Open the model →")
with c2:
    st.subheader("🗺️ Developable Land Map")
    st.write("City + ETJ parcels by development tier and proposed zoning, with the ESD #2 "
             "revenue potential of each.")
    st.page_link("pages/1_GIS_Map.py", label="Open the map →")
with c3:
    st.subheader("🏘️ Land Use & Zoning")
    st.write("Existing use, the adopted Future Land Use, and a rebalanced scenario — over aerial "
             "imagery, FEMA flood, pipelines, and jurisdiction overlays.")
    st.page_link("pages/2_Land_Use_and_Zoning_Map.py", label="Open the map →")

st.markdown("---")
st.markdown("#### What this is — and isn't")
st.markdown(
    "- **Planning-level**, not a certified forecast. Inputs are documented and adjustable.\n"
    "- The City / ESD **split is blank by design** — it is a negotiation parameter you set.\n"
    "- Built on **public data**: Comptroller sales-tax sourcing (Pub. 94-105), Austin CAD "
    "exemptions, City budgets/ACFRs, and Census figures.\n"
    "- **Not** legal, financial, or official City advice."
)
st.caption("© Bobby Necker · Independent councilmember analysis · neckerstx.com")

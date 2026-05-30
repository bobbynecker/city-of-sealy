"""
Sealy / ESD #2 Fiscal Impact — Web App
A friendly web front-end over the audited v7 Excel model. The Excel is the calculation
engine (this app writes your inputs into it, recalculates, and reads results back), so
every number here matches the workbook exactly. Split-neutral; planning-level.
"""
import streamlit as st
import pandas as pd
import esd_backend as backend

st.set_page_config(page_title="Sealy ESD #2 Fiscal Model", page_icon="🏛️", layout="wide")

TYPES = ["Single-Family Subdivision","Single-Family Urban / Patio","Townhome / Condo",
         "Multifamily Apartments","Big-Box / Anchor Retail","Retail Center / Strip",
         "Office / Business Park","Hotel","Manufacturing","Industrial / Logistics",
         "Light Industrial / Flex","Mixed-Use Pad / Vertical","Civic / Institutional",
         "Parks / Open Space","Vacant / Holding Land"]
QTY_TYPES = ["lots","units","acres","sqft","rooms"]

st.title("Sealy / Austin County ESD #2 — Fiscal Impact Model")
st.caption("Planning-level scenario builder for the sales-tax Interlocal Agreement. "
           "The audited v7 Excel workbook is the calculation engine, so results match it exactly. "
           "Split-neutral — no preferred allocation is implied.")

# ---------------- Sidebar: assumptions ----------------
with st.sidebar:
    st.header("Assumptions")
    with st.expander("Sales-tax split & rates", expanded=True):
        city_share = st.slider("City General Fund share of pool", 0, 100, 50, 5,
                               help="ESD gets the remainder. The split is a negotiation parameter.") / 100
        st.caption(f"ESD #2 share: **{100-int(city_share*100)}%**")
        pool_rate = st.number_input("Pool rate", 0.0, 0.02, 0.015, 0.0005, format="%.4f")
        city_pt = st.number_input("City property-tax rate (per $1 AV)", 0.0, 0.01, 0.0037731, 0.0001, format="%.7f")
        esd_pt  = st.number_input("ESD #2 property-tax rate (per $1 AV)", 0.0, 0.01, 0.000931, 0.0001, format="%.6f")
    with st.expander("Growth & finance"):
        pop_cagr  = st.number_input("Population CAGR", 0.0, 0.10, 0.032, 0.001, format="%.3f")
        pool_cagr = st.number_input("Sales-tax pool CAGR", 0.0, 0.15, 0.065, 0.005, format="%.3f")
        av_cagr   = st.number_input("Property AV growth CAGR", 0.0, 0.10, 0.06, 0.005, format="%.3f")
        opex_infl = st.number_input("Operating-cost inflation", 0.0, 0.10, 0.025, 0.005, format="%.3f")
        collection= st.number_input("Property-tax collection rate", 0.5, 1.1, 1.0, 0.01, format="%.2f")
    with st.expander("Exemptions (effective taxable-value haircut)"):
        st.caption("City of Sealy grants no general homestead; ESD #2 grants 1%. Confirm vs Austin CAD.")
        res_c = st.number_input("Residential — City %", 0.0, 0.5, 0.02, 0.005, format="%.3f")
        res_e = st.number_input("Residential — ESD %", 0.0, 0.5, 0.035, 0.005, format="%.3f")
        com   = st.number_input("Commercial — City & ESD %", 0.0, 0.5, 0.01, 0.005, format="%.3f")
        ind   = st.number_input("Industrial — City & ESD %", 0.0, 0.5, 0.08, 0.01, format="%.3f")
    with st.expander("Geometry & incentives"):
        far = st.number_input("Floor-Area-Ratio (for sqft entries)", 0.05, 1.0, 0.30, 0.05, format="%.2f")
        abate = st.number_input("Industrial abatement %", 0.0, 1.0, 0.0, 0.05, format="%.2f",
                                help="Generic Ch. 312-style abatement on new industrial property tax.")
        abate_term = st.number_input("Abatement term (years)", 0, 30, 10, 1,
                                     help="Ch. 312 max is 10 years; full tax resumes after.")

inputs = dict(city_share=city_share, pool_rate=pool_rate, city_pt_rate=city_pt, esd_pt_rate=esd_pt,
              pop_cagr=pop_cagr, pool_cagr=pool_cagr, av_cagr=av_cagr, opex_infl=opex_infl,
              collection=collection, far=far, abatement=abate, abate_term=abate_term)
exemptions = {"Residential":{"city":res_c,"esd":res_e},
              "Commercial":{"city":com,"esd":com},
              "Industrial":{"city":ind,"esd":ind}}

# ---------------- Main: scenario projects ----------------
st.subheader("Scenario projects")
st.caption("Add the development projects to test. Check 'Active' to include a project. "
           "Enter manufacturing/industrial by acres where possible (sqft uses the FAR above).")
default = pd.DataFrame([
    {"Active":True,  "Name":"20-acre retail center","Type":"Retail Center / Strip","Qty Type":"acres","Qty":20,"Manual Acres":None,"Start":2,"Buildout":3,"Capture %":100},
    {"Active":False, "Name":"250-unit multifamily apartments","Type":"Multifamily Apartments","Qty Type":"units","Qty":250,"Manual Acres":None,"Start":2,"Buildout":3,"Capture %":100},
    {"Active":False, "Name":"100-home SFR subdivision","Type":"Single-Family Subdivision","Qty Type":"lots","Qty":100,"Manual Acres":None,"Start":1,"Buildout":5,"Capture %":100},
    {"Active":False, "Name":"40-acre logistics","Type":"Industrial / Logistics","Qty Type":"acres","Qty":40,"Manual Acres":None,"Start":2,"Buildout":4,"Capture %":100},
])
edited = st.data_editor(default, num_rows="dynamic", use_container_width=True, key="scn",
    column_config={
        "Active": st.column_config.CheckboxColumn(),
        "Type": st.column_config.SelectboxColumn(options=TYPES, width="large"),
        "Qty Type": st.column_config.SelectboxColumn(options=QTY_TYPES),
        "Capture %": st.column_config.NumberColumn(min_value=0, max_value=100),
    })

if st.button("▶  Calculate fiscal impact", type="primary"):
    scenarios = []
    for _, row in edited.iterrows():
        if pd.isna(row.get("Type")) or pd.isna(row.get("Qty")):
            continue
        scenarios.append(dict(name=row["Name"], active=bool(row["Active"]), type=row["Type"],
                              qty_type=row["Qty Type"], qty=float(row["Qty"]),
                              manual_acres=(None if pd.isna(row["Manual Acres"]) else float(row["Manual Acres"])),
                              start=int(row["Start"]), buildout=int(row["Buildout"]),
                              capture=float(row["Capture %"])/100))
    with st.spinner("Recalculating the model…"):
        r = backend.compute(inputs, scenarios, exemptions)

    def g(label, h=4):  # h: 0=5y,1=10y,2=15y,3=20y,4=30y
        return r.get(label, [0,0,0,0,0])[h]

    st.subheader("Results — 30-year net fiscal position")
    c1,c2,c3 = st.columns(3)
    c1.metric("City NET", f"${g('City NET'):,.0f}")
    c2.metric("ESD NET", f"${g('ESD NET'):,.0f}")
    c3.metric("Combined NET", f"${g('Combined NET'):,.0f}")

    horizons = ["5-yr","10-yr","15-yr","20-yr","30-yr"]
    rows = ["1.5% ILA sales-tax pool","City sales-tax share (net of EDC)","ESD sales-tax share",
            "City property tax (net of exemptions)","ESD property tax (net of exemptions)",
            "Impact fees (one-time)","City operating cost","ESD operating cost",
            "City NET","ESD NET","Combined NET"]
    tbl = pd.DataFrame({lbl: r.get(lbl,[None]*5) for lbl in rows}, index=horizons).T
    st.dataframe(tbl.style.format("${:,.0f}", na_rep="—"), use_container_width=True)

    st.markdown("**Does the sales-tax split move the needle?**")
    iso = pd.DataFrame({
        "City NET excl. sales tax": r.get("City NET excluding sales-tax allocation",[None]*5),
        "+ City sales-tax share":   r.get("City sales-tax share (net of EDC)",[None]*5),
        "= City NET incl. sales tax": r.get("City NET",[None]*5),
    }, index=horizons).T
    st.dataframe(iso.style.format("${:,.0f}", na_rep="—"), use_container_width=True)

    st.markdown("**Net fiscal position by horizon**")
    chart = pd.DataFrame({"City NET": r.get("City NET",[0]*5), "ESD NET": r.get("ESD NET",[0]*5)}, index=horizons)
    st.bar_chart(chart)

    capex = r.get("__capex__", [])
    if capex:
        st.markdown("**Large capital items included in the net**")
        cap_df = pd.DataFrame(capex)[["item","qty","unit","payer","treatment","cost10y"]]
        cap_df.columns = ["Item","Quantity","Unit","Payer","How paid","10-yr cost in NET"]
        st.dataframe(cap_df.style.format({"Quantity":"{:,.0f}","10-yr cost in NET":"${:,.0f}"}, na_rep="—"),
                     use_container_width=True, hide_index=True)

    st.caption("Planning-level estimates. Property tax is net of exemptions; sales-tax sourcing per "
               "Comptroller Pub. 94-105 (retail = origin; residential = online use-tax only; "
               "warehouse/manufacturing ≈ $0 local sales tax). Engine: audited v7 workbook.")
else:
    st.info("Set your assumptions in the sidebar, edit the projects above, then click **Calculate fiscal impact**.")

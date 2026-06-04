"""
Sealy / Austin County ESD #2 — Fiscal Impact Model (web app)
A friendly front-end over the City's fiscal-model workbook. The Excel workbook is the
calculation engine — this app writes your inputs into a copy, recalculates, and reads the
results back — so every number here matches the workbook exactly. Planning-level.
"""
import io

import streamlit as st
import _brand
import pandas as pd
import esd_backend as backend

st.set_page_config(page_title="Sealy ESD #2 Fiscal Model", page_icon="assets/favicon.png", layout="wide")
_brand.hide_chrome()
_brand.top_nav()

_brand.page_header(
    "ESD #2 fiscal impact model",
    "Planning-level scenario builder for the sales-tax Interlocal Agreement. The City's fiscal-model "
    "workbook is the calculation engine — results match it exactly. The City / ESD split is a "
    "negotiation parameter: set it and see the effect.")

# Canonical development types (match the workbook's 02_Type_Assumptions list)
TYPES = ["Single-Family Subdivision","Single-Family Urban / Patio","Townhome / Condo",
         "Multifamily Apartments","Big-Box / Anchor Retail","Retail Center / Strip",
         "Office / Business Park","Hotel","Manufacturing","Industrial / Logistics",
         "Light Industrial / Flex","Mixed-Use Pad / Vertical","Civic / Institutional",
         "Parks / Open Space","Vacant / Holding Land","Gas / Convenience Store",
         "Large Travel Center (C-store)","Fast Food / QSR","Restaurant (Full-Service)",
         "Grocery / Supermarket","Auto Parts / Service","Car Wash"]

# ---------------- Sidebar: assumptions ----------------
with st.sidebar:
    st.header("Assumptions")
    with st.expander("Sales-tax split & rates", expanded=True):
        city_share = st.slider("City General Fund share of pool (%)", 0, 100, 50, 5,
                               help="ESD gets the remainder. The split is a negotiation parameter.") / 100
        st.caption(f"ESD #2 share: **{100-int(round(city_share*100))}%**")
        edc = st.number_input("EDC retention (% of City share)", 0.0, 1.0, 0.0, 0.05, format="%.2f",
                              help="Sealy EDC half-cent carve-out from the City's share.")
        pool_rate = st.number_input("Sales-tax pool rate", 0.0, 0.02, 0.015, 0.0005, format="%.4f")
        city_pt = st.number_input("City property-tax rate (per $1 AV)", 0.0, 0.01, 0.0037731, 0.0001, format="%.7f")
        esd_pt  = st.number_input("ESD #2 property-tax rate (per $1 AV)", 0.0, 0.01, 0.000931, 0.0001, format="%.6f")
    with st.expander("Growth & finance"):
        pop_cagr  = st.number_input("Population CAGR", 0.0, 0.10, 0.032, 0.001, format="%.3f")
        pool_cagr = st.number_input("Sales-tax pool CAGR", 0.0, 0.15, 0.065, 0.005, format="%.3f")
        av_cagr   = st.number_input("Property AV growth CAGR", 0.0, 0.10, 0.06, 0.005, format="%.3f")
        opex_infl = st.number_input("Operating-cost inflation", 0.0, 0.10, 0.025, 0.005, format="%.3f")
        collection= st.number_input("Property-tax collection rate", 0.5, 1.1, 1.0, 0.01, format="%.2f")
    with st.expander("Exemptions (effective taxable-value haircut)"):
        st.caption("City of Sealy grants no general homestead; ESD #2 grants ~1%. Confirm vs Austin CAD.")
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

inputs = dict(city_share=city_share, edc=edc, pool_rate=pool_rate, city_pt_rate=city_pt, esd_pt_rate=esd_pt,
              pop_cagr=pop_cagr, pool_cagr=pool_cagr, av_cagr=av_cagr, opex_infl=opex_infl,
              collection=collection, far=far, abatement=abate, abate_term=abate_term)
exemptions = {"Residential":{"city":res_c,"esd":res_e},
              "Commercial":{"city":com,"esd":com},
              "Industrial":{"city":ind,"esd":ind}}

# ---------------- Main: scenario projects ----------------
def _row(active, name, typ, qty, lot=None, gross=None, manual=None, start=1, build=4, capture=100):
    return {"Active":active, "Name":name, "Type":typ, "Qty":qty, "Lot size (ac)":lot,
            "Gross-up %":gross, "Manual Acres":manual, "Start":start, "Buildout":build, "Capture %":capture}

PRESETS = {
    "ESD baseline — retail + homes": [
        _row(True,  "10-acre big-box / anchor retail", "Big-Box / Anchor Retail", 10),
        _row(True,  "100-home single-family subdivision", "Single-Family Subdivision", 100, lot=0.125, gross=50, build=5),
        _row(False, "250-unit multifamily apartments", "Multifamily Apartments", 250, start=2, build=3),
        _row(False, "40-acre logistics", "Industrial / Logistics", 40, start=2, build=4),
    ],
    "Residential push — 300 homes + multifamily": [
        _row(True,  "300-home single-family subdivision", "Single-Family Subdivision", 300, lot=0.125, gross=50, build=6),
        _row(True,  "60 townhomes", "Townhome / Condo", 60, start=2, build=3),
        _row(True,  "250-unit multifamily apartments", "Multifamily Apartments", 250, start=2, build=3),
        _row(False, "10-acre big-box / anchor retail", "Big-Box / Anchor Retail", 10),
    ],
    "Industrial corridor — logistics + manufacturing": [
        _row(True,  "40-acre logistics", "Industrial / Logistics", 40, build=3),
        _row(True,  "25-acre manufacturing", "Manufacturing", 25, start=2, build=4),
        _row(True,  "10-acre big-box / anchor retail", "Big-Box / Anchor Retail", 10, start=2),
        _row(False, "100-home single-family subdivision", "Single-Family Subdivision", 100, lot=0.125, gross=50, build=5),
    ],
}

st.subheader("Scenario projects")
st.caption("Pick a preset or edit the table. Check **Active** to include a project. The type sets the unit "
           "(lots / units / acres / sqft / rooms). For subdivisions, set **Lot size** and a **Gross-up %** "
           "(extra land for streets / detention / open space — Sealy newer subdivisions ≈ 50%).")

pc1, pc2 = st.columns([2.6, 5.4])
with pc1:
    preset_name = st.selectbox("Quick presets", list(PRESETS), label_visibility="collapsed")
with pc2:
    if st.button("Load preset"):
        st.session_state["fm_df"] = pd.DataFrame(PRESETS[preset_name])
        st.session_state["fm_ver"] = st.session_state.get("fm_ver", 0) + 1
        st.rerun()

base_df = st.session_state.get("fm_df", pd.DataFrame(PRESETS["ESD baseline — retail + homes"]))
edited = st.data_editor(base_df, num_rows="dynamic", use_container_width=True,
    key=f"scn{st.session_state.get('fm_ver', 0)}",
    column_config={
        "Active": st.column_config.CheckboxColumn(),
        "Type": st.column_config.SelectboxColumn(options=TYPES, width="large"),
        "Lot size (ac)": st.column_config.NumberColumn(help="Residential only — acres per lot/unit", format="%.3f"),
        "Gross-up %": st.column_config.NumberColumn(min_value=0, max_value=200, help="Residential only — non-lot land (streets/detention/open space)"),
        "Capture %": st.column_config.NumberColumn(min_value=0, max_value=100),
    })


def parse_scenarios(df):
    out = []
    for _, row in df.iterrows():
        if pd.isna(row.get("Type")) or pd.isna(row.get("Qty")):
            continue
        def num(v):
            return None if pd.isna(v) else float(v)
        out.append(dict(
            name=row["Name"], active=bool(row["Active"]), type=row["Type"], qty=float(row["Qty"]),
            lot=num(row.get("Lot size (ac)")),
            grossup=(None if pd.isna(row.get("Gross-up %")) else float(row["Gross-up %"])/100),
            manual_acres=num(row.get("Manual Acres")),
            start=int(row["Start"]), buildout=int(row["Buildout"]), capture=float(row["Capture %"])/100))
    return out


@st.cache_data(show_spinner=False, max_entries=24)
def cached_compute(inputs, scenarios, exemptions):
    return backend.compute(inputs, scenarios, exemptions)


run_clicked = st.button("▶  Calculate fiscal impact", type="primary")
first_visit = "fm_result" not in st.session_state
if run_clicked or first_visit:
    scenarios = parse_scenarios(edited)
    msg = "Recalculating the model…" if run_clicked else "Running the baseline scenario for you…"
    with st.spinner(msg):
        r = cached_compute(inputs, scenarios, exemptions)
    st.session_state["fm_result"] = r
    st.session_state["fm_ctx"] = {"share": city_share, "edc": edc}

r = st.session_state["fm_result"]
ctx = st.session_state["fm_ctx"]
if not run_clicked:
    st.caption("Showing the **last calculated** results — press *Calculate fiscal impact* after changing inputs.")


def g(key, h=4):  # h: 0=5y,1=10y,2=15y,3=20y,4=30y
    return (r.get(key) or [0,0,0,0,0])[h] or 0


st.subheader("Results — 30-year net fiscal position")
c1,c2,c3 = st.columns(3)
c1.metric("City NET", f"${g('city_net'):,.0f}")
c2.metric("ESD #2 NET", f"${g('esd_net'):,.0f}")
c3.metric("Combined NET", f"${g('comb_net'):,.0f}")

# ---- Negotiation lever: NET vs City share of the pool (derived from one engine run —
#      the sales-tax line is linear in the split, everything else is unchanged) ----
pool30, cst30, est30 = g("pool"), g("city_salestax"), g("esd_salestax")
if pool30:
    e0 = ctx["edc"]; s0 = ctx["share"]
    shares = list(range(0, 101, 5))
    city_line = [g("city_net") - cst30 + pool30*(s/100)*(1-e0) for s in shares]
    esd_line  = [g("esd_net")  - est30 + pool30*(1 - s/100)    for s in shares]
    st.markdown("**The negotiation lever — 30-yr NET at every City / ESD split**")
    sens = pd.DataFrame({"City NET": city_line, "ESD #2 NET": esd_line},
                        index=pd.Index(shares, name="City share of pool (%)"))
    st.line_chart(sens)
    notes = [f"Currently set at **{s0*100:.0f}% City / {100-s0*100:.0f}% ESD**."]
    denom = pool30*(1-e0)
    if denom > 0:
        sb = (cst30 - g("city_net")) / denom * 100
        if 0 <= sb <= 100:
            notes.append(f"City 30-yr NET breaks even at ≈ **{sb:.0f}%** City share.")
    if pool30 > 0:
        se = (1 - (est30 - g("esd_net")) / pool30) * 100
        if 0 <= se <= 100:
            notes.append(f"ESD #2 30-yr NET breaks even at ≈ **{se:.0f}%** City share.")
    st.caption(" ".join(notes))

horizons = ["5-yr","10-yr","15-yr","20-yr","30-yr"]
label_key = [
    ("1.5% sales-tax pool","pool"),
    ("→ City General Fund (net of EDC)","city_salestax"),
    ("→ Sealy EDC (carve-out)","edc"),
    ("→ ESD #2 share","esd_salestax"),
    ("City property tax","city_pt"),
    ("ESD #2 property tax","esd_pt"),
    ("Impact fees (one-time)","impact"),
    ("City operating cost","city_opex"),
    ("ESD operating cost","esd_opex"),
    ("City capital / debt service","city_capital"),
    ("ESD capital / debt service","esd_capital"),
    ("City NET","city_net"),
    ("ESD #2 NET","esd_net"),
    ("Combined NET","comb_net"),
]
tbl = pd.DataFrame({lbl: r.get(key,[None]*5) for lbl,key in label_key}, index=horizons).T
st.dataframe(tbl.style.format("${:,.0f}", na_rep="—"), use_container_width=True)

d1, d2, _sp = st.columns([1.6, 1.6, 4.8])
with d1:
    st.download_button("⬇ Results (CSV)", tbl.to_csv().encode("utf-8"),
                       "sealy_esd2_fiscal_results.csv", "text/csv")
with d2:
    xbuf = io.BytesIO()
    tbl.to_excel(xbuf, sheet_name="Results")
    st.download_button("⬇ Results (Excel)", xbuf.getvalue(), "sealy_esd2_fiscal_results.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.markdown("**Does the sales-tax split move the needle?**")
city_excl = [(r.get("city_net") or [0]*5)[i] - (r.get("city_salestax") or [0]*5)[i] for i in range(5)]
iso = pd.DataFrame({
    "City NET excl. sales tax":   city_excl,
    "+ City sales-tax share":     r.get("city_salestax",[None]*5),
    "= City NET incl. sales tax": r.get("city_net",[None]*5),
}, index=horizons).T
st.dataframe(iso.style.format("${:,.0f}", na_rep="—"), use_container_width=True)

st.markdown("**Net fiscal position by horizon**")
chart = pd.DataFrame({"City NET": r.get("city_net",[0]*5), "ESD NET": r.get("esd_net",[0]*5)}, index=horizons)
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
           "warehouse/manufacturing ≈ $0 local sales tax). Residential capital is sized off gross "
           "subdivision acres (lot size × gross-up); value & tax stay per-home.")

_brand.footer()

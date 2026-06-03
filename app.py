"""
Sealy / Austin County — Fiscal & Land-Use Analysis  (landing hub)
Independent analysis by Councilmember Bobby Necker, Place 1.
Premium "Modern Civic" landing: full-bleed hero, tool cards, trust strip, footer.
Tool navigation uses st.page_link so the password-gate session carries across pages.
"""
import streamlit as st
import _brand

st.set_page_config(page_title="Sealy — Necker Analysis", page_icon="🏛️",
                   layout="wide", initial_sidebar_state="collapsed")
_brand.hide_chrome()

st.markdown("""
<style>
[data-testid="stHeader"] {display:none;}
.stApp {background:#F3F5F6;}
.block-container {padding:0 !important; max-width:100% !important;}
.st-key-toolkit {padding:4px 48px 22px;}
.st-key-card_fm, .st-key-card_map, .st-key-card_lu {
  background:#fff; border:1px solid #E4E7E9; border-radius:14px; padding:20px 20px 12px;}
[data-testid="stPageLink"] a {color:#1F6F6B !important; font-weight:600;}
[data-testid="stPageLink"] a:hover {color:#14181C !important;}
@media (max-width: 740px) {.st-key-toolkit {padding:4px 20px 18px;}}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background:#fff;border-bottom:1px solid #E4E7E9;padding:15px 48px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;">
  <div style="display:flex;gap:12px;align-items:center;">
    <div style="width:34px;height:34px;border-radius:9px;background:#14181C;display:flex;align-items:center;justify-content:center;">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2FA897" stroke-width="2" stroke-linecap="round"><path d="M3 21h18M5 21V7l7-4 7 4v14M9 9h1m4 0h1M9 13h1m4 0h1M9 17h1m4 0h1"/></svg>
    </div>
    <div>
      <div style="font-weight:700;font-size:15px;color:#1F2428;letter-spacing:.03em;">SEALY / AUSTIN COUNTY</div>
      <div style="font-size:11.5px;color:#7A828A;margin-top:-2px;">fiscal &amp; land-use analysis</div>
    </div>
  </div>
  <div style="font-size:12px;color:#5C636B;border:1px solid #CFD4D8;border-radius:20px;padding:6px 14px;">Councilmember analysis — not an official City site</div>
</div>

<div style="background:#14181C;color:#EAEDEF;padding:50px 48px 42px;">
  <span style="display:inline-block;font-size:11.5px;letter-spacing:.08em;color:#2FA897;border:1px solid #2c4a45;border-radius:20px;padding:5px 14px;margin-bottom:20px;">INDEPENDENT ANALYSIS · COUNCILMEMBER BOBBY NECKER, PLACE 1</span>
  <div style="font-size:clamp(28px,4.5vw,40px);line-height:1.15;font-weight:650;max-width:640px;letter-spacing:-.01em;">Know what growth really costs — before the vote.</div>
  <p style="font-size:16px;line-height:1.65;color:#A9B1B8;max-width:580px;margin:18px 0 0;">Model the ESD #2 sales-tax agreement, annexation, and land use on one transparent engine. Every number is computed by the fiscal-model workbook itself — public data in, defensible numbers out.</p>
  <div style="display:flex;gap:38px;margin-top:32px;padding-top:24px;border-top:1px solid #262C31;flex-wrap:wrap;">
    <div><div style="font-size:22px;font-weight:650;color:#fff;">$98.6M</div><div style="font-size:12.5px;color:#828A91;">30-yr sales-tax pool modeled</div></div>
    <div><div style="font-size:22px;font-weight:650;color:#fff;">5,463</div><div style="font-size:12.5px;color:#828A91;">parcels mapped — city + ETJ</div></div>
    <div><div style="font-size:22px;font-weight:650;color:#fff;">22</div><div style="font-size:12.5px;color:#828A91;">land-use types, per-acre</div></div>
  </div>
</div>
""", unsafe_allow_html=True)

ICON_BOX = ('<div style="width:40px;height:40px;border-radius:10px;background:#E7F3F0;'
            'display:flex;align-items:center;justify-content:center;margin-bottom:12px;">{svg}</div>')
TITLE = '<div style="font-size:16px;font-weight:650;color:#1F2428;margin-bottom:6px;">{t}</div>'
DESC = '<p style="font-size:13px;line-height:1.6;color:#5C636B;margin:0;">{d}</p>'

SVG_CALC = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1F6F6B" stroke-width="2" stroke-linecap="round">'
            '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 7h8M8 12h.01M12 12h.01M16 12h.01M8 16h.01M12 16h.01M16 16h.01"/></svg>')
SVG_MAP = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1F6F6B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
           '<path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2-6-2zM9 4v14M15 6v14"/></svg>')
SVG_CITY = ('<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1F6F6B" stroke-width="2" stroke-linecap="round">'
            '<path d="M3 21h18M5 21V8l5-3v16M14 21V11l5 3v7M8 9h.01M8 13h.01M8 17h.01"/></svg>')

with st.container(key="toolkit"):
    st.markdown('<div style="font-size:12px;letter-spacing:.07em;color:#8A9097;margin:16px 0 12px;">THE TOOLKIT</div>',
                unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3, gap="medium")
    with c1, st.container(key="card_fm"):
        st.markdown(ICON_BOX.format(svg=SVG_CALC)
                    + TITLE.format(t="Fiscal impact model")
                    + DESC.format(d="Scenario builder for the 1.5% sales-tax pool, the City / ESD split, "
                                    "property tax, impact fees, capital, and the 30-year net."),
                    unsafe_allow_html=True)
        st.page_link("pages/0_Fiscal_Model.py", label="Open the model →")
    with c2, st.container(key="card_map"):
        st.markdown(ICON_BOX.format(svg=SVG_MAP)
                    + TITLE.format(t="Developable land map")
                    + DESC.format(d="City + ETJ parcels by development tier and proposed zoning, "
                                    "with the ESD #2 revenue potential of each."),
                    unsafe_allow_html=True)
        st.page_link("pages/1_GIS_Map.py", label="Open the map →")
    with c3, st.container(key="card_lu"):
        st.markdown(ICON_BOX.format(svg=SVG_CITY)
                    + TITLE.format(t="Land use & zoning")
                    + DESC.format(d="Existing use, the adopted Future Land Use, and a rebalanced scenario — "
                                    "over aerial, FEMA flood, pipelines, and jurisdictions."),
                    unsafe_allow_html=True)
        st.page_link("pages/2_Land_Use_and_Zoning_Map.py", label="Open the map →")

st.markdown("""
<div style="background:#fff;border-top:1px solid #E8EAEC;border-bottom:1px solid #E8EAEC;padding:22px 48px;display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:16px;">
  <div style="display:flex;gap:9px;align-items:flex-start;"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#1F6F6B" stroke-width="2.4" stroke-linecap="round" style="margin-top:1px;"><path d="M5 13l4 4L19 7"/></svg><div style="font-size:12.5px;color:#43494F;line-height:1.5;">Built on <b>public data</b> — Comptroller, Austin CAD, Census</div></div>
  <div style="display:flex;gap:9px;align-items:flex-start;"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#1F6F6B" stroke-width="2.4" stroke-linecap="round" style="margin-top:1px;"><path d="M5 13l4 4L19 7"/></svg><div style="font-size:12.5px;color:#43494F;line-height:1.5;"><b>Peer-validated</b> methodology, documented sources</div></div>
  <div style="display:flex;gap:9px;align-items:flex-start;"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#1F6F6B" stroke-width="2.4" stroke-linecap="round" style="margin-top:1px;"><path d="M5 13l4 4L19 7"/></svg><div style="font-size:12.5px;color:#43494F;line-height:1.5;">Every input <b>transparent and adjustable</b></div></div>
  <div style="display:flex;gap:9px;align-items:flex-start;"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#1F6F6B" stroke-width="2.4" stroke-linecap="round" style="margin-top:1px;"><path d="M5 13l4 4L19 7"/></svg><div style="font-size:12.5px;color:#43494F;line-height:1.5;">City / ESD split <b>blank by design</b> — you set it</div></div>
</div>

""", unsafe_allow_html=True)

_brand.footer()

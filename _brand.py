"""Shared branding, theme, password gate, page header + footer for the Necker analysis app.
Set env var SITE_PASSWORD on the host to require the shared password; unset/empty = open site."""
import hmac
import os

import streamlit as st

DISCLAIMER = ("⚖️ **Independent analysis by Councilmember Bobby Necker, Place 1.** "
              "Not an official City of Sealy website. Planning-level estimates from public data.")


def disclaimer():
    st.caption(DISCLAIMER)


_MARK = ('<div style="width:{s}px;height:{s}px;border-radius:9px;background:#14181C;display:flex;'
         'align-items:center;justify-content:center;flex:none;">'
         '<svg width="{i}" height="{i}" viewBox="0 0 24 24" fill="none" stroke="#2FA897" stroke-width="2" stroke-linecap="round">'
         '<path d="M3 21h18M5 21V7l7-4 7 4v14M9 9h1m4 0h1M9 13h1m4 0h1M9 17h1m4 0h1"/></svg></div>')

_SVG_LOCK = ('<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#1F6F6B" stroke-width="2" stroke-linecap="round">'
             '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>')
_SVG_SHIELD = ('<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#1F6F6B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
               '<path d="M12 3l8 4v5c0 5-3.4 8.2-8 9-4.6-.8-8-4-8-9V7z"/><path d="M9 12l2 2 4-4"/></svg>')
_SVG_KEY = ('<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#1F6F6B" stroke-width="2" stroke-linecap="round">'
            '<circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M17 4l3 3M14 7l2 2"/></svg>')
_SVG_DATA = ('<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#1F6F6B" stroke-width="2" stroke-linecap="round">'
             '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v6c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 11v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/></svg>')


def _badge(svg, text):
    return ('<span style="display:inline-flex;align-items:center;gap:7px;font-size:12px;color:#43494F;">'
            + svg + "<span>" + text + "</span></span>")


SECURITY_BADGES = ('<div style="display:flex;gap:14px 22px;flex-wrap:wrap;align-items:center;">'
                   + _badge(_SVG_LOCK, "TLS-encrypted (HTTPS)")
                   + _badge(_SVG_SHIELD, "Hosted on Microsoft Azure")
                   + _badge(_SVG_KEY, "Password-protected access")
                   + _badge(_SVG_DATA, "Public data only — nothing personal collected")
                   + "</div>")

_THEME = """
<style>
#MainMenu, footer, [data-testid='stToolbar'] {visibility:hidden;}
html, body, p, div, span, label, input, textarea, button, h1, h2, h3, h4 {
  font-family:"Segoe UI", system-ui, -apple-system, "Helvetica Neue", sans-serif;}
h1, h2, h3 {color:#1F2428; letter-spacing:-.01em;}
[data-testid="stMetric"] {background:#fff; border:1px solid #E4E7E9; border-radius:12px;
  padding:14px 18px; box-shadow:0 1px 2px rgba(20,24,28,.05);}
[data-testid="stMetricLabel"] p {color:#5C636B;}
[data-testid="stSidebar"] {background:#FBFCFC; border-right:1px solid #E8EAEC;}
[data-testid="stExpander"] {background:#fff; border:1px solid #E8EAEC; border-radius:10px;}
.stButton button, .stFormSubmitButton button {border-radius:9px; font-weight:600;}
[data-testid="stDataFrame"] {border:1px solid #E4E7E9; border-radius:10px;}
[data-testid="stPageLink"] p {font-size:13.5px; font-weight:600;}
.st-key-topnav {background:#fff; border:1px solid #E4E7E9; border-radius:12px; padding:2px 12px; margin-bottom:6px;}
</style>"""


def _password_gate():
    """One shared password (env var SITE_PASSWORD), no accounts. Session-scoped."""
    required = os.environ.get("SITE_PASSWORD", "").strip()
    if not required or st.session_state.get("_site_authed"):
        return
    st.markdown(_THEME + """
<style>
[data-testid="stSidebar"], [data-testid="stHeader"] {display:none;}
.stApp {background:#F3F5F6;}
.st-key-gate_card {background:#fff; border:1px solid #E4E7E9; border-radius:16px;
  padding:28px 28px 18px; box-shadow:0 10px 30px rgba(20,24,28,.07); margin-top:7vh;}
</style>""", unsafe_allow_html=True)
    left, mid, right = st.columns([1, 1.25, 1])
    with mid, st.container(key="gate_card"):
        st.markdown(
            _MARK.format(s=40, i=22)
            + '<div style="font-size:19px;font-weight:700;color:#1F2428;margin:12px 0 2px;letter-spacing:.02em;">SEALY / AUSTIN COUNTY</div>'
            + '<div style="font-size:13px;color:#5C636B;margin-bottom:4px;">Fiscal &amp; land-use analysis · '
              'Councilmember Bobby Necker, Place 1</div>',
            unsafe_allow_html=True)
        with st.form("site_gate"):
            pw = st.text_input("Site password", type="password",
                               help="Provided by Councilmember Necker.")
            ok = st.form_submit_button("Enter the site", type="primary", use_container_width=True)
        if ok:
            if hmac.compare_digest(pw, required):
                st.session_state["_site_authed"] = True
                st.rerun()
            st.error("That's not it — check the password and try again.")
        st.markdown('<div style="border-top:1px solid #EEF1F2;padding-top:13px;margin-top:2px;">'
                    + SECURITY_BADGES + "</div>", unsafe_allow_html=True)
    st.stop()


def hide_chrome():
    """Gate (if enabled) + global Modern Civic theme. Call once at the top of every page."""
    _password_gate()
    st.markdown(_THEME, unsafe_allow_html=True)


def top_nav():
    """Site navigation row — on every page; st.page_link keeps the password session alive."""
    with st.container(key="topnav"):
        cols = st.columns([0.8, 1.2, 1.5, 1.7, 1.0, 3.8])
        with cols[0]:
            st.page_link("app.py", label="Home")
        with cols[1]:
            st.page_link("pages/0_Fiscal_Model.py", label="Fiscal model")
        with cols[2]:
            st.page_link("pages/1_GIS_Map.py", label="Developable land")
        with cols[3]:
            st.page_link("pages/2_Land_Use_and_Zoning_Map.py", label="Land use & zoning")
        with cols[4]:
            st.page_link("pages/3_Sources_and_Methodology.py", label="Sources")


def page_header(title, sub=""):
    """Slim ink identity band — use instead of st.title on inner pages."""
    sub_html = ('<div style="font-size:13px;color:#A9B1B8;margin-top:4px;max-width:780px;line-height:1.55;">'
                + sub + "</div>") if sub else ""
    st.markdown(
        '<div style="background:#14181C;border-radius:14px;padding:20px 26px;margin:6px 0 16px;'
        'display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">'
        '<div style="display:flex;align-items:flex-start;gap:14px;">' + _MARK.format(s=38, i=20)
        + '<div><div style="font-size:11px;letter-spacing:.07em;color:#2FA897;">SEALY / AUSTIN COUNTY · INDEPENDENT ANALYSIS</div>'
        + '<div style="font-size:clamp(20px,2.6vw,27px);font-weight:650;color:#fff;line-height:1.25;">' + title + "</div>"
        + sub_html + "</div></div>"
        '<div style="font-size:11.5px;color:#828A91;border:1px solid #2A3137;border-radius:18px;padding:5px 12px;">'
        "Councilmember Necker · Place 1</div></div>",
        unsafe_allow_html=True)


def footer():
    """Security-badge strip + disclaimer bar. Call as the last element of every page."""
    st.markdown(
        '<div style="margin-top:30px;">'
        '<div style="background:#FAFBFB;border:1px solid #E8EAEC;border-bottom:none;padding:13px 26px;">'
        + SECURITY_BADGES + "</div>"
        '<div style="background:#14181C;color:#7E868D;padding:16px 26px;font-size:11.5px;line-height:1.55;'
        'display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;">'
        "<div>Independent analysis by Councilmember Bobby Necker, Place 1 — not an official City of Sealy "
        "website. Planning-level estimates from public data; not legal, financial, or official City advice.</div>"
        '<div style="color:#9AA1A8;">Model &amp; parcel data updated 2026-06-02 · © 2026 Bobby Necker · neckerstx.com</div>'
        "</div></div>", unsafe_allow_html=True)

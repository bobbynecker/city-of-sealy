"""Shared branding + legal disclaimer for the Necker analysis app (TOMA/TPIA posture).
Also holds the optional shared-password gate: set env var SITE_PASSWORD on the host
to require it; leave SITE_PASSWORD unset/empty for a fully open site."""
import hmac
import os

import streamlit as st

DISCLAIMER = ("⚖️ **Independent analysis by Councilmember Bobby Necker, Place 1.** "
              "Not an official City of Sealy website. Planning-level estimates from public data.")


def disclaimer():
    st.caption(DISCLAIMER)


def _password_gate():
    """One shared password (chosen by Bobby), no accounts. Skipped when SITE_PASSWORD is unset."""
    required = os.environ.get("SITE_PASSWORD", "").strip()
    if not required:
        return
    if st.session_state.get("_site_authed"):
        return

    st.markdown("## Sealy / Austin County — Fiscal & Land-Use Analysis")
    st.caption(DISCLAIMER)
    with st.form("site_gate"):
        pw = st.text_input("Site password", type="password",
                           help="Provided by Councilmember Necker.")
        ok = st.form_submit_button("Enter")
    if ok:
        if hmac.compare_digest(pw, required):
            st.session_state["_site_authed"] = True
            st.rerun()
        st.error("That's not it — check the password and try again.")
    st.stop()


def hide_chrome():
    _password_gate()
    st.markdown("<style>#MainMenu{visibility:hidden} footer{visibility:hidden} "
                "[data-testid='stToolbar']{visibility:hidden}</style>", unsafe_allow_html=True)

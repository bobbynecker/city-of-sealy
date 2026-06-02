"""Shared branding + legal disclaimer for the Necker analysis app (TOMA/TPIA posture)."""
import streamlit as st
DISCLAIMER = ("⚖️ **Independent analysis by Councilmember Bobby Necker, Place 1.** "
              "Not an official City of Sealy website. Planning-level estimates from public data.")
def disclaimer():
    st.caption(DISCLAIMER)
def hide_chrome():
    st.markdown("<style>#MainMenu{visibility:hidden} footer{visibility:hidden} "
                "[data-testid='stToolbar']{visibility:hidden}</style>", unsafe_allow_html=True)

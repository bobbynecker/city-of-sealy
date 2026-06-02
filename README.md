# Sealy / ESD #2 Fiscal Model — Web App

A browser front-end for the ESD #2 fiscal model. You set the assumptions and projects in a
clean web UI; the app writes them into the audited **v7 Excel workbook**, recalculates it, and
shows the results — so **the web numbers always match the Excel exactly**. No re-implementation,
no divergence: the Excel stays the single source of truth.

The **city app** is two pages: **Fiscal Model** (`app.py`) and **GIS Map** (`pages/1_GIS_Map.py`). Streamlit shows both in the sidebar automatically.

## Files
| File | Purpose |
|---|---|
| `app.py` | City app, page 1 — fiscal model UI (assumptions, scenario table, results + charts). |
| `pages/1_GIS_Map.py` | City app, page 2 — interactive map of City+ETJ developable parcels (colored by dev tier). |
| `gis_data/` | GeoJSON layers (City Limits, 2019 ETJ, developable parcels) from `06_GIS/Developable_Land_Model_2026-05`. |
| `esd_backend.py` | Writes inputs into the Excel, recalculates with LibreOffice, reads RESULTS back. |
| `engine.xlsx` | The calculation engine = a copy of the v7 model. **Update this file to update the app.** |
| `requirements.txt` | Python packages (Streamlit, openpyxl, pandas, folium, streamlit-folium). |
| `packages.txt` | System package (LibreOffice) for Streamlit Community Cloud. |
| `Dockerfile` | Container for professional hosting (Azure / Render / Cloud Run). |
| `DEPLOY_AND_SECURITY.md` | **Step-by-step Azure deploy + how to lock down the city app** (login, MFA, IP allowlist). |
| `_Railroad_Starter_RELOCATE/` | Starter for the second (railroad ROM) app — move to your railroad repo before deploying. |

## Run it on your computer (quick test)
1. Install Python 3.11+ and LibreOffice (the app needs `soffice` for recalculation).
2. In a terminal, from this folder:
   ```
   pip install -r requirements.txt
   streamlit run app.py
   ```
3. It opens in your browser at `http://localhost:8501`.

## Put it online (pick one)
All of these give a real URL you can share. Since cost isn't the constraint, option B or C looks the most professional (custom domain + password).

**A. Streamlit Community Cloud — fastest, free.** Push this folder to a GitHub repo, then at share.streamlit.io point it at `app.py`. The included `packages.txt` installs LibreOffice automatically. Good for a quick, shareable link; URL looks like `yourapp.streamlit.app`.

**B. Render or Railway — professional, custom domain.** Create a new "Web Service" from the GitHub repo; it auto-detects the `Dockerfile`. Add your own domain (e.g., `models.yourfirm.com`) and turn on password protection / basic auth. ~$7–25/mo. Best balance of polish and simplicity.

**C. Microsoft Azure App Service or Google Cloud Run — enterprise.** Deploy the same `Dockerfile`. Supports custom domains, SSO/Single-Sign-On, and access controls if you want to gate it to specific clients. Most "corporate," a bit more setup.

## About Clinked (your question)
**Clinked is a client portal — for sharing files and branded workspaces with clients — not an app host.** It can't *run* an interactive web app like this. The right pattern: deploy the app to one of the hosts above (B or C for a professional look), then **link to it from your Clinked portal** (a button/tile: "Open the Fiscal Model"). Clients click through from Clinked into the live tool. So Clinked stays your front door; the app lives on a real app host.

## Roadmap — turning this into a reusable platform
This same pattern (clean web UI → Excel engine → results) generalizes well to the other tools you mentioned:
- **Railroad ROM budget estimator** — a second page/module with your unit costs; same Excel-as-engine approach so your estimating workbook stays the source of truth.
- **Schedules / Microsoft Project** — the app can build and show Gantt-style schedules natively. Note: native `.mpp` files are proprietary; the clean integration is via MS Project's **XML export/import** (or building the schedule in the app and exporting to that format). Full read/write of `.mpp` is limited but workable.
- **GIS map** — Streamlit has strong map support (`st.map`, pydeck, or Folium). We can add a "Map" tab that renders the City + ETJ parcels / developable-land layers you already exported, and even tie a clicked parcel to a scenario. Easy to add as a second tab here or stand it up as its own module.

Multi-tool structure: make this a multi-page app (a `pages/` folder) — one page per tool (Fiscal Model, ROM Estimator, Schedule, Map) — all behind one branded site and one login.

---
*Engine: audited v7 workbook (`engine.xlsx`). Split-neutral; planning-level. Update the workbook to update the app's math.*

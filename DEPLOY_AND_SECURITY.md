# Deploy & Secure — Azure App Service (city + railroad, one account, separate domains)

This sets up **both** apps under **one Azure subscription**, each on its **own web address**, with the **city app locked down**. The included `Dockerfile` bundles LibreOffice so the Excel engine recalculates on the server.

## What you'll end up with
| App | Code | Example domain | Security |
|---|---|---|---|
| City fiscal model + GIS map | this `Web_App/` folder | `sealy-model.yourfirm.com` | Entra ID login **required** + MFA + (optional) IP allowlist |
| Railroad ROM / schedule tools | a separate repo (see `_Railroad_Starter`) | `tools.yourfirm.com` | per-client logins |

Both bill to one Azure account; you manage them from one portal.

## One-time prerequisites
1. A **GitHub** account (free) — push each app's folder to its own repo.
2. An **Azure** subscription (your Microsoft account; pay-as-you-go).
3. Your **domain name** (e.g., from your registrar) — you'll point subdomains at the apps.

## Deploy the city app (repeat for railroad with its own repo + domain)
1. Push the `Web_App/` folder to a GitHub repo (include `app.py`, `pages/`, `esd_backend.py`, `engine.xlsx`, `gis_data/`, `requirements.txt`, `Dockerfile`).
2. In the **Azure Portal** → **Create a resource → Web App**:
   - Publish: **Container**; Operating System: **Linux**.
   - Create a new **App Service Plan** (pick **B1/B2 Basic** to start; scale up later — it can host multiple apps).
   - Deployment: connect the **GitHub** repo; Azure builds the `Dockerfile` automatically (GitHub Actions).
3. After it builds, the app is live at `https://<name>.azurewebsites.net`.

## Custom domain + free SSL
- Web App → **Custom domains → Add** → enter `sealy-model.yourfirm.com`, add the CNAME it shows at your registrar, validate.
- **Create App Service Managed Certificate** (free) and **bind** it → HTTPS works automatically.
- Web App → **Configuration → General settings → HTTPS Only = On**, **Minimum TLS = 1.2**.

## Lock down the city app (high security)
1. **Require login (no anonymous access).** Web App → **Authentication → Add identity provider → Microsoft (Entra ID)**. Set **"Restrict access = Require authentication"** and **"Unauthenticated requests = Return HTTP 302 (log in)"**. Now nobody loads the page without signing in.
2. **Limit to specific people.** In Entra → the app registration → **Enterprise application → Properties → "Assignment required = Yes"**, then **Users and groups →** add only the councilmembers/staff you authorize. Everyone else is denied even with a Microsoft account.
3. **MFA.** Entra → **Security → Conditional Access →** new policy targeting this app → **Grant = Require multi-factor authentication**. (Microsoft is also moving to MFA-by-default.)
4. **IP allowlist (optional, stronger).** Web App → **Networking → Access restrictions →** allow only city hall / your office IP ranges; deny all else.
5. **Full privacy (optional, maximum).** Add a **Private Endpoint** so the app is reachable only on a private network — not the public internet at all.
6. **WAF/DDoS (optional).** Front the app with **Azure Front Door** + **WAF** for attack filtering and a global edge.

> For the **railroad** apps, do the same Authentication step but invite **each client** (or use a B2B guest / per-client group), so each client only sees their own tool.

## Link it from Clinked
Clinked is your client **portal** (file sharing), not an app host. After deploy, add a tile/link in Clinked — e.g., "Open the Fiscal Model" → `https://sealy-model.yourfirm.com`. Clients click through from Clinked into the secured app.

## Updating the model later
The app's math = `engine.xlsx`. To update assumptions/coefficients, edit that workbook (or drop in a newer model version renamed to `engine.xlsx`), commit to GitHub → Azure redeploys automatically. No app-code changes needed.

## Cost (ballpark, 2026)
A Basic (B1) App Service plan is roughly $13–55/mo per plan; one plan can host both apps. Custom domains + managed SSL are free. MFA/Conditional Access requires Entra ID P1 (~$6/user/mo) — only for the accounts you protect. Negligible for this scale.

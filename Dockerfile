# Professional hosting image (Render / Railway / Google Cloud Run / Azure App Service).
# Bundles LibreOffice so the Excel engine can recalculate on the server.
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        libreoffice-calc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENV SOFFICE=soffice
EXPOSE 8501
# $PORT is provided by most hosts; default to 8501 locally.
CMD streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0

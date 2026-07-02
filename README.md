# POS DATA CLEANING, MARKET BASKET ANALYSIS & BRAND AFFINITY PLATFORM

This repository contains an end-to-end data pipeline for cleaning beauty supply POS data, generating copurchase and brand-affinity analytics, enriching results with Revlon metadata, and serving insights through a Streamlit + DuckDB application.

---

## OVERVIEW

This project supports:

- Cleaning raw POS transaction files
- Combining cleaned datasets across time
- Detecting newly introduced UPCs
- Market Basket Analysis (MBA)
- UPC-level copurchase analytics
- Brand-level affinity analytics
- Revlon metadata enrichment
- Interactive analytics via Streamlit + DuckDB
- Cloud storage and retrieval via Google Cloud Storage (GCS)

---

## SYSTEM REQUIREMENTS

- Python 3.10 or later
- macOS, Linux, or Windows
- Git
- Google Cloud Platform account with access to GCS

---

## RUN FROM SCRATCH (STEP-BY-STEP)

### 1. Clone or unzip the project

If using Git:

```
git clone <repo-url>
cd pos-data-cleaning-automation
```

If using a ZIP file:

```
unzip pos-data-cleaning-automation.zip
cd pos-data-cleaning-automation
```

Verify location:

```
ls
```

---

### 2. Create a clean virtual environment

```
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):

```
.venv\Scripts\Activate.ps1
```

Verify Python version:

```
python --version
```

---

### 3. Repair pip and install dependencies

```
python -m ensurepip --upgrade
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

Verify environment:

```
python - <<EOF
import pandas, duckdb, streamlit
print("Environment OK")
EOF
```

---

## GOOGLE CLOUD SETUP

### 4. Service account key

Place the key at:

```
gcp/config/pos-data-key.json
```

---

### 5. Local config file

Create:

```
gcp/config/config.py
```

Contents:

```
GCP_KEY_PATH = "gcp/config/pos-data-key.json"
```

---

## INPUT DATA

Raw POS files:

```
data/raw/
```

Expected filename:

```
POS_Data(YYYY-MM-DD_YYYY-MM-DD).csv
```

Reference file:

```
data/reference/FORANJ.csv
```

Revlon data:

```
data/revlonData/revlon_all_columns_clean.csv
```

---

## RUNNING THE PIPELINE

```
python scripts/file_upload.py
```

Set run mode inside the script:

```
RUN_MODE = "prod"
RUN_MODE = "test"
```

---

## RUNNING STREAMLIT

```
streamlit run scripts/app.py
```

---

## CACHE RESET

```
rm -rf .cache cache
rm -f *.duckdb *.duckdb.wal *.duckdb.tmp *.wal *.wal.corrupt
```

---

## TROUBLESHOOTING

- Missing modules: reinstall requirements
- DuckDB WAL errors: delete .wal files
- GCS errors: verify IAM permissions

---

## NOTES

- GCS is the source of truth
- DuckDB files are disposable cache
- master_cleaned_data.csv is optional

---

## HANDOFF CHECKLIST

- Environment created
- Dependencies installed
- GCP configured
- Pipeline runs
- App launches

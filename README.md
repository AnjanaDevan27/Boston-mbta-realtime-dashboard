# Boston MBTA Real-Time Dashboard

![CI Pipeline](https://github.com/AnjanaDevan27/Boston-mbta-realtime-dashboard/actions/workflows/ci.yaml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11-blue)
![PostgreSQL](https://img.shields.io/badge/postgresql-15-blue)
![AWS](https://img.shields.io/badge/aws-EC2%20%7C%20RDS-orange)
![Streamlit](https://img.shields.io/badge/streamlit-deployed-brightgreen)

A production-grade real-time ETL pipeline that fetches live transit data from the MBTA V3 API every 2 minutes, stores it in PostgreSQL on AWS RDS, and visualizes it in an interactive Streamlit dashboard.

**[Live Dashboard](https://boston-mbta-realtime-dashboard-z2hhv5gwxdiqqsyhxi6rtt.streamlit.app)**

---

## Architecture

```
MBTA V3 API
     ↓
mbta_api_client.py (Extract)
     ↓
mbta_data_transformer.py (Transform)
     ↓
mbta_db_loader.py (Load)
     ↓
PostgreSQL on AWS RDS
     ↓
Streamlit Dashboard (Streamlit Cloud)

Orchestration:  systemd service (every 2 minutes) — Airflow DAG ready
CI/CD:          GitHub Actions (64 tests on every push)
Server:         AWS EC2 t3.micro (us-east-2)
```

---

## Project Structure

```
boston-mbta-realtime-dashboard/
├── dags/
│   └── mbta_realtime_etl_dag.py       # Airflow DAG (Airflow-compatible structure)
├── pipeline/
│   ├── mbta_api_client.py             # MBTA V3 API calls with retry logic
│   ├── mbta_data_transformer.py       # Data cleaning and validation
│   └── mbta_db_loader.py              # PostgreSQL bulk insert
├── config/
│   ├── mbta_pipeline_config.py        # Centralized configuration
│   ├── stop_names.json                # 265 stop names across 7 routes
│   ├── stop_coords.json               # GPS coordinates for 118 stops
│   └── route_shapes.json              # Encoded polylines for route map overlays
├── include/sql/
│   └── mbta_schema.sql                # Database schema and indexes
├── tests/
│   ├── conftest.py                    # Shared fixtures
│   ├── test_mbta_api_client.py        # API client tests (20)
│   ├── test_mbta_data_transformer.py  # Transformer tests (29)
│   └── test_mbta_data_loader.py       # DB loader tests (15)
├── .github/workflows/
│   └── ci.yaml                        # GitHub Actions CI pipeline
├── dashboard.py                       # Streamlit dashboard
├── run_pipeline.py                    # EC2 runner (schedule library)
├── .python-version                    # Python 3.11 pin
├── .env.example                       # Environment variable template
├── .streamlit/secrets.toml.example    # Streamlit Cloud secrets template
├── Makefile                           # Project automation
├── requirements.txt                   # Production dependencies
└── requirements-dev.txt               # Development dependencies
```

---

## Data Pipeline

The pipeline runs every 2 minutes via a systemd service on EC2 and collects three live data streams:

| Data | Endpoint | Records/run |
|------|----------|-------------|
| Predictions | `/predictions` | ~2,200 |
| Vehicle positions | `/vehicles` | ~114 |
| Service alerts | `/alerts` | ~8 |

Each run follows the ETL pattern:
1. **Extract** — fetch from MBTA V3 API with automatic retries and exponential backoff
2. **Transform** — validate coordinates, parse timestamps, strip whitespace, drop malformed records
3. **Load** — bulk insert into PostgreSQL with `ON CONFLICT DO NOTHING`
4. **Log** — record run metadata to `pipeline_runs` audit table

**16+ million predictions ingested to date.**

---

## Dashboard Features

The dashboard connects directly to RDS and queries the last 24 hours of data with a 120-second cache TTL.

**Filters:** Route, direction (inbound/outbound), stop, time of day

**KPI Cards:** Total predictions, active vehicles, active alerts, on-time rate

**Live Vehicle Map:**
- Route lines drawn from decoded polylines
- Vehicle dots color-coded by MBTA official route colors
- White stop markers with hover names
- Zooms to selected stop automatically

**Charts:**
- Predictions by route (horizontal bar)
- Schedule relationship breakdown (donut)
- Peak hour activity by arrival time
- Delay distribution by route (box plot)
- Predictions over time (area chart)
- On-time rate by route
- Direction split by route (stacked bar)
- Busiest stops top 15

**Stop Drill-Down:** Next 5 predicted arrivals when a stop is selected

**Auto-refresh:** Page refreshes every 120 seconds

---

## Database Schema

| Table | Description | Key columns |
|-------|-------------|-------------|
| `predictions` | Real-time arrival/departure predictions | route, stop_id, arrival_time, schedule_relationship |
| `vehicles` | Live GPS positions of all trains | latitude, longitude, current_status, bearing |
| `alerts` | Active service disruptions | effect, cause, severity, affected_routes |
| `pipeline_runs` | Audit log of every ETL run | status, records_inserted, duration_seconds |

All tables include a `fetched_at` timestamp with timezone. Indexed on `route` and `fetched_at`.

---

## Testing

```bash
# Run all tests
make test

# Run with coverage report
make coverage

# Lint
make lint
```

**64 tests across 3 files:**

| File | Tests | Covers |
|------|-------|--------|
| `test_mbta_api_client.py` | 20 | API calls, timeouts, 500 errors, rate limiting, empty responses |
| `test_mbta_data_transformer.py` | 29 | Timestamps, coordinates, strings, edge cases, timezone handling |
| `test_mbta_data_loader.py` | 15 | DB inserts, connection failures, conflict handling, audit logging |

Coverage threshold enforced at 70% in CI.

---

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15
- Free MBTA API key from [api-v3.mbta.com](https://api-v3.mbta.com)

### Setup

```bash
# Clone the repo
git clone https://github.com/AnjanaDevan27/Boston-mbta-realtime-dashboard.git
cd Boston-mbta-realtime-dashboard

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
make setup

# Configure environment
cp .env.example .env
# Edit .env with your MBTA API key and database credentials

# Run tests
make test

# Run pipeline locally
python run_pipeline.py
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `MBTA_API_KEY` | Free API key from api-v3.mbta.com |
| `DB_HOST` | PostgreSQL host (RDS endpoint) |
| `DB_PORT` | PostgreSQL port (default: 5432) |
| `DB_NAME` | Database name |
| `DB_USER` | Database user |
| `DB_PASSWORD` | Database password |

---

## Deployment

### AWS Infrastructure
- **RDS:** PostgreSQL 15 on `db.t3.micro` (us-east-2)
- **EC2:** Ubuntu 22.04 on `t3.micro` (us-east-2)
- Pipeline runs as `mbta-pipeline.service` via systemd

### Streamlit Cloud
Dashboard deployed at Streamlit Cloud using `.python-version` to pin Python 3.11.
Secrets configured via Streamlit Cloud Settings → Secrets.

---

## Roadmap

- [x] Real-time ETL pipeline (Extract, Transform, Load)
- [x] AWS RDS + EC2 deployment
- [x] 64 unit tests with GitHub Actions CI/CD
- [x] Airflow-compatible DAG structure
- [x] Streamlit dashboard deployed on Streamlit Cloud
- [ ] Migrate orchestration from systemd to Airflow on a larger instance
- [ ] Add dbt transform layer
- [ ] CloudWatch monitoring and alerting
- [ ] Partition predictions table by date for query performance

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11 |
| Database | PostgreSQL 15 (AWS RDS) |
| Cloud | AWS EC2 + RDS (us-east-2) |
| Orchestration | systemd (Airflow DAG ready) |
| Dashboard | Streamlit + Plotly |
| Deployment | Streamlit Cloud |
| CI/CD | GitHub Actions |
| Testing | pytest, pytest-cov |
| ORM | SQLAlchemy + psycopg2 |
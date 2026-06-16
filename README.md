# Boston MBTA Real-Time Dashboard

![CI Pipeline](https://github.com/AnjanaDevan27/Boston-mbta-realtime-dashboard/actions/workflows/ci.yaml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11-blue)
![Airflow](https://img.shields.io/badge/airflow-2.9-green)
![PostgreSQL](https://img.shields.io/badge/postgresql-15-blue)
![AWS](https://img.shields.io/badge/aws-EC2%20%7C%20RDS-orange)

A production-grade real-time ETL pipeline that fetches live transit data 
from the MBTA V3 API every 2 minutes and stores it in PostgreSQL on AWS 
for Tableau dashboarding.

## Architecture

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
Tableau Dashboard

Orchestration:  Apache Airflow DAG (every 2 minutes)
CI/CD:          GitHub Actions (64 tests on every push)
Server:         AWS EC2 t2.micro
Monitoring:     pipeline_runs audit table + rotating log files

## Project Structure

```
boston-mbta-realtime-dashboard/
├── dags/
│   └── mbta_realtime_etl_dag.py     # Airflow DAG definition
├── pipeline/
│   ├── mbta_api_client.py           # MBTA V3 API calls with retry logic
│   ├── mbta_data_transformer.py     # Data cleaning and validation
│   └── mbta_db_loader.py            # PostgreSQL bulk insert
├── config/
│   └── mbta_pipeline_config.py      # Centralized configuration
├── include/
│   └── sql/
│       └── mbta_schema.sql          # Database schema and indexes
├── tests/
│   ├── conftest.py                  # Shared fixtures
│   ├── test_mbta_api_client.py      # API client tests
│   ├── test_mbta_data_transformer.py # Transformer tests
│   └── test_mbta_data_loader.py     # DB loader tests
├── .github/workflows/
│   └── ci.yaml                      # GitHub Actions CI pipeline
├── .env.example                     # Environment variable template
├── Makefile                         # Project automation
├── requirements.txt                 # Production dependencies
└── requirements-dev.txt             # Development dependencies
```

## Data Pipeline

The pipeline runs every 2 minutes and collects three data streams:

| Data | Source | Records/run |
|------|--------|-------------|
| Predictions | `/predictions` endpoint | ~2,200 |
| Vehicle positions | `/vehicles` endpoint | ~114 |
| Service alerts | `/alerts` endpoint | ~8 |

Each run follows the ETL pattern:
1. **Extract** — fetch from MBTA V3 API with automatic retries
2. **Transform** — validate, clean, and normalize all fields
3. **Load** — bulk insert into PostgreSQL with transaction safety
4. **Log** — record run metadata to `pipeline_runs` audit table


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

# Test pipeline locally
make run
```


## Database Schema

| Table | Description | Key columns |
|-------|-------------|-------------|
| `predictions` | Real-time arrival/departure predictions | route, stop_id, arrival_time |
| `vehicles` | Live GPS positions of all trains | latitude, longitude, current_status |
| `alerts` | Active service disruptions | effect, cause, severity |
| `pipeline_runs` | Audit log of every ETL run | status, records_inserted, duration |

All tables include a `fetched_at` timestamp with timezone and are indexed 
on `route` and `fetched_at` for fast Tableau queries.



## Testing

```bash
# Run all tests
make test

# Run with coverage report
make coverage
```

**Test suite: 64 tests across 3 files**

| File | Tests | Coverage |
|------|-------|----------|
| `test_mbta_api_client.py` | 20 | API calls, timeouts, 500 errors, rate limiting |
| `test_mbta_data_transformer.py` | 29 | Timestamps, coordinates, strings, edge cases |
| `test_mbta_data_loader.py` | 15 | DB inserts, connection failures, SQL validation |

Tests cover happy paths, failure scenarios, malformed data, and boundary values.



## Deployment

### AWS Infrastructure
- **RDS:** PostgreSQL 15 on `db.t3.micro` (free tier)
- **EC2:** Ubuntu 22.04 on `t2.micro` (free tier)
- **Region:** us-east-2 (Ohio)

### Deploy to EC2

```bash
make deploy
```

This SSHes into EC2, pulls latest code, and restarts the pipeline service.

### Environment Variables

| Variable | Description |
|----------|-------------|
| `MBTA_API_KEY` | Free API key from api-v3.mbta.com |
| `DB_HOST` | RDS endpoint |
| `DB_PORT` | PostgreSQL port (default: 5432) |
| `DB_NAME` | Database name (default: postgres) |
| `DB_USER` | Database user |
| `DB_PASSWORD` | Database password |
| `FETCH_INTERVAL_MINUTES` | Pipeline frequency (default: 2) |
| `LOG_LEVEL` | Logging level (default: INFO) |
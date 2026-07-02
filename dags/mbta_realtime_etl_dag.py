"""
MBTA Real-Time ETL DAG
Fetches live predictions, vehicles, and alerts from the MBTA V3 API
every 2 minutes and loads them into PostgreSQL on AWS RDS.
"""

import logging
import logging.handlers
from datetime import datetime, timezone, timedelta
import pytz
UTC = pytz.UTC

from airflow.sdk import dag, task

from pipeline.mbta_api_client import fetch_predictions, fetch_vehicles, fetch_alerts
from pipeline.mbta_data_transformer import (
    transform_predictions,
    transform_vehicles,
    transform_alerts,
)
from pipeline.mbta_db_loader import (
    load_predictions,
    load_vehicles,
    load_alerts,
    log_pipeline_run,
    init_schema,
    delete_old_records,
)
from config.mbta_pipeline_config import LOG_LEVEL, LOG_FILE


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
def setup_logging():
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

    console = logging.StreamHandler()
    console.setFormatter(formatter)

    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5
    )
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    root.addHandler(console)
    root.addHandler(file_handler)


logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default args
# ---------------------------------------------------------------------------
default_args = {
    "owner": "anjana",
    "retries": 3,
    "retry_delay": timedelta(seconds=60),
    "email_on_failure": False,
    "depends_on_past": False,
}


# ---------------------------------------------------------------------------
# DAG definition
# ---------------------------------------------------------------------------
@dag(
    dag_id="mbta_realtime_etl_dag",
    description="Real-time ETL pipeline fetching live MBTA transit data into PostgreSQL",
    schedule="*/2 * * * *",
    start_date=datetime(2026, 7, 1, tzinfo=UTC),
    catchup=False,
    max_active_runs=1,
    default_args=default_args,
    tags=["mbta", "realtime", "etl", "transit"],
)
def mbta_realtime_etl_dag():

    @task()
    def initialise_schema():
        setup_logging()
        init_schema()
        logger.info("Schema initialised successfully")

    @task()
    def extract_transit_data():
        setup_logging()
        logger.info("Starting MBTA data extraction")

        predictions = fetch_predictions()
        vehicles = fetch_vehicles()
        alerts = fetch_alerts()

        logger.info(
            f"Extracted {len(predictions)} predictions, "
            f"{len(vehicles)} vehicles, "
            f"{len(alerts)} alerts"
        )

        return {
            "predictions": predictions,
            "vehicles": vehicles,
            "alerts": alerts,
            "started_at": datetime.now(UTC).isoformat(),
        }

    @task()
    def transform_transit_data(raw_data: dict):
        setup_logging()
        clean_predictions = transform_predictions(raw_data["predictions"])
        clean_vehicles = transform_vehicles(raw_data["vehicles"])
        clean_alerts = transform_alerts(raw_data["alerts"])

        return {
            "predictions": clean_predictions,
            "vehicles": clean_vehicles,
            "alerts": clean_alerts,
            "started_at": raw_data["started_at"],
        }

    @task()
    def load_transit_data(clean_data: dict):
        setup_logging()
        started_at = datetime.fromisoformat(clean_data["started_at"])
        total_inserted = 0
        error_msg = None

        try:
            total_inserted += load_predictions(clean_data["predictions"])
            total_inserted += load_vehicles(clean_data["vehicles"])
            total_inserted += load_alerts(clean_data["alerts"])
            status = "success"
            logger.info(f"Loaded {total_inserted} total records")

        except Exception as e:
            status = "failed"
            error_msg = str(e)
            logger.exception(f"Load failed: {e}")
            raise

        finally:
            finished_at = datetime.now(UTC)
            log_pipeline_run(
                started_at, finished_at, status, total_inserted, error_msg
            )

        return total_inserted
    @task()
    def cleanup_old_records():
        setup_logging()
        deleted = delete_old_records(days=30)
        logger.info(f"Cleanup complete — {deleted} old records removed")

    # -----------------------------------------------------------------------
    # Task dependencies
    # schema must be ready before extract runs
    # cleanup runs after load completes
    # -----------------------------------------------------------------------
    schema = initialise_schema()
    raw_data = extract_transit_data()
    clean_data = transform_transit_data(raw_data)
    loaded = load_transit_data(clean_data)

    schema >> raw_data
    loaded >> cleanup_old_records()


mbta_realtime_etl_dag()
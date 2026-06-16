#import libraries
import logging
import logging.handlers
from datetime import datetime, timezone
from airflow.decorators import dag, task
from airflow.utils.dates import days_ago

from pipeline.mbta_api_client import fetch_predictions, fetch_vehicles, fetch_alerts
from pipeline.mbta_data_transformer import transform_predictions, transform_vehicles, transform_alerts
from pipeline.mbta_db_loader import load_predictions, load_vehicles, load_alerts, log_pipeline_run, init_schema
from config.mbta_pipeline_config import LOG_LEVEL, LOG_FILE

#logging setup
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

default_args = {
    "owner": "anjana",
    "retries": 3,
    "retry_delay": 60,
    "email_on_failure": False,
    "depends_on_past": False,
}


#dag definition
@dag(
    dag_id="mbta_realtime_etl_dag",
    description="Real-time ETL pipeline fetching live MBTA transit data into PostgreSQL",
    schedule="*/2 * * * *",
    start_date=days_ago(1),
    catchup=False,
    default_args=default_args,
    tags=["mbta", "realtime", "etl", "transit"],
)
def mbta_realtime_etl_dag():
    @task()
    def extract_transit_data():
        setup_logging()
        logger.info("Starting MBTA data extraction")

        predictions = fetch_predictions()
        vehicles = fetch_vehicles()
        alerts = fetch_alerts()

        logger.info(f"Extracted {len(predictions)} predictions, {len(vehicles)} vehicles, {len(alerts)} alerts")

        return {
            "predictions": predictions,
            "vehicles": vehicles,
            "alerts": alerts,
        }

    @task()
    def transform_transit_data(raw_data: dict):
        setup_logging()
        logger.info("Starting MBTA data transformation")

        clean_predictions = transform_predictions(raw_data["predictions"])
        clean_vehicles = transform_vehicles(raw_data["vehicles"])
        clean_alerts = transform_alerts(raw_data["alerts"])

        logger.info(f"Transformed {len(clean_predictions)} predictions, {len(clean_vehicles)} vehicles, {len(clean_alerts)} alerts")

        return {
            "predictions": clean_predictions,
            "vehicles": clean_vehicles,
            "alerts": clean_alerts,
        }

    @task()
    def load_transit_data(clean_data: dict):
        setup_logging()
        started_at = datetime.now(timezone.utc)
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
            finished_at = datetime.now(timezone.utc)
            log_pipeline_run(started_at, finished_at, status, total_inserted, error_msg)

        return total_inserted

    @task()
    def initialise_schema():
        setup_logging()
        init_schema()
        logger.info("Schema initialised successfully")
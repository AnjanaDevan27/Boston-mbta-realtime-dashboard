import schedule
import time
import logging
from pipeline.mbta_api_client import fetch_predictions, fetch_vehicles, fetch_alerts
from pipeline.mbta_data_transformer import transform_predictions, transform_vehicles, transform_alerts
from pipeline.mbta_db_loader import load_predictions, load_vehicles, load_alerts, log_pipeline_run, init_schema
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def run_pipeline():
    started_at = datetime.now(timezone.utc)
    total = 0
    try:
        init_schema()
        total += load_predictions(transform_predictions(fetch_predictions()))
        total += load_vehicles(transform_vehicles(fetch_vehicles()))
        total += load_alerts(transform_alerts(fetch_alerts()))
        logger.info(f"Pipeline complete — {total} records inserted")
        log_pipeline_run(started_at, datetime.now(timezone.utc), "success", total)
    except Exception as e:
        logger.exception(f"Pipeline failed: {e}")
        log_pipeline_run(started_at, datetime.now(timezone.utc), "failed", 0, str(e))


run_pipeline()
schedule.every(2).minutes.do(run_pipeline)
while True:
    schedule.run_pending()
    time.sleep(10)
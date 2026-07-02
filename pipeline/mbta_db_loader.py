# import libraries
import logging
import psycopg2
import psycopg2.extras
from contextlib import contextmanager
from datetime import datetime
from config.mbta_pipeline_config import DB_CONFIG

logger = logging.getLogger(__name__)


# DB connection
@contextmanager
def get_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _convert_timestamps(records):
    """Convert ISO string timestamps back to datetime objects for DB insert."""
    timestamp_fields = [
        "fetched_at", "arrival_time", "departure_time",
        "active_period_start", "active_period_end",
    ]
    for r in records:
        for field in timestamp_fields:
            if field in r and isinstance(r[field], str):
                try:
                    r[field] = datetime.fromisoformat(r[field])
                except (ValueError, TypeError):
                    r[field] = None
    return records


# bulk insert helper
def _bulk_insert(conn, table, records):
    if not records:
        return 0
    records = _convert_timestamps(records)
    columns = list(records[0].keys())
    sql = f"""
        INSERT INTO {table} ({', '.join(columns)})
        VALUES %s
    """
    psycopg2.extras.execute_values(
        conn.cursor(),
        sql,
        [tuple(r[c] for c in columns) for r in records]
    )
    return len(records)


# public load functions
def load_predictions(records):
    with get_connection() as conn:
        count = _bulk_insert(conn, "predictions", records)
    logger.info(f"Inserted {count} prediction records")
    return count


def load_vehicles(records):
    with get_connection() as conn:
        count = _bulk_insert(conn, "vehicles", records)
    logger.info(f"Inserted {count} vehicle records")
    return count


def load_alerts(records):
    if not records:
        return 0
    records = _convert_timestamps(records)
    columns = list(records[0].keys())
    sql = f"""
        INSERT INTO alerts ({', '.join(columns)})
        VALUES %s
        ON CONFLICT DO NOTHING
    """
    with get_connection() as conn:
        psycopg2.extras.execute_values(
            conn.cursor(),
            sql,
            [tuple(r[c] for c in columns) for r in records]
        )
    logger.info(f"Inserted {len(records)} alert records")
    return len(records)


# pipeline run logger
def log_pipeline_run(started_at, finished_at, status, records_inserted, error=None):
    sql = """
        INSERT INTO pipeline_runs
        (started_at, finished_at, status, records_inserted, error_message)
        VALUES (%s, %s, %s, %s, %s)
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (started_at, finished_at, status, records_inserted, error))


# schema init
def init_schema():
    with open("include/sql/mbta_schema.sql", "r") as f:
        sql = f.read()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
    logger.info("Schema initialized successfully")


# cleanup old records
def delete_old_records(days: int = 30) -> int:
    """Delete records older than specified days to manage storage."""
    sql_predictions = "DELETE FROM predictions WHERE fetched_at < NOW() - INTERVAL '%s days'"
    sql_vehicles = "DELETE FROM vehicles WHERE fetched_at < NOW() - INTERVAL '%s days'"
    sql_alerts = "DELETE FROM alerts WHERE fetched_at < NOW() - INTERVAL '%s days'"

    total_deleted = 0
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql_predictions, (days,))
            total_deleted += cur.rowcount
            cur.execute(sql_vehicles, (days,))
            total_deleted += cur.rowcount
            cur.execute(sql_alerts, (days,))
            total_deleted += cur.rowcount

    logger.info(f"Deleted {total_deleted} records older than {days} days")
    return total_deleted
#import libraries
import logging
import psycopg2
import psycopg2.extras
from contextlib import contextmanager
from config.mbta_pipeline_config import DB_CONFIG

logger = logging.getLogger(__name__)

#dB connection
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
        

#bulk insert helper
def _bulk_insert(conn, table, records):
    if not records:
        return 0
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


#public load functions
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


# pipeline run logger and schema init
def log_pipeline_run(started_at, finished_at, status, records_inserted, error=None):
    sql = """
        INSERT INTO pipeline_runs 
        (started_at, finished_at, status, records_inserted, error_message)
        VALUES (%s, %s, %s, %s, %s)
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (started_at, finished_at, status, records_inserted, error))


def init_schema():
    with open("include/sql/mbta_schema.sql", "r") as f:
        sql = f.read()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
    logger.info("Schema initialized successfully")
    
    
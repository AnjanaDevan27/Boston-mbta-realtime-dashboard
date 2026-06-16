#import libraries
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config.settings import MBTA_API_KEY, MBTA_BASE_URL, MBTA_ROUTES

logger = logging.getLogger(__name__)

def _get_session() -> requests.Session:
    """Create a session with retry strategy."""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429,500,502,503,504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    return session

def _get(endpoint: str, params:dict) -> list:
    session = _get_session()
    params["api_key"] = MBTA_API_KEY
    url = f"{MBTA_BASE_URL}/{endpoint}"
    try:
        reponse = session.get(url, params=params, timeout=10)
        reponse.raise_for_status()
        return reponse.json().get("data", [])
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP error fetching {endpoint}: {e}")
        return []
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error fetching {endpoint}: {e}")
        return []
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout error fetching {endpoint}: {e}")
        return []

def fetch_predictions() -> list[dict]:
    """Fetch predictions for specified routes."""
    records =[]
    for route in MBTA_ROUTES:
        data = _get("predictions", {"filter[route]": route})
        for item in data:
            atttr = item.get("attributes", {})
            rel = item.get("relationships", {})
            stop = rel.get("stop", {}).get("data")
            records.append({
                "route": route,
                "stop_id": stop["id" if stop else None],
                "direction_id": atttr.get("direction_id"),
                "arrival_time": atttr.get("arrival_time"),
                "departure_time": atttr.get("departure_time"),
                "status": atttr.get("status"),
                "schedule_relationship": atttr.get("schedule_relationship"),       
            })
        logger.debug(f"Fetched {len(data)} predictions for route {route}")
        logger.info(f"Total predictions fetched: {len(records)}")
    return records

def  fetch_alerts() -> list[dict]:
    """Fetch alerts for specified routes."""
    data = _get("alerts", {
        "filter[route_type]": "0,1",
    })
    records = []
    for item in data:
        attr = item.get("attributes", {})
        periods = attr.get("active_period", [{}])
        first_period = periods[0] if periods else {}
        records.append({
            "alert_id": item.get("id"),
            "header": attr.get("header"),
            "severity": attr.get("severity"),
            "effect": attr.get("effect"),
            "cause": attr.get("cause"),
            "active_period_start": first_period.get("start"),
            "active_period_end": first_period.get("end"),
        })
    logger.info(f"Total alerts fetched: {len(records)}")
    return records
#import libraries
import logging
from datetime import datetime,timezone

logger = logging.getLogger(__name__)

#helper_functions
def _parse_timestamp(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        logger.warning(f"Could not parse timestamp: {value}")
        return None
    
    
def _clean_str(value,max_len=255):
    if value is None:
        return None
    return str(value).strip()[:max_len]
    
    
#transform predicitons
def transform_predictions(records):
    cleaned=[]
    for r in records:
        cleaned.append({
            "route": _clean_str(r.get("route"),20),
            "stop_id": _clean_str(r.get("stop_id"),50),
            "direction_id": r.get("direction_id"),
            "arrival_time": _parse_timestamp(r.get("arrival_time")),
            "departure_time": _parse_timestamp(r.get("departure_time")),
            "status": _clean_str(r.get("status"),50),
            "schedule_relationship": _clean_str(r.get("schedule_relationship"),50),
            "fetched_at": datetime.now(timezone.utc),
        })
    logger.info(f"Transformed {len(cleaned)} prediction records")
    return cleaned


#transform vehicles
def transform_vehicles(records):
    cleaned=[]
    for r in records:
        lat = r.get("latitude")
        lon = r.get("longitude")
        
        if lat is not None:
            try:
                lat = float(lat)
                if not (-90 <= lat <= 90):
                    logger.warning(f"Invalid latitude for vehicle {r.get('vehicle_id')}: {lat}")
                    lat = None
            except (TypeError, ValueError):
                logger.warning(f"Non-numeric latitude for vehicle {r.get('vehicle_id')}: {lat}")
                lat = None

        if lon is not None:
            try:
                lon = float(lon)
                if not (-180 <= lon <= 180):
                    logger.warning(f"Invalid longitude for vehicle {r.get('vehicle_id')}: {lon}")
                    lon = None
            except (TypeError, ValueError):
                logger.warning(f"Non-numeric longitude for vehicle {r.get('vehicle_id')}: {lon}")
                lon = None   
        cleaned.append({
            "vehicle_id": _clean_str(r.get("vehicle_id"),50),
            "route": _clean_str(r.get("route"),20),
            "latitude": lat,
            "longitude": lon,
            "bearing": r.get("bearing"),
            "speed": r.get("speed"),
            "current_status": _clean_str(r.get("current_status"),50),
            "occupancy_status": _clean_str(r.get("occupancy_status"),50),
            "fetched_at": datetime.now(timezone.utc),
            
        })
    logger.info(f"Transformed {len(cleaned)} vehicle records")
    return cleaned


#transform alerts
def transform_alerts(records):
    cleaned=[]
    for r in records:
        cleaned.append({
            "alert_id":_clean_str(r.get("alert_id"),50),
            "header": _clean_str(r.get("header")),
            "severity": r.get("severity"),
            "effect": _clean_str(r.get("effect"),100),
            "Cause": _clean_str(r.get("cause"),100),
            "active_period_start": _parse_timestamp(r.get("active_period_start")),
            "active_period_end": _parse_timestamp(r.get("active_period_end")),
            "fetched_at": datetime.now(timezone.utc),
        })
    logger.info(f"Transformed {len(cleaned)} alert records")
    return cleaned  
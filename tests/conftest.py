#import libraries
import pytest
from datetime import datetime, timezone



#prediction fixtures
@pytest.fixture(scope="session")
def valid_prediction():
    return {
        "route": "Red",
        "stop_id": "place-pktrm",
        "direction_id": 0,
        "arrival_time": "2024-01-15T10:30:00-05:00",
        "departure_time": "2024-01-15T10:31:00-05:00",
        "status": None,
        "schedule_relationship": "SCHEDULED",
    }


@pytest.fixture(scope="session")
def prediction_missing_stop():
    return {
        "route": "Orange",
        "stop_id": None,
        "direction_id": 1,
        "arrival_time": None,
        "departure_time": None,
        "status": "Stopped",
        "schedule_relationship": None,
    }


@pytest.fixture(scope="session")
def prediction_missing_attributes():
    return {"id": "prediction-1"}


@pytest.fixture(scope="session")
def prediction_long_route():
    return {
        "route": "R" * 50,
        "stop_id": "place-pktrm",
        "direction_id": 0,
        "arrival_time": None,
        "departure_time": None,
        "status": None,
        "schedule_relationship": None,
    }
    
    
    
#vehicle fixtures
@pytest.fixture(scope="session")
def valid_vehicle():
    return {
        "vehicle_id": "vehicle-1234",
        "route": "Red",
        "latitude": 42.3601,
        "longitude": -71.0589,
        "bearing": 180,
        "speed": 15.5,
        "current_status": "IN_TRANSIT_TO",
        "occupancy_status": "MANY_SEATS_AVAILABLE",
    }


@pytest.fixture(scope="session")
def vehicle_invalid_latitude():
    return {
        "vehicle_id": "vehicle-bad-lat",
        "route": "Orange",
        "latitude": 999.0,
        "longitude": -71.0589,
        "bearing": 90,
        "speed": 10.0,
        "current_status": "STOPPED_AT",
        "occupancy_status": None,
    }


@pytest.fixture(scope="session")
def vehicle_invalid_longitude():
    return {
        "vehicle_id": "vehicle-bad-lon",
        "route": "Blue",
        "latitude": 42.3601,
        "longitude": 999.0,
        "bearing": 90,
        "speed": 10.0,
        "current_status": "IN_TRANSIT_TO",
        "occupancy_status": None,
    }


@pytest.fixture(scope="session")
def vehicle_boundary_coordinates():
    return {
        "vehicle_id": "vehicle-boundary",
        "route": "Green-B",
        "latitude": 90.0,
        "longitude": -180.0,
        "bearing": 0,
        "speed": 0.0,
        "current_status": "STOPPED_AT",
        "occupancy_status": None,
    }


@pytest.fixture(scope="session")
def vehicle_negative_speed():
    return {
        "vehicle_id": "vehicle-neg-speed",
        "route": "Green-C",
        "latitude": 42.3601,
        "longitude": -71.0589,
        "bearing": 180,
        "speed": -5.0,
        "current_status": "IN_TRANSIT_TO",
        "occupancy_status": None,
    }


@pytest.fixture(scope="session")
def vehicle_string_coordinates():
    return {
        "vehicle_id": "vehicle-str-coords",
        "route": "Green-D",
        "latitude": "not-a-number",
        "longitude": -71.0589,
        "bearing": 180,
        "speed": 10.0,
        "current_status": "IN_TRANSIT_TO",
        "occupancy_status": None,
    }
    
    
    
    
@pytest.fixture(scope="session")
def valid_alert():
    return {
        "alert_id": "alert-99",
        "header": "Red Line delays due to signal problem",
        "severity": 7,
        "effect": "SIGNIFICANT_DELAYS",
        "cause": "TECHNICAL_PROBLEM",
        "active_period_start": "2024-01-15T08:00:00-05:00",
        "active_period_end": None,
    }


@pytest.fixture(scope="session")
def alert_whitespace_fields():
    return {
        "alert_id": "  alert-1  ",
        "header": "  Delays on Red Line  ",
        "severity": 7,
        "effect": "SIGNIFICANT_DELAYS",
        "cause": "TECHNICAL_PROBLEM",
        "active_period_start": None,
        "active_period_end": None,
    }


@pytest.fixture(scope="session")
def alert_string_severity():
    return {
        "alert_id": "alert-2",
        "header": "Orange Line suspension",
        "severity": "high",
        "effect": "SUSPENSION",
        "cause": "MAINTENANCE",
        "active_period_start": None,
        "active_period_end": None,
    }


@pytest.fixture(scope="session")
def alert_missing_header():
    return {
        "alert_id": "alert-3",
        "header": None,
        "severity": 5,
        "effect": "DELAY",
        "cause": "TECHNICAL_PROBLEM",
        "active_period_start": None,
        "active_period_end": None,
    }
    
    
    
    
    
    
#alert fixtures
@pytest.fixture(scope="session")
def valid_alert():
    return {
        "alert_id": "alert-99",
        "header": "Red Line delays due to signal problem",
        "severity": 7,
        "effect": "SIGNIFICANT_DELAYS",
        "cause": "TECHNICAL_PROBLEM",
        "active_period_start": "2024-01-15T08:00:00-05:00",
        "active_period_end": None,
    }


@pytest.fixture(scope="session")
def alert_whitespace_fields():
    return {
        "alert_id": "  alert-1  ",
        "header": "  Delays on Red Line  ",
        "severity": 7,
        "effect": "SIGNIFICANT_DELAYS",
        "cause": "TECHNICAL_PROBLEM",
        "active_period_start": None,
        "active_period_end": None,
    }


@pytest.fixture(scope="session")
def alert_string_severity():
    return {
        "alert_id": "alert-2",
        "header": "Orange Line suspension",
        "severity": "high",
        "effect": "SUSPENSION",
        "cause": "MAINTENANCE",
        "active_period_start": None,
        "active_period_end": None,
    }


@pytest.fixture(scope="session")
def alert_missing_header():
    return {
        "alert_id": "alert-3",
        "header": None,
        "severity": 5,
        "effect": "DELAY",
        "cause": "TECHNICAL_PROBLEM",
        "active_period_start": None,
        "active_period_end": None,
    }
    
    
    
#MBTA API MOCK RESPONSES FIXTURES
@pytest.fixture(scope="session")
def mock_api_prediction():
    return {
        "id": "prediction-1",
        "attributes": {
            "arrival_time": "2024-01-15T10:30:00-05:00",
            "departure_time": "2024-01-15T10:31:00-05:00",
            "direction_id": 0,
            "status": None,
            "schedule_relationship": "SCHEDULED",
        },
        "relationships": {
            "stop": {"data": {"id": "place-pktrm"}},
        },
    }


@pytest.fixture(scope="session")
def mock_api_prediction_no_stop():
    return {
        "id": "prediction-2",
        "attributes": {
            "arrival_time": None,
            "departure_time": None,
            "direction_id": 1,
            "status": None,
            "schedule_relationship": "CANCELLED",
        },
        "relationships": {
            "stop": {"data": None},
        },
    }


@pytest.fixture(scope="session")
def mock_api_vehicle():
    return {
        "id": "vehicle-1234",
        "attributes": {
            "latitude": 42.3601,
            "longitude": -71.0589,
            "bearing": 180,
            "speed": 15.5,
            "current_status": "IN_TRANSIT_TO",
            "occupancy_status": "MANY_SEATS_AVAILABLE",
        },
    }


@pytest.fixture(scope="session")
def mock_api_alert():
    return {
        "id": "alert-99",
        "attributes": {
            "header": "Red Line delays due to signal problem",
            "severity": 7,
            "effect": "SIGNIFICANT_DELAYS",
            "cause": "TECHNICAL_PROBLEM",
            "active_period": [{"start": "2024-01-15T08:00:00-05:00", "end": None}],
        },
    }
    
    
@pytest.fixture
def mock_db_connection():
    with patch("pipeline.mbta_db_loader.get_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.return_value.__enter__ = MagicMock(return_value=MagicMock(cursor=MagicMock(return_value=mock_cursor)))
        mock_conn.return_value.__exit__ = MagicMock(return_value=False)
        yield mock_conn, mock_cursor


@pytest.fixture
def sample_predictions():
    return [
        {
            "route": "Red",
            "stop_id": "place-pktrm",
            "direction_id": 0,
            "arrival_time": datetime(2024, 1, 15, 10, 30, tzinfo=timezone.utc),
            "departure_time": datetime(2024, 1, 15, 10, 31, tzinfo=timezone.utc),
            "status": None,
            "schedule_relationship": "SCHEDULED",
            "fetched_at": datetime(2024, 1, 15, 10, 29, tzinfo=timezone.utc),
        }
    ]


@pytest.fixture
def sample_vehicles():
    return [
        {
            "vehicle_id": "vehicle-1234",
            "route": "Red",
            "latitude": 42.3601,
            "longitude": -71.0589,
            "bearing": 180,
            "speed": 15.5,
            "current_status": "IN_TRANSIT_TO",
            "occupancy_status": "MANY_SEATS_AVAILABLE",
            "fetched_at": datetime(2024, 1, 15, 10, 29, tzinfo=timezone.utc),
        }
    ]


@pytest.fixture
def sample_alerts():
    return [
        {
            "alert_id": "alert-99",
            "header": "Red Line delays",
            "severity": 7,
            "effect": "SIGNIFICANT_DELAYS",
            "cause": "TECHNICAL_PROBLEM",
            "active_period_start": datetime(2024, 1, 15, 8, 0, tzinfo=timezone.utc),
            "active_period_end": None,
            "fetched_at": datetime(2024, 1, 15, 10, 29, tzinfo=timezone.utc),
        }
    ]
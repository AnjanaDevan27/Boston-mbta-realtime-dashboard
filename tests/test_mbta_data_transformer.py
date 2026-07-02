#import libraries
import pytest
from datetime import datetime
from pipeline.mbta_data_transformer import (
    transform_predictions,
    transform_vehicles,
    transform_alerts,
)


#prediction tests
class TestTransformPredictions:

    def test_parses_valid_timestamps(self, valid_prediction):
        result = transform_predictions([valid_prediction])
        assert isinstance(result[0]["arrival_time"], datetime)
        assert isinstance(result[0]["departure_time"], datetime)
        assert isinstance(result[0]["fetched_at"], datetime)

    def test_handles_null_timestamps(self, prediction_missing_stop):
        result = transform_predictions([prediction_missing_stop])
        assert result[0]["arrival_time"] is None
        assert result[0]["departure_time"] is None

    def test_truncates_long_route_name(self, prediction_long_route):
        result = transform_predictions([prediction_long_route])
        assert len(result[0]["route"]) <= 20

    def test_handles_empty_input(self):
        result = transform_predictions([])
        assert result == []

    def test_handles_missing_attributes(self, prediction_missing_attributes):
        result = transform_predictions([prediction_missing_attributes])
        assert len(result) == 1
        assert result[0]["route"] is None
        assert result[0]["arrival_time"] is None

    def test_strips_whitespace_from_strings(self):
        raw = [{
            "route": "  Red  ",
            "stop_id": "  place-pktrm  ",
            "direction_id": 0,
            "arrival_time": None,
            "departure_time": None,
            "status": None,
            "schedule_relationship": None,
        }]
        result = transform_predictions(raw)
        assert result[0]["route"] == "Red"
        assert result[0]["stop_id"] == "place-pktrm"

    def test_handles_invalid_timestamp_format(self):
        raw = [{
            "route": "Red",
            "stop_id": "place-pktrm",
            "direction_id": 0,
            "arrival_time": "not-a-timestamp",
            "departure_time": "also-invalid",
            "status": None,
            "schedule_relationship": None,
        }]
        result = transform_predictions(raw)
        assert result[0]["arrival_time"] is None
        assert result[0]["departure_time"] is None

    def test_preserves_direction_id(self, valid_prediction):
        result = transform_predictions([valid_prediction])
        assert result[0]["direction_id"] == 0

    def test_fetched_at_is_timezone_aware(self, valid_prediction):
        result = transform_predictions([valid_prediction])
        assert result[0]["fetched_at"].tzinfo is not None

    def test_handles_multiple_records(self, valid_prediction, prediction_missing_stop):
        result = transform_predictions([valid_prediction, prediction_missing_stop])
        assert len(result) == 2
    
    
    
#vehicle tests  
class TestTransformVehicles:

    def test_accepts_valid_coordinates(self, valid_vehicle):
        result = transform_vehicles([valid_vehicle])
        assert result[0]["latitude"] == 42.3601
        assert result[0]["longitude"] == -71.0589

    def test_rejects_invalid_latitude(self, vehicle_invalid_latitude):
        result = transform_vehicles([vehicle_invalid_latitude])
        assert result[0]["latitude"] is None
        assert result[0]["longitude"] == -71.0589

    def test_rejects_invalid_longitude(self, vehicle_invalid_longitude):
        result = transform_vehicles([vehicle_invalid_longitude])
        assert result[0]["latitude"] == 42.3601
        assert result[0]["longitude"] is None

    def test_accepts_boundary_coordinates(self, vehicle_boundary_coordinates):
        result = transform_vehicles([vehicle_boundary_coordinates])
        assert result[0]["latitude"] == 90.0
        assert result[0]["longitude"] == -180.0

    def test_handles_empty_input(self):
        result = transform_vehicles([])
        assert result == []

    def test_handles_none_coordinates(self):
        raw = [{
            "vehicle_id": "v1",
            "route": "Red",
            "latitude": None,
            "longitude": None,
            "bearing": None,
            "speed": None,
            "current_status": None,
            "occupancy_status": None,
        }]
        result = transform_vehicles(raw)
        assert result[0]["latitude"] is None
        assert result[0]["longitude"] is None

    def test_handles_string_coordinates(self, vehicle_string_coordinates):
        result = transform_vehicles([vehicle_string_coordinates])
        assert result[0]["latitude"] is None

    def test_fetched_at_is_timezone_aware(self, valid_vehicle):
        result = transform_vehicles([valid_vehicle])
        assert result[0]["fetched_at"].tzinfo is not None

    def test_handles_multiple_records(self, valid_vehicle, vehicle_invalid_latitude):
        result = transform_vehicles([valid_vehicle, vehicle_invalid_latitude])
        assert len(result) == 2
        assert result[0]["latitude"] == 42.3601
        assert result[1]["latitude"] is None

    def test_preserves_vehicle_id(self, valid_vehicle):
        result = transform_vehicles([valid_vehicle])
        assert result[0]["vehicle_id"] == "vehicle-1234"
    
    
    
#alert tests
class TestTransformAlerts:

    def test_parses_valid_timestamps(self, valid_alert):
        result = transform_alerts([valid_alert])
        assert isinstance(result[0]["active_period_start"], datetime)
        assert result[0]["active_period_end"] is None

    def test_strips_whitespace(self, alert_whitespace_fields):
        result = transform_alerts([alert_whitespace_fields])
        assert result[0]["alert_id"] == "alert-1"
        assert result[0]["header"] == "Delays on Red Line"

    def test_handles_missing_header(self, alert_missing_header):
        result = transform_alerts([alert_missing_header])
        assert result[0]["header"] is None

    def test_handles_empty_input(self):
        result = transform_alerts([])
        assert result == []

    def test_truncates_long_effect(self):
        raw = [{
            "alert_id": "alert-long",
            "header": "Test",
            "severity": 5,
            "effect": "E" * 200,
            "cause": "TECHNICAL_PROBLEM",
            "active_period_start": None,
            "active_period_end": None,
        }]
        result = transform_alerts(raw)
        assert len(result[0]["effect"]) <= 100

    def test_handles_invalid_timestamp(self):
        raw = [{
            "alert_id": "alert-bad-ts",
            "header": "Test",
            "severity": 5,
            "effect": "DELAY",
            "cause": "TECHNICAL_PROBLEM",
            "active_period_start": "not-a-timestamp",
            "active_period_end": "also-invalid",
        }]
        result = transform_alerts(raw)
        assert result[0]["active_period_start"] is None
        assert result[0]["active_period_end"] is None

    def test_fetched_at_is_timezone_aware(self, valid_alert):
        result = transform_alerts([valid_alert])
        assert result[0]["fetched_at"].tzinfo is not None

    def test_handles_multiple_records(self, valid_alert, alert_missing_header):
        result = transform_alerts([valid_alert, alert_missing_header])
        assert len(result) == 2

    def test_preserves_severity(self, valid_alert):
        result = transform_alerts([valid_alert])
        assert result[0]["severity"] == 7
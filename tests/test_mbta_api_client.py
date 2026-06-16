#import libraries
import pytest
import requests
from unittest.mock import patch, MagicMock
from pipeline.mbta_api_client import fetch_predictions, fetch_vehicles, fetch_alerts



#prediction tests
class TestFetchPredictions:

    @patch("pipeline.mbta_api_client._get")
    def test_returns_records(self, mock_get, mock_api_prediction):
        mock_get.return_value = [mock_api_prediction]
        results = fetch_predictions()
        assert len(results) > 0
        assert results[0]["stop_id"] == "place-pktrm"
        assert results[0]["direction_id"] == 0

    @patch("pipeline.mbta_api_client._get")
    def test_handles_empty_response(self, mock_get):
        mock_get.return_value = []
        results = fetch_predictions()
        assert results == []

    @patch("pipeline.mbta_api_client._get")
    def test_returns_correct_fields(self, mock_get, mock_api_prediction):
        mock_get.return_value = [mock_api_prediction]
        results = fetch_predictions()
        record = results[0]
        assert "route" in record
        assert "stop_id" in record
        assert "arrival_time" in record
        assert "departure_time" in record
        assert "schedule_relationship" in record

    @patch("pipeline.mbta_api_client._get")
    def test_handles_no_stop_data(self, mock_get, mock_api_prediction_no_stop):
        mock_get.return_value = [mock_api_prediction_no_stop]
        results = fetch_predictions()
        assert results[0]["stop_id"] is None

    @patch("pipeline.mbta_api_client._get_session")
    def test_handles_api_timeout(self, mock_session):
        mock_session.return_value.get.side_effect = requests.exceptions.Timeout
        results = fetch_predictions()
        assert results == []

    @patch("pipeline.mbta_api_client._get_session")
    def test_handles_connection_error(self, mock_session):
        mock_session.return_value.get.side_effect = requests.exceptions.ConnectionError
        results = fetch_predictions()
        assert results == []

    @patch("pipeline.mbta_api_client._get_session")
    def test_handles_500_error(self, mock_session):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=MagicMock(status_code=500)
        )
        mock_session.return_value.get.return_value = mock_response
        results = fetch_predictions()
        assert results == []

    @patch("pipeline.mbta_api_client._get_session")
    def test_handles_rate_limit(self, mock_session):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=MagicMock(status_code=429)
        )
        mock_session.return_value.get.return_value = mock_response
        results = fetch_predictions()
        assert results == []
        
        
    
#vehicle tests
class TestFetchVehicles:

    @patch("pipeline.mbta_api_client._get")
    def test_returns_records(self, mock_get, mock_api_vehicle):
        mock_get.return_value = [mock_api_vehicle]
        results = fetch_vehicles()
        assert len(results) > 0
        assert results[0]["vehicle_id"] == "vehicle-1234"
        assert results[0]["latitude"] == 42.3601

    @patch("pipeline.mbta_api_client._get")
    def test_handles_empty_response(self, mock_get):
        mock_get.return_value = []
        results = fetch_vehicles()
        assert results == []

    @patch("pipeline.mbta_api_client._get")
    def test_returns_correct_fields(self, mock_get, mock_api_vehicle):
        mock_get.return_value = [mock_api_vehicle]
        results = fetch_vehicles()
        record = results[0]
        assert "vehicle_id" in record
        assert "route" in record
        assert "latitude" in record
        assert "longitude" in record
        assert "current_status" in record

    @patch("pipeline.mbta_api_client._get_session")
    def test_handles_api_timeout(self, mock_session):
        mock_session.return_value.get.side_effect = requests.exceptions.Timeout
        results = fetch_vehicles()
        assert results == []

    @patch("pipeline.mbta_api_client._get_session")
    def test_handles_connection_error(self, mock_session):
        mock_session.return_value.get.side_effect = requests.exceptions.ConnectionError
        results = fetch_vehicles()
        assert results == []

    @patch("pipeline.mbta_api_client._get_session")
    def test_handles_500_error(self, mock_session):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=MagicMock(status_code=500)
        )
        mock_session.return_value.get.return_value = mock_response
        results = fetch_vehicles()
        assert results == []
    
    
    
    
#alert tests
class TestFetchAlerts:

    @patch("pipeline.mbta_api_client._get")
    def test_returns_records(self, mock_get, mock_api_alert):
        mock_get.return_value = [mock_api_alert]
        results = fetch_alerts()
        assert len(results) > 0
        assert results[0]["alert_id"] == "alert-99"
        assert results[0]["effect"] == "SIGNIFICANT_DELAYS"

    @patch("pipeline.mbta_api_client._get")
    def test_handles_empty_response(self, mock_get):
        mock_get.return_value = []
        results = fetch_alerts()
        assert results == []

    @patch("pipeline.mbta_api_client._get")
    def test_returns_correct_fields(self, mock_get, mock_api_alert):
        mock_get.return_value = [mock_api_alert]
        results = fetch_alerts()
        record = results[0]
        assert "alert_id" in record
        assert "header" in record
        assert "severity" in record
        assert "effect" in record
        assert "cause" in record

    @patch("pipeline.mbta_api_client._get_session")
    def test_handles_api_timeout(self, mock_session):
        mock_session.return_value.get.side_effect = requests.exceptions.Timeout
        results = fetch_alerts()
        assert results == []

    @patch("pipeline.mbta_api_client._get_session")
    def test_handles_connection_error(self, mock_session):
        mock_session.return_value.get.side_effect = requests.exceptions.ConnectionError
        results = fetch_alerts()
        assert results == []

    @patch("pipeline.mbta_api_client._get")
    def test_handles_alert_with_no_active_period(self, mock_get):
        mock_get.return_value = [{
            "id": "alert-no-period",
            "attributes": {
                "header": "Service change",
                "severity": 3,
                "effect": "OTHER_EFFECT",
                "cause": "OTHER_CAUSE",
                "active_period": [],
            },
        }]
        results = fetch_alerts()
        assert results[0]["active_period_start"] is None
        assert results[0]["active_period_end"] is None
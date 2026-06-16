#import libraries
import pytest
import psycopg2
from unittest.mock import patch, MagicMock, call
from pipeline.mbta_db_loader import (
    load_predictions,
    load_vehicles,
    load_alerts,
    log_pipeline_run,
    init_schema,
)
from datetime import datetime, timezone




#predictions tests
class TestLoadPredictions:

    @patch("pipeline.mbta_db_loader.get_connection")
    @patch("pipeline.mbta_db_loader.psycopg2.extras.execute_values")
    def test_inserts_records_successfully(self, mock_execute, mock_conn, sample_predictions):
        mock_conn.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_conn.return_value.__exit__ = MagicMock(return_value=False)
        result = load_predictions(sample_predictions)
        assert result == len(sample_predictions)
        assert mock_execute.called

    @patch("pipeline.mbta_db_loader.get_connection")
    @patch("pipeline.mbta_db_loader.psycopg2.extras.execute_values")
    def test_returns_zero_for_empty_input(self, mock_execute, mock_conn):
        result = load_predictions([])
        assert result == 0
        assert not mock_execute.called

    @patch("pipeline.mbta_db_loader.get_connection")
    def test_raises_on_db_connection_failure(self, mock_conn, sample_predictions):
        mock_conn.side_effect = psycopg2.OperationalError("connection refused")
        with pytest.raises(psycopg2.OperationalError):
            load_predictions(sample_predictions)

    @patch("pipeline.mbta_db_loader.get_connection")
    @patch("pipeline.mbta_db_loader.psycopg2.extras.execute_values")
    def test_handles_multiple_records(self, mock_execute, mock_conn, sample_predictions):
        many_records = sample_predictions * 10
        mock_conn.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_conn.return_value.__exit__ = MagicMock(return_value=False)
        result = load_predictions(many_records)
        assert result == 10
        
        
        
        
#vehicles tests
class TestLoadVehicles:

    @patch("pipeline.mbta_db_loader.get_connection")
    @patch("pipeline.mbta_db_loader.psycopg2.extras.execute_values")
    def test_inserts_records_successfully(self, mock_execute, mock_conn, sample_vehicles):
        mock_conn.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_conn.return_value.__exit__ = MagicMock(return_value=False)
        result = load_vehicles(sample_vehicles)
        assert result == len(sample_vehicles)
        assert mock_execute.called

    @patch("pipeline.mbta_db_loader.get_connection")
    @patch("pipeline.mbta_db_loader.psycopg2.extras.execute_values")
    def test_returns_zero_for_empty_input(self, mock_execute, mock_conn):
        result = load_vehicles([])
        assert result == 0
        assert not mock_execute.called

    @patch("pipeline.mbta_db_loader.get_connection")
    def test_raises_on_db_connection_failure(self, mock_conn, sample_vehicles):
        mock_conn.side_effect = psycopg2.OperationalError("connection refused")
        with pytest.raises(psycopg2.OperationalError):
            load_vehicles(sample_vehicles)
            
            
            

#alerts tests        
class TestLoadAlerts:

    @patch("pipeline.mbta_db_loader.get_connection")
    @patch("pipeline.mbta_db_loader.psycopg2.extras.execute_values")
    def test_inserts_records_successfully(self, mock_execute, mock_conn, sample_alerts):
        mock_conn.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_conn.return_value.__exit__ = MagicMock(return_value=False)
        result = load_alerts(sample_alerts)
        assert result == len(sample_alerts)
        assert mock_execute.called

    @patch("pipeline.mbta_db_loader.get_connection")
    @patch("pipeline.mbta_db_loader.psycopg2.extras.execute_values")
    def test_returns_zero_for_empty_input(self, mock_execute, mock_conn):
        result = load_alerts([])
        assert result == 0
        assert not mock_execute.called

    @patch("pipeline.mbta_db_loader.get_connection")
    def test_raises_on_db_connection_failure(self, mock_conn, sample_alerts):
        mock_conn.side_effect = psycopg2.OperationalError("connection refused")
        with pytest.raises(psycopg2.OperationalError):
            load_alerts(sample_alerts)

    @patch("pipeline.mbta_db_loader.get_connection")
    @patch("pipeline.mbta_db_loader.psycopg2.extras.execute_values")
    def test_uses_on_conflict_do_nothing(self, mock_execute, mock_conn, sample_alerts):
        mock_conn.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_conn.return_value.__exit__ = MagicMock(return_value=False)
        load_alerts(sample_alerts)
        sql_used = mock_execute.call_args[0][1]
        assert "ON CONFLICT DO NOTHING" in sql_used
        
        
        
class TestLogPipelineRun:

    @patch("pipeline.mbta_db_loader.get_connection")
    def test_logs_successful_run(self, mock_conn):
        mock_cursor = MagicMock()
        mock_context = MagicMock()
        mock_context.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_context.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_conn.return_value.__enter__ = MagicMock(return_value=mock_context)
        mock_conn.return_value.__exit__ = MagicMock(return_value=False)

        started = datetime.now(timezone.utc)
        finished = datetime.now(timezone.utc)
        log_pipeline_run(started, finished, "success", 2393, None)
        assert mock_cursor.execute.called

    @patch("pipeline.mbta_db_loader.get_connection")
    def test_logs_failed_run_with_error(self, mock_conn):
        mock_cursor = MagicMock()
        mock_context = MagicMock()
        mock_context.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_context.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_conn.return_value.__enter__ = MagicMock(return_value=mock_context)
        mock_conn.return_value.__exit__ = MagicMock(return_value=False)

        started = datetime.now(timezone.utc)
        finished = datetime.now(timezone.utc)
        log_pipeline_run(started, finished, "failed", 0, "Connection refused")
        assert mock_cursor.execute.called


class TestInitSchema:

    @patch("pipeline.mbta_db_loader.get_connection")
    @patch("builtins.open")
    def test_reads_schema_file_and_executes(self, mock_open, mock_conn):
        mock_open.return_value.__enter__ = MagicMock(
            return_value=MagicMock(read=MagicMock(return_value="CREATE TABLE IF NOT EXISTS predictions();"))
        )
        mock_open.return_value.__exit__ = MagicMock(return_value=False)
        mock_cursor = MagicMock()
        mock_context = MagicMock()
        mock_context.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_context.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_conn.return_value.__enter__ = MagicMock(return_value=mock_context)
        mock_conn.return_value.__exit__ = MagicMock(return_value=False)
        init_schema()
        assert mock_cursor.execute.called

    @patch("pipeline.mbta_db_loader.get_connection")
    @patch("builtins.open")
    def test_raises_if_schema_file_missing(self, mock_open, mock_conn):
        mock_open.side_effect = FileNotFoundError("schema file not found")
        with pytest.raises(FileNotFoundError):
            init_schema()
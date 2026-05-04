"""Tests for Phase 1: Data Foundation (INFRA-01 through INFRA-04).

These tests are written RED-first: they call functions that don't exist yet
or have wrong signatures, so they will FAIL until implementation is complete.
"""
import json
import io
import sys
import os
import urllib.error
from unittest.mock import patch, MagicMock, call

import pytest

# Add repo root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from generate_dashboard import (
    notion_request,
    query_database,
)


# ---------------------------------------------------------------------------
# INFRA-02: Parameterized query_database
# ---------------------------------------------------------------------------

class TestQueryDatabaseParameterized:
    """INFRA-02: query_database accepts database_id parameter."""

    def test_query_database_parameterized(self, mock_notion_success):
        """query_database(database_id) calls notion_request with the provided
        database_id in the URL path, not the global DATABASE_ID."""
        mock_notion_success.return_value = {
            "results": [{"id": "page-1"}],
            "has_more": False,
            "next_cursor": None,
        }

        custom_db_id = "aaaa1111-bbbb-2222-cccc-333344445555"
        result = query_database(custom_db_id)

        # Verify it called notion_request with the custom DB ID in the path
        mock_notion_success.assert_called_once()
        call_args = mock_notion_success.call_args
        assert custom_db_id in call_args[0][1], (
            f"Expected database_id '{custom_db_id}' in URL path, "
            f"got: {call_args[0][1]}"
        )
        assert result == [{"id": "page-1"}]

    def test_query_database_with_filters(self, mock_notion_success):
        """query_database(database_id, filters={...}) includes the filter
        in the POST body."""
        mock_notion_success.return_value = {
            "results": [],
            "has_more": False,
            "next_cursor": None,
        }

        custom_db_id = "aaaa1111-bbbb-2222-cccc-333344445555"
        test_filter = {"property": "Estado", "select": {"equals": "Completado"}}
        query_database(custom_db_id, filters=test_filter)

        # Verify the filter was passed in the body
        call_args = mock_notion_success.call_args
        body = call_args[0][2]  # Third positional arg is body
        assert "filter" in body, "Expected 'filter' key in request body"
        assert body["filter"] == test_filter


# ---------------------------------------------------------------------------
# INFRA-03: Retry logic on notion_request
# ---------------------------------------------------------------------------

class TestRetryOn429:
    """INFRA-03: notion_request retries on HTTP 429."""

    def test_retry_on_429(self, mock_notion_error):
        """notion_request retries when it gets HTTP 429, eventually succeeds."""
        # Create mock responses: 2 failures then success
        error_429 = urllib.error.HTTPError(
            "https://api.notion.com/v1/test", 429, "Rate limited",
            {"Retry-After": "1"}, io.BytesIO(b"rate limited")
        )

        success_response = MagicMock()
        success_response.read.return_value = b'{"ok": true}'
        success_response.__enter__ = MagicMock(return_value=success_response)
        success_response.__exit__ = MagicMock(return_value=False)

        mock_notion_error.side_effect = [error_429, error_429, success_response]

        with patch("time.sleep"):  # Don't actually sleep in tests
            result = notion_request("GET", "/test")

        assert result == {"ok": True}
        assert mock_notion_error.call_count == 3


class TestRetryOnServerError:
    """INFRA-03: notion_request retries on 500, 502, 503, 504."""

    def test_retry_on_server_error(self, mock_notion_error):
        """notion_request retries on server errors (500, 502, 503, 504)."""
        for status_code in [500, 502, 503, 504]:
            mock_notion_error.reset_mock()

            error = urllib.error.HTTPError(
                "https://api.notion.com/v1/test", status_code,
                f"Server Error {status_code}",
                {}, io.BytesIO(b"server error")
            )

            success_response = MagicMock()
            success_response.read.return_value = b'{"ok": true}'
            success_response.__enter__ = MagicMock(return_value=success_response)
            success_response.__exit__ = MagicMock(return_value=False)

            mock_notion_error.side_effect = [error, success_response]

            with patch("time.sleep"):
                result = notion_request("GET", "/test")

            assert result == {"ok": True}, (
                f"Expected success after retry on {status_code}"
            )


class TestNoRetryOnClientError:
    """INFRA-03: notion_request does NOT retry on client errors."""

    def test_no_retry_on_client_error(self, mock_notion_error):
        """notion_request raises immediately on 400, 401, 403, 404."""
        for status_code in [400, 401, 403, 404]:
            mock_notion_error.reset_mock()

            error = urllib.error.HTTPError(
                "https://api.notion.com/v1/test", status_code,
                f"Client Error {status_code}",
                {}, io.BytesIO(b"client error")
            )
            mock_notion_error.side_effect = error

            with pytest.raises(urllib.error.HTTPError) as exc_info:
                with patch("time.sleep") as mock_sleep:
                    notion_request("GET", "/test")

            assert exc_info.value.code == status_code
            # Should NOT have retried (only 1 call to urlopen)
            assert mock_notion_error.call_count == 1, (
                f"Expected no retry on {status_code}, "
                f"but urlopen was called {mock_notion_error.call_count} times"
            )


class TestRetryRespectsRetryAfterHeader:
    """INFRA-03: notion_request uses Retry-After header value for sleep delay."""

    def test_retry_respects_retry_after_header(self, mock_notion_error):
        """When 429 response includes Retry-After header, the sleep delay
        uses that value (with jitter)."""
        retry_after_seconds = "5"
        error_429 = urllib.error.HTTPError(
            "https://api.notion.com/v1/test", 429, "Rate limited",
            {"Retry-After": retry_after_seconds}, io.BytesIO(b"rate limited")
        )

        success_response = MagicMock()
        success_response.read.return_value = b'{"ok": true}'
        success_response.__enter__ = MagicMock(return_value=success_response)
        success_response.__exit__ = MagicMock(return_value=False)

        mock_notion_error.side_effect = [error_429, success_response]

        with patch("time.sleep") as mock_sleep:
            with patch("random.uniform", return_value=0.0):  # No jitter for predictability
                result = notion_request("GET", "/test")

        assert result == {"ok": True}
        # Sleep should have been called with a value derived from Retry-After (5s)
        mock_sleep.assert_called_once()
        sleep_value = mock_sleep.call_args[0][0]
        # With Retry-After=5 and jitter range +/- 25%, expect 3.75 to 6.25
        # But with mocked random.uniform returning 0.0, jitter = 5 * 0.0 = 0
        # So delay = max(0.1, 5.0 + 0.0) = 5.0
        assert 3.5 <= sleep_value <= 7.0, (
            f"Expected sleep around 5s (Retry-After value), got {sleep_value}"
        )


# ---------------------------------------------------------------------------
# INFRA-01: State history parsing and normalization
# ---------------------------------------------------------------------------

class TestParseStateHistory:
    """INFRA-01: parse_state_history converts raw Notion results."""

    def test_parse_state_history(self, state_history_sample):
        """parse_state_history() converts raw Notion response into flat dicts
        with keys: Cambio, Cliente, EstadoAnterior, EstadoNuevo, FechaCambio,
        Motivo, Origen, TareaPeM."""
        from generate_dashboard import parse_state_history

        records = parse_state_history(state_history_sample["results"])

        assert len(records) == 3

        # Record 1: Prinorte
        r1 = records[0]
        assert r1["Cambio"] == "Tarea movida a En progreso"
        assert r1["Cliente"] == "Prinorte"
        assert r1["EstadoAnterior"] == "Pendiente"  # emoji stripped
        assert r1["EstadoNuevo"] == "En progreso"   # emoji stripped
        assert r1["Motivo"] == "Inicio de trabajo"
        assert r1["Origen"] == "Manual"
        assert r1["TareaPeM"] == ["task-id-abc"]

        # Record 2: Caren (has datetime with time component)
        r2 = records[1]
        assert r2["Cliente"] == "Caren"
        assert r2["EstadoAnterior"] == "En progreso"
        assert r2["EstadoNuevo"] == "Completado"

        # Record 3: El Muneco (empty relation, rework)
        r3 = records[2]
        assert r3["Cliente"] == "El Mu\u00f1eco"
        assert r3["EstadoAnterior"] == "Completado"
        assert r3["EstadoNuevo"] == "En progreso"
        assert r3["TareaPeM"] == []  # empty relation


class TestNormalizeState:
    """INFRA-01: normalize_state strips emoji prefixes."""

    def test_normalize_state(self):
        """normalize_state strips emoji prefixes correctly:
        - '\ud83d\udea6Pendiente' -> 'Pendiente' (emoji, no space)
        - '\ud83d\udd04 En progreso' -> 'En progreso' (emoji + space)
        - '\u2705 Completado' -> 'Completado'
        - None -> ''
        - '' -> ''
        """
        from generate_dashboard import normalize_state

        assert normalize_state("\ud83d\udea6Pendiente") == "Pendiente"
        assert normalize_state("\ud83d\udd04 En progreso") == "En progreso"
        assert normalize_state("\u2705 Completado") == "Completado"
        assert normalize_state(None) == ""
        assert normalize_state("") == ""


# ---------------------------------------------------------------------------
# INFRA-04: None convention and safe_ratio
# ---------------------------------------------------------------------------

class TestSafeRatio:
    """INFRA-04: safe_ratio returns None for insufficient data."""

    def test_safe_ratio(self):
        """safe_ratio: normal division, zero denominator, None inputs."""
        from generate_dashboard import safe_ratio

        assert safe_ratio(10, 5) == 2.0
        assert safe_ratio(10, 0) is None
        assert safe_ratio(None, 5) is None
        assert safe_ratio(10, None) is None


class TestNoneJsonSerialization:
    """INFRA-04: None serializes to JSON null."""

    def test_none_json_serialization(self):
        """json.dumps({'metric': None}) produces '{"metric": null}'."""
        result = json.dumps({"metric": None})
        assert result == '{"metric": null}'
        # Verify round-trip
        parsed = json.loads(result)
        assert parsed["metric"] is None


# ---------------------------------------------------------------------------
# Graceful Degradation: state history failure does not crash dashboard
# ---------------------------------------------------------------------------

class TestGracefulDegradation:
    """When state history query fails, main() still generates the dashboard."""

    def test_graceful_degradation_on_history_failure(self, monkeypatch, tmp_path):
        """When state history query fails, main() should still generate index.html."""
        import generate_dashboard

        # Set NOTION_TOKEN so main() doesn't exit
        monkeypatch.setattr(generate_dashboard, "NOTION_TOKEN", "test-token")

        # Create a minimal dashboard template in the project dir
        template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dashboard_template.html")
        original_template_exists = os.path.exists(template_path)

        # We need a template file -- use a minimal one if it already exists
        # Mock generate_html to avoid file dependency
        def mock_generate_html(records, now_str, kpis=None):
            return "<html>__DATA_JSON__</html>"

        monkeypatch.setattr(generate_dashboard, "generate_html", mock_generate_html)

        # Track calls to query_database
        call_count = [0]

        def mock_query_database(database_id, filters=None):
            call_count[0] += 1
            if database_id == generate_dashboard.DATABASE_ID:
                # Return minimal task data
                return [{
                    "properties": {
                        "Tarea": {"type": "title", "title": [{"plain_text": "Test task"}]},
                        "Tipo": {"type": "select", "select": {"name": "Desarrollo"}},
                        "Cliente": {"type": "select", "select": {"name": "Prinorte"}},
                        "Estado": {"type": "status", "status": {"name": "Pendiente"}},
                        "Fase": {"type": "select", "select": {"name": "1. Levantamiento"}},
                        "Fecha inicio": {"type": "date", "date": {"start": "2026-03-01", "end": None}},
                        "Fecha t\u00e9rmino": {"type": "date", "date": None},
                        "Bloqueado por": {"type": "rich_text", "rich_text": []},
                        "Notas": {"type": "rich_text", "rich_text": []},
                        "Responsables": {"type": "people", "people": []},
                    }
                }]
            elif database_id == generate_dashboard.STATE_HISTORY_DB_ID:
                # Simulate failure
                raise Exception("Connection timeout")
            return []

        monkeypatch.setattr(generate_dashboard, "query_database", mock_query_database)

        # Override __file__ path to write index.html to tmp_path
        output_path = os.path.join(str(tmp_path), "index.html")
        monkeypatch.setattr(
            generate_dashboard.os.path, "dirname",
            lambda f: str(tmp_path) if f == generate_dashboard.__file__ else os.path.dirname(f)
        )

        # Capture stderr
        captured_stderr = io.StringIO()
        monkeypatch.setattr(sys, "stderr", captured_stderr)

        # Run main
        generate_dashboard.main()

        # Verify index.html was created despite state history failure
        assert os.path.exists(output_path), "index.html should be created even when state history fails"

        # Verify warning was printed to stderr
        stderr_output = captured_stderr.getvalue()
        assert "WARNING: State history query failed" in stderr_output, (
            f"Expected warning about state history failure in stderr, got: {stderr_output}"
        )

        # Verify both databases were queried
        assert call_count[0] == 2, f"Expected 2 query_database calls, got {call_count[0]}"

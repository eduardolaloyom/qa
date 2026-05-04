"""Shared fixtures for PeM Dashboard test suite."""
import json
import os
import sys
from unittest.mock import patch, MagicMock

import pytest

# Add repo root to sys.path so we can import generate_dashboard
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import generate_dashboard


@pytest.fixture
def state_history_sample():
    """Load the state history sample fixture and return the parsed dict."""
    fixture_path = os.path.join(
        os.path.dirname(__file__), "fixtures", "state_history_sample.json"
    )
    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def mock_notion_success():
    """Patch generate_dashboard.notion_request to return a configurable response.

    Usage:
        def test_something(mock_notion_success):
            mock_notion_success.return_value = {"results": [], "has_more": False}
            result = generate_dashboard.query_database("some-db-id")
    """
    with patch.object(generate_dashboard, "notion_request") as mock_fn:
        yield mock_fn


@pytest.fixture
def tasks_sample():
    """Load the tasks sample fixture and return the parsed list."""
    fixture_path = os.path.join(
        os.path.dirname(__file__), "fixtures", "tasks_sample.json"
    )
    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def state_history_transitions():
    """Load parsed state history transitions fixture."""
    fixture_path = os.path.join(
        os.path.dirname(__file__), "fixtures", "state_history_transitions.json"
    )
    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def mock_notion_error():
    """Patch urllib.request.urlopen to raise HTTPError with configurable status codes.

    Supports side_effect lists for retry testing, e.g.:
        mock_notion_error.side_effect = [HTTPError(429), HTTPError(429), success_response]

    Usage:
        def test_retry(mock_notion_error):
            error = urllib.error.HTTPError(url, 429, "Rate limited", {}, None)
            mock_notion_error.side_effect = [error, error, mock_response]
    """
    with patch("urllib.request.urlopen") as mock_urlopen:
        yield mock_urlopen

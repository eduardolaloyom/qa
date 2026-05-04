"""Integration tests for KPI wiring into the generator pipeline.

Tests verify:
- compute_all_kpis returns all 11 KPI keys from both data tracks
- generate_html injects DATA_OPS alongside existing DATA
- Graceful degradation with empty/missing inputs
- No circular import issues
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from generate_dashboard import compute_all_kpis, generate_html

EXPECTED_KPI_KEYS = {
    "time_to_live", "cycle_time_stddev", "bug_rate",
    "atraso_promedio", "integraciones_en_tiempo", "capacidad_equipo",
    "retrabajo", "block_resolution_time", "bug_recurrence",
    "cruce_limpio", "tasa_rechazo",
}

DATE_MATH_KEYS = {
    "time_to_live", "cycle_time_stddev", "bug_rate",
    "atraso_promedio", "integraciones_en_tiempo", "capacidad_equipo",
}

STATE_HISTORY_KEYS = {
    "retrabajo", "block_resolution_time", "bug_recurrence",
    "cruce_limpio", "tasa_rechazo",
}

# Minimal record for generate_html tests -- has all fields the function reads
MINIMAL_RECORD = {
    "PageId": "test-page-001",
    "Tarea": "Test task",
    "Tipo": "Tarea",
    "Cliente": "TestClient",
    "Estado": "Completado",
    "Fase": "1. Levantamiento",
    "FechaInicio": "2025-01-01",
    "FechaTermino": "2025-01-15",
    "FechaFinalizacion": "2025-01-20",
    "Bloqueado": "",
    "Notas": "",
    "Responsables": [],
    "Relacion": [],
}

NOW_STR = "2025-01-01T00:00:00Z"


class TestComputeAllKpis:
    """Tests for compute_all_kpis orchestrator function."""

    def test_compute_all_kpis_returns_11_keys(self, tasks_sample, state_history_transitions):
        result = compute_all_kpis(tasks_sample, state_history_transitions)
        assert set(result.keys()) == EXPECTED_KPI_KEYS

    def test_compute_all_kpis_no_key_overlap(self, tasks_sample, state_history_transitions):
        result = compute_all_kpis(tasks_sample, state_history_transitions)
        date_keys = set(result.keys()) & DATE_MATH_KEYS
        history_keys = set(result.keys()) & STATE_HISTORY_KEYS
        assert len(date_keys & history_keys) == 0, "Date-math and state-history keys must not overlap"

    def test_compute_all_kpis_empty_history(self, tasks_sample):
        result = compute_all_kpis(tasks_sample, [])
        assert set(result.keys()) == EXPECTED_KPI_KEYS
        # Date-math KPIs should still compute normally
        assert result["time_to_live"] is not None

    def test_compute_all_kpis_empty_records(self):
        result = compute_all_kpis([], [])
        assert set(result.keys()) == EXPECTED_KPI_KEYS


class TestGenerateHtmlDataOps:
    """Tests for DATA_OPS injection into generated HTML."""

    def test_generate_html_includes_data_ops(self):
        kpis = {k: {} for k in EXPECTED_KPI_KEYS}
        html = generate_html([MINIMAL_RECORD], NOW_STR, kpis)
        assert "const DATA_OPS = " in html
        assert "__DATA_OPS_JSON__" not in html

    def test_generate_html_preserves_data(self):
        kpis = {k: {} for k in EXPECTED_KPI_KEYS}
        html = generate_html([MINIMAL_RECORD], NOW_STR, kpis)
        assert "const DATA = " in html
        assert "__DATA_JSON__" not in html

    def test_generate_html_kpis_none_fallback(self):
        html = generate_html([MINIMAL_RECORD], NOW_STR, kpis=None)
        assert "const DATA_OPS = {};" in html or "const DATA_OPS = {}" in html

    def test_generated_html_under_200kb(self):
        kpis = {k: {} for k in EXPECTED_KPI_KEYS}
        html = generate_html([MINIMAL_RECORD], NOW_STR, kpis)
        assert len(html) < 200 * 1024, f"HTML is {len(html)} bytes, exceeds 200KB limit"


class TestCircularImport:
    """Test that importing compute_all_kpis does not trigger circular imports."""

    def test_no_circular_import(self):
        from generate_dashboard import compute_all_kpis
        assert callable(compute_all_kpis)

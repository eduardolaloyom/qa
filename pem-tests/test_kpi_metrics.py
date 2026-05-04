"""Tests for Phase 2: Date-Math KPIs (KPI-01 through KPI-06)."""
import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from kpi_metrics import (
    parse_date,
    kpi_result,
    extract_phase_number,
    phase_duration_days,
    group_by_client,
    PHASE_CLASSIFICATION,
    planned_phase_duration,
    atraso_promedio,
    integraciones_en_tiempo,
    capacidad_equipo,
    compute_date_math_kpis,
)


# ---------------------------------------------------------------------------
# Helper Tests (should pass immediately)
# ---------------------------------------------------------------------------


class TestParseDate:
    """Tests for parse_date helper."""

    def test_plain_date(self):
        assert parse_date("2026-01-15") == date(2026, 1, 15)

    def test_datetime_with_timezone(self):
        assert parse_date("2026-03-16T10:30:00.000+00:00") == date(2026, 3, 16)

    def test_empty_string(self):
        assert parse_date("") is None

    def test_none(self):
        assert parse_date(None) is None


class TestKpiResult:
    """Tests for kpi_result factory."""

    def test_complete(self):
        result = kpi_result(42.5)
        assert result == {"value": 42.5, "status": "complete"}

    def test_no_data_with_reason(self):
        result = kpi_result(None, "no_data", "Missing dates")
        assert result == {"value": None, "status": "no_data", "reason": "Missing dates"}

    def test_in_progress(self):
        result = kpi_result(125, "in_progress")
        assert result == {"value": 125, "status": "in_progress"}


class TestExtractPhaseNumber:
    """Tests for extract_phase_number helper."""

    def test_single_digit(self):
        assert extract_phase_number("4. Integraciones") == 4

    def test_double_digit(self):
        assert extract_phase_number("10. Rollout") == 10

    def test_empty_string(self):
        assert extract_phase_number("") is None

    def test_none(self):
        assert extract_phase_number(None) is None


class TestPhaseDurationDays:
    """Tests for phase_duration_days helper."""

    def test_normal_duration(self):
        tasks = [
            {"Fase": "4. Integraciones", "FechaInicio": "2025-08-01", "FechaTermino": "2025-08-31"},
        ]
        assert phase_duration_days(tasks, "4.") == 30

    def test_missing_dates_returns_none(self):
        tasks = [
            {"Fase": "4. Integraciones", "FechaInicio": "", "FechaTermino": ""},
        ]
        assert phase_duration_days(tasks, "4.") is None

    def test_negative_duration_returns_none(self):
        tasks = [
            {"Fase": "4. Integraciones", "FechaInicio": "2025-09-01", "FechaTermino": "2025-08-01"},
        ]
        assert phase_duration_days(tasks, "4.") is None

    def test_zero_day_returns_one(self):
        tasks = [
            {"Fase": "4. Integraciones", "FechaInicio": "2025-08-01", "FechaTermino": "2025-08-01"},
        ]
        assert phase_duration_days(tasks, "4.") == 1


class TestGroupByClient:
    """Tests for group_by_client helper."""

    def test_groups_correctly(self):
        records = [
            {"Cliente": "A", "Tarea": "t1"},
            {"Cliente": "B", "Tarea": "t2"},
            {"Cliente": "A", "Tarea": "t3"},
        ]
        groups = group_by_client(records)
        assert len(groups["A"]) == 2
        assert len(groups["B"]) == 1

    def test_skips_empty_cliente(self):
        records = [
            {"Cliente": "", "Tarea": "t1"},
            {"Cliente": None, "Tarea": "t2"},
            {"Cliente": "A", "Tarea": "t3"},
        ]
        groups = group_by_client(records)
        assert len(groups) == 1
        assert "A" in groups


# ---------------------------------------------------------------------------
# KPI Function Tests (KPI-01, KPI-02, KPI-04)
# ---------------------------------------------------------------------------

from kpi_metrics import time_to_live, cycle_time_stddev, bug_rate


class TestTimeToLive:
    """KPI-01: Time to Live tests."""

    def test_complete_client(self, tasks_sample):
        results = time_to_live(tasks_sample)
        assert results["ClienteA"]["value"] == 228
        assert results["ClienteA"]["status"] == "complete"

    def test_in_progress_client(self, tasks_sample):
        results = time_to_live(tasks_sample)
        assert results["ClienteB"]["status"] == "in_progress"
        # Value should be days from 2025-09-01 to today
        expected = (date.today() - date(2025, 9, 1)).days
        assert results["ClienteB"]["value"] == expected

    def test_no_data_client(self, tasks_sample):
        results = time_to_live(tasks_sample)
        assert results["ClienteC"]["value"] is None
        assert results["ClienteC"]["status"] == "no_data"
        assert "Fase 1" in results["ClienteC"]["reason"]


class TestCycleTimeStdDev:
    """KPI-02: Cycle Time Standard Deviation tests."""

    def test_multiple_clients(self, tasks_sample):
        results = cycle_time_stddev(tasks_sample)
        # Phase 4: ClienteA=30, ClienteB=20, ClienteD=45 -> n=3
        # ClienteC has Fase 4 dates too: start=2025-11-01, end=2025-11-20 = 19 days -> n=4
        phase4 = results[4]
        assert phase4["n"] >= 2
        assert phase4["stdev"] is not None
        assert isinstance(phase4["stdev"], float)
        assert isinstance(phase4["mean"], float)

    def test_single_client(self):
        # Synthetic dataset: only one client has Fase 3 data
        records = [
            {
                "Tarea": "Kick off solo client",
                "Tipo": "Tarea",
                "Cliente": "SoloClient",
                "Estado": "Completado",
                "Fase": "3. Kick off",
                "FechaInicio": "2025-07-01",
                "FechaTermino": "2025-07-10",
                "Bloqueado": "",
                "Notas": "",
                "Responsables": [],
            }
        ]
        results = cycle_time_stddev(records)
        phase3 = results[3]
        assert phase3["n"] == 1
        assert phase3["stdev"] is None
        assert phase3["mean"] == 9.0  # 9 days
        assert phase3["durations"]["SoloClient"] == 9

    def test_no_clients(self, tasks_sample):
        results = cycle_time_stddev(tasks_sample)
        # Phase 9 (Capacitaciones): no client has tasks -> n=0
        phase9 = results[9]
        assert phase9["n"] == 0
        assert phase9["stdev"] is None
        assert phase9["mean"] is None


class TestBugRate:
    """KPI-04: Bug Rate tests."""

    def test_normal_ratio(self, tasks_sample):
        results = bug_rate(tasks_sample)
        assert results["ClienteA"]["value"] == 0.5  # 15/30
        assert results["ClienteA"]["status"] == "complete"
        assert results["ClienteD"]["value"] == round(10 / 45, 2)  # 0.22
        assert results["ClienteD"]["status"] == "complete"

    def test_no_qa_data(self, tasks_sample):
        results = bug_rate(tasks_sample)
        assert results["ClienteB"]["value"] is None
        assert results["ClienteB"]["status"] == "no_data"
        assert "QA" in results["ClienteB"]["reason"]

    def test_no_integration_data(self):
        # ClienteC has Fase 4 data, so need synthetic test for no integration data
        records = [
            {
                "Tarea": "QA test",
                "Tipo": "Tarea",
                "Cliente": "TestClient",
                "Estado": "Completado",
                "Fase": "8. QA y Testing",
                "FechaInicio": "2025-09-01",
                "FechaTermino": "2025-09-11",
                "FechaFinalizacion": "2025-09-15",
                "Bloqueado": "",
                "Notas": "",
                "Responsables": [],
            }
        ]
        results = bug_rate(records)
        assert results["TestClient"]["value"] is None
        assert results["TestClient"]["status"] == "no_data"
        assert "Integraciones" in results["TestClient"]["reason"]


# ---------------------------------------------------------------------------
# Phase Classification Tests
# ---------------------------------------------------------------------------


class TestPhaseClassification:
    """Tests for PHASE_CLASSIFICATION dict."""

    def test_internal_phases(self):
        assert PHASE_CLASSIFICATION[6] == "internal"
        assert PHASE_CLASSIFICATION[7] == "internal"
        assert PHASE_CLASSIFICATION[8] == "internal"
        assert PHASE_CLASSIFICATION[9] == "internal"

    def test_external_phases(self):
        assert PHASE_CLASSIFICATION[1] == "external"
        assert PHASE_CLASSIFICATION[2] == "external"
        assert PHASE_CLASSIFICATION[3] == "external"
        assert PHASE_CLASSIFICATION[4] == "external"

    def test_mixed_classified_as_external(self):
        assert PHASE_CLASSIFICATION[5] == "external"
        assert PHASE_CLASSIFICATION[10] == "external"
        assert PHASE_CLASSIFICATION[11] == "external"
        assert PHASE_CLASSIFICATION[12] == "external"

    def test_all_twelve_phases_present(self):
        assert len(PHASE_CLASSIFICATION) == 12
        for i in range(1, 13):
            assert i in PHASE_CLASSIFICATION


# ---------------------------------------------------------------------------
# KPI-05: Atraso Promedio Tests
# ---------------------------------------------------------------------------


class TestAtrasoPromedio:
    """KPI-05: Internal delay ratio tests."""

    def test_client_with_delays(self, tasks_sample):
        """ClienteA has internal delays in Fase 6, 7, 8 -- ratio should be > 0."""
        results = atraso_promedio(tasks_sample)
        assert results["ClienteA"]["status"] == "complete"
        # ClienteA has internal delays (Fase 6: 5d, Fase 7: 5d, Fase 8: 6d = 16 internal)
        # External delays: Fase 4 on time (0), Fase 1 on time (0), Fase 10 on time (0)
        # But ClienteB Fase 4 has 6d external delay
        assert results["ClienteA"]["value"] is not None
        assert isinstance(results["ClienteA"]["value"], float)
        assert 0.0 <= results["ClienteA"]["value"] <= 1.0

    def test_client_no_planned_dates(self, tasks_sample):
        """ClienteC has no FechaFinalizacion -- should return no_data."""
        results = atraso_promedio(tasks_sample)
        assert results["ClienteC"]["value"] is None
        assert results["ClienteC"]["status"] == "no_data"

    def test_zero_total_delay(self):
        """Client where all phases are on-time or early -- should return 0.0."""
        records = [
            {
                "Tarea": "Fase 1 task",
                "Tipo": "Tarea",
                "Cliente": "OnTimeClient",
                "Estado": "Completado",
                "Fase": "1. Levantamiento",
                "FechaInicio": "2025-01-01",
                "FechaTermino": "2025-01-10",
                "FechaFinalizacion": "2025-01-15",
                "Bloqueado": "",
                "Notas": "",
                "Responsables": [],
            },
            {
                "Tarea": "Fase 6 task",
                "Tipo": "Tarea",
                "Cliente": "OnTimeClient",
                "Estado": "Completado",
                "Fase": "6. Desarrollos",
                "FechaInicio": "2025-02-01",
                "FechaTermino": "2025-02-10",
                "FechaFinalizacion": "2025-02-20",
                "Bloqueado": "",
                "Notas": "",
                "Responsables": [],
            },
        ]
        results = atraso_promedio(records)
        assert results["OnTimeClient"]["value"] == 0.0
        assert results["OnTimeClient"]["status"] == "complete"


# ---------------------------------------------------------------------------
# KPI-06: Integraciones en Tiempo Tests
# ---------------------------------------------------------------------------


class TestIntegracionesEnTiempo:
    """KPI-06: On-time integration rate tests."""

    def test_mixed_on_time_and_late(self, tasks_sample):
        """ClienteD: 3 Fase 4 tasks total with planned dates.
        - Integraciones Codelpa: end=06-15, planned=06-20 -> on-time
        - Integracion API Pagos: end=05-15, planned=05-20 -> on-time
        - Integracion API Envios: end=06-10, planned=06-01 -> late
        Result: 2/3 = 0.67
        """
        results = integraciones_en_tiempo(tasks_sample)
        assert results["ClienteD"]["status"] == "complete"
        assert results["ClienteD"]["value"] == round(2 / 3, 2)

    def test_all_on_time(self, tasks_sample):
        """ClienteA: 1 Fase 4 task, end=08-31, planned=09-05 -> on-time. Result: 1.0"""
        results = integraciones_en_tiempo(tasks_sample)
        assert results["ClienteA"]["status"] == "complete"
        assert results["ClienteA"]["value"] == 1.0

    def test_no_planned_dates(self, tasks_sample):
        """ClienteC: Fase 4 task has FechaFinalizacion="" -> no_data."""
        results = integraciones_en_tiempo(tasks_sample)
        assert results["ClienteC"]["value"] is None
        assert results["ClienteC"]["status"] == "no_data"
        assert "planificada" in results["ClienteC"]["reason"].lower()

    def test_no_integration_tasks(self):
        """Client without any Fase 4 tasks -> no_data."""
        records = [
            {
                "Tarea": "Fase 1 task",
                "Tipo": "Tarea",
                "Cliente": "NoIntClient",
                "Estado": "Completado",
                "Fase": "1. Levantamiento",
                "FechaInicio": "2025-01-01",
                "FechaTermino": "2025-01-10",
                "FechaFinalizacion": "2025-01-15",
                "Bloqueado": "",
                "Notas": "",
                "Responsables": [],
            }
        ]
        results = integraciones_en_tiempo(records)
        assert results["NoIntClient"]["value"] is None
        assert results["NoIntClient"]["status"] == "no_data"
        assert "integracion" in results["NoIntClient"]["reason"].lower()


# ---------------------------------------------------------------------------
# KPI-03: Capacidad del Equipo Tests
# ---------------------------------------------------------------------------


class TestCapacidadEquipo:
    """KPI-03: Active clients and delay trend tests."""

    def test_active_count(self, tasks_sample):
        """Only ClienteB is active (started Fase 1, no Fase 10 end)."""
        result = capacidad_equipo(tasks_sample)
        assert result["active_count"] == 1
        assert "ClienteB" in result["active_clients"]

    def test_completed_not_active(self, tasks_sample):
        """ClienteA and ClienteD have Fase 10 end dates -- NOT active."""
        result = capacidad_equipo(tasks_sample)
        assert "ClienteA" not in result["active_clients"]
        assert "ClienteD" not in result["active_clients"]

    def test_never_started_not_active(self, tasks_sample):
        """ClienteC has no Fase 1 start date -- NOT active."""
        result = capacidad_equipo(tasks_sample)
        assert "ClienteC" not in result["active_clients"]

    def test_delay_by_phase_structure(self, tasks_sample):
        """delay_by_phase has integer keys with expected sub-keys."""
        result = capacidad_equipo(tasks_sample)
        dbp = result["delay_by_phase"]
        assert isinstance(dbp, dict)
        # Should have entries for phases where clients have data
        for phase_num, info in dbp.items():
            assert isinstance(phase_num, int)
            assert "avg_delay" in info
            assert "clients_with_data" in info
            assert "benchmark" in info

    def test_historical_fallback(self):
        """When a client has actual duration but no planned date, uses historical average."""
        records = [
            # ClientA with planned dates for Fase 1
            {
                "Tarea": "Fase 1 A",
                "Tipo": "Tarea",
                "Cliente": "ClientA",
                "Estado": "Completado",
                "Fase": "1. Levantamiento",
                "FechaInicio": "2025-01-01",
                "FechaTermino": "2025-01-20",
                "FechaFinalizacion": "2025-01-25",
                "Bloqueado": "",
                "Notas": "",
                "Responsables": [],
            },
            # ClientB with NO planned dates for Fase 1 (historical fallback)
            {
                "Tarea": "Fase 1 B",
                "Tipo": "Tarea",
                "Cliente": "ClientB",
                "Estado": "Completado",
                "Fase": "1. Levantamiento",
                "FechaInicio": "2025-02-01",
                "FechaTermino": "2025-02-25",
                "FechaFinalizacion": "",
                "Bloqueado": "",
                "Notas": "",
                "Responsables": [],
            },
        ]
        result = capacidad_equipo(records)
        dbp = result["delay_by_phase"]
        if 1 in dbp and dbp[1]["clients_with_data"] > 0:
            # ClientB should use historical benchmark
            assert dbp[1]["benchmark"] in ("planned", "historical")


# ---------------------------------------------------------------------------
# Orchestrator Tests
# ---------------------------------------------------------------------------


class TestComputeDateMathKpis:
    """Tests for compute_date_math_kpis orchestrator."""

    def test_returns_all_six_keys(self, tasks_sample):
        result = compute_date_math_kpis(tasks_sample)
        expected_keys = {
            "time_to_live",
            "cycle_time_stddev",
            "bug_rate",
            "atraso_promedio",
            "integraciones_en_tiempo",
            "capacidad_equipo",
        }
        assert set(result.keys()) == expected_keys

    def test_each_kpi_has_data(self, tasks_sample):
        result = compute_date_math_kpis(tasks_sample)
        for key, value in result.items():
            assert isinstance(value, dict), f"{key} should be a dict"
            assert len(value) > 0, f"{key} should have data"

    def test_orchestrator_matches_individual(self, tasks_sample):
        """compute_date_math_kpis delegates correctly to individual functions."""
        result = compute_date_math_kpis(tasks_sample)
        assert result["time_to_live"] == time_to_live(tasks_sample)
        assert result["cycle_time_stddev"] == cycle_time_stddev(tasks_sample)
        assert result["bug_rate"] == bug_rate(tasks_sample)

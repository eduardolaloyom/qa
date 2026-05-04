"""Tests for Phase 3: State-History KPIs (KPI-07 through KPI-11 + Orchestrator)."""
import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from state_history_kpis import (
    BACKWARD_TRANSITIONS,
    is_backward_transition,
    group_by_task,
    extract_block_episodes,
    retrabajo_ratio,
    block_resolution_time,
    bug_recurrence,
    cruce_limpio_rate,
    tasa_rechazo,
    compute_state_history_kpis,
)


# ---------------------------------------------------------------------------
# Helper Tests (should pass immediately)
# ---------------------------------------------------------------------------


class TestIsBackwardTransition:
    """Tests for is_backward_transition helper."""

    def test_done_to_progress_is_backward(self):
        assert is_backward_transition("Completado", "En progreso") is True

    def test_done_to_pending_is_backward(self):
        assert is_backward_transition("Completado", "Pendiente") is True

    def test_review_to_progress_is_backward(self):
        assert is_backward_transition("En revision", "En progreso") is True

    def test_review_to_pending_is_backward(self):
        assert is_backward_transition("En revision", "Pendiente") is True

    def test_blocked_to_pending_is_backward(self):
        assert is_backward_transition("Bloqueado", "Pendiente") is True

    def test_progress_to_pending_is_backward(self):
        assert is_backward_transition("En progreso", "Pendiente") is True

    def test_pending_to_progress_is_forward(self):
        assert is_backward_transition("Pendiente", "En progreso") is False

    def test_progress_to_review_is_forward(self):
        assert is_backward_transition("En progreso", "En revision") is False

    def test_progress_to_blocked_is_not_rework(self):
        assert is_backward_transition("En progreso", "Bloqueado") is False

    def test_blocked_to_progress_is_not_rework(self):
        assert is_backward_transition("Bloqueado", "En progreso") is False

    def test_unknown_states_return_false(self):
        assert is_backward_transition("Desconocido", "En progreso") is False

    def test_backward_transitions_set_size(self):
        assert len(BACKWARD_TRANSITIONS) == 6


class TestGroupByTask:
    """Tests for group_by_task helper."""

    def test_groups_by_single_task_id(self):
        records = [
            {"TareaPeM": ["task-001"], "Cambio": "a"},
            {"TareaPeM": ["task-001"], "Cambio": "b"},
            {"TareaPeM": ["task-002"], "Cambio": "c"},
        ]
        groups = group_by_task(records)
        assert len(groups["task-001"]) == 2
        assert len(groups["task-002"]) == 1

    def test_empty_tarea_gets_unlinked_key(self):
        records = [
            {"TareaPeM": [], "Cambio": "unlinked"},
        ]
        groups = group_by_task(records)
        assert "_unlinked_0" in groups
        assert len(groups["_unlinked_0"]) == 1

    def test_multiple_task_ids_per_record(self):
        records = [
            {"TareaPeM": ["task-A", "task-B"], "Cambio": "shared"},
        ]
        groups = group_by_task(records)
        assert len(groups["task-A"]) == 1
        assert len(groups["task-B"]) == 1

    def test_empty_records(self):
        groups = group_by_task([])
        assert len(groups) == 0


class TestExtractBlockEpisodes:
    """Tests for extract_block_episodes helper."""

    def test_extracts_paired_episodes(self):
        transitions = [
            {"EstadoAnterior": "En progreso", "EstadoNuevo": "Bloqueado", "FechaCambio": "2026-03-04"},
            {"EstadoAnterior": "Bloqueado", "EstadoNuevo": "En progreso", "FechaCambio": "2026-03-07"},
        ]
        episodes = extract_block_episodes(transitions)
        assert len(episodes) == 1
        assert episodes[0] == (date(2026, 3, 4), date(2026, 3, 7))

    def test_excludes_open_blocks(self):
        transitions = [
            {"EstadoAnterior": "En progreso", "EstadoNuevo": "Bloqueado", "FechaCambio": "2026-03-03"},
        ]
        episodes = extract_block_episodes(transitions)
        assert len(episodes) == 0

    def test_multiple_episodes(self):
        transitions = [
            {"EstadoAnterior": "En progreso", "EstadoNuevo": "Bloqueado", "FechaCambio": "2026-03-04"},
            {"EstadoAnterior": "Bloqueado", "EstadoNuevo": "En progreso", "FechaCambio": "2026-03-07"},
            {"EstadoAnterior": "En progreso", "EstadoNuevo": "Bloqueado", "FechaCambio": "2026-03-09"},
            {"EstadoAnterior": "Bloqueado", "EstadoNuevo": "En progreso", "FechaCambio": "2026-03-12"},
        ]
        episodes = extract_block_episodes(transitions)
        assert len(episodes) == 2
        assert episodes[0] == (date(2026, 3, 4), date(2026, 3, 7))
        assert episodes[1] == (date(2026, 3, 9), date(2026, 3, 12))

    def test_empty_transitions(self):
        episodes = extract_block_episodes([])
        assert len(episodes) == 0


# ---------------------------------------------------------------------------
# KPI Function Tests (should FAIL on NotImplementedError stubs)
# ---------------------------------------------------------------------------


class TestRetrabajoRatio:
    """KPI-07: Retrabajo ratio tests."""

    def test_cliente_a_rework(self, state_history_transitions):
        """ClienteA: 6 tasks, 3 with backward transitions (task-001, page-a-qa, page-a-qa2). Retrabajo = 3/6."""
        results = retrabajo_ratio(state_history_transitions)
        assert results["ClienteA"]["status"] == "complete"
        assert results["ClienteA"]["value"] == round(3 / 6, 4)

    def test_cliente_b_no_rework(self, state_history_transitions):
        """ClienteB: 4 tasks, 0 backward transitions. Retrabajo = 0.0."""
        results = retrabajo_ratio(state_history_transitions)
        assert results["ClienteB"]["status"] == "complete"
        assert results["ClienteB"]["value"] == 0.0

    def test_empty_records_returns_empty_dict(self):
        """No records -> empty dict."""
        results = retrabajo_ratio([])
        assert results == {}

    def test_skips_unlinked_records(self, state_history_transitions):
        """Unlinked record (empty TareaPeM) should not affect task counts."""
        results = retrabajo_ratio(state_history_transitions)
        # ClienteA has 6 linked tasks (unlinked record excluded)
        assert results["ClienteA"]["value"] == round(3 / 6, 4)


class TestBlockResolutionTime:
    """KPI-08: Block resolution time tests."""

    def test_cliente_a_avg_block_time(self, state_history_transitions):
        """ClienteA: task-002 has 2 episodes of 3 days each. Avg = 3.0."""
        results = block_resolution_time(state_history_transitions)
        assert results["ClienteA"]["status"] == "complete"
        assert results["ClienteA"]["value"] == 3.0

    def test_cliente_b_no_blocks(self, state_history_transitions):
        """ClienteB: no block episodes. Returns no_data."""
        results = block_resolution_time(state_history_transitions)
        assert results["ClienteB"]["status"] == "no_data"
        assert results["ClienteB"]["value"] is None

    def test_cliente_d_open_block_excluded(self, state_history_transitions):
        """ClienteD: task-006 still blocked (excluded), task-007 has 1 episode of 2 days."""
        results = block_resolution_time(state_history_transitions)
        assert results["ClienteD"]["status"] == "complete"
        assert results["ClienteD"]["value"] == 2.0

    def test_empty_records(self):
        """No records -> empty dict."""
        results = block_resolution_time([])
        assert results == {}


class TestBugRecurrence:
    """KPI-09: Bug recurrence tests."""

    def test_cliente_a_recurrence(self, state_history_transitions):
        """ClienteA: task-002 blocked 2x, page-a-rollout blocked 1x. 1 with 2+ / 2 with any = 0.5."""
        results = bug_recurrence(state_history_transitions)
        assert results["ClienteA"]["status"] == "complete"
        assert results["ClienteA"]["value"] == 0.5

    def test_cliente_b_no_blocks(self, state_history_transitions):
        """ClienteB: no block episodes. Returns no_data."""
        results = bug_recurrence(state_history_transitions)
        assert results["ClienteB"]["status"] == "no_data"
        assert results["ClienteB"]["value"] is None

    def test_cliente_d_no_recurrence(self, state_history_transitions):
        """ClienteD: task-006 blocked 1x, task-007 blocked 1x. 0 with 2+ / 2 with any = 0.0."""
        results = bug_recurrence(state_history_transitions)
        assert results["ClienteD"]["status"] == "complete"
        assert results["ClienteD"]["value"] == 0.0

    def test_empty_records(self):
        """No records -> empty dict."""
        results = bug_recurrence([])
        assert results == {}


# ---------------------------------------------------------------------------
# Phase-Scoped KPI Tests (KPI-10, KPI-11) -- require both fixtures
# ---------------------------------------------------------------------------


class TestCruceLimpio:
    """KPI-10: Cruce Limpio Rate tests."""

    def test_clean_rollout(self, state_history_transitions, tasks_sample):
        """ClienteB has Rollout task (page-b-rollout), no blocks -> 100."""
        results = cruce_limpio_rate(state_history_transitions, tasks_sample)
        assert results["ClienteB"]["value"] == 100
        assert results["ClienteB"]["status"] == "complete"
        assert "approximate" in results["ClienteB"]["reason"]

    def test_dirty_rollout(self, state_history_transitions, tasks_sample):
        """ClienteA has Rollout task (page-a-rollout) with blocked transition -> 0."""
        results = cruce_limpio_rate(state_history_transitions, tasks_sample)
        assert results["ClienteA"]["value"] == 0
        assert results["ClienteA"]["status"] == "complete"
        assert "approximate" in results["ClienteA"]["reason"]

    def test_no_rollout_tasks(self, state_history_transitions, tasks_sample):
        """ClienteC has no Rollout tasks in task_records -> N/A."""
        results = cruce_limpio_rate(state_history_transitions, tasks_sample)
        assert results["ClienteC"]["value"] is None
        assert results["ClienteC"]["status"] == "no_data"
        assert "approximate" in results["ClienteC"]["reason"]

    def test_approximate_label(self, state_history_transitions, tasks_sample):
        """All results contain 'approximate' in reason field."""
        results = cruce_limpio_rate(state_history_transitions, tasks_sample)
        for client, result in results.items():
            assert "approximate" in result.get("reason", ""), (
                f"{client} missing 'approximate' in reason"
            )

    def test_no_task_records(self, state_history_transitions):
        """When task_records=None, all clients get no_data."""
        results = cruce_limpio_rate(state_history_transitions, None)
        for client, result in results.items():
            assert result["status"] == "no_data"
            assert result["value"] is None


class TestTasaRechazo:
    """KPI-11: Tasa de Rechazo tests."""

    def test_with_rejections(self, state_history_transitions, tasks_sample):
        """ClienteA: page-a-qa has 1 rejection (rate=0.5), page-a-qa2 has 2 rejections (rate=0.6667).
        Average = (0.5 + 0.6667) / 2 = 0.5833."""
        results = tasa_rechazo(state_history_transitions, tasks_sample)
        assert results["ClienteA"]["status"] == "complete"
        # page-a-qa: 1 rejection, 2 attempts, rate = 1/2 = 0.5
        # page-a-qa2: 2 rejections, 3 attempts, rate = 2/3 = 0.6667
        # Average: (0.5 + 0.6667) / 2 = 0.5833
        assert results["ClienteA"]["value"] == round((0.5 + 2 / 3) / 2, 4)

    def test_no_rejections(self, state_history_transitions, tasks_sample):
        """ClienteB: page-b-qa has 0 rejections -> kpi_result(0.0, 'complete')."""
        results = tasa_rechazo(state_history_transitions, tasks_sample)
        assert results["ClienteB"]["status"] == "complete"
        assert results["ClienteB"]["value"] == 0.0

    def test_no_qa_tasks(self, state_history_transitions, tasks_sample):
        """ClienteC has no QA tasks -> N/A."""
        results = tasa_rechazo(state_history_transitions, tasks_sample)
        assert results["ClienteC"]["value"] is None
        assert results["ClienteC"]["status"] == "no_data"

    def test_attempts_formula(self, state_history_transitions, tasks_sample):
        """Verify per-task: 1 rejection = 2 attempts, 2 rejections = 3 attempts."""
        # page-a-qa: review->progress (backward) = 1 rejection, attempts = 2, rate = 0.5
        # page-a-qa2: 2 x review->progress (backward) = 2 rejections, attempts = 3, rate = 2/3
        results = tasa_rechazo(state_history_transitions, tasks_sample)
        # The average of 0.5 and 2/3 confirms attempts formula is correct
        expected = round((1 / 2 + 2 / 3) / 2, 4)
        assert results["ClienteA"]["value"] == expected


class TestOrchestrator:
    """Tests for compute_state_history_kpis orchestrator."""

    def test_returns_all_five_keys(self, state_history_transitions, tasks_sample):
        """compute_state_history_kpis returns dict with exactly 5 KPI keys."""
        result = compute_state_history_kpis(state_history_transitions, tasks_sample)
        expected_keys = {"retrabajo", "block_resolution_time", "bug_recurrence",
                         "cruce_limpio", "tasa_rechazo"}
        assert set(result.keys()) == expected_keys

    def test_with_empty_records(self, tasks_sample):
        """Empty history_records returns empty dicts for first 3 KPIs.
        Phase-scoped KPIs still return results for clients with Rollout/QA tasks
        (100 for cruce_limpio since no blocked transitions, no_data for tasa_rechazo
        since no transitions found in empty history)."""
        result = compute_state_history_kpis([], tasks_sample)
        assert result["retrabajo"] == {}
        assert result["block_resolution_time"] == {}
        assert result["bug_recurrence"] == {}
        # Phase-scoped KPIs with empty history but valid task_records ->
        # Clients with Rollout tasks get 100 (clean, no blocks in empty history)
        for client in result["cruce_limpio"]:
            r = result["cruce_limpio"][client]
            if r["status"] == "complete":
                assert r["value"] == 100
        # Clients with QA tasks but no history -> no_data (no transitions)
        for client in result["tasa_rechazo"]:
            r = result["tasa_rechazo"][client]
            assert r["status"] == "no_data"

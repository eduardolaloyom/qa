"""State History KPIs -- transition-based KPI functions for PeM Dashboard.

Each KPI function accepts a list of parsed state history records
(from parse_state_history()) and returns a dict mapping client name
to a kpi_result dict.
"""
from collections import defaultdict

from generate_dashboard import state_key, safe_ratio
from kpi_metrics import kpi_result, parse_date, group_by_client

# Explicit backward transition pairs (from CONTEXT.md locked decisions).
# These are workflow regressions, NOT block/unblock transitions.
BACKWARD_TRANSITIONS = {
    ("done", "progress"),
    ("done", "pending"),
    ("review", "progress"),
    ("review", "pending"),
    ("blocked", "pending"),
    ("progress", "pending"),
}


def is_backward_transition(from_state, to_state):
    """Return True if this transition is a backward (rework) transition.

    Uses explicit set from user's locked decisions rather than rank arithmetic.
    state_key() is applied to normalize inputs.
    """
    from_key = state_key(from_state)
    to_key = state_key(to_state)
    return (from_key, to_key) in BACKWARD_TRANSITIONS


def group_by_task(history_records):
    """Group state history records by task ID (TareaPeM relation).

    TareaPeM is a list of relation IDs (usually 1 element).
    Records with empty TareaPeM are grouped under a synthetic '_unlinked_N' key.
    Returns defaultdict(list) mapping task_id -> [records].
    """
    tasks = defaultdict(list)
    unlinked_counter = 0
    for r in history_records:
        task_ids = r.get("TareaPeM", [])
        if task_ids:
            for tid in task_ids:
                tasks[tid].append(r)
        else:
            tasks[f"_unlinked_{unlinked_counter}"].append(r)
            unlinked_counter += 1
    return tasks


def extract_block_episodes(task_transitions):
    """Extract paired block episodes from a task's chronological transitions.

    Returns list of (block_date, unblock_date) as date objects.
    Sorts by FechaCambio. Open blocks (no unblock) are excluded.
    """
    sorted_trans = sorted(
        task_transitions,
        key=lambda r: parse_date(r.get("FechaCambio", "")) or parse_date("9999-12-31")
    )
    episodes = []
    block_start = None
    for t in sorted_trans:
        to_key = state_key(t.get("EstadoNuevo", ""))
        from_key = state_key(t.get("EstadoAnterior", ""))
        if to_key == "blocked":
            block_start = parse_date(t.get("FechaCambio", ""))
        elif from_key == "blocked" and block_start is not None:
            unblock_date = parse_date(t.get("FechaCambio", ""))
            if unblock_date:
                episodes.append((block_start, unblock_date))
            block_start = None
    return episodes


def retrabajo_ratio(history_records):
    """KPI-07: Ratio de Retrabajo -- percentage of tasks with backward transitions per client.

    A task has rework if ANY of its transitions is in BACKWARD_TRANSITIONS set.
    Only considers records linked to a task (non-empty TareaPeM).
    Unlinked records (empty TareaPeM) are excluded.

    Returns: dict mapping client name -> kpi_result dict.
    """
    clients = group_by_client(history_records)
    results = {}
    for client, records in clients.items():
        # Group by task, excluding unlinked records
        tasks = group_by_task([r for r in records if r.get("TareaPeM")])
        # Remove synthetic _unlinked keys (shouldn't exist after filter, but safety)
        task_ids = [tid for tid in tasks if not tid.startswith("_unlinked_")]
        if not task_ids:
            results[client] = kpi_result(None, "no_data", "Sin tareas con transiciones")
            continue
        rework_count = 0
        for tid in task_ids:
            has_rework = any(
                is_backward_transition(t.get("EstadoAnterior", ""), t.get("EstadoNuevo", ""))
                for t in tasks[tid]
            )
            if has_rework:
                rework_count += 1
        ratio = safe_ratio(rework_count, len(task_ids))
        if ratio is None:
            results[client] = kpi_result(None, "no_data", "Sin tareas con transiciones")
        else:
            results[client] = kpi_result(round(ratio, 4), "complete")
    return results


def block_resolution_time(history_records):
    """KPI-08: Tiempo Medio de Resolucion de Bloqueos -- avg calendar days blocked per client.

    Uses extract_block_episodes() to find paired block/unblock transitions per task.
    Open blocks (still blocked, no unblock transition) are excluded.
    Averages across ALL block episodes for the client (not per-task average).

    Returns: dict mapping client name -> kpi_result dict.
    """
    clients = group_by_client(history_records)
    results = {}
    for client, records in clients.items():
        tasks = group_by_task(records)
        all_durations = []
        for tid, transitions in tasks.items():
            if tid.startswith("_unlinked_"):
                continue
            episodes = extract_block_episodes(transitions)
            for block_date, unblock_date in episodes:
                if block_date and unblock_date:
                    days = (unblock_date - block_date).days
                    all_durations.append(max(days, 0))
        if not all_durations:
            results[client] = kpi_result(None, "no_data", "Sin episodios de bloqueo resueltos")
        else:
            avg_days = round(sum(all_durations) / len(all_durations), 1)
            results[client] = kpi_result(avg_days, "complete")
    return results


def bug_recurrence(history_records):
    """KPI-09: Bug Recurrence -- ratio of tasks with multiple block episodes per client.

    A "fix" = transition from blocked to non-blocked. A "recurrence" = same task blocked again.
    Formula: tasks with 2+ block episodes / tasks with 1+ block episodes.

    Uses total_block_starts (transitions TO blocked) rather than completed episodes,
    so that open second blocks still count as recurrence.

    Returns: dict mapping client name -> kpi_result dict.
    """
    clients = group_by_client(history_records)
    results = {}
    for client, records in clients.items():
        tasks = group_by_task(records)
        tasks_with_any_block = 0
        tasks_with_recurrence = 0
        for tid, transitions in tasks.items():
            if tid.startswith("_unlinked_"):
                continue
            sorted_trans = sorted(
                transitions,
                key=lambda r: parse_date(r.get("FechaCambio", "")) or parse_date("9999-12-31")
            )
            total_block_starts = sum(
                1 for t in sorted_trans if state_key(t.get("EstadoNuevo", "")) == "blocked"
            )
            if total_block_starts > 0:
                tasks_with_any_block += 1
            if total_block_starts >= 2:
                tasks_with_recurrence += 1
        if tasks_with_any_block == 0:
            results[client] = kpi_result(None, "no_data", "Sin tareas bloqueadas")
        else:
            ratio = safe_ratio(tasks_with_recurrence, tasks_with_any_block)
            if ratio is None:
                results[client] = kpi_result(None, "no_data", "Sin tareas bloqueadas")
            else:
                results[client] = kpi_result(round(ratio, 4), "complete")
    return results


def cruce_limpio_rate(history_records, task_records=None):
    """KPI-10: Cruce Limpio Rate -- binary clean/dirty per client for Rollout phase.

    Score per client:
    - 100 = clean pass (Rollout tasks exist, no transitions TO blocked)
    - 0 = had errors (any transition TO blocked during Rollout tasks)
    - N/A = client has no Rollout tasks in task_records

    Always labeled "approximate" (inferred from state history, not dedicated field).

    Args:
        history_records: parsed state history records
        task_records: parsed task records (with PageId and Fase fields)
    """
    if not task_records:
        # Cannot determine which tasks are Rollout without task records
        clients = group_by_client(history_records)
        return {
            client: kpi_result(None, "no_data", "Sin datos de tareas para determinar Rollout (approximate)")
            for client in clients
        }

    from kpi_metrics import extract_phase_number

    # Build set of Rollout (Fase 10) task IDs per client
    client_rollout_tasks = defaultdict(set)
    for t in task_records:
        pid = t.get("PageId", "")
        fase_num = extract_phase_number(t.get("Fase", ""))
        cliente = t.get("Cliente", "")
        if pid and fase_num == 10 and cliente:
            client_rollout_tasks[cliente].add(pid)

    # Check each client's history for blocked transitions on Rollout tasks
    clients = group_by_client(history_records)
    all_clients = set(clients.keys()) | set(client_rollout_tasks.keys())
    results = {}

    for client in all_clients:
        rollout_tasks = client_rollout_tasks.get(client, set())
        if not rollout_tasks:
            results[client] = kpi_result(None, "no_data", "Sin tareas de Rollout (approximate)")
            continue

        # Check if any history record for this client's Rollout tasks has transition TO blocked
        client_records = clients.get(client, [])
        had_block = False
        for r in client_records:
            task_ids = r.get("TareaPeM", [])
            to_key = state_key(r.get("EstadoNuevo", ""))
            if to_key == "blocked" and any(tid in rollout_tasks for tid in task_ids):
                had_block = True
                break

        if had_block:
            results[client] = kpi_result(0, "complete", "approximate")
        else:
            results[client] = kpi_result(100, "complete", "approximate")

    return results


def tasa_rechazo(history_records, task_records=None):
    """KPI-11: Tasa de Rechazo -- rejections per QA attempt per client.

    A "rejection" = backward transition during Fase 8 (QA y Testing) tasks.
    Per task: attempts = rejections + 1 (the final successful pass).
    Average rejection rate across all QA tasks per client.

    Args:
        history_records: parsed state history records
        task_records: parsed task records (with PageId and Fase fields)
    """
    if not task_records:
        clients = group_by_client(history_records)
        return {
            client: kpi_result(None, "no_data", "Sin datos de tareas para determinar QA")
            for client in clients
        }

    from kpi_metrics import extract_phase_number

    # Build set of QA (Fase 8) task IDs per client
    client_qa_tasks = defaultdict(set)
    for t in task_records:
        pid = t.get("PageId", "")
        fase_num = extract_phase_number(t.get("Fase", ""))
        cliente = t.get("Cliente", "")
        if pid and fase_num == 8 and cliente:
            client_qa_tasks[cliente].add(pid)

    clients = group_by_client(history_records)
    all_clients = set(clients.keys()) | set(client_qa_tasks.keys())
    results = {}

    for client in all_clients:
        qa_tasks = client_qa_tasks.get(client, set())
        if not qa_tasks:
            results[client] = kpi_result(None, "no_data", "Sin tareas de QA")
            continue

        client_records = clients.get(client, [])

        # Group history records by QA task
        qa_task_records = defaultdict(list)
        for r in client_records:
            for tid in r.get("TareaPeM", []):
                if tid in qa_tasks:
                    qa_task_records[tid].append(r)

        if not qa_task_records:
            results[client] = kpi_result(None, "no_data", "Sin transiciones en tareas de QA")
            continue

        # Per task: count backward transitions (rejections), attempts = rejections + 1
        task_rates = []
        for tid, records_for_task in qa_task_records.items():
            rejections = sum(
                1 for r in records_for_task
                if is_backward_transition(r.get("EstadoAnterior", ""), r.get("EstadoNuevo", ""))
            )
            attempts = rejections + 1
            rate = rejections / attempts  # Always safe: attempts >= 1
            task_rates.append(rate)

        if not task_rates:
            results[client] = kpi_result(None, "no_data", "Sin tareas de QA con transiciones")
        else:
            avg_rate = round(sum(task_rates) / len(task_rates), 4)
            results[client] = kpi_result(avg_rate, "complete")

    return results


def compute_state_history_kpis(history_records, task_records=None):
    """Orchestrator: compute all 5 state-history KPIs.

    Args:
        history_records: list of parsed state history records (from parse_state_history())
        task_records: optional list of parsed task records (with PageId, for phase-scoped KPIs)

    Returns: dict with keys for each KPI:
        "retrabajo": {client -> kpi_result}
        "block_resolution_time": {client -> kpi_result}
        "bug_recurrence": {client -> kpi_result}
        "cruce_limpio": {client -> kpi_result}
        "tasa_rechazo": {client -> kpi_result}
    """
    return {
        "retrabajo": retrabajo_ratio(history_records),
        "block_resolution_time": block_resolution_time(history_records),
        "bug_recurrence": bug_recurrence(history_records),
        "cruce_limpio": cruce_limpio_rate(history_records, task_records),
        "tasa_rechazo": tasa_rechazo(history_records, task_records),
    }

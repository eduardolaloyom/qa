"""KPI Metrics -- Date-math KPI functions for PeM Dashboard.

Each KPI function accepts a list of parsed task records (from parse_records())
and returns a dict mapping client name to a kpi_result dict.
"""
from datetime import datetime, date
from collections import defaultdict
from statistics import stdev, mean, StatisticsError

from generate_dashboard import safe_ratio


def parse_date(date_str):
    """Parse a Notion date string to a Python date object.

    Handles 'YYYY-MM-DD', 'YYYY-MM-DDTHH:MM:SS.000+00:00', '' and None.
    """
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str).date()
    except (ValueError, TypeError):
        return None


def kpi_result(value, status="complete", reason=None):
    """Create a standardized KPI result dict.

    status: 'complete' | 'in_progress' | 'no_data'
    """
    result = {"value": value, "status": status}
    if reason:
        result["reason"] = reason
    return result


def extract_phase_number(fase_str):
    """Extract the phase number from a string like '4. Integraciones'.

    Returns int or None.
    """
    if not fase_str:
        return None
    try:
        return int(fase_str.split(".")[0].strip())
    except (ValueError, IndexError):
        return None


def group_by_client(records):
    """Group task records by client name.

    Returns defaultdict(list) mapping client -> [task dicts].
    Skips records with empty/None Cliente.
    """
    clients = defaultdict(list)
    for r in records:
        if r.get("Cliente"):
            clients[r["Cliente"]].append(r)
    return clients


def phase_duration_days(tasks, phase_prefix):
    """Compute calendar days for a phase from earliest start to latest end.

    Args:
        tasks: list of task dicts for a single client
        phase_prefix: e.g. "4." or "8."

    Returns:
        int (days) or None if dates are missing.
        Returns None for negative durations (data error).
        Returns 1 for zero-day phases (minimum duration).
    """
    starts = []
    ends = []
    for t in tasks:
        if t.get("Fase", "").startswith(phase_prefix):
            s = parse_date(t.get("FechaInicio", ""))
            e = parse_date(t.get("FechaTermino", ""))
            if s:
                starts.append(s)
            if e:
                ends.append(e)

    if not starts or not ends:
        return None
    days = (max(ends) - min(starts)).days
    if days < 0:
        return None  # Data error: end before start
    if days == 0:
        return 1  # Minimum 1 day to avoid division by zero
    return days


# ---------------------------------------------------------------------------
# KPI Functions
# ---------------------------------------------------------------------------


def time_to_live(records):
    """KPI-01: Calendar days from Fase 1 start to Fase 10 end per client.

    Returns: dict mapping client name -> kpi_result dict.
    - Completed clients: {"value": days, "status": "complete"}
    - In-progress clients: {"value": elapsed_days, "status": "in_progress"}
    - Missing Fase 1 start: {"value": None, "status": "no_data", "reason": "..."}
    """
    clients = group_by_client(records)
    results = {}

    for client, tasks in clients.items():
        fase1_start = None
        fase10_end = None

        for t in tasks:
            fase = t.get("Fase", "")
            if fase.startswith("1."):
                d = parse_date(t.get("FechaInicio", ""))
                if d and (fase1_start is None or d < fase1_start):
                    fase1_start = d
            if fase.startswith("10."):
                d = parse_date(t.get("FechaTermino", ""))
                if d and (fase10_end is None or d > fase10_end):
                    fase10_end = d

        if fase1_start is None:
            results[client] = kpi_result(
                None, "no_data", "Sin fecha de inicio en Fase 1"
            )
        elif fase10_end is None:
            # In progress: days elapsed to today
            days = (date.today() - fase1_start).days
            results[client] = kpi_result(days, "in_progress")
        else:
            days = (fase10_end - fase1_start).days
            if days < 0:
                results[client] = kpi_result(
                    None, "no_data", "Fechas inconsistentes"
                )
            else:
                results[client] = kpi_result(days, "complete")

    return results


def cycle_time_stddev(records):
    """KPI-02: Standard deviation of cycle time per phase across clients.

    Returns: dict mapping phase_number (int) -> {
        "stdev": float|None,
        "mean": float|None,
        "n": int,
        "durations": {client: days}
    }
    """
    clients = group_by_client(records)
    results = {}

    for phase_num in range(1, 13):
        prefix = f"{phase_num}."
        durations = {}

        for client, tasks in clients.items():
            dur = phase_duration_days(tasks, prefix)
            if dur is not None:
                durations[client] = dur

        n = len(durations)
        values = list(durations.values())

        if n == 0:
            results[phase_num] = {
                "stdev": None,
                "mean": None,
                "n": 0,
                "durations": {},
            }
        elif n == 1:
            results[phase_num] = {
                "stdev": None,
                "mean": float(values[0]),
                "n": 1,
                "durations": durations,
            }
        else:
            try:
                sd = round(stdev(values), 1)
                mn = round(mean(values), 1)
            except StatisticsError:
                # Safety net -- should not trigger with n >= 2 guard
                sd = None
                mn = None
            results[phase_num] = {
                "stdev": sd,
                "mean": mn,
                "n": n,
                "durations": durations,
            }

    return results


def bug_rate(records):
    """KPI-04: Fase 8 (QA) calendar days / Fase 4 (Integraciones) days per client.

    Returns: dict mapping client name -> kpi_result dict.
    - Normal: {"value": ratio, "status": "complete"}
    - No QA data: {"value": None, "status": "no_data", "reason": "Cliente no ha llegado a QA"}
    - No integration data: {"value": None, "status": "no_data", "reason": "Sin datos de Integraciones"}
    """
    clients = group_by_client(records)
    results = {}

    for client, tasks in clients.items():
        qa_days = phase_duration_days(tasks, "8.")
        integration_days = phase_duration_days(tasks, "4.")

        if qa_days is None:
            results[client] = kpi_result(
                None, "no_data", "Cliente no ha llegado a QA"
            )
        elif integration_days is None:
            results[client] = kpi_result(
                None, "no_data", "Sin datos de Integraciones"
            )
        else:
            ratio = safe_ratio(qa_days, integration_days)
            if ratio is None:
                results[client] = kpi_result(
                    None, "no_data", "Fase de Integraciones sin duracion"
                )
            else:
                results[client] = kpi_result(round(ratio, 2), "complete")

    return results


# Phase classification for delay analysis (CONTEXT.md locked decision)
# Internal = team controls, External = client dependency, Mixed = classify as external
PHASE_CLASSIFICATION = {
    1: "external",   # Levantamiento (client dependency)
    2: "external",   # Entrega datos
    3: "external",   # Kick off
    4: "external",   # Integraciones
    5: "external",   # Cuadratura (mixed -> external per user decision)
    6: "internal",   # Desarrollos (team controls)
    7: "internal",   # Configuraciones
    8: "internal",   # QA y Testing
    9: "internal",   # Capacitaciones
    10: "external",  # Rollout (mixed -> external per user decision)
    11: "external",  # Traspaso (mixed -> external per user decision)
    12: "external",  # Review (mixed -> external per user decision)
}


def planned_phase_duration(tasks, phase_prefix):
    """Compute planned calendar days for a phase.

    Uses earliest FechaInicio to latest FechaFinalizacion for tasks in this phase.
    Returns int days or None if planned date missing.
    """
    starts = []
    planned_ends = []
    for t in tasks:
        if t.get("Fase", "").startswith(phase_prefix):
            s = parse_date(t.get("FechaInicio", ""))
            p = parse_date(t.get("FechaFinalizacion", ""))
            if s:
                starts.append(s)
            if p:
                planned_ends.append(p)
    if not starts or not planned_ends:
        return None
    days = (max(planned_ends) - min(starts)).days
    if days < 0:
        return None
    return max(days, 1)


def atraso_promedio(records):
    """KPI-05: Internal delay days / total delay days per client.

    Delay = actual days - planned days per phase (positive = late, negative = early).
    Only positive delays count (phases completed early have 0 delay contribution).
    Internal phases: 6, 7, 8, 9. External: 1, 2, 3, 4, 5, 10, 11, 12.

    Returns: dict mapping client name -> kpi_result dict.
    """
    clients = group_by_client(records)
    results = {}

    for client, tasks in clients.items():
        internal_delay = 0
        total_delay = 0
        phases_with_data = 0

        for phase_num in range(1, 13):
            prefix = f"{phase_num}."
            actual_days = phase_duration_days(tasks, prefix)
            planned_days = planned_phase_duration(tasks, prefix)

            if actual_days is None or planned_days is None:
                continue

            delay = max(0, actual_days - planned_days)
            phases_with_data += 1
            classification = PHASE_CLASSIFICATION.get(phase_num, "external")

            if classification == "internal":
                internal_delay += delay
            total_delay += delay

        if phases_with_data == 0:
            results[client] = kpi_result(
                None, "no_data", "Sin datos de fechas planificadas"
            )
        elif total_delay == 0:
            results[client] = kpi_result(0.0, "complete")
        else:
            ratio = safe_ratio(internal_delay, total_delay)
            results[client] = kpi_result(
                round(ratio if ratio is not None else 0, 2), "complete"
            )

    return results


def integraciones_en_tiempo(records):
    """KPI-06: On-time integrations / total integrations per client.

    On-time = FechaTermino <= FechaFinalizacion for tasks in Fase 4.
    Per-task granularity (not per-phase).

    Returns: dict mapping client name -> kpi_result dict.
    """
    clients = group_by_client(records)
    results = {}

    for client, tasks in clients.items():
        fase4_tasks = [t for t in tasks if t.get("Fase", "").startswith("4.")]

        if not fase4_tasks:
            results[client] = kpi_result(
                None, "no_data", "Sin tareas de integracion"
            )
            continue

        on_time = 0
        total = 0

        for t in fase4_tasks:
            actual_end = parse_date(t.get("FechaTermino", ""))
            planned_end = parse_date(t.get("FechaFinalizacion", ""))

            if actual_end is None or planned_end is None:
                continue

            total += 1
            if actual_end <= planned_end:
                on_time += 1

        if total == 0:
            results[client] = kpi_result(
                None, "no_data", "Sin fecha planificada"
            )
        else:
            results[client] = kpi_result(round(on_time / total, 2), "complete")

    return results


def capacidad_equipo(records):
    """KPI-03: Active clients count and delay trend data.

    Active client = started Fase 1 (any Fase 1 task has FechaInicio)
                    AND NOT completed Fase 10 (no Fase 10 task has FechaTermino).

    Returns: dict with:
        "active_count": int (number of active clients),
        "active_clients": list of client names,
        "delay_by_phase": dict mapping phase_number -> {
            "avg_delay": float|None (average delay in days),
            "clients_with_data": int,
            "benchmark": "planned"|"historical" (which benchmark was used)
        }
    """
    clients = group_by_client(records)

    # Determine active status per client
    active_clients = []
    for client, tasks in clients.items():
        started_fase1 = any(
            t.get("Fase", "").startswith("1.")
            and parse_date(t.get("FechaInicio", "")) is not None
            for t in tasks
        )
        completed_fase10 = any(
            t.get("Fase", "").startswith("10.")
            and parse_date(t.get("FechaTermino", "")) is not None
            for t in tasks
        )
        if started_fase1 and not completed_fase10:
            active_clients.append(client)

    # Compute delay_by_phase for phases 1-12
    delay_by_phase = {}
    for phase_num in range(1, 13):
        prefix = f"{phase_num}."
        delays = []
        benchmark_type = None

        # Compute historical average for fallback: mean of actual_days across
        # all clients that have both start and end dates for this phase
        all_actual = []
        for client, tasks in clients.items():
            dur = phase_duration_days(tasks, prefix)
            if dur is not None:
                all_actual.append(dur)
        historical_avg = (sum(all_actual) / len(all_actual)) if all_actual else None

        for client, tasks in clients.items():
            actual_days = phase_duration_days(tasks, prefix)
            if actual_days is None:
                continue

            planned_days = planned_phase_duration(tasks, prefix)
            if planned_days is not None:
                delay = actual_days - planned_days
                delays.append(delay)
                benchmark_type = "planned"
            elif historical_avg is not None:
                delay = actual_days - historical_avg
                delays.append(delay)
                benchmark_type = "historical"

        if delays:
            avg_delay = round(sum(delays) / len(delays), 1)
            delay_by_phase[phase_num] = {
                "avg_delay": avg_delay,
                "clients_with_data": len(delays),
                "benchmark": benchmark_type,
            }
        else:
            delay_by_phase[phase_num] = {
                "avg_delay": None,
                "clients_with_data": 0,
                "benchmark": None,
            }

    return {
        "active_count": len(active_clients),
        "active_clients": active_clients,
        "delay_by_phase": delay_by_phase,
    }


def compute_date_math_kpis(records):
    """Orchestrator: compute all 6 date-math KPIs.

    Args:
        records: list of parsed task records (from parse_records())

    Returns: dict with keys for each KPI:
        "time_to_live": {client -> kpi_result}
        "cycle_time_stddev": {phase_number -> stats dict}
        "bug_rate": {client -> kpi_result}
        "atraso_promedio": {client -> kpi_result}
        "integraciones_en_tiempo": {client -> kpi_result}
        "capacidad_equipo": {active_count, active_clients, delay_by_phase}
    """
    return {
        "time_to_live": time_to_live(records),
        "cycle_time_stddev": cycle_time_stddev(records),
        "bug_rate": bug_rate(records),
        "atraso_promedio": atraso_promedio(records),
        "integraciones_en_tiempo": integraciones_en_tiempo(records),
        "capacidad_equipo": capacidad_equipo(records),
    }

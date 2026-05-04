#!/usr/bin/env python3
"""
PeM Dashboard Generator — queries Notion API directly and generates index.html
Runs as GitHub Action. Requires NOTION_TOKEN env var.
"""
import os
import sys
import json
import re
import time
import random
import urllib.request
import urllib.error
from datetime import datetime, timezone

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
DATABASE_ID = "ffd65269-a0b9-4f93-8cf1-cf9fdb0bda3c"
NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"
STATE_HISTORY_DB_ID = "8418c239fcfc4a278d517f127564470f"
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
MAX_RETRIES = 5
BASE_DELAY = 1.0
MAX_DELAY = 30.0


def notion_request(method, path, body=None):
    """Make a request to Notion API with retry on rate limits and server errors."""
    url = f"{NOTION_API}{path}"
    data = json.dumps(body).encode() if body else None

    for attempt in range(MAX_RETRIES + 1):
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"Bearer {NOTION_TOKEN}")
        req.add_header("Notion-Version", NOTION_VERSION)
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in RETRYABLE_STATUS_CODES and attempt < MAX_RETRIES:
                # Respect Retry-After header if present (429), else use exponential backoff
                retry_after = e.headers.get("Retry-After")
                if retry_after:
                    delay = float(retry_after)
                else:
                    delay = min(BASE_DELAY * (2 ** attempt), MAX_DELAY)
                # Add jitter: +/- 25% of delay
                jitter = delay * random.uniform(-0.25, 0.25)
                delay = max(0.1, delay + jitter)
                print(f"Notion API {e.code} on attempt {attempt + 1}/{MAX_RETRIES + 1}, "
                      f"retrying in {delay:.1f}s...", file=sys.stderr)
                time.sleep(delay)
                continue
            print(f"Notion API error {e.code}: {e.read().decode()}", file=sys.stderr)
            raise


def query_database(database_id, filters=None):
    """Query all pages from a Notion database (handles pagination)."""
    all_results = []
    has_more = True
    start_cursor = None

    while has_more:
        body = {"page_size": 100}
        if start_cursor:
            body["start_cursor"] = start_cursor
        if filters:
            body["filter"] = filters

        resp = notion_request("POST", f"/databases/{database_id}/query", body)
        all_results.extend(resp.get("results", []))
        has_more = resp.get("has_more", False)
        start_cursor = resp.get("next_cursor")

    print(f"Fetched {len(all_results)} records from Notion DB {database_id[:8]}...")
    return all_results


def extract_property(prop):
    """Extract a readable value from a Notion property object."""
    ptype = prop.get("type", "")

    if ptype == "title":
        return "".join(t.get("plain_text", "") for t in prop.get("title", []))
    elif ptype == "rich_text":
        return "".join(t.get("plain_text", "") for t in prop.get("rich_text", []))
    elif ptype == "select":
        sel = prop.get("select")
        return sel.get("name", "") if sel else ""
    elif ptype == "multi_select":
        return [s.get("name", "") for s in prop.get("multi_select", [])]
    elif ptype == "date":
        d = prop.get("date")
        if d:
            return {"start": d.get("start", ""), "end": d.get("end", "")}
        return {"start": "", "end": ""}
    elif ptype == "people":
        return [p.get("name", "") for p in prop.get("people", [])]
    elif ptype == "formula":
        f = prop.get("formula", {})
        ft = f.get("type", "")
        if ft == "string":
            return f.get("string", "")
        elif ft == "number":
            return f.get("number", "")
        elif ft == "boolean":
            return f.get("boolean", False)
        elif ft == "date":
            fd = f.get("date")
            return fd.get("start", "") if fd else ""
        return ""
    elif ptype == "relation":
        return [r.get("id", "") for r in prop.get("relation", [])]
    elif ptype == "status":
        s = prop.get("status")
        return s.get("name", "") if s else ""
    return ""

CLIENT_COLORS = {
    "Prinorte": "#ef4444",
    "Caren": "#eab308",
    "Basti\u00e9n": "#ec4899",
    "Codelpa Per\u00fa": "#3b82f6",
    "Soprole": "#f97316",
    "Cedisur": "#06b6d4",
    "Co\u00e9xito": "#8b5cf6",
}

CLIENT_DRIVE_LINKS = {
    "Caren":   "https://drive.google.com/drive/folders/10hI38BgXKyOXKqYaa9jim0l2Im76mDkQ",
    "Soprole": "https://drive.google.com/drive/folders/1D4xbaNxw6xY18NzyOGJJuly_9qM0zW3h",
    "Cedisur": "https://drive.google.com/drive/folders/1OYSPvRgLXOI-fSg0IN2cj-F1zzBPsKhh",
}

PHASES = [
    "1. Levantamiento",
    "2. Entrega de datos y servicios",
    "3. Kick off",
    "4. Integraciones",
    "5. Cuadratura",
    "6. Desarrollos",
    "7. Configuraciones",
    "8. QA y Testing",
    "9. Capacitaciones",
    "10. Rollout",
    "11. Traspaso",
    "12. Review",
]

STATES = [
    "\U0001f6a6Pendiente",
    "\U0001f504 En progreso",
    "\u2705 Completado",
    "\U0001f6ab Bloqueado",
    "\U0001f50d En revisi\u00f3n",
    "\U0001f4e6 Archivado",
]


def parse_records(raw_results):
    """Convert raw Notion results to task objects matching the dashboard template format."""
    records = []
    for page in raw_results:
        props = page.get("properties", {})

        fi = extract_property(props.get("Fecha inicio", {}))
        ft = extract_property(props.get("Fecha t\u00e9rmino", {}))
        fecha_inicio = fi.get("start", "") if isinstance(fi, dict) else ""
        fecha_termino = ft.get("start", "") if isinstance(ft, dict) else ""

        # Planned date field -- "Fecha finalizacion" (verify exact name at runtime)
        ff = extract_property(props.get("Fecha finalizacion", {}))
        if not ff or ff == {"start": "", "end": ""}:
            # Try alternate name with accent
            ff = extract_property(props.get("Fecha finalizaci\u00f3n", {}))
        fecha_finalizacion = ff.get("start", "") if isinstance(ff, dict) else ""

        record = {
            "PageId": page.get("id", ""),
            "Tarea": extract_property(props.get("Tarea", {})),
            "Tipo": extract_property(props.get("Tipo", {})),
            "Cliente": extract_property(props.get("Cliente", {})),
            "Estado": extract_property(props.get("Estado", {})),
            "Fase": extract_property(props.get("Fase", {})),
            "FechaInicio": fecha_inicio,
            "FechaTermino": fecha_termino,
            "FechaFinalizacion": fecha_finalizacion,
            "Bloqueado": extract_property(props.get("Bloqueado por", {})),
            "Notas": extract_property(props.get("Notas", {})),
            "Responsables": extract_property(props.get("Responsables", {})),
            "Relacion": extract_property(props.get("Relación", {})),
            "ParentId": extract_property(props.get("Tarea padre", {})),
        }
        records.append(record)

    return records


def normalize_state(raw_state):
    """Strip emoji prefixes from state names for consistent matching.

    Handles both 'emoji-no-space' and 'emoji space' patterns.
    Examples: '\ud83d\udea6Pendiente' -> 'Pendiente', '\ud83d\udd04 En progreso' -> 'En progreso'
    """
    if not raw_state:
        return ""
    # Remove leading non-word characters (emojis, symbols) and whitespace
    cleaned = re.sub(r'^[^\w]+', '', raw_state, flags=re.UNICODE).strip()
    return cleaned if cleaned else raw_state


def state_key(raw_state):
    """Map a Spanish state name to a canonical key.
    Input should already be emoji-stripped via normalize_state().
    """
    if not raw_state:
        return "pending"
    s = raw_state.lower()
    if "bloqueado" in s:
        return "blocked"
    if "progreso" in s:
        return "progress"
    if "completado" in s:
        return "done"
    if "revisi" in s:
        return "review"
    if "archivado" in s:
        return "archived"
    return "pending"


def parse_state_history(raw_results):
    """Convert raw Notion state history results to transition records.
    Each record has: Cambio, Cliente, EstadoAnterior, EstadoNuevo,
    FechaCambio, Motivo, Origen, TareaPeM.
    Estado fields are emoji-stripped via normalize_state().
    """
    records = []
    for page in raw_results:
        props = page.get("properties", {})

        fecha = extract_property(props.get("Fecha Cambio", {}))
        fecha_str = ""
        if isinstance(fecha, dict):
            fecha_str = fecha.get("start", "") or ""
        elif isinstance(fecha, str):
            fecha_str = fecha

        record = {
            "Cambio": extract_property(props.get("Cambio", {})),
            "Cliente": extract_property(props.get("Cliente", {})),
            "EstadoAnterior": normalize_state(extract_property(props.get("Estado Anterior", {}))),
            "EstadoNuevo": normalize_state(extract_property(props.get("Estado Nuevo", {}))),
            "FechaCambio": fecha_str,
            "Motivo": extract_property(props.get("Motivo", {})),
            "Origen": extract_property(props.get("Origen", {})),
            "TareaPeM": extract_property(props.get("Tarea PeM", {})),
        }
        records.append(record)

    return records


def safe_ratio(numerator, denominator, min_denominator=1):
    """Return numerator/denominator or None if denominator is insufficient.

    Args:
        numerator: The dividend (can be None).
        denominator: The divisor (can be None or 0).
        min_denominator: Minimum denominator value to consider data sufficient.

    Returns:
        float ratio or None if data is insufficient.
    """
    if numerator is None or denominator is None:
        return None
    if denominator < min_denominator:
        return None
    return numerator / denominator


def compute_phase_weights(records):
    """Calculate phase durations (days) from actual task dates.

    For each phase, compute the average span (min FechaInicio to max FechaTermino)
    across clients that have valid dates for that phase.
    Falls back to 1 day if no dates available for a phase.
    """
    from datetime import date

    # Group tasks by (client, phase)
    phase_durations = {}  # phase -> list of durations in days
    client_phase = {}  # (client, phase) -> list of tasks with dates
    for r in records:
        if not r["Cliente"] or not r["Fase"] or r["Tipo"] != "Tarea":
            continue
        key = (r["Cliente"], r["Fase"])
        if key not in client_phase:
            client_phase[key] = []
        client_phase[key].append(r)

    for (client, phase), tasks in client_phase.items():
        starts = []
        ends = []
        for t in tasks:
            if t["FechaInicio"]:
                try:
                    starts.append(date.fromisoformat(t["FechaInicio"][:10]))
                except ValueError:
                    pass
            if t["FechaTermino"]:
                try:
                    ends.append(date.fromisoformat(t["FechaTermino"][:10]))
                except ValueError:
                    pass
        if starts and ends:
            span = (max(ends) - min(starts)).days
            if span >= 1:
                if phase not in phase_durations:
                    phase_durations[phase] = []
                phase_durations[phase].append(span)

    weights = {}
    for phase in PHASES:
        if phase in phase_durations and phase_durations[phase]:
            weights[phase] = round(sum(phase_durations[phase]) / len(phase_durations[phase]))
        else:
            weights[phase] = 1  # fallback

    total = sum(weights.values())
    return weights, total


def compute_all_kpis(records, history):
    """Compute all 11 KPIs from both data sources.

    Args:
        records: parsed task records (from parse_records())
        history: parsed state history records (from parse_state_history())

    Returns:
        dict with 11 KPI keys (6 date-math + 5 state-history)
    """
    # Function-level imports to avoid circular dependency:
    # kpi_metrics imports safe_ratio FROM this module
    # state_history_kpis imports state_key, safe_ratio FROM this module
    from kpi_metrics import compute_date_math_kpis
    from state_history_kpis import compute_state_history_kpis

    date_kpis = compute_date_math_kpis(records)
    state_kpis = compute_state_history_kpis(history, task_records=records)
    return {**date_kpis, **state_kpis}


def state_key(estado):
    """Map Notion estado string to a state key (mirrors JS stateKey)."""
    s = estado.lower() if estado else ""
    if "bloq" in s: return "blocked"
    if "progreso" in s: return "progress"
    if "completado" in s: return "done"
    if "revisi" in s: return "review"
    if "archivado" in s: return "archived"
    return "pending"


def detect_patterns(records, history):
    """Detect cross-client patterns from task data. Returns list of pattern dicts."""
    from datetime import date
    today = date.today()
    tasks = [r for r in records if r.get("Tipo") == "Tarea" and r.get("Cliente")]
    patterns = []

    def parse_d(s):
        if not s: return None
        try: return date.fromisoformat(s[:10])
        except: return None

    def due_bucket(t):
        k = state_key(t.get("Estado", ""))
        if k in ("done", "archived"): return None
        end = parse_d(t.get("FechaTermino"))
        if not end: return None
        diff = (end - today).days
        if diff < 0: return "overdue"
        if diff <= 3: return "soon"
        return None

    def is_stale(t):
        k = state_key(t.get("Estado", ""))
        if k not in ("progress", "review"): return False
        start = parse_d(t.get("FechaInicio"))
        end = parse_d(t.get("FechaTermino"))
        if not start or not end: return False
        planned = max((end - start).days, 1)
        elapsed = (today - start).days
        return elapsed >= planned * 0.5 and k != "done"

    # P1: Bloqueos por fase
    block_by_phase = {}
    for t in tasks:
        if state_key(t["Estado"]) == "blocked" and t.get("Fase"):
            block_by_phase.setdefault(t["Fase"], {"clients": set(), "count": 0})
            block_by_phase[t["Fase"]]["clients"].add(t["Cliente"])
            block_by_phase[t["Fase"]]["count"] += 1
    for fase, d in block_by_phase.items():
        if len(d["clients"]) >= 2 or d["count"] >= 3:
            patterns.append({"id": f"block_{fase}", "title": f"{fase} genera bloqueos recurrentes",
                "type": "bloqueo", "severity": "critico" if len(d["clients"]) >= 3 else "alto",
                "clients": sorted(d["clients"]), "count": d["count"]})

    # P2: Atrasos por fase
    overdue_by_phase = {}
    for t in tasks:
        if due_bucket(t) == "overdue" and t.get("Fase"):
            overdue_by_phase.setdefault(t["Fase"], {"clients": set(), "count": 0, "days": 0})
            overdue_by_phase[t["Fase"]]["clients"].add(t["Cliente"])
            overdue_by_phase[t["Fase"]]["count"] += 1
            end = parse_d(t["FechaTermino"])
            if end: overdue_by_phase[t["Fase"]]["days"] += (today - end).days
    for fase, d in overdue_by_phase.items():
        if len(d["clients"]) >= 2 or d["count"] >= 3:
            patterns.append({"id": f"overdue_{fase}", "title": f"{fase} acumula atrasos",
                "type": "atraso", "severity": "critico" if len(d["clients"]) >= 3 else "alto",
                "clients": sorted(d["clients"]), "count": d["count"]})

    # P3: Estancamiento por fase
    stale_by_phase = {}
    for t in tasks:
        if is_stale(t) and t.get("Fase"):
            stale_by_phase.setdefault(t["Fase"], {"clients": set(), "count": 0})
            stale_by_phase[t["Fase"]]["clients"].add(t["Cliente"])
            stale_by_phase[t["Fase"]]["count"] += 1
    for fase, d in stale_by_phase.items():
        if len(d["clients"]) >= 2 or d["count"] >= 3:
            patterns.append({"id": f"stale_{fase}", "title": f"Estancamiento en {fase}",
                "type": "estancamiento", "severity": "medio",
                "clients": sorted(d["clients"]), "count": d["count"]})

    # P4: Cliente concentrador
    for client in set(t["Cliente"] for t in tasks):
        ct = [t for t in tasks if t["Cliente"] == client]
        blocked = sum(1 for t in ct if state_key(t["Estado"]) == "blocked")
        overdue = sum(1 for t in ct if due_bucket(t) == "overdue")
        stale = sum(1 for t in ct if is_stale(t))
        total = blocked + overdue + stale
        if total >= 5:
            patterns.append({"id": f"concentrated_{client}", "title": f"{client} concentra problemas",
                "type": "concentracion", "severity": "critico" if total >= 8 else "alto",
                "clients": [client], "count": total})

    # P5: Retrabajo (from history)
    ret_clients = []
    for h in history:
        if h.get("EstadoAnterior") and "Completado" in h["EstadoAnterior"] and h.get("EstadoNuevo") and "progreso" in h["EstadoNuevo"].lower():
            ret_clients.append(h.get("Cliente", ""))
    ret_unique = set(c for c in ret_clients if c)
    if len(ret_unique) >= 2:
        patterns.append({"id": "retrabajo_multi", "title": "Retrabajo en múltiples clientes",
            "type": "retrabajo", "severity": "medio",
            "clients": sorted(ret_unique), "count": len(ret_clients)})

    return patterns


def update_pattern_history(patterns, history_path, max_months=4):
    """Append today's patterns to history file, prune entries older than max_months."""
    from datetime import date, timedelta
    today_str = date.today().isoformat()
    cutoff = (date.today() - timedelta(days=max_months * 30)).isoformat()

    # Load existing
    history = []
    if os.path.exists(history_path):
        try:
            with open(history_path, "r") as f:
                history = json.load(f)
        except (json.JSONDecodeError, IOError):
            history = []

    # Remove today's existing entry (re-run idempotency)
    history = [h for h in history if h.get("date") != today_str]

    # Add today's snapshot
    history.append({
        "date": today_str,
        "patterns": patterns,
        "summary": {
            "total": len(patterns),
            "critico": sum(1 for p in patterns if p["severity"] == "critico"),
            "alto": sum(1 for p in patterns if p["severity"] == "alto"),
            "medio": sum(1 for p in patterns if p["severity"] == "medio"),
        }
    })

    # Prune old entries
    history = [h for h in history if h.get("date", "") >= cutoff]

    # Sort by date
    history.sort(key=lambda h: h.get("date", ""))

    # Save
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    return history


def generate_html(records, now_str, kpis=None, pattern_history=None):
    """Generate the full dashboard HTML."""
    # Discover clients from data — only clients with tasks are shown
    discovered = []
    for r in records:
        if r["Cliente"] and r["Cliente"] not in discovered:
            discovered.append(r["Cliente"])
    all_colors = {c: CLIENT_COLORS.get(c, "#94a3b8") for c in discovered}

    phase_weights, total_days = compute_phase_weights(records)

    data_obj = {
        "generated": now_str,
        "clients": list(all_colors.keys()),
        "clientColors": all_colors,
        "phases": PHASES,
        "states": STATES,
        "tasks": records,
        "phaseWeights": phase_weights,
        "totalProjectDays": total_days,
        "driveLinks": CLIENT_DRIVE_LINKS,
    }
    data_json = json.dumps(data_obj, ensure_ascii=False)
    # DATA_OPS: operational KPIs (separate from DATA per locked decision)
    data_ops_json = json.dumps(kpis if kpis else {}, ensure_ascii=False, default=str)
    # Pattern history for trend visualization
    pattern_hist_json = json.dumps(pattern_history if pattern_history else [], ensure_ascii=False)

    html = open(os.path.join(os.path.dirname(__file__), "dashboard_template.html"), "r").read()
    html = html.replace("__DATA_JSON__", data_json)
    html = html.replace("__DATA_OPS_JSON__", data_ops_json)
    html = html.replace("__PATTERN_HISTORY_JSON__", pattern_hist_json)
    return html


def main():
    if not NOTION_TOKEN:
        print("ERROR: NOTION_TOKEN env var not set", file=sys.stderr)
        sys.exit(1)

    print("Querying Notion PeM tasks database...")
    raw = query_database(DATABASE_ID)

    print("Parsing records...")
    records = parse_records(raw)
    records = [r for r in records if r["Cliente"]]
    print(f"Parsed {len(records)} client records")

    # State history: graceful degradation -- if this fails, dashboard still generates
    history = []
    try:
        print("Querying Notion state history database...")
        raw_history = query_database(STATE_HISTORY_DB_ID)
        history = parse_state_history(raw_history)
        print(f"Parsed {len(history)} state history records")
    except Exception as e:
        print(f"WARNING: State history query failed: {e}", file=sys.stderr)
        print("Continuing without state history data -- state-history KPIs will show 'Sin datos'", file=sys.stderr)

    # Compute operational KPIs from both data sources
    print("Computing operational KPIs...")
    kpis = compute_all_kpis(records, history)
    print(f"Computed {len(kpis)} KPI categories")

    # Detect patterns and update history
    print("Detecting patterns...")
    current_patterns = detect_patterns(records, history)
    print(f"Detected {len(current_patterns)} patterns")
    history_path = os.path.join(os.path.dirname(__file__), "pattern_history.json")
    pattern_history = update_pattern_history(current_patterns, history_path)
    print(f"Pattern history: {len(pattern_history)} snapshots")

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    print("Generating HTML...")
    html = generate_html(records, now_str, kpis, pattern_history)

    output_path = os.path.join(os.path.dirname(__file__), "public", "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Dashboard generated: {len(html)} bytes -> {output_path}")


if __name__ == "__main__":
    main()

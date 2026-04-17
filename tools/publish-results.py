#!/usr/bin/env python3
"""
Publish QA test results to GitHub Pages.

Copies Playwright reports to public/ and generates history JSON files.

Usage:
    python3 tools/publish-results.py [--date YYYY-MM-DD]

If --date is not provided, uses today's date.
"""

import json
import re
import shutil
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone
from typing import Optional


def load_results(results_file: Path) -> dict:
    """Load Playwright JSON results."""
    if not results_file.exists():
        print(f"⚠️  No results.json found at {results_file}", file=sys.stderr)
        print("   Run tests first: npx playwright test", file=sys.stderr)
        return {}

    with open(results_file) as f:
        return json.load(f)


def copy_playwright_report(src: Path, dst: Path) -> None:
    """Copy entire Playwright HTML report."""
    if src.exists():
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f"✅ Copied Playwright report to {dst}")
    else:
        print(f"⚠️  Playwright report not found at {src}", file=sys.stderr)


def copy_test_results_artifacts(src: Path, dst: Path) -> None:
    """Copy screenshots and artifacts from test results."""
    if not src.exists():
        return

    dst.mkdir(parents=True, exist_ok=True)

    # Copy all .png screenshots (skip broken symlinks)
    png_count = 0
    try:
        png_files = list(src.rglob("*.png"))
    except OSError:
        png_files = []
    for png_file in png_files:
        try:
            rel_path = png_file.relative_to(src)
            dst_file = dst / rel_path.name
            shutil.copy2(png_file, dst_file)
            png_count += 1
        except OSError:
            pass

    if png_count > 0:
        print(f"✅ Copied {png_count} screenshot(s) to {dst}")


def flatten_tests(suite: dict, file_hint: str = "", suite_title: str = "") -> list:
    """Recursively extract all tests from Playwright JSON suite structure."""
    tests = []
    file_name = suite.get("file", file_hint)
    current_title = suite.get("title", suite_title) or suite_title
    for spec in suite.get("specs", []):
        for test in spec.get("tests", []):
            results = test.get("results", [])
            last = results[-1] if results else {}
            error_msg = last.get("error", {}).get("message", "") if last else ""
            # Collect all annotations from all retries
            annotations = []
            for r in results:
                annotations.extend(r.get("annotations", []))
            tests.append({
                "file": file_name.split("/")[-1] if file_name else file_name,
                "title": spec.get("title", ""),
                "suite_title": current_title,
                "status": test.get("status"),
                "error": error_msg,
                "annotations": annotations,
            })
    for sub in suite.get("suites", []):
        tests.extend(flatten_tests(sub, file_name, current_title))
    return tests


def extract_suite_stats(results: dict, suite_name: str) -> dict:
    """Extract stats for a specific suite from Playwright results."""
    all_tests = []
    for suite in results.get("suites", []):
        all_tests.extend(flatten_tests(suite))

    suite_tests = [t for t in all_tests if suite_name in t.get("file", "")]

    passed = sum(1 for t in suite_tests if t.get("status") in ("expected", "flaky"))
    failed = sum(1 for t in suite_tests if t.get("status") == "unexpected")
    skipped = sum(1 for t in suite_tests if t.get("status") == "skipped")

    return {
        "tests": len(suite_tests),
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
    }


def strip_ansi(text: str) -> str:
    return re.sub(r'\x1b\[[0-9;]*m', '', text)


def _clean_title(title: str) -> str:
    """Remove 'client: ' prefix and test ID (C2-11, PM1-03, etc.) from test title."""
    # Strip "bastien: " prefix
    t = re.sub(r'^[a-z0-9_-]+:\s*', '', title)
    # Strip leading test IDs like "C2-11 ", "PM1-03 ", "PAG-04 "
    t = re.sub(r'^[A-Z][A-Z0-9]+-\d+\s+', '', t)
    return t.strip()


def classify_error(error: str, annotations: list = None, title: str = "") -> tuple:
    """
    Classify a test error into (category, reason, owner, action).
    owner: 'dev' | 'qa'
    action: concrete next step — clear and actionable for the team
    reason: human-readable, no raw Playwright output
    """
    error = strip_ansi(error)
    annotations = annotations or []

    ann_texts = " ".join(a.get("description", "") for a in annotations)
    ann_error_texts = " ".join(a.get("description", "") for a in annotations if a.get("type") == "error")
    clean = _clean_title(title)

    # ── Ambiente: 5xx server errors (detected via annotations) ───────────────
    server_error_match = re.search(r"Requests 5xx:\s*(.+?)(?:\n|$)", ann_error_texts)
    if server_error_match:
        urls_raw = server_error_match.group(1).strip()
        entries = [e.strip() for e in urls_raw.split(",") if e.strip()]
        url_codes: dict = {}
        for entry in entries:
            parts = entry.split(" ", 1)
            if len(parts) == 2:
                code, url = parts[0], parts[1]
                url = re.split(r'\s+Requests', url)[0].strip()
                if re.match(r'https?://', url):
                    # Normalize: strip query params for grouping key
                    url_codes[url.split("?")[0]] = code
        unique_urls = list(url_codes.keys())
        # Use only path for display
        paths = [re.sub(r'https?://[^/]+', '', u) for u in unique_urls[:2]]
        path_str = " / ".join(f"`{p}`" for p in paths)
        reason = f"API devuelve 5xx: {path_str}"
        action = f"Revisar logs del servidor para {', '.join(unique_urls[:2])} — retorna 500 en staging."
        return ("ambiente", reason, "dev", action)

    # ── Bug: ERR_ABORTED — page load rejected ────────────────────────────────
    e = error.lower()
    if "err_aborted" in e or "net::err_aborted" in e:
        url_match = re.search(r'at (https?://\S+)', error)
        path = re.sub(r'https?://[^/]+', '', url_match.group(1)).split('?')[0] if url_match else "la URL"
        return ("bug",
                f"La página `{path}` es abortada — ruta bloqueada o inaccesible",
                "dev",
                f"La navegación a `{path}` da ERR_ABORTED en Bastien staging. Verificar que la ruta existe, que el usuario tiene permisos y que no hay un redirect bloqueante. Reproducir en staging manualmente.")

    # ── Ambiente: test infrastructure error (ENOENT / file not found) ────────
    if "enoent" in e or ("no such file or directory" in e):
        return ("ambiente",
                "Error de infraestructura del test runner — archivo temporal no encontrado",
                "qa",
                "Re-ejecutar los tests en ambiente limpio. Si persiste, revisar espacio en disco o permisos en test-results/.")

    # ── Assertion failures with no error message ─────────────────────────────
    if not error:
        if ann_texts:
            return ("bug", f"{clean}: {ann_texts[:100]}" if clean else ann_texts[:120],
                    "dev", "Revisar el Trace del test — la app devolvió un valor inesperado.")
        return ("bug", f"Aserción fallida en: {clean}" if clean else "Aserción fallida",
                "dev", "Revisar el Trace del test para identificar qué devolvió la app.")

    t = title.lower()

    # ── UX: toBeDisabled failures ────────────────────────────────────────────
    if "tobedisabled" in e or ("expected: disabled" in e and "received: enabled" in e):
        btn_match = re.search(r"name:\s*/([^/]+)/i?\)", error)
        btn_name = btn_match.group(1) if btn_match else "confirmar pedido"
        return ("ux",
                f"Botón '{btn_name}' activo cuando debería estar deshabilitado",
                "dev",
                f"Agregar validación en el componente para deshabilitar '{btn_name}' en el estado correcto.")

    # ── Bug: confirmCartText not applied ────────────────────────────────────
    if "confirmcarttext" in t or "pasar a confirmación" in t:
        return ("bug",
                "Texto del botón del carrito no coincide con confirmCartText en config",
                "dev",
                "Verificar que el componente del carrito lee confirmCartText desde la config del cliente.")

    # ── Bug/Ambiente: page load timeout (waitForLoadState) ───────────────────
    if "waitforloadstate" in e and "timeout" in e:
        # Checkout/historial timeouts are likely caused by the order not being created
        if any(k in t for k in ("checkout", "historial", "pedido", "order", "pago", "payment", "document")):
            return ("bug",
                    f"Página post-checkout no carga — timeout en: {clean}" if clean else "Página post-checkout no carga",
                    "dev",
                    "La página no termina de cargar después del flujo de checkout. Probablemente relacionado con que el POST a /order no completa. Verificar en bastien.solopide.me que crear un pedido funciona end-to-end.")
        return ("ambiente",
                f"Página no terminó de cargar — timeout en: {clean}" if clean else "Página no terminó de cargar (timeout)",
                "qa",
                "Verificar que staging responde en tiempos normales. Si el problema es solo en staging, puede ser lentitud del ambiente.")

    # ── Ambiente: navigation timeout ─────────────────────────────────────────
    if "navigation" in e and "timeout" in e:
        return ("ambiente",
                f"Timeout de navegación en: {clean}" if clean else "Timeout de navegación",
                "qa",
                "Verificar que el ambiente staging esté activo. Si persiste, aumentar navigationTimeout en playwright.config.ts.")

    # ── Ambiente: selector / elemento no encontrado ──────────────────────────
    if "element(s) not found" in e or ("not found" in e and "locator" in e):
        match = re.search(r"locator\('([^']+)'\)", error)
        locator = match.group(1) if match else "selector desconocido"
        return ("ambiente", f"Elemento no encontrado: `{locator}`",
                "qa", f"Inspeccionar staging y actualizar el selector `{locator}` en el spec.")

    if "tobevisible" in e and "timeout" in e:
        match = re.search(r"locator\('([^']+)'\)", error)
        locator = match.group(1) if match else None
        if locator:
            return ("ambiente", f"Elemento no visible: `{locator}`",
                    "qa", f"Verificar si `{locator}` existe en staging o si cambió su clase/estructura.")
        return ("ambiente",
                f"Elemento esperado no aparece — timeout en: {clean}" if clean else "Elemento no visible (timeout)",
                "qa", "Verificar en staging que el elemento existe y es visible en el flujo correcto.")

    if "waitforresponse" in e and "timeout" in e:
        return ("ambiente",
                "Request HTTP al carrito nunca ocurrió — botón Agregar no respondió",
                "qa",
                "Verificar que el botón 'Agregar' dispara el POST a /cart. Puede estar relacionado con otro fallo de selector.")

    if "locator.fill" in e or "locator.click" in e:
        match = re.search(r"waiting for (.+?)[\n\r]", error)
        detail = match.group(1).strip()[:60] if match else "campo desconocido"
        return ("ambiente", f"No se pudo interactuar con: `{detail}`",
                "qa", "Verificar en staging que el campo existe con el label/placeholder correcto y actualizar el selector.")

    if "401" in error or "unauthorized" in e:
        return ("ambiente", "Error de autenticación (401) — credenciales inválidas o sesión expirada",
                "qa", "Verificar las credenciales en .env para este cliente.")

    # ── Bug: valor incorrecto (expected/received) ────────────────────────────
    if "expected:" in e and "received:" in e:
        m_exp = re.search(r"expected:\s*(.+)", error, re.IGNORECASE)
        m_rec = re.search(r"received:\s*(.+)", error, re.IGNORECASE)
        exp = m_exp.group(1).strip()[:40] if m_exp else "?"
        rec = m_rec.group(1).strip()[:40] if m_rec else "?"
        # Dedup annotation text (may repeat across retries)
        ann_dedup = " ".join(dict.fromkeys(ann_texts.split(". "))).strip() if ann_texts else ""

        if "no disponible" in (e + ann_texts.lower()):
            # Count how many "No disponible" orders
            count_match = re.search(r'(\d+)\s+pedidos?\s+con\s+estado', ann_dedup or ann_texts, re.IGNORECASE)
            count_str = f"{count_match.group(1)} pedidos con" if count_match else "pedidos con"
            reason = f"{count_str} estado 'No disponible' — estado sin mapear en el frontend"
            action = "En YOMCL/b2b buscar el componente de historial de pedidos (OrderStatus o similar) y agregar el estado 'No disponible' al mapa de estados."
        elif "> 0" in exp and rec.strip() in ("0", "0.0", "0\x1b[2m"):
            if "anonym" in t or "hideprice" in t or "price" in t:
                reason = f"Precios no visibles en catálogo anónimo (devolvió 0)"
                action = "Falso positivo probable: sin comercio seleccionado, Bastien no muestra precios en catálogo anónimo. Agregar skip condicional para clientes que requieren comercio."
            else:
                reason = f"{clean}: se esperaba al menos 1 resultado pero la app devolvió 0"
                action = f"En staging verificar que '{clean}' devuelve datos. Si el cliente requiere comercio seleccionado, el test debe seleccionarlo primero."
        elif ann_dedup:
            reason = f"{clean}: {ann_dedup[:100]}" if clean else ann_dedup[:120]
            action = ann_dedup[:200]
        else:
            reason = f"{clean}: esperado {exp}, recibido {rec}" if clean else f"Valor incorrecto — esperado: {exp}, recibido: {rec}"
            action = f"En staging comprobar manualmente el flujo '{clean}' e identificar por qué devuelve {rec} en lugar de {exp}."
        return ("bug", reason, "dev", action)

    if "tohaveurl" in e:
        return ("bug",
                f"Redirección incorrecta en: {clean}" if clean else "La app no redirigió a la URL esperada",
                "dev",
                "Revisar el routing — la app quedó en la misma URL en lugar de avanzar al paso siguiente.")

    # ── Generic fallback — human-readable, no raw error ──────────────────────
    if "timeout" in e:
        return ("ambiente",
                f"Timeout en: {clean}" if clean else "Timeout — elemento o página no respondió",
                "qa",
                f"Verificar en staging que '{clean}' funciona. Puede ser lentitud del ambiente.")

    # Catch null / not.toBeNull() assertion
    if "not.tonull" in e or "not.tobenull" in e or "received: null" in e:
        if "cupon" in t or "cupón" in t or "orden" in t or "order" in t:
            reason = f"{clean}: el POST al backend devolvió null"
            action = "El servidor no respondió al crear la orden. Verificar en bastien.solopide.me que el flujo de checkout completa el POST a /order. Puede ser que el botón de confirmar pedido esté deshabilitado o el endpoint no esté activo."
        else:
            reason = f"{clean}: la app devolvió null"
            action = f"El componente '{clean}' retornó null. Abrir staging y reproducir manualmente para identificar si es un error de datos o de lógica."
        return ("bug", reason, "dev", action)

    # Absolute fallback — use clean title only, no raw error
    reason = clean if clean else "Fallo desconocido"
    action = f"Revisar en staging el flujo '{clean}'." if clean else "Revisar el Trace del test en el reporte Playwright."
    return ("bug", reason, "qa", action)


CATEGORY_ORDER = {"bug": 0, "ux": 1, "ambiente": 2, "flaky": 3}
CATEGORY_LABELS = {
    "bug":      "🔴 Bug",
    "ux":       "🟡 Mejora UX",
    "ambiente": "🔵 Ambiente / Servidor",
    "flaky":    "⚠️ Flaky",
}


def generate_failure_groups(results: dict) -> list:
    """Group failed tests by root cause for dashboard display."""
    all_tests = []
    for suite in results.get("suites", []):
        all_tests.extend(flatten_tests(suite))

    failed = [t for t in all_tests if t.get("status") == "unexpected"]
    flaky  = [t for t in all_tests if t.get("status") == "flaky"]

    def extract_client(t: dict) -> str:
        """Extract client name from test title prefix (e.g. 'bastien: C2-08...' → 'bastien')."""
        title = t.get("title", "")
        m = re.match(r'^([a-z0-9][a-z0-9_-]*):', title)
        if m:
            return m.group(1)
        # Fallback: derive from file name (codelpa.spec.ts → codelpa)
        f = t.get("file", "")
        if f:
            return re.sub(r'\.spec\.ts$', '', f.split("/")[-1]).lower()
        return "unknown"

    # Group failures by (category, reason)
    groups: dict = defaultdict(list)
    cause_map: dict = {}
    group_clients: dict = defaultdict(set)
    group_error_sample: dict = {}
    group_annotations_sample: dict = {}
    group_spec_file: dict = {}

    for t in failed:
        category, reason, owner, action = classify_error(t.get("error", ""), t.get("annotations", []), t.get("title", ""))
        key = f"{category}::{reason}"
        groups[key].append(f"[{t['file']}] {t['title']}")
        cause_map[key] = (category, reason, owner, action)
        group_clients[key].add(extract_client(t))
        if key not in group_error_sample:
            group_error_sample[key] = strip_ansi(t.get("error", ""))[:600]
            group_spec_file[key] = t.get("file", "")
            group_annotations_sample[key] = [
                a.get("description", "")
                for a in t.get("annotations", [])
                if a.get("type") == "error" and a.get("description")
            ][:3]

    sorted_keys = sorted(groups.keys(), key=lambda k: CATEGORY_ORDER.get(cause_map[k][0], 9))

    result = []
    for key in sorted_keys:
        category, reason, owner, action = cause_map[key]
        result.append({
            "category": category,
            "label": CATEGORY_LABELS.get(category, category),
            "reason": reason,
            "owner": owner,
            "action": action,
            "count": len(groups[key]),
            "tests": groups[key],
            "clients": sorted(group_clients[key]),
            "error_sample": group_error_sample.get(key, ""),
            "annotations_sample": group_annotations_sample.get(key, []),
            "spec_file": group_spec_file.get(key, ""),
        })

    if flaky:
        flaky_clients = sorted(set(extract_client(t) for t in flaky))
        result.append({
            "category": "flaky",
            "label": "⚠️ Flaky",
            "reason": "Pasaron en retry — no son bugs confirmados",
            "owner": "qa",
            "action": "Monitorear en próximas ejecuciones. Si siguen apareciendo, investigar causa de inestabilidad",
            "count": len(flaky),
            "tests": [f"[{t['file']}] {t['title']}" for t in flaky],
            "clients": flaky_clients,
        })

    return result


def generate_pending_b2b(results: dict) -> list:
    """
    Extract tests skipped because the variable is not implemented in B2B frontend.
    Returns list of {variable, clients, tests} grouped by variable name.
    """
    all_tests = []
    for suite in results.get("suites", []):
        all_tests.extend(flatten_tests(suite))

    B2B_SKIP_PATTERN = re.compile(r"^(.+?) no implementado en B2B frontend")

    def extract_client(t: dict) -> str:
        title = t.get("title", "")
        m = re.match(r'^([a-z0-9][a-z0-9_-]*):', title)
        if m:
            return m.group(1)
        f = t.get("file", "")
        if f:
            return re.sub(r'\.spec\.ts$', '', f.split("/")[-1]).lower()
        return "unknown"

    # Group by variable name
    groups: dict = defaultdict(lambda: {"tests": [], "clients": set()})
    for t in all_tests:
        if t.get("status") != "skipped":
            continue
        for ann in t.get("annotations", []):
            if ann.get("type") != "skip":
                continue
            desc = ann.get("description", "")
            m = B2B_SKIP_PATTERN.match(desc)
            if m:
                var_name = m.group(1)
                groups[var_name]["tests"].append(f"[{t['file']}] {t['title']}")
                groups[var_name]["clients"].add(extract_client(t))

    return [
        {
            "variable": var,
            "clients": sorted(data["clients"]),
            "tests": data["tests"],
            "action": f"Se debe implementar '{var}' en el B2B frontend (YOMCL/b2b) para activar este test.",
        }
        for var, data in sorted(groups.items())
    ]


def load_staging_urls(project_root: Path) -> dict:
    """Load client slug → URL mapping from qa-matrix-staging.json."""
    matrix_file = project_root / "data" / "qa-matrix-staging.json"
    if not matrix_file.exists():
        return {}
    with open(matrix_file) as f:
        data = json.load(f)
    clients = data.get("clients", {})
    # Map: stripped slug → {name, url}
    # Keys in matrix look like "bastien-staging", strip "-staging" suffix
    result = {}
    for key, val in clients.items():
        slug = re.sub(r"-staging$", "", key)
        domain = val.get("domain", "")
        name = val.get("name", slug.capitalize())
        url = f"https://{domain}" if domain and not domain.startswith("http") else domain
        result[slug] = {"name": name, "url": url}
    return result


def extract_config_validation_clients(all_tests_flat: list, staging_urls: dict) -> dict:
    """
    Extract per-client stats aggregating ALL multi-client tests.
    All multi-client tests use '{clientKey}: test name' format in their title.
    This gives accurate totals across config-validation, checkout, payments, etc.
    """
    # Group ALL tests by client key prefix ("bastien: ", "sonrie: ", etc.)
    client_tests: dict = defaultdict(list)
    for t in all_tests_flat:
        title = t.get("title", "")
        m = re.match(r'^([a-z0-9_-]+):', title)
        if m:
            client_tests[m.group(1)].append(t)

    clients = {}
    for client_key, tests in client_tests.items():
        # Only include clients that exist in staging_urls (skip generic test IDs)
        if client_key not in staging_urls:
            continue
        passed = sum(1 for t in tests if t.get("status") in ("expected", "flaky"))
        failed = sum(1 for t in tests if t.get("status") == "unexpected")
        skipped = sum(1 for t in tests if t.get("status") == "skipped")
        info = staging_urls.get(client_key, {})
        display_name = info.get("name", client_key.capitalize())
        url = info.get("url", f"https://{client_key}.solopide.me")
        clients[client_key] = {
            "name": display_name,
            "url": url,
            "environment": "staging" if "solopide.me" in url else "production",
            "tests": len(tests) - skipped,  # show only executed tests
            "passed": passed,
            "failed": failed,
            "reportUrl": "reports/index.html",
            # last_tested will be set by generate_run_json
        }

    return clients


def generate_run_json(results: dict, date: str, project_root: Path = None) -> dict:
    """Generate the detailed run JSON."""
    if project_root is None:
        project_root = Path(__file__).parent.parent

    # Only include suites that actually ran (tests > 0)
    all_tests_flat = []
    for suite in results.get("suites", []):
        all_tests_flat.extend(flatten_tests(suite))

    # Discover which spec files actually had tests
    ran_files = sorted(set(t.get("file", "") for t in all_tests_flat if t.get("file")))

    suites = []
    total_tests = 0
    total_passed = 0
    total_failed = 0

    for file_path in ran_files:
        suite_name = file_path.split("/")[-1] if "/" in file_path else file_path
        suite_tests = [t for t in all_tests_flat if t.get("file") == file_path]
        passed = sum(1 for t in suite_tests if t.get("status") in ("expected", "flaky"))
        failed = sum(1 for t in suite_tests if t.get("status") == "unexpected")
        suites.append({
            "name": suite_name,
            "tests": len(suite_tests),
            "passed": passed,
            "failed": failed,
            "reportUrl": "reports/index.html",
        })
        total_tests += len(suite_tests)
        total_passed += passed
        total_failed += failed

    # Calculate duration (in seconds from Playwright data)
    duration = 0
    if results.get("stats"):
        duration = int(results["stats"].get("duration", 0) / 1000)

    # Per-client stats: dynamically extracted from config-validation.spec.ts
    staging_urls = load_staging_urls(project_root)
    clients = extract_config_validation_clients(all_tests_flat, staging_urls)

    # Also pick up legacy per-client spec files (codelpa.spec.ts, sonrie.spec.ts, etc.)
    # Only add if the spec name matches a known client in staging_urls — avoids adding
    # generic specs (cart.spec.ts, checkout.spec.ts, etc.) as fake clients.
    for file_path in ran_files:
        if file_path == "config-validation.spec.ts":
            continue
        suite_name = re.sub(r"\.spec\.ts$", "", file_path.split("/")[-1])
        if suite_name in clients:
            continue  # Already covered by config-validation
        if suite_name not in staging_urls:
            continue  # Not a real client — skip generic spec files
        stats = extract_suite_stats(results, file_path.split("/")[-1])
        if stats["tests"] == 0:
            continue
        info = staging_urls.get(suite_name, {})
        url = info.get("url", f"https://{suite_name}.solopide.me")
        clients[suite_name] = {
            "name": info.get("name", suite_name.capitalize()),
            "url": url,
            "environment": "staging" if "solopide.me" in url else "production",
            "tests": stats["tests"],
            "passed": stats["passed"],
            "failed": stats["failed"],
            "reportUrl": "reports/index.html",
        }

    # Stamp all clients with last_tested = today
    for k in clients:
        clients[k]["last_tested"] = date

    return {
        "date": date,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total": total_tests,
        "passed": total_passed,
        "failed": total_failed,
        "duration": duration,
        "suites": suites,
        "clients": clients,
        "failure_groups": generate_failure_groups(results),
        "pending_b2b": generate_pending_b2b(results),
        "evidence": {
            "screenshots": [],
            "errors": [],
        },
    }


def update_history_index(history_dir: Path, date: str, run_json: dict) -> None:
    """Update history/index.json with the new run."""
    index_file = history_dir / "index.json"

    # Load existing index or create new
    if index_file.exists():
        with open(index_file) as f:
            index = json.load(f)
    else:
        index = {"runs": []}

    # Check if this date already exists
    existing_run = next((r for r in index["runs"] if r["date"] == date), None)
    new_run_entry = {
        "date": date,
        "total": run_json["total"],
        "passed": run_json["passed"],
        "failed": run_json["failed"],
        "duration": run_json["duration"],
    }

    if existing_run:
        # Update existing
        idx = index["runs"].index(existing_run)
        index["runs"][idx] = new_run_entry
    else:
        # Insert at beginning (most recent first)
        index["runs"].insert(0, new_run_entry)

    # Keep only last 30 days
    index["runs"] = index["runs"][:30]

    with open(index_file, "w") as f:
        json.dump(index, f, indent=2)


def load_previous_clients(history_dir: Path, current_date: str) -> dict:
    """Return the most recent result per client from previous days.

    Used to seed a new day's run so clients tested on prior days remain visible
    in the dashboard even when not re-tested today.
    """
    files = sorted(history_dir.glob("20*.json"), reverse=True)
    accumulated: dict = {}
    for f in files:
        if f.stem >= current_date:
            continue  # skip today or future
        try:
            with open(f) as fp:
                data = json.load(fp)
        except Exception:
            continue
        for k, v in data.get("clients", {}).items():
            if k not in accumulated and isinstance(v, dict) and v.get("tests", 0) > 0:
                entry = dict(v)
                if "last_tested" not in entry:
                    entry["last_tested"] = f.stem
                accumulated[k] = entry
    return accumulated


def merge_run_json(existing: dict, new: dict) -> dict:
    """Merge new run results into existing {date}.json, accumulating clients and suites."""
    merged = dict(existing)

    # Timestamp: use most recent
    merged["timestamp"] = new["timestamp"]

    # Clients: merge by slug (new data wins if same slug)
    merged_clients = dict(existing.get("clients", {}))
    merged_clients.update(new.get("clients", {}))
    merged["clients"] = merged_clients

    # Suites: merge by name — update if exists, add if new
    existing_suites = {s["name"]: s for s in existing.get("suites", [])}
    for suite in new.get("suites", []):
        existing_suites[suite["name"]] = suite
    merged["suites"] = list(existing_suites.values())

    # Recalculate totals from merged suites
    merged["total"]    = sum(s["tests"]  for s in merged["suites"])
    merged["passed"]   = sum(s["passed"] for s in merged["suites"])
    merged["failed"]   = sum(s["failed"] for s in merged["suites"])
    merged["duration"] = existing.get("duration", 0) + new.get("duration", 0)

    # failure_groups: replace groups for clients that appear in the new run
    new_clients = set(c for g in new.get("failure_groups", []) for c in g.get("clients", []))
    # Keep existing groups only if they belong to clients NOT in this run
    kept = [g for g in existing.get("failure_groups", [])
            if not any(c in new_clients for c in g.get("clients", []))]
    merged["failure_groups"] = kept + new.get("failure_groups", [])

    # pending_b2b: union deduplicating by slug
    existing_pb = {p.get("slug", str(p)): p for p in existing.get("pending_b2b", [])}
    for p in new.get("pending_b2b", []):
        existing_pb[p.get("slug", str(p))] = p
    merged["pending_b2b"] = list(existing_pb.values())

    # evidence: concatenate lists
    merged["evidence"] = {
        "screenshots": (existing.get("evidence", {}).get("screenshots", []) +
                        new.get("evidence", {}).get("screenshots", [])),
        "errors": (existing.get("evidence", {}).get("errors", []) +
                   new.get("evidence", {}).get("errors", [])),
    }

    return merged


def main():
    """Main entry point.

    Usage:
        python3 tools/publish-results.py [--date YYYY-MM-DD] [--results-file PATH] [--client SLUG]

    --client stores the Playwright report in public/reports/{slug}/ so each client
    has its own report URL. Without --client, auto-detects from results if only one
    client ran, otherwise falls back to shared public/reports/.

    Example for two parallel sessions:
        npx playwright test --project=b2b --grep "Sonrie" --reporter=json,outputFile=playwright-report/results-sonrie.json
        python3 tools/publish-results.py --results-file tests/e2e/playwright-report/results-sonrie.json --client sonrie

        npx playwright test --project=b2b --grep "Bastien" --reporter=json,outputFile=playwright-report/results-bastien.json
        python3 tools/publish-results.py --results-file tests/e2e/playwright-report/results-bastien.json --client bastien
    """
    # Parse arguments
    date = None
    custom_results_file: Optional[str] = None
    client_slug: Optional[str] = None

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--date" and i + 1 < len(args):
            date = args[i + 1]
            i += 2
        elif args[i] == "--results-file" and i + 1 < len(args):
            custom_results_file = args[i + 1]
            i += 2
        elif args[i] == "--client" and i + 1 < len(args):
            client_slug = args[i + 1]
            i += 2
        else:
            print(f"Usage: python3 {sys.argv[0]} [--date YYYY-MM-DD] [--results-file PATH] [--client SLUG]", file=sys.stderr)
            sys.exit(1)

    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    print(f"Publishing results for {date}...")

    # Paths
    project_root = Path(__file__).parent.parent

    if custom_results_file:
        results_file = Path(custom_results_file)
        if not results_file.is_absolute():
            results_file = project_root / results_file
        # Derive report dir from results file (parent dir)
        src_report = results_file.parent
    else:
        results_file = project_root / "tests" / "e2e" / "playwright-report" / "results.json"
        src_report = project_root / "tests" / "e2e" / "playwright-report"
    src_test_results = project_root / "tests" / "e2e" / "test-results"

    dst_data = project_root / "public" / "data"
    history_dir = project_root / "public" / "history"

    # Ensure history directory exists
    history_dir.mkdir(parents=True, exist_ok=True)

    # Load results
    results = load_results(results_file)

    # Auto-detect client slug from results if not provided
    if not client_slug:
        detected = list(results.get("suites", []))
        # Try to find a single client key from config-validation suites
        from collections import Counter
        all_titles = []
        def _collect_titles(suite):
            all_titles.append(suite.get("title", ""))
            for s in suite.get("suites", []):
                _collect_titles(s)
        for s in results.get("suites", []):
            _collect_titles(s)
        # Look for patterns like "Config validation: Sonrie (staging)"
        import re as _re
        slugs = _re.findall(r'^(\w[\w-]+):\s', " ".join(all_titles))
        unique_slugs = list(dict.fromkeys(slugs))
        if len(unique_slugs) == 1:
            client_slug = unique_slugs[0]
            print(f"ℹ️  Auto-detected client: {client_slug}")

    # Report directory: per-client if slug known, shared fallback otherwise
    if client_slug:
        dst_reports = project_root / "public" / "reports" / client_slug
        report_url = f"reports/{client_slug}/index.html"
    else:
        dst_reports = project_root / "public" / "reports"
        report_url = "reports/index.html"

    # Copy reports
    copy_playwright_report(src_report, dst_reports)

    # Copy artifacts
    copy_test_results_artifacts(src_test_results, dst_data)

    # Generate run JSON
    run_json = generate_run_json(results, date, project_root=project_root)

    # Update reportUrl only for the client(s) that actually ran in this batch
    # When --client is explicit, only update that one client
    # Otherwise update all clients that had non-skipped tests
    if client_slug and client_slug in run_json["clients"]:
        run_json["clients"][client_slug]["reportUrl"] = report_url
    else:
        for slug, client_data in run_json["clients"].items():
            if client_data.get("passed", 0) + client_data.get("failed", 0) > 0:
                client_data["reportUrl"] = f"reports/{slug}/index.html" if not client_slug else report_url

    # Write run details — merge with existing if present (accumulate clients across runs)
    run_file = history_dir / f"{date}.json"
    if run_file.exists():
        with open(run_file) as f:
            existing_run = json.load(f)
        run_json = merge_run_json(existing_run, run_json)
        print(f"ℹ️  Merged with existing {run_file.name}")
    else:
        # New day: seed with clients from previous days so they stay visible in
        # the dashboard even when not re-tested today.
        prev_clients = load_previous_clients(history_dir, date)
        if prev_clients:
            # Only let today's clients override seeded data if they actually ran (tests > 0).
            # A run with 0 tests (all skipped / grep miss) must not wipe previous results.
            today_active = {k: v for k, v in run_json["clients"].items()
                            if v.get("tests", 0) > 0}
            run_json["clients"] = {**prev_clients, **today_active}
            print(f"ℹ️  Seeded {len(prev_clients)} clients from previous runs "
                  f"({len(today_active)} updated by today's run)")
    with open(run_file, "w") as f:
        json.dump(run_json, f, indent=2)
    print(f"✅ Generated {run_file}")

    # Update history index
    update_history_index(history_dir, date, run_json)
    print(f"✅ Updated history/index.json")

    # Summary
    print(f"\n📊 Summary:")
    print(f"   Total: {run_json['total']}")
    print(f"   Passed: {run_json['passed']} ✅")
    print(f"   Failed: {run_json['failed']} ❌")
    print(f"   Duration: {run_json['duration']}s ({run_json['duration'] / 60:.1f}m)")
    print(f"\n✨ Dashboard ready: open public/index.html or visit GitHub Pages")


if __name__ == "__main__":
    main()

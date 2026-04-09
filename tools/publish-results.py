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

    # Copy all .png screenshots
    png_count = 0
    for png_file in src.rglob("*.png"):
        rel_path = png_file.relative_to(src)
        dst_file = dst / rel_path.name  # Flatten to data/ root
        shutil.copy2(png_file, dst_file)
        png_count += 1

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


def classify_error(error: str, annotations: list = None, title: str = "") -> tuple:
    """
    Classify a test error into (category, reason, owner, action).
    owner: 'dev' | 'qa'
    action: concrete next step
    """
    error = strip_ansi(error)
    annotations = annotations or []

    # Extract annotation text for richer context
    ann_texts = " ".join(a.get("description", "") for a in annotations)
    ann_error_texts = " ".join(a.get("description", "") for a in annotations if a.get("type") == "error")

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
                    url_codes[url] = code
        unique_urls = list(url_codes.keys())
        url_list = ", ".join(f"`{url}` ({url_codes[url]})" for url in unique_urls[:3])
        reason = f"Error de servidor (5xx) en: {url_list}"
        action = (
            f"Se debe revisar los logs del servidor para el endpoint {', '.join(unique_urls[:3])} "
            f"(GET, staging). El servidor retorna 500 — se debe identificar y corregir el error interno."
        )
        return ("ambiente", reason, "dev", action)

    # ── Assertion failures enriched by annotations ────────────────────────────
    if not error:
        if ann_texts:
            return ("bug", f"Aserción fallida: {ann_texts[:120]}",
                    "dev", "Se debe revisar el Trace del test para ver qué devolvió la app e identificar la causa raíz")
        return ("bug", "Aserción fallida — la app devolvió un valor incorrecto",
                "dev", "Se debe revisar el Trace del test para ver qué devolvió la app e identificar la causa raíz")

    e = error.lower()
    t = title.lower()

    # ── UX: toBeDisabled failures ────────────────────────────────────────────
    if "tobedisabled" in e or ("expected: disabled" in e and "received: enabled" in e):
        btn_match = re.search(r"name:\s*/([^/]+)/i?\)", error)
        btn_name = btn_match.group(1) if btn_match else "confirmar pedido"
        return ("ux",
                f"Botón '{btn_name}' habilitado en estado donde debería estar deshabilitado",
                "dev",
                f"Se debe agregar validación en el componente para deshabilitar el botón '{btn_name}' cuando no corresponde interactuar.")

    # ── Bug: confirmCartText not applied ────────────────────────────────────
    if "confirmcarttext" in t or "pasar a confirmación" in t:
        return ("bug",
                "confirmCartText no se aplica — texto del botón no coincide con la config",
                "dev",
                "Se debe verificar que el componente del carrito lee confirmCartText desde la config del cliente. "
                "En MongoDB está configurado como 'Pasar a confirmación del pedido' pero el botón muestra otro texto.")

    # ── Ambiente: selector / elemento no encontrado ──────────────────────────
    if "element(s) not found" in e or ("not found" in e and "locator" in e):
        match = re.search(r"locator\('([^']+)'\)", error)
        locator = match.group(1) if match else "locator desconocido"
        return ("ambiente", f"Elemento no encontrado en staging: `{locator}`",
                "qa", f"Se debe inspeccionar el sitio staging, buscar el elemento real y actualizar el selector `{locator}` en el spec")

    if "tobevisible" in e and "timeout" in e:
        match = re.search(r"locator\('([^']+)'\)", error)
        locator = match.group(1) if match else "locator desconocido"
        return ("ambiente", f"Elemento no visible tras timeout: `{locator}`",
                "qa", f"Se debe verificar si el elemento `{locator}` existe en staging o si cambió de clase/estructura")

    if "waitforresponse" in e and "timeout" in e:
        return ("ambiente", "Request HTTP esperada nunca ocurrió (botón no se pudo clickear antes)",
                "qa", "Se resuelve al arreglar el selector del botón de carrito en el grupo anterior")

    if "locator.fill" in e or "locator.click" in e:
        match = re.search(r"waiting for (.+?)[\n\r]", error)
        detail = match.group(1).strip()[:80] if match else "locator desconocido"
        return ("ambiente", f"No se pudo interactuar con: `{detail}`",
                "qa", "Se debe inspeccionar el sitio staging, verificar que el campo existe con el label/placeholder correcto y actualizar el selector en el spec")

    if "navigation" in e and "timeout" in e:
        return ("ambiente", "La página tardó demasiado en cargar (timeout de navegación)",
                "qa", "Se debe verificar que el ambiente staging esté activo. Si persiste, se debe aumentar navigationTimeout en playwright.config.ts")

    if "401" in error or "unauthorized" in e:
        return ("ambiente", "Error de autenticación (401) — credenciales inválidas",
                "qa", "Se debe verificar que las credenciales en .env sean correctas para este cliente")

    # ── Bug: valor incorrecto (expected/received) ────────────────────────────
    if "expected:" in e and "received:" in e:
        m_exp = re.search(r"expected:\s*(.+)", error, re.IGNORECASE)
        m_rec = re.search(r"received:\s*(.+)", error, re.IGNORECASE)
        exp = m_exp.group(1).strip()[:50] if m_exp else "?"
        rec = m_rec.group(1).strip()[:50] if m_rec else "?"
        reason = f"Expected: {exp} → Received: {rec}"
        if "no disponible" in e or "disponible" in rec.lower():
            action = "Se debe verificar el mapeo de estados de pedido para este cliente — hay pedidos con estado 'No disponible' sin mapear en el frontend"
        elif ann_texts:
            action = f"{ann_texts[:200]}"
        else:
            action = f"Se debe revisar en staging el comportamiento de '{title}' — la app devolvió un valor inesperado."
        return ("bug", reason, "dev", action)

    if "tohaveurl" in e:
        return ("bug", "La app no redirigió a la URL esperada",
                "dev", "Se debe revisar el routing de este flujo — la app quedó en la misma URL en lugar de avanzar.")

    return ("bug", f"{title}: {error[:80]}" if title else error[:100],
            "qa", f"Se debe revisar manualmente en staging el test '{title}'." if title else "Se debe revisar manualmente en staging.")


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
        """Extract client name from suite_title or file name."""
        suite = t.get("suite_title", "")
        if suite:
            # suite_title is often "Codelpa — Login" or "codelpa (https://...)"
            # Take the part before ' —', ' (', or ':'
            m = re.match(r'^([^—(\-:]+)', suite)
            if m:
                return m.group(1).strip().lower()
        # Fallback: derive from file name (codelpa.spec.ts → codelpa)
        f = t.get("file", "")
        if f:
            return re.sub(r'\.spec\.ts$', '', f.split("/")[-1]).lower()
        return "unknown"

    # Group failures by (category, reason)
    groups: dict = defaultdict(list)
    cause_map: dict = {}
    group_clients: dict = defaultdict(set)

    for t in failed:
        category, reason, owner, action = classify_error(t.get("error", ""), t.get("annotations", []), t.get("title", ""))
        key = f"{category}::{reason}"
        groups[key].append(f"[{t['file']}] {t['title']}")
        cause_map[key] = (category, reason, owner, action)
        group_clients[key].add(extract_client(t))

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
        suite = t.get("suite_title", "")
        if suite:
            m = re.match(r'^([^—(\-:]+)', suite)
            if m:
                return m.group(1).strip().lower()
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


def generate_run_json(results: dict, date: str) -> dict:
    """Generate the detailed run JSON."""
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

    # Per-client stats derived from actual results
    codelpa_stats = extract_suite_stats(results, "codelpa.spec.ts")
    surtiventas_stats = extract_suite_stats(results, "surtiventas.spec.ts")

    clients = {
        "codelpa": {
            "name": "Codelpa",
            "url": "https://beta-codelpa.solopide.me",
            "tests": codelpa_stats["tests"],
            "passed": codelpa_stats["passed"],
            "failed": codelpa_stats["failed"],
            "reportUrl": "reports/index.html",
        },
        "surtiventas": {
            "name": "Surtiventas",
            "url": "https://surtiventas.solopide.me",
            "tests": surtiventas_stats["tests"],
            "passed": surtiventas_stats["passed"],
            "failed": surtiventas_stats["failed"],
            "reportUrl": "reports/index.html",
        },
    }

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


def main():
    """Main entry point."""
    # Parse date argument
    date = None
    if len(sys.argv) > 1:
        if sys.argv[1] == "--date" and len(sys.argv) > 2:
            date = sys.argv[2]
        else:
            print(f"Usage: python3 {sys.argv[0]} [--date YYYY-MM-DD]", file=sys.stderr)
            sys.exit(1)

    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    print(f"Publishing results for {date}...")

    # Paths
    project_root = Path(__file__).parent.parent
    results_file = project_root / "tests" / "e2e" / "playwright-report" / "results.json"
    src_report = project_root / "tests" / "e2e" / "playwright-report"
    src_test_results = project_root / "tests" / "e2e" / "test-results"

    dst_reports = project_root / "public" / "reports"
    dst_data = project_root / "public" / "data"
    history_dir = project_root / "public" / "history"

    # Ensure history directory exists
    history_dir.mkdir(parents=True, exist_ok=True)

    # Load results
    results = load_results(results_file)

    # Copy reports
    copy_playwright_report(src_report, dst_reports)

    # Copy artifacts
    copy_test_results_artifacts(src_test_results, dst_data)

    # Generate run JSON
    run_json = generate_run_json(results, date)

    # Write run details
    run_file = history_dir / f"{date}.json"
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

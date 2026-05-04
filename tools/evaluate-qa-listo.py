#!/usr/bin/env python3
"""
Evaluate QA LISTO deploy-readiness per client.

Reads:
  public/manifest.json   — Cowork verdicts (platform:b2b) + Maestro scores (platform:app)
  public/history/20*.json — Playwright results per client (most recent real run)

Writes:
  public/weekly-status.json — LISTO / PENDIENTE / BLOQUEADO per client + thresholds

Usage:
    python3 tools/evaluate-qa-listo.py [--dry-run]

--dry-run: print table to stdout without writing or committing.
"""

import glob
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Thresholds (D-01, D-02, D-03) ─────────────────────────────────────────────
PLAYWRIGHT_MIN_PASS_PCT = 80
MAESTRO_MIN_HEALTH = 60

# ── Console sort order ──────────────────────────────────────────────────────────
STATUS_ORDER = {"BLOQUEADO": 0, "PENDIENTE": 1, "LISTO": 2}


def load_manifest_data(project_root: Path) -> tuple:
    """Return (cowork_by_slug, maestro_by_slug).

    cowork_by_slug: {slug: {verdict, score, date}} — platform == 'b2b'
    maestro_by_slug: {slug: {score, date}}         — platform == 'app'

    Only the most recent entry per slug (by date DESC) is kept.
    Maestro N/A: slug absent from maestro_by_slug (D-08 — determined dynamically).
    """
    manifest_path = project_root / "public" / "qa" / "manifest.json"
    with open(manifest_path) as f:
        manifest = json.load(f)

    cowork: dict = {}
    maestro: dict = {}

    for r in manifest.get("reports", []):
        slug = r.get("client_slug")
        date = r.get("date", "")
        if not slug or not date:
            continue
        platform = r.get("platform")
        if platform == "b2b":
            if slug not in cowork or date > cowork[slug]["date"]:
                cowork[slug] = {
                    "verdict": r.get("verdict"),
                    "score": r.get("score"),
                    "date": date,
                }
        elif platform == "app":
            if slug not in maestro or date > maestro[slug]["date"]:
                maestro[slug] = {
                    "score": r.get("score", 0),
                    "date": date,
                }

    return cowork, maestro


def load_playwright_data(project_root: Path) -> dict:
    """Return most recent real Playwright result per client_slug.

    'Real run' detection: passed + failed > 0 (NOT tests > 0, because tests can be
    non-zero when all tests are skipped). Seeded entries from load_previous_clients()
    always have passed=0 and failed=0 — these are correctly skipped (D-07).

    Walks history files DESC; continues to older files if a client has only seeded data
    in more recent files (do NOT break on the first zero-entry for a slug).

    Returns {} for clients with no real run across all history files.
    """
    pattern = str(project_root / "public" / "qa" / "history" / "20*.json")
    files = sorted(
        (f for f in glob.glob(pattern) if not f.endswith("index.json")),
        reverse=True,
    )

    result: dict = {}

    for f in files:
        with open(f) as fp:
            data = json.load(fp)
        for slug, c in data.get("clients", {}).items():
            if slug in result:
                continue  # already found a real run for this slug
            passed = c.get("passed", 0)
            failed = c.get("failed", 0)
            tests = c.get("tests", 0)
            if passed + failed > 0:  # real run — not seeded
                result[slug] = {
                    "tests": tests,
                    "passed": passed,
                    "failed": failed,
                    "date": Path(f).stem,
                }
            # else: seeded or all-skipped — continue to older files for this slug

    return result


def classify_client(
    slug: str,
    pw_data: dict,
    cowork_data: dict,
    maestro_data: dict,
) -> dict:
    """Classify a client as BLOQUEADO / LISTO / PENDIENTE.

    Evaluation order: BLOQUEADO first (D-04). Two flags track composite state:
    - blocked  : any single signal blocks the deploy
    - all_green: ALL required signals are green (no missing data, no conditions)

    Returns:
        {"status": "LISTO"}                                for fully green
        {"status": "PENDIENTE", "reason": "..."}          for default / conditional
        {"status": "BLOQUEADO", "reason": "reason1; ..."}  for explicit blockers

    LISTO entries have NO "reason" key (avoids empty title="" tooltip — D-03).
    """
    blocked = False
    all_green = True
    reasons: list = []

    # ── Playwright ──────────────────────────────────────────────────────────────
    pw = pw_data.get(slug)
    if pw:
        tests = pw["tests"]
        passed = pw["passed"]
        pct = round(passed / tests * 100, 1) if tests > 0 else 0.0
        if pct < PLAYWRIGHT_MIN_PASS_PCT:
            blocked = True
            reasons.append(f"Playwright {pct}% < {PLAYWRIGHT_MIN_PASS_PCT}%")
        # else: PW is green — all_green stays True for this dimension
    else:
        # No real Playwright run found (D-07)
        all_green = False
        reasons.append("Playwright: sin datos recientes")

    # ── Cowork ─────────────────────────────────────────────────────────────────
    cw = cowork_data.get(slug)
    if cw:
        verdict = cw.get("verdict", "")
        if verdict == "BLOQUEADO":
            blocked = True
            reasons.append("Cowork: BLOQUEADO")
        elif verdict == "LISTO":
            pass  # green — all_green stays True for this dimension
        else:
            # CON_CONDICIONES or anything else → PENDIENTE (D-05)
            all_green = False
            reasons.append(f"Cowork: {verdict}" if verdict else "Cowork: sin veredicto")
    else:
        # No Cowork report yet (D-06)
        all_green = False
        reasons.append("Cowork: sin reporte")

    # ── Maestro (only if client has APP entries in manifest) ───────────────────
    mt = maestro_data.get(slug)  # None = N/A client (D-08)
    if mt is not None:
        score = mt.get("score", 0)
        if score < MAESTRO_MIN_HEALTH:
            blocked = True
            reasons.append(f"Maestro score {score} < {MAESTRO_MIN_HEALTH}")
        # else: Maestro green — all_green stays True for this dimension
    # If mt is None: N/A — does NOT affect blocked or all_green

    # ── Final classification ────────────────────────────────────────────────────
    if blocked:
        return {"status": "BLOQUEADO", "reason": "; ".join(reasons)}
    if all_green:
        return {"status": "LISTO"}  # No "reason" key — correct per spec
    return {"status": "PENDIENTE", "reason": reasons[0] if reasons else ""}


def build_all_slugs(
    pw_data: dict,
    cowork_data: dict,
    maestro_data: dict,
) -> set:
    """Return union of all client slugs across the three data sources.

    Ensures clients with Cowork/Maestro data but no Playwright history are still
    evaluated (they become PENDIENTE "Playwright: sin datos recientes").
    """
    return set(pw_data.keys()) | set(cowork_data.keys()) | set(maestro_data.keys())


def git_commit_push(project_root: Path, date: str) -> None:
    """Commit and push weekly-status.json (pull --rebase on rejection — D-14)."""
    subprocess.run(
        ["git", "add", "public/qa/weekly-status.json"],
        cwd=project_root,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", f"chore(weekly-status): update QA LISTO status {date}"],
        cwd=project_root,
        check=True,
    )
    result = subprocess.run(
        ["git", "push", "origin", "main"],
        cwd=project_root,
    )
    if result.returncode != 0:
        print("push rejected — pulling --rebase and retrying...", file=sys.stderr)
        subprocess.run(
            ["git", "pull", "--rebase", "origin", "main"],
            cwd=project_root,
            check=True,
        )
        subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=project_root,
            check=True,
        )


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    project_root = Path(__file__).parent.parent

    # ── Load data sources ───────────────────────────────────────────────────────
    cowork_data, maestro_data = load_manifest_data(project_root)
    pw_data = load_playwright_data(project_root)

    # ── Build union of slugs ────────────────────────────────────────────────────
    all_slugs = build_all_slugs(pw_data, cowork_data, maestro_data)

    # ── Classify each client ────────────────────────────────────────────────────
    clients: dict = {}
    for slug in sorted(all_slugs):
        clients[slug] = classify_client(slug, pw_data, cowork_data, maestro_data)

    # ── Build output JSON ───────────────────────────────────────────────────────
    now = datetime.now(timezone.utc)
    output = {
        "generated_at": now.isoformat(),
        "reference_date": now.strftime("%Y-%m-%d"),
        "thresholds": {
            "playwright_min_pass_pct": PLAYWRIGHT_MIN_PASS_PCT,
            "maestro_min_health": MAESTRO_MIN_HEALTH,
        },
        "clients": clients,
    }

    # ── Console table (D-15): BLOQUEADO first, PENDIENTE second, LISTO last ────
    sorted_clients = sorted(
        clients.items(),
        key=lambda x: (STATUS_ORDER.get(x[1]["status"], 9), x[0]),
    )

    date_str = now.strftime("%Y-%m-%d")
    sep = "\u2500" * 54
    print(f"\nEstado QA LISTO \u2014 {date_str}")
    print(sep)
    for slug, entry in sorted_clients:
        status = entry["status"]
        reason = entry.get("reason", "")
        slug_col = slug.ljust(15)
        status_col = status.ljust(10)
        print(f"{status_col} {slug_col} {reason}")
    print(sep)

    n_bloqueado = sum(1 for e in clients.values() if e["status"] == "BLOQUEADO")
    n_pendiente = sum(1 for e in clients.values() if e["status"] == "PENDIENTE")
    n_listo = sum(1 for e in clients.values() if e["status"] == "LISTO")
    print(f"{n_bloqueado} BLOQUEADO \u00b7 {n_pendiente} PENDIENTES \u00b7 {n_listo} LISTOS")

    if dry_run:
        print("\nDRY RUN \u2014 no escribiendo archivo")
        sys.exit(0)

    # ── Write weekly-status.json ────────────────────────────────────────────────
    output_path = project_root / "public" / "qa" / "weekly-status.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"\u2192 public/weekly-status.json updated")

    # ── Git commit + push ───────────────────────────────────────────────────────
    git_commit_push(project_root, date_str)


if __name__ == "__main__":
    main()

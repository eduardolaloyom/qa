# Architecture — QA Reporting Pipeline

**Analysis Date:** 2026-04-19
**Focus:** How test results flow from run to public GitHub Pages dashboard

---

## Pipeline Overview

Three result types feed the dashboard independently. None are connected to each other in real-time — they publish to `public/` via different mechanisms and the dashboard reads them from GitHub Pages.

```
Playwright run → live.json (real-time) → publish-results.py → public/history/{date}.json
Maestro run    → run-maestro.sh        → public/app-reports/{client}-{date}.html
Cowork session → /report-qa command    → public/qa-reports/{client}-{date}.html

All three → public/manifest.json (unified listing)
           public/ committed to git → GitHub Pages
```

---

## Layer 1 — Test Execution

### Playwright (B2B and Admin)

Entry point: `tests/e2e/playwright.config.ts`

- **Workers:** `workers: 4` — four spec files run concurrently
- **fullyParallel: true** — tests within a spec also run in parallel
- **Retries:** 1 locally, 2 in CI
- **Reporters active per run:**
  - `html` → `tests/e2e/playwright-report/` (Playwright's native HTML report)
  - `json` → `tests/e2e/playwright-report/results.json` (machine-readable source of truth)
  - `list` → stdout
  - `../../tools/live-reporter.js` → `public/live.json` (only when `CI` env var is not set)

Parallel results aggregate into a single `results.json`. The JSON has a nested suite tree; `publish-results.py` flattens it recursively via `flatten_tests()`.

**Per-client runs** are also supported: run Playwright with `--grep {client_slug}`, copy `results.json` to `results-{client}.json`, then call `publish-results.py --results-file results-{client}.json --client {slug}`. This allows parallel publish sessions without overwriting each other.

### Maestro (APP mobile)

Entry point: `tools/run-maestro.sh <cliente>`

- Reads flow definitions from `tests/app/flows/{cliente}-session.yaml` or numbered flows `tests/app/flows/{cliente}-NN-{feature}.yaml`
- Reads env vars from `tests/app/config/config.{cliente}.yaml` (preferred) or `env.{cliente}.yaml` (legacy)
- Runs each flow via `maestro test` subprocess with up to 3 automatic retries (1 for session flows)
- Writes raw log to `QA/{Cliente}/{date}/maestro.log`
- Generates HTML report inline (Python embedded in shell script) and writes to `public/app-reports/{client}-{date}.html`
- Updates `public/manifest.json` immediately after the run (no git commit step inside the script)

### Cowork (manual + AI-assisted sessions)

No automated execution. Output is:

1. Tester saves HANDOFF blocks to `QA/{CLIENT}/{DATE}/cowork-session.md` (one file per day, all modes appended)
2. `/report-qa {CLIENT} {DATE}` command (defined in `ai-specs/.commands/report-qa.md`) reads that file
3. Command generates `public/qa-reports/{client}-{date}.html` and updates `public/manifest.json`

---

## Layer 2 — Live Reporting (Playwright only)

**File:** `tools/live-reporter.js`

Implements the Playwright `Reporter` interface. Active during local runs only (skipped when `CI` env var is set — see `playwright.config.ts` line 25).

**Atomic write pattern:**
```
state → JSON.stringify → write to public/live.json.tmp → fs.renameSync → public/live.json
```
The `rename` is atomic on POSIX — the dashboard never reads a partially-written file.

**GitHub push cadence:** Maximum once every 10 seconds (`PUSH_INTERVAL_MS = 10_000`). Uses GitHub Contents API (PUT to `/repos/eduardolaloyom/qa/contents/public/live.json`). Caches the SHA of `public/live.json` to avoid a GET on every push.

**On test end:** `onEnd()` forces an immediate push (bypasses the 10s interval) to ensure the final state is published even if the run is short.

**State shape:**
```json
{
  "running": true,
  "startTime": "2026-04-19T10:00:00.000Z",
  "total": 252,
  "passed": 120,
  "failed": 3,
  "skipped": 0,
  "currentTest": "bastien: C2-08 cart adds product",
  "recentTests": [
    { "title": "...", "status": "passed", "duration": 1230 }
  ]
}
```

**Dashboard polling:** `public/index.html` polls `live.json?t={timestamp}` every 3 seconds (`setTimeout(pollLive, 3000)`) and shows a live panel (dark navy card with pulse dot) when `running: true`.

**Gitignore:** `public/live.json` and `public/live.json.tmp` are gitignored — they exist only locally during a run and are pushed directly to GitHub via API, not via git commit.

---

## Layer 3 — Result Publishing (Playwright)

**File:** `tools/publish-results.py`

Triggered two ways:
1. Automatically via `tests/e2e/global-teardown.ts` — executes `python3 tools/publish-results.py` after every `npx playwright test` invocation
2. Manually via `tools/run-live.sh` — called explicitly after the test run completes

**What it does:**

1. Reads `tests/e2e/playwright-report/results.json` (or a custom `--results-file`)
2. Copies the Playwright HTML report directory to `public/reports/` (or `public/reports/{slug}/` for per-client runs)
3. Copies failure screenshots from `tests/e2e/test-results/*.png` to `public/data/`
4. Generates a structured run JSON via `generate_run_json()`:
   - Extracts per-client stats from test titles using the `{client_slug}: test name` prefix convention
   - Loads client metadata (name, staging URL, environment) from `data/qa-matrix-staging.json` via `load_staging_urls()`
   - Classifies failures via `classify_error()` into categories: `bug`, `ux`, `ambiente`, `flaky`
   - Groups failures by root cause for dashboard display (`generate_failure_groups()`)
   - Identifies skipped tests with `{var} no implementado en B2B frontend` annotation (`generate_pending_b2b()`)
   - Redacts secrets from error messages before writing (`mask_secrets()`)
5. Writes `public/history/{date}.json` — merges with existing file if same date (`merge_run_json()`); seeds with previous days' clients if new date (`load_previous_clients()`)
6. Updates `public/history/index.json` (rolling 30-day index of run summaries)

**Merge behavior (same date, multiple runs):**
- `merge_run_json()` keeps the client with more active tests (passed + failed) — new data wins only if it ran at least as many tests as existing
- Failure groups: replaces groups for clients that appeared in the new run; keeps others
- Duration: accumulated (sum of all runs that day)
- Totals: recalculated from merged client data, not raw suite counts

**Persistence across days:**
New day's `{date}.json` is seeded with the most recent result per client from prior days via `load_previous_clients()`. This keeps all clients visible in the dashboard even if only a subset ran today. Seeded clients are overridden by today's results only if the new run has active (non-skipped) tests.

---

## Layer 4 — Dashboard (GitHub Pages)

**File:** `public/index.html`

Single-file static dashboard (~2600 lines). No build step, no bundler. Fetches all data client-side via `fetch()` with cache-busting query params.

**Data sources fetched at load:**

| Source | What it provides |
|--------|-----------------|
| `history/index.json` | List of run dates (last 30 days) |
| `history/{date}.json` | Full run stats, per-client results, failure groups, pending B2B vars |
| `live.json` | Real-time test progress (polled every 3s during active run) |
| `manifest.json` | List of all Cowork + Maestro HTML reports |

**Tabs:**
- **B2B tab:** reads `history/{date}.json` — shows per-client pass/fail, failure groups grouped by category (bug/ux/ambiente/flaky), pending B2B variables
- **APP tab:** reads `manifest.json` filtering `platform: "app"` — shows Maestro reports grouped by client with drill-down history
- **Cowork reports:** links to `public/qa-reports/index.html` — a separate directory index

**History navigation:** user selects any date from the last 30 runs; dashboard re-fetches `history/{date}.json` and re-renders.

---

## Layer 5 — manifest.json (Unified Report Listing)

**File:** `public/manifest.json`

Single JSON file listing all completed QA reports (Cowork B2B and Maestro APP).

Entry shape:
```json
{
  "client": "Bastien",
  "client_slug": "bastien",
  "date": "2026-04-15",
  "file": "qa-reports/bastien-2026-04-15.html",
  "verdict": "CON_CONDICIONES",
  "score": 82,
  "modes_done": ["A", "B", "D"],
  "platform": "b2b",
  "environment": "staging"
}
```

**Writers:**
- `tools/run-maestro.sh` (Python embedded) — writes `platform: "app"`, `file: "app-reports/{client}-{date}.html"`, `health` instead of `score`
- `/report-qa` command (Claude Code) — writes `platform: "b2b"`, `file: "qa-reports/{client}-{date}.html"`, `score`, `modes_done`

**Write pattern:** load existing → remove matching `(client_slug, date)` entry → append new → sort descending by date → write back. No atomic rename; no concurrent writes expected.

---

## Layer 6 — git Commit → GitHub Pages

**Trigger:** `tests/e2e/global-teardown.ts` (after Playwright) or `tools/run-live.sh`

```bash
git add public/
git commit -m "chore: publish playwright results {date}"
git push || (git pull --rebase && git push)
```

In CI: `global-teardown.ts` skips the git step (handled by the CI workflow instead).

GitHub Pages serves the `public/` directory directly from `main` branch. No build step, no Jekyll.

**What gets committed:**
- `public/history/{date}.json` and `public/history/index.json`
- `public/reports/{slug}/` (full Playwright HTML report tree)
- `public/data/*.png` (failure screenshots)
- `public/app-reports/{client}-{date}.html` (Maestro reports — committed manually or after run-maestro.sh)
- `public/qa-reports/{client}-{date}.html` (Cowork reports — committed by Claude/tester)
- `public/manifest.json`

**What is NOT committed (gitignored):**
- `public/live.json` and `public/live.json.tmp` — pushed directly via GitHub Contents API during the run
- `public/reports/data/*.webm`, `*.zip` — large video/trace artifacts
- `public/reports/trace/` — Playwright traces

---

## grouped-report.html

**File:** `public/grouped-report.html`

Static HTML grouping all tests by tag category (crítico, funcional, configuración, regresión). Generated by:

- `tests/e2e/reporters/grouped-report.ts` — Playwright Reporter that groups tests by `@tag` annotations during a run
- `tools/report/generate-grouped-report.py` — standalone generator that parses spec files without running them

Referenced in `/run-playwright` command docs as the expected HTML summary output. Not wired into `global-teardown.ts` — must be regenerated manually or configured as an additional reporter.

---

## /report-qa Command Flow

Defined in `ai-specs/.commands/report-qa.md`. Claude Code adopts QA Coordinator role and:

1. Reads `QA/{CLIENT}/{DATE}/cowork-session.md` (all mode HANDOFFs for the day)
2. Reads `public/grouped-report.html` or `QA/{CLIENT}/{DATE}/` for Playwright results
3. Extracts: flows completed, issues found, staging blockers, coverage from HANDOFF fields
4. Cross-references with Linear tickets
5. Writes two files simultaneously:
   - `QA/{CLIENT}/{DATE}/qa-report-{DATE}.md` — markdown for GitHub/local reading
   - `public/qa-reports/{CLIENT}-{DATE}.html` — standalone HTML for dashboard
6. Updates `public/manifest.json` with new entry

---

## Gaps: What Is NOT Connected

| Gap | Detail |
|-----|--------|
| Cowork not in live view | `live.json` is Playwright-only. Cowork sessions have no real-time dashboard status |
| Maestro not in history/ | Maestro results populate `manifest.json` and `app-reports/` only — NOT `history/{date}.json`. The B2B history tab never shows Maestro pass/fail counts |
| Cowork not in history/ | Cowork HTML reports update `manifest.json` but never update `history/{date}.json` totals |
| No unified health score | Each pipeline has its own metric: Playwright pass rate, Maestro health %, Cowork verdict score — no single combined number |
| grouped-report not auto-updated | Not wired into `global-teardown.ts`; requires manual invocation |
| staging-full-report not auto-updated | `public/staging-full-report.html` is not regenerated by the main pipeline |
| Cowork session unstructured | `cowork-session.md` is free-form markdown; no parser extracts structured data into JSON for the dashboard |
| manifest.json not committed automatically | After Maestro or `/report-qa`, the tester must manually `git add public/ && git commit && git push` to publish to GitHub Pages |

---

*Pipeline architecture analysis: 2026-04-19*

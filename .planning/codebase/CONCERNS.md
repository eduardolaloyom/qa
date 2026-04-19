# Codebase Concerns — QA Reporting Pipeline

**Analysis Date:** 2026-04-19

---

## 1. Pipeline Gaps

### Cowork results are not in the live dashboard — they live in a separate silo

**Issue:** The live dashboard (`public/index.html`) renders two separate data streams: Playwright results (from `public/history/{date}.json` via `public/history/index.json`) and Cowork reports (from `public/manifest.json`). These are never merged into a unified "QA status per client" view.

- Playwright tab shows pass/fail counts per client, updated automatically after each run.
- The "Reportes QA Cowork" card reads `public/manifest.json` and renders cards per client-date.
- There is no view that joins both: you cannot see "Bastien — Playwright 82% + Cowork CON_CONDICIONES + App BLOQUEADO" in a single row.

**Files:** `public/index.html` lines 1311-1317, 2261-2307; `public/manifest.json`

**Impact:** To get a full QA picture for a client you must check the Playwright tab, then scroll to the Cowork card, then check the APP tab. There is no single "is this client QA-ready?" answer.

**Fix approach:** Add a "QA Status" summary section at the top of the dashboard that, for each client, aggregates `clients[slug]` from history JSON (Playwright score), `manifest.json` (Cowork verdict + score), and `app-reports/manifest.json` (Maestro health). One row per client, three status badges.

---

### Two separate manifests for Cowork and Maestro are never merged

**Issue:** `run-maestro.sh` writes to `public/app-reports/manifest.json`. `/report-qa` (per `report-qa.md` line 59-65) writes to `public/manifest.json`. The dashboard's APP tab reads `manifest.json?v=...` (line 2323 of `index.html`), which is the same file as the B2B tab — but `run-maestro.sh` writes to `app-reports/manifest.json`, not `manifest.json`.

**Files:** `tools/run-maestro.sh` lines 53-55 (`MANIFEST_FILE="$PUBLIC_DIR/manifest.json"` where `PUBLIC_DIR=public/app-reports`); `public/index.html` line 2323; `public/app-reports/manifest.json`

**Impact:** APP reports from `run-maestro.sh` go to `public/app-reports/manifest.json`. The dashboard reads `public/manifest.json`. The APP tab is currently populated by `run-maestro.sh` reports only if they were produced by `/report-qa` (which writes to `public/manifest.json`). Maestro HTML reports in `public/app-reports/` (e.g., `bastien-2026-04-15.html`) exist but their manifest is never read by the dashboard.

**Fix approach:** Either (a) unify both manifests into `public/manifest.json` and update `run-maestro.sh` to write there, or (b) make the dashboard read both files and merge client data.

---

### No automatic trigger from `/run-playwright` to `publish-results.py` in docs

**Issue:** `publish-results.py` IS automatically invoked — it runs in `global-teardown.ts` (line 19: `execSync('python3 tools/publish-results.py', ...)`), which Playwright calls after every test run. However, the command documentation in `ai-specs/.commands/run-playwright.md` does not mention this. Step 5 ("Generate report") says to create a file in `QA/{CLIENT}/{DATE}/playwright-report.html` — but the actual automated output goes to `public/history/`. The command doc is misleading.

**Files:** `tests/e2e/global-teardown.ts` lines 18-22; `ai-specs/.commands/run-playwright.md` lines 38-50

**Impact:** Users reading the docs believe they need to manually run `publish-results.py`. They also believe reports go to `QA/{CLIENT}/{DATE}/` (the doc says "Create `QA/{CLIENT}/{DATE}/playwright-report.html`"), but the real output is in `public/history/{date}.json` and `public/reports/`.

**Fix approach:** Update `run-playwright.md` step 5 to reflect real behavior: Playwright automatically publishes via `global-teardown.ts` → `publish-results.py`. Remove the stale `QA/{CLIENT}/{DATE}/playwright-report.html` claim.

---

### Admin tests are permanently skipped and invisible in the dashboard

**Issue:** All 4 admin specs (`tests/e2e/admin/login.spec.ts`, `orders.spec.ts`, `reports.spec.ts`, `stores.spec.ts`, total 321 lines) require `ADMIN_PASSWORD` in `.env`. Per `PENDING.md` lines 20-26, this variable is empty in the active `.env`. Tests auto-skip. `publish-results.py` has no code to handle admin specs separately — they either appear as skipped in the general count or are invisible. The dashboard has no admin section.

**Files:** `tests/e2e/admin/` (4 specs); `PENDING.md` lines 19-26; `tests/e2e/.env.example` line 33; `public/index.html` (no admin section)

**Impact:** 321 lines of admin test code produce zero QA value. Admin panel regressions go undetected.

**Fix approach:** Add `ADMIN_PASSWORD` to `.env` (per PENDING.md). Add an admin results card to the dashboard that reads from the `admin` project suites in the history JSON.

---

### No smoke test for production — staging pass does not imply production pass

**Issue:** `publish-results.py` determines environment from the URL in `qa-matrix-staging.json` (line 535: `"staging" if "solopide.me" in url else "production"`). All day-to-day tests run against staging (`*.solopide.me`). There is no automated validation that passes on production (`youorder.me`) after deploy. Per `PENDING.md` lines 28-38, a production smoke test is planned but does not exist.

**Files:** `tools/publish-results.py` lines 487-535; `PENDING.md` lines 28-38

**Impact:** A client can be marked "QA LISTO" in staging, deploy to production, and have a different MongoDB config (e.g., different banner, price list) that is never validated.

---

## 2. Reliability Concerns

### live.json is stale and shows misleading data between runs

**Issue:** `public/live.json` currently shows `running: false, total: 2932, passed: 0, failed: 0`. The `total: 2932` is the count of all tests discovered at suite start (line 30 in `live-reporter.js`: `this.state.total = suite.allTests().length`), but `passed` and `failed` are 0 because the run from 2026-04-17 21:35 UTC finished in 0.4 seconds (start/end diff) — likely a dry run or error. Between test runs, the dashboard live panel shows this stale state.

**Files:** `public/live.json`; `tools/live-reporter.js` lines 29-31, 55-60

**Impact:** Dashboard always shows a "finished run" state with suspicious totals. Users cannot distinguish "no tests have run today" from "tests ran and passed". `total: 2932` with `passed: 0` looks like a failure.

**Fix approach:** Reset `live.json` to a "no active run" sentinel value (`running: false, total: 0`) after a configurable idle period, or add a `lastRunDate` field the dashboard can compare to today's date to hide stale data.

---

### GitHub API failure in live-reporter.js silently drops all pushes

**Issue:** `live-reporter.js` pushes to GitHub API to update `public/live.json` in the remote repo. The error handler at lines 115, 147 only sets `this._pushPending = false` — there is no retry, no alerting, and no fallback. If the GitHub API is unavailable (rate limit, network issue, bad token), live updates silently stop.

**Files:** `tools/live-reporter.js` lines 86-151

**Impact:** Live dashboard stops updating mid-run with no indication. The `GITHUB_TOKEN` requirement is undocumented in `.env.example` — if token is missing or expired, `_pushToGitHub` returns silently at line 75 (`if (!token) return`). No warning shown.

**Fix approach:** Log a warning to stderr when `GITHUB_TOKEN` is missing. Add exponential backoff with a maximum of 3 retries on API errors. Document `GITHUB_TOKEN` in `tests/e2e/.env.example`.

---

### live-reporter.js has a hardcoded private GitHub repo reference

**Issue:** Line 8 of `tools/live-reporter.js`: `const GITHUB_REPO = 'eduardolaloyom/qa';`. This is hardcoded — if the repo is renamed or transferred, live updates silently stop. No config file or env var controls this.

**Files:** `tools/live-reporter.js` line 8

**Impact:** Breaking change on repo rename. Also exposes the repo slug in committed source.

**Fix approach:** Replace with `process.env.GITHUB_REPO || 'eduardolaloyom/qa'` and document the var in `.env.example`.

---

### publish-results.py called without --client in teardown — client auto-detect may fail

**Issue:** `global-teardown.ts` line 19 calls `python3 tools/publish-results.py` with no arguments. `publish-results.py` lines 823-839 attempt to auto-detect client slug from suite titles. If tests ran across multiple clients (the common case for the full B2B suite), `unique_slugs` will have >1 entry and auto-detection returns None, falling back to the shared `public/reports/` directory instead of per-client report paths.

**Files:** `tests/e2e/global-teardown.ts` line 19; `tools/publish-results.py` lines 820-851

**Impact:** Multi-client runs always write to `public/reports/index.html` (shared), not `public/reports/{slug}/index.html` (per-client). The `reportUrl` in history JSON points to `reports/index.html` for all clients, which is the generic shared report, not the client-specific one.

**Fix approach:** The global teardown should accept a `--client` param when running single-client. For multi-client runs, consider running `publish-results.py --client {slug}` once per client using the per-client results files mentioned in the docstring (lines 762-771 of `publish-results.py`).

---

### Git commit in teardown can fail silently — dashboard may not update on GitHub Pages

**Issue:** `global-teardown.ts` lines 27-34 run `git add public/ && git commit && git push` in a shell command. The outer `try/catch` at line 35 only logs `⚠️ git push falló` to console — the test run still exits 0. If push fails (merge conflict, auth error, network), the dashboard is not updated on GitHub Pages but the local run shows success.

**Files:** `tests/e2e/global-teardown.ts` lines 24-36

**Impact:** Silent dashboard staleness. Playwright run "succeeds" locally but results never reach the public dashboard.

**Fix approach:** Exit non-zero if push fails (or at minimum emit a clear warning block that includes "Dashboard NOT updated"). Add a post-push check that verifies the remote `public/history/index.json` SHA matches local.

---

### Maestro flakiness handled by manual-pass — not tracked in reports as flaky

**Issue:** `run-maestro.sh` supports 3 auto-retries for individual flows and 1 attempt for session flows. When all retries fail, interactive mode prompts `[m] Manual-Pass`. A manual-pass is logged as `[Manual-Pass] {flow_name}` and counted identically to auto-pass when computing health score (line 318: `(passed + manual) / effective`). The dashboard HTML report shows a "👤 MANUAL-PASS" badge, but `manifest.json` does not distinguish manual from auto — both contribute to `health`. Persistent flakiness is invisible at the manifest level.

**Files:** `tools/run-maestro.sh` lines 218-266, 312-318; `public/app-reports/manifest.json` (no `manual_pass_count` field in read entries)

**Impact:** A Maestro run with 8/10 auto-pass + 2/10 manual-pass reports `health: 100%` — identical to a fully automated pass. Trend analysis cannot distinguish genuine stability from human intervention masking failures.

**Fix approach:** Add `manual_pass_count` as a distinct field in the manifest entry (it's present in the HTML but not committed to the manifest's top-level stats). Surface it in the dashboard APP card as a separate badge.

---

## 3. Reporting Completeness

### Manual checklist results are not in the dashboard — only in local markdown files

**Issue:** `tools/checklist-generator.py` produces `QA/{CLIENT}/{DATE}/checklist.md`. These are never parsed and published. The dashboard has no section for manual checklist results. The "Cowork Reports" card in the dashboard (`public/index.html` lines 1311-1317) shows `/report-qa` HTML output, which includes a checklist summary from reading `cowork-session.md` — but only if `/report-qa` was run and the HTML was placed in `public/qa-reports/`.

**Files:** `tools/checklist-generator.py`; `tools/run-qa.sh` line 36; `public/index.html` lines 1311-1317

**Impact:** Manual checklist execution results (regression, post-mortems, ERP integrations) are invisible in the dashboard unless a full Cowork session + `/report-qa` is completed. Ad-hoc checklist runs have no visibility.

**Fix approach:** Add a lightweight "Checklist Status" panel to the dashboard that reads from a committed `public/checklists/{CLIENT}-{DATE}.json` — generated by `checklist-generator.py` if an `--output-json` flag is added.

---

### Manual QA notes in APP tab are localStorage-only — not committed or visible across machines

**Issue:** The APP tab has an inline "Manual QA" system (lines 2496-2596 of `index.html`). Notes are stored in `localStorage` with key `yom-manual-qa-entries`. The "Export" button generates a JSON file, but there is no import or commit flow. Notes are device-specific and invisible to other team members.

**Files:** `public/index.html` lines 2496-2596; `MQ_KEY = 'yom-manual-qa-entries'`

**Impact:** QA findings added via the dashboard UI are lost on page reload in a different browser or another device. No team-visible record of manual QA observations.

**Fix approach:** Add an export-then-commit flow: "Export + Save to repo" that writes to `public/data/manual-notes-{CLIENT}.json` and triggers a git commit via the existing teardown pattern. Or use GitHub API directly (the `GITHUB_TOKEN` is already available for live-reporter).

---

### Staging vs production distinction exists in data but not enforced in UI

**Issue:** `publish-results.py` line 535 sets `environment: "staging"` or `"production"` based on URL. The dashboard has an environment landing screen (lines 722-796 of `index.html`) that filters by `selectedEnv`. But the history JSON `clients[slug].environment` is always `"staging"` because `load_staging_urls()` only reads `qa-matrix-staging.json` — there is no production matrix equivalent loaded. So selecting "Producción" in the dashboard shows zero B2B Playwright results.

**Files:** `tools/publish-results.py` lines 487-503 (`load_staging_urls` reads only staging matrix); `public/index.html` lines 1376-1416 (env filter logic)

**Impact:** The production/staging split in the dashboard is cosmetic — production view is always empty for Playwright. The environment filter only meaningfully affects Cowork reports (which have an explicit `environment` field in `manifest.json`).

**Fix approach:** Either remove the environment landing for Playwright (B2B is always staging) and reserve it for Cowork reports, or implement a production matrix extraction and publication path.

---

## 4. Process Clarity Gaps

### When to run /report-qa vs just viewing HTML is ambiguous

**Issue:** `CLAUDE.md` says "Para debugging rápido, leer el HTML de Playwright directamente" and "generar reporte solo cuando hay una sesión Cowork completa o al cierre de una semana QA." `/report-qa` generates two outputs: `QA/{CLIENT}/{DATE}/qa-report-{DATE}.md` and `public/qa-reports/{CLIENT}-{DATE}.html`. But `run-playwright.md` says to create `QA/{CLIENT}/{DATE}/playwright-report.html` (a file that does not exist in the real pipeline). The actual Playwright HTML is at `tests/e2e/playwright-report/index.html` and published to `public/reports/`.

**Files:** `CLAUDE.md` lines in "Cuándo reportar vs solo ver resultados"; `ai-specs/.commands/run-playwright.md` line 39; `tests/e2e/global-teardown.ts` line 19

**Impact:** Claude instances (and human users) are confused about where Playwright results are after a run. The command doc points to a non-existent path. The real path (`public/reports/index.html`) is only documented in `publish-results.py` internals.

**Fix approach:** Update `run-playwright.md` step 5 and `CLAUDE.md` to state: "After each test run, results are auto-published to `public/history/{date}.json` and `public/reports/` via `global-teardown.ts`. View via `public/index.html` or directly at `public/reports/index.html`."

---

### No definition of "QA done for the week" — no dashboard completion indicator

**Issue:** No document defines what makes a client's QA complete for a week. There is no "Done" flag in `history/{date}.json` or `manifest.json`. The dashboard shows individual run results but no aggregate weekly completion status. A client could have Playwright passing, Cowork not run, and Maestro blocked — and the dashboard shows three separate data points with no rollup verdict.

**Files:** `public/manifest.json` (per-run verdict only); `public/history/{date}.json` (per-run stats); `public/index.html` (no weekly summary)

**Impact:** The QA team cannot tell from the dashboard alone whether this week's QA is complete for each client. This is assessed manually by cross-referencing Playwright stats, Cowork manifest cards, and Maestro health — a mental aggregation step.

**Fix approach:** Define a weekly QA completion criteria document (e.g., Playwright ≥ 80% + Cowork verdict not null + Maestro health ≥ 70% or N/A). Write a script that evaluates these criteria per client from the three data sources and updates a `public/weekly-status.json`. Add a "Weekly Status" card to `index.html` that reads it.

---

### /triage-playwright triggers after run but no triage output appears in dashboard

**Issue:** `global-teardown.ts` lines 39-52 print a triage hint to the console when failures exist: `"corre /triage-playwright para analizar"`. But `/triage-playwright` is a Claude command (prompt-based), not a script — its output is a chat response, not a committed file. There is no mechanism to surface triage analysis in the dashboard.

**Files:** `tests/e2e/global-teardown.ts` lines 39-52; `ai-specs/.commands/triage-playwright.md`

**Impact:** Triage insights live only in Claude chat sessions. After a failed run, the failure classification in the dashboard (bug/ambiente/ux) comes from `publish-results.py`'s `classify_error()` — which is good — but the actionable triage from `/triage-playwright` is never committed. Future Claude instances and team members cannot see why a failure was triaged as "won't fix" vs "open bug".

**Fix approach:** Add a `QA/{CLIENT}/{DATE}/triage-{date}.md` output convention for `/triage-playwright`. Teach `publish-results.py` to read an optional triage file for each run date and embed its conclusions in the history JSON.

---

## 5. Dashboard UX Gaps

### B2B client cards show seeded data from previous days without date staleness indicator

**Issue:** `publish-results.py` lines 879-887 seed today's run with clients from previous days so they "stay visible in the dashboard." As of the 2026-04-17 run, 3 of 40 clients (Bastien, Codelpa, Surtiventas) have `last_tested: 2026-04-15` or `2026-04-16`. The dashboard shows their pass rates without visually distinguishing them from clients tested today.

**Files:** `tools/publish-results.py` lines 673-695 (`load_previous_clients`), 879-887; `public/history/2026-04-17.json`

**Impact:** A stale client's 2026-04-15 results appear alongside fresh 2026-04-17 results with no visual difference. Users cannot tell which clients were actually tested in this run.

**Fix approach:** In the client card rendering in `index.html`, display `last_tested` date and apply a visual indicator (e.g., amber color, "Stale" badge) when `last_tested` is more than 2 days older than the selected run date.

---

### Dashboard "Tendencia Histórica" chart ignores per-client trends

**Issue:** The trend chart (line 1320-1336 of `index.html`) shows aggregate pass/fail counts across all clients. There is no way to select a single client and see its pass-rate trend over time. The history JSON has per-client data across all run files — the chart just does not use it.

**Files:** `public/index.html` lines 1319-1336; `public/history/` (contains per-client breakdown in each date JSON)

**Impact:** Cannot tell if a client's quality is improving or degrading over time. Aggregate trend hides individual regressions.

**Fix approach:** Add a client selector to the trend chart section that filters `public/history/*.json` files for the chosen client slug and renders its individual pass-rate over time.

---

### Cowork report cards show verdict and score but no Playwright pass rate alongside

**Issue:** The "Reportes QA Cowork" card (lines 2277-2303 of `index.html`) renders verdict, score, and modes-done from `manifest.json`. It does not look up the corresponding Playwright stats from `history/{date}.json`. A card saying "CON_CONDICIONES 87/100" gives no indication of whether Playwright was also run on that date.

**Files:** `public/index.html` lines 2277-2303; `public/manifest.json`; `public/history/{date}.json`

**Impact:** Cowork report cards are not actionable without opening the linked HTML report to see Playwright results. The dashboard fails to provide a unified answer.

**Fix approach:** In `loadCoworkReports()`, for each report, cross-reference `history/{rep.date}.json` and display the client's Playwright pass rate as a secondary badge on the Cowork card.

---

*Concerns audit: 2026-04-19*

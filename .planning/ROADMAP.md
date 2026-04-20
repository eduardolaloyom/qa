# Roadmap: QA Pipeline & Dashboard v2

**Created:** 2026-04-19
**Granularity:** standard
**Mode:** yolo
**Model profile:** quality
**Coverage:** 18/18 v1 requirements mapped

## Core Value

El equipo puede ver en un solo lugar si un cliente está QA-listo para deploy, con datos frescos de las tres herramientas.

## Strategy

Brownfield improvements to an existing, functioning QA pipeline. Phases are ordered by dependency and by value-to-risk ratio: fix pipeline bugs first (they block accuracy), then add freshness signals, then deliver the core unified view, then improve process (triage persistence, QA LISTO), and finally harden reports + Claude agent specs.

Each phase produces a visible, testable outcome. No phase leaves the dashboard in a broken state — all changes are additive (new JSON files, new dashboard sections, new agent instructions).

## Phases

- [x] **Phase 1: Pipeline Bug Fixes** — Fix manifest path and stale live.json so downstream dashboard data is trustworthy
- [x] **Phase 2: Data Freshness Signals** — Make stale client cards visually obvious so users trust (or distrust) what they see
- [ ] **Phase 3: Unified QA Status View** — Deliver the core value — one row per client showing all three pipelines + per-client trend
- [ ] **Phase 4: Triage Persistence** — Capture triage decisions as committed files so history is auditable
- [ ] **Phase 5: QA LISTO Weekly Status** — Give Tech a deploy-readiness signal driven by objective criteria
- [ ] **Phase 6: Actionable Reports & Agent Precision** — Make HTML reports useful to stakeholders and make Claude agents consistent in triage/classification

## Phase Details

### Phase 1: Pipeline Bug Fixes
**Goal**: Pipeline publishes results to the places the dashboard actually reads, and live state is never misleading between runs
**Depends on**: Nothing (first phase)
**Requirements**: PIPE-01, PIPE-02
**Success Criteria** (what must be TRUE):
  1. After `tools/run-maestro.sh {client}` finishes, the new Maestro report is listed in `public/manifest.json` (single source of truth) and the APP tab on the dashboard shows it immediately
  2. Between Playwright runs, `public/live.json` is either absent or shows a clean "no active run" sentinel (`running: false, total: 0`) — never carries over stale counts like `total: 2932, passed: 0`
  3. Dashboard live panel does not render a misleading "finished run" state when no run is in progress
  4. No existing Playwright, Cowork, or Maestro flow is broken by the fix (backward-compatible manifest read paths)
**Plans:** 2 plans
- [x] 01-01-PLAN.md — PIPE-01: run-maestro.sh writes unified manifest to public/manifest.json
- [x] 01-02-PLAN.md — PIPE-02: live-reporter.js onBegin full-state reset + run-live.sh pre-run sentinel

### Phase 2: Data Freshness Signals
**Goal**: Users can tell at a glance whether a client card reflects today's run or data seeded from previous days
**Depends on**: Phase 1
**Requirements**: DASH-01, DASH-02
**Success Criteria** (what must be TRUE):
  1. Every client card in the B2B tab shows the `last_tested` date explicitly (always visible, not on hover)
  2. When `last_tested` is more than 2 days older than the selected run date, the card shows an amber badge with text "Hace N días"
  3. Client cards tested today (or within the 2-day window) render with the normal color scheme — no false positives
  4. Changing the selected run date via the dashboard history navigation re-evaluates freshness against the new reference date
**Plans:** 2 plans
- [x] 02-01-PLAN.md — CSS foundations (`.client-last-tested`, `.freshness-badge`, `.run-nav`) + run-nav skeleton HTML before `#clientsContainer`
- [x] 02-02-PLAN.md — Refactor `updateClients(run = latestRun)` with class-based freshness rendering + `populateRunSelector()` + change-listener wiring
**UI hint**: yes

### Phase 3: Unified QA Status View
**Goal**: One scrollable section answers "is this client QA-ready?" by combining Playwright, Cowork, and Maestro in a single row per client, plus a per-client historical trend
**Depends on**: Phase 1, Phase 2
**Requirements**: DASH-03, DASH-04, DASH-05
**Success Criteria** (what must be TRUE):
  1. A new "Estado QA por Cliente" section appears in the dashboard with one row per client showing three badges: Playwright pass%, Cowork veredicto, Maestro health (or explicit "N/A" when a pipeline does not apply to that client)
  2. Each of the three badges in the unified row shows a stale indicator when its source data is more than 2 days older than the selected run date
  3. The "Tendencia Histórica" chart has a client selector; choosing a client filters `public/history/*.json` to plot that client's pass rate over time
  4. Selecting "All clients" (or leaving the filter empty) preserves the existing aggregate trend behavior — no regression for current users
  5. Existing B2B tab, APP tab, and Cowork reports card continue to render unchanged (unified view is additive)
**Plans:** 3 plans
- [ ] 03-01-PLAN.md — CSS foundations + HTML skeleton (unified table, filter pills, trend header wrap)
- [ ] 03-02-PLAN.md — updateUnifiedQaTable + 3 badge renderers + filter pills wiring + #runSelector integration (DASH-03, DASH-04)
- [ ] 03-03-PLAN.md — populateTrendClientSelector + updateTrendChart(filterSlug) + Chart.getChart destroy + lazy-load allRunsDetailed (DASH-05)
**UI hint**: yes

### Phase 4: Triage Persistence
**Goal**: Triage decisions made by `/triage-playwright` are captured as committed files and surfaced in the history JSON instead of disappearing into chat
**Depends on**: Phase 1
**Requirements**: PROC-01, PROC-02
**Success Criteria** (what must be TRUE):
  1. Running `/triage-playwright` produces `QA/{CLIENT}/{DATE}/triage-{date}.md` with one entry per failure classifying it as `bug`, `flaky`, or `ambiente` and recording the rationale
  2. `tools/publish-results.py` detects `QA/{CLIENT}/{DATE}/triage-{date}.md` when present and incorporates triage decisions into `public/history/{date}.json` (e.g., as a `triage` field per failure or per client)
  3. If no triage file exists, `publish-results.py` continues to work exactly as before — no failure, no regression
  4. A user inspecting `public/history/{date}.json` for a past date can see which failures were triaged and how, without opening chat history
**Plans**: TBD

### Phase 5: QA LISTO Weekly Status
**Goal**: Tech has an objective, dashboard-visible signal of whether each client is ready to deploy, derived from the three pipelines
**Depends on**: Phase 3, Phase 4
**Requirements**: PROC-03, PROC-04
**Success Criteria** (what must be TRUE):
  1. A script/command evaluates QA LISTO criteria per client (Playwright ≥ N% + Cowork veredicto not null + Maestro health ≥ N% or N/A) and writes `public/weekly-status.json`
  2. The dashboard renders an "Estado Semanal" card (or section) per client that reads `public/weekly-status.json` and labels each client as LISTO, PENDIENTE, or BLOQUEADO
  3. The thresholds used for classification are documented (in the script and/or in `ai-specs/`) so the team can adjust them without reverse-engineering the code
  4. Re-running the script with updated source data (new Playwright run, new Cowork report) changes the card state without manual dashboard edits
**Plans**: TBD
**UI hint**: yes

### Phase 6: Actionable Reports & Agent Precision
**Goal**: HTML reports are useful to non-QA stakeholders in the first 3 lines, and Claude agents apply consistent criteria for classifying failures, retrying tests, and handling Maestro manual-pass
**Depends on**: Phase 4
**Requirements**: PROC-05, PROC-06, AGENT-01, AGENT-02, AGENT-03, AGENT-04, AGENT-05
**Success Criteria** (what must be TRUE):
  1. The `/report-qa` template produces HTML reports whose first 3 lines always show veredicto + score + número de issues críticos — readable by a Tech Lead or PM without scrolling
  2. Every issue in the "Accionables" section of a generated report has an explicit owner (Tech / QA / PM) and a plazo
  3. `ai-specs/.agents/playwright-specialist.md` defines explicit, testable criteria for classifying a failure as `flaky` (<30% failure rate), `ambiente` (staging/network timeout), or `bug` (reproducible, deterministic), and defines when to retry vs escalate
  4. `/triage-playwright` command documentation includes the timeout classification rubric (<5s = selector issue, 5-30s = red/staging, >30s = bug or infinite loop) and uses it during triage
  5. `ai-specs/.agents/maestro-specialist.md` defines the protocol for a flow that fails its 3 auto-retries, and manual-pass decisions are recorded with their reason in the run log (not only as an HTML badge)
**Plans**: TBD

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Pipeline Bug Fixes | 2/2 | Complete ✓ | 2026-04-19 |
| 2. Data Freshness Signals | 2/2 | Complete ✓ | 2026-04-19 |
| 3. Unified QA Status View | 0/3 | In progress | - |
| 4. Triage Persistence | 0/? | Not started | - |
| 5. QA LISTO Weekly Status | 0/? | Not started | - |
| 6. Actionable Reports & Agent Precision | 0/? | Not started | - |

## Coverage Validation

| Requirement | Phase |
|-------------|-------|
| PIPE-01 | Phase 1 |
| PIPE-02 | Phase 1 |
| DASH-01 | Phase 2 |
| DASH-02 | Phase 2 |
| DASH-03 | Phase 3 |
| DASH-04 | Phase 3 |
| DASH-05 | Phase 3 |
| PROC-01 | Phase 4 |
| PROC-02 | Phase 4 |
| PROC-03 | Phase 5 |
| PROC-04 | Phase 5 |
| PROC-05 | Phase 6 |
| PROC-06 | Phase 6 |
| AGENT-01 | Phase 6 |
| AGENT-02 | Phase 6 |
| AGENT-03 | Phase 6 |
| AGENT-04 | Phase 6 |
| AGENT-05 | Phase 6 |

**v1 total:** 18
**Mapped:** 18
**Orphans:** 0

---
*Roadmap created: 2026-04-19*

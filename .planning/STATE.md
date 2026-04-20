---
gsd_state_version: 1.0
milestone: v2.0
milestone_name: QA Pipeline & Dashboard v2
status: active
stopped_at: Phase 4 complete — awaiting Phase 5 planning
last_updated: "2026-04-21"
last_activity: 2026-04-21 — Phase 4 (Triage Persistence) executed — 2/2 plans complete in 1 wave
progress:
  total_phases: 6
  completed_phases: 4
  total_plans: 9
  completed_plans: 9
  percent: 67
---

# STATE — QA Pipeline & Dashboard v2

## Project Reference

**Project:** QA Pipeline & Dashboard v2
**Core Value:** El equipo puede ver en un solo lugar si un cliente está QA-listo para deploy, con datos frescos de las tres herramientas.
**Mode:** yolo
**Granularity:** standard
**Model profile:** quality

## Current Position

**Phase:** Phase 5 — QA LISTO Weekly Status (not started)
**Plan:** None yet
**Status:** Phase 4 complete — PROC-01 and PROC-02 closed. Next: /gsd-plan-phase 5
**Progress:** 4/6 phases complete

```
[█████████████░░░░░░░] 67%
Phase 1 ✓ ──▶ Phase 2 ✓ ──▶ Phase 3 ✓ ──▶ Phase 4 ✓ ──▶ Phase 5 ──▶ Phase 6
```

## Active Requirements (v1)

**Total:** 18 requirements across 6 phases
**Mapped:** 18/18
**Completed:** 2 (PIPE-01, PIPE-02)

## Performance Metrics

| Metric | Value |
|--------|-------|
| Phases defined | 6 |
| Phases complete | 1 |
| Plans executed | 2 |
| Requirements closed | 2/18 |

## Accumulated Context

### Key Decisions

- **Unified manifest in `public/manifest.json`:** `run-maestro.sh` now writes to the single manifest the dashboard reads. Simplest fix; avoids teaching the dashboard two sources.
- **Unified view as additive section:** New "Estado QA por Cliente" section sits alongside existing B2B and APP tabs. No replacement, no regression for current workflows.
- **Triage as committed markdown:** `QA/{CLIENT}/{DATE}/triage-{date}.md` mirrors the existing `cowork-session.md` pattern — easy to find, easy to commit.
- **Vanilla JS only:** Dashboard stays a single static HTML file. No bundler, no framework.
- **live.json sentinel via EXIT trap:** `run-live.sh` uses a pre-run heredoc to reset sentinel AND the existing EXIT trap handles cleanup. Full reset in `onBegin()` covers any case where sentinel is absent.

### Phase 1 — Completed Changes

- `tools/run-maestro.sh`: `MANIFEST_FILE` now points to `$QA_ROOT/public/manifest.json`; Python section adds `"platform": "app"` and prefixes file path with `app-reports/`
- `tools/verify-maestro-manifest.sh`: New smoke test for PIPE-01
- `public/app-reports/manifest.json`: Deleted (orphaned duplicate)
- `tools/live-reporter.js`: `onBegin()` does full state replacement — resets `passed`, `failed`, `skipped`, `currentTest`, `recentTests`
- `tools/run-live.sh`: Pre-run heredoc writes sentinel (`running: false, total: 0`) before Playwright starts

### Open Todos

- Begin Phase 2 planning (`/gsd-plan-phase 2`)

### Blockers

- None

### Risks / Watch List

- Dashboard is ~2600 lines of vanilla JS in a single file — large changes risk regressions. Each phase must keep existing tabs/cards working.
- `publish-results.py` has complex merge logic (`merge_run_json`, `load_previous_clients`). Triage file integration in Phase 4 must not disturb that logic.
- `live.json` is pushed via GitHub Contents API, not git — Phase 1 reset behavior must play nicely with the live-reporter push cadence.

## Session Continuity

**Last session:** 2026-04-20 — Phase 3 executed (DASH-03/04/05), client cleanup applied (17 active via ACTIVE_CLIENTS allowlist in sync-clients.py), Phase 4 discuss-phase complete. End-of-day pause.
**Next session:** Run `/gsd-plan-phase 4` to generate research + plans for Phase 4 (Triage Persistence). CONTEXT.md already captured 17 decisions (YAML frontmatter format, per-client file, overlay strategy, commit+push immediate).
**Resume file:** `.planning/phases/04-triage-persistence/04-CONTEXT.md`

**Files for orientation:**
- `.planning/PROJECT.md` — core value, constraints, key decisions
- `.planning/REQUIREMENTS.md` — all 18 v1 requirements + traceability table
- `.planning/ROADMAP.md` — 6 phases with success criteria
- `.planning/codebase/ARCHITECTURE.md` — pipeline layers (Playwright, Maestro, Cowork)
- `.planning/codebase/CONCERNS.md` — known gaps and concerns driving this project

---
*State initialized: 2026-04-19*
*Phase 1 completed: 2026-04-19*

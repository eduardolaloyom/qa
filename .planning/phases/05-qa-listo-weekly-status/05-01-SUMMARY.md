---
phase: 05-qa-listo-weekly-status
plan: "01"
subsystem: qa-pipeline
tags: [evaluation-script, deploy-readiness, weekly-status, documentation]
dependency_graph:
  requires:
    - public/manifest.json
    - public/history/20*.json
  provides:
    - tools/evaluate-qa-listo.py
    - public/weekly-status.json
    - ai-specs/specs/qa-listo-criteria.mdc
  affects:
    - public/index.html (consumed by 05-02 dashboard plan)
tech_stack:
  added: []
  patterns:
    - Python 3 stdlib-only script (mirrors publish-results.py pattern)
    - Threshold constants at top of file (D-01, D-02, D-03)
    - Real-run detection via passed+failed>0 (not tests>0)
    - Maestro N/A determined dynamically from manifest (no hardcoded list)
key_files:
  created:
    - tools/evaluate-qa-listo.py
    - public/weekly-status.json
    - ai-specs/specs/qa-listo-criteria.mdc
  modified: []
decisions:
  - "PLAYWRIGHT_MIN_PASS_PCT=80 and MAESTRO_MIN_HEALTH=60 as locked thresholds (D-01, D-02)"
  - "CON_CONDICIONES maps to PENDIENTE not BLOQUEADO (D-05)"
  - "Maestro N/A determined dynamically — no hardcoded client list (D-08)"
  - "LISTO entries have no reason key to avoid empty title= tooltip (plan spec)"
metrics:
  duration: "3m 31s"
  completed_date: "2026-04-20"
  tasks_completed: 2
  tasks_total: 2
  files_created: 3
  files_modified: 0
---

# Phase 05 Plan 01: QA LISTO Evaluation Script Summary

Python 3 script that reads manifest.json (Cowork/Maestro) + history/*.json (Playwright) and writes `public/weekly-status.json` with BLOQUEADO/PENDIENTE/LISTO per client using locked thresholds (PW>=80%, MT>=60%).

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create tools/evaluate-qa-listo.py | f33dd21 | tools/evaluate-qa-listo.py, public/weekly-status.json |
| 2 | Create ai-specs/specs/qa-listo-criteria.mdc | 226b9c3 | ai-specs/specs/qa-listo-criteria.mdc |

## Verification Results

All plan success criteria verified:

- `python3 tools/evaluate-qa-listo.py --dry-run` exits 0 and prints sorted table (BLOQUEADO/PENDIENTE/LISTO)
- `weekly-status.json` contains top-level keys: `generated_at`, `reference_date`, `thresholds`, `clients`
- `thresholds` block has `playwright_min_pass_pct=80` and `maestro_min_health=60`
- `prinorte` classified BLOQUEADO (Maestro score 0 < 60) — confirmed
- Clients with only seeded data (passed+failed=0 in all history files) correctly classified PENDIENTE "Playwright: sin datos recientes"
- `CON_CONDICIONES` Cowork verdict maps to PENDIENTE — confirmed (bastien, sonrie)
- LISTO entries in JSON have NO `reason` key — verified by assertion
- Console output sorts: BLOQUEADO first, PENDIENTE second, LISTO last — confirmed
- `ai-specs/specs/qa-listo-criteria.mdc` documents both thresholds and Maestro N/A rule in plain Spanish

**Live classification results (2026-04-20 data):**

| Client | Status | Reason |
|--------|--------|--------|
| prinorte | BLOQUEADO | Playwright: sin datos recientes; Cowork: sin reporte; Maestro score 0 < 60 |
| bastien | PENDIENTE | Cowork: CON_CONDICIONES |
| codelpa | PENDIENTE | Cowork: sin reporte |
| new-soprole | PENDIENTE | Playwright: sin datos recientes |
| sonrie | PENDIENTE | Cowork: CON_CONDICIONES |
| surtiventas | PENDIENTE | Cowork: sin reporte |

## Deviations from Plan

None — plan executed exactly as written.

The `reason` field for prinorte BLOQUEADO includes all three blocking reasons joined by `;` (PW no data + Cowork no report + Maestro 0 < 60), which is correct behavior per the classification logic — all three sources block prinorte independently.

## Known Stubs

None. `public/weekly-status.json` is fully populated with real data from manifest.json and history/*.json.

## Threat Flags

No new threat surface beyond what was documented in the plan's threat model. The `reason` field contains only plain-text pipeline status descriptions (no credentials, no error stack traces). The `escapeHtml()` mitigation for D-17 (XSS in title attribute) is the responsibility of the 05-02 dashboard plan.

## Self-Check: PASSED

- `tools/evaluate-qa-listo.py` exists and runs
- `public/weekly-status.json` exists and passes all JSON assertions
- `ai-specs/specs/qa-listo-criteria.mdc` exists with thresholds documented
- Commits f33dd21 and 226b9c3 exist in git log

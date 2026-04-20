---
phase: 06-actionable-reports-agent-precision
plan: "03"
subsystem: ai-specs/commands
tags: [triage, playwright, timeout, rubric, agent-precision]
dependency_graph:
  requires: []
  provides: [AGENT-03]
  affects: [triage-playwright.md, playwright-failure-analyst]
tech_stack:
  added: []
  patterns: [markdown-decision-rules]
key_files:
  created: []
  modified:
    - ai-specs/.commands/triage-playwright.md
decisions:
  - "Rubric inserted in BOTH locations: Step 4 ambiente block (operational) and ## Reglas (quick-reference)"
  - "Rubric placed before 'Leer el spec afectado' so classification happens before reading the spec"
  - "Three thresholds: <5s=selector issue, 5-30s=red/staging, >30s=bug or infinite loop (from D-08)"
metrics:
  duration: "5m"
  completed: "2026-04-20"
  tasks_completed: 1
  tasks_total: 1
  files_modified: 1
---

# Phase 6 Plan 03: Timeout Rubric in triage-playwright Summary

Rúbrica `<5s / 5-30s / >30s` integrada en Step 4 bloque `ambiente` y sección `## Reglas` de `triage-playwright.md` — convierte clasificación subjetiva de timeouts en criterio reproducible por duración observable.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Insertar rúbrica de timeout en Step 4 bloque ambiente y en sección Reglas | a3bcd4e | ai-specs/.commands/triage-playwright.md |

## What Was Built

The file `ai-specs/.commands/triage-playwright.md` received two additions:

**Addition 1 — Step 4, bloque `ambiente`** (line 74-77):
A 4-line block immediately after `**Si 'ambiente' (owner: qa):**` and before `- Leer el spec afectado`. When Claude encounters an `ambiente` timeout during triage, it now reads the error duration from Playwright output and classifies:
- `<5s` → selector issue (reclassify as `bug` if reproducible)
- `5-30s` → red/staging (ignore this run, verify staging URL)
- `>30s` → bug or infinite loop (escalate as `bug`)

**Addition 2 — ## Reglas section** (line 240):
First bullet added: `**Rúbrica de timeout por duración**` as a quick-reference summary of the three thresholds.

## Verification Results

```
75:  - `<5s` → **selector issue**: el elemento no existe o cambió ...
76:  - `5-30s` → **red/staging**: staging lento o caído ...
77:  - `>30s` → **bug o infinite loop**: lógica de la app ...
240:- **Rúbrica de timeout por duración**: `<5s` = selector issue, `5-30s` = red/staging ...
```

All 6 original steps intact (verified via grep).

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None.

## Threat Flags

None — modification is to Markdown instruction file only; no new network endpoints, auth paths, or schema changes introduced.

## Self-Check: PASSED

- [x] `grep "selector issue"` returns 2 lines (Step 4 line 75 and Reglas line 240) — FOUND
- [x] `grep "5-30s"` returns classification line — FOUND
- [x] `grep "Rúbrica de timeout"` returns Reglas bullet — FOUND
- [x] `grep "infinite loop"` returns >30s classification — FOUND
- [x] Commit a3bcd4e exists in git log — FOUND
- [x] All 6 Steps intact — VERIFIED

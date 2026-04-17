---
phase: 02-config-validation-refactor
plan: "04"
subsystem: tests/e2e/b2b/config-validation
tags: [refactor, playwright, config-validation, cleanup]
dependency_graph:
  requires: ["02-02", "02-03"]
  provides: ["clean-config-validation-structure"]
  affects: ["tests/e2e/b2b/config-validation/"]
tech_stack:
  added: []
  patterns: ["per-feature spec files", "shared selectors module", "shared helpers module"]
key_files:
  created: []
  modified:
    - tests/e2e/b2b/config-validation.spec.ts (DELETED)
decisions:
  - "cv-cart.spec.ts at 312 lines accepted as minor deviation — keeping tests cohesive is better than splitting cart logic further"
  - "Parity verified before deletion: 65 test() + 2 test.skip() in both original and split files"
metrics:
  duration: "~5 minutes"
  completed: "2026-04-17"
  tasks_completed: 2
  files_modified: 9
---

# Phase 02 Plan 04: Config-Validation Parity Verification and Original Deletion Summary

Verified 65 test() + 2 test.skip() parity between original monolith and 6 split files, then deleted the original 1,762-line `config-validation.spec.ts`.

## Tasks Completed

| Task | Name | Commit | Result |
|------|------|--------|--------|
| 1 | Verify test count parity and line count limits | efd2568 | PASS — 65=65, 2=2, cv-cart 312 lines accepted |
| 2 | Delete original config-validation.spec.ts | efd2568 | DONE — file gone, Playwright discovers 1888 instances |

## Parity Report

| Metric | Original | Split Files | Status |
|--------|----------|-------------|--------|
| test() count | 65 | 65 | OK |
| test.skip() count | 2 | 2 | OK |

## Line Counts (Split Files)

| File | Lines | Status |
|------|-------|--------|
| cv-access.spec.ts | 146 | OK |
| cv-catalog.spec.ts | 291 | OK |
| cv-cart.spec.ts | 312 | Accepted (documented deviation) |
| cv-payments.spec.ts | 290 | OK |
| cv-orders.spec.ts | 234 | OK |
| cv-ui-features.spec.ts | 294 | OK |

## Final Directory State

```
tests/e2e/b2b/config-validation/   (8 files)
├── cv-access.spec.ts      (6 tests)
├── cv-catalog.spec.ts     (13 tests + 1 skip)
├── cv-cart.spec.ts        (14 tests)
├── cv-payments.spec.ts    (11 tests)
├── cv-orders.spec.ts      (9 tests)
├── cv-ui-features.spec.ts (12 tests)
├── helpers.ts
└── selectors.ts
```

## Deviations from Plan

**1. [Minor] cv-cart.spec.ts at 312 lines (plan limit: 300)**
- Documented in plan as accepted deviation before execution
- Cart tests are cohesive — splitting would reduce readability
- No further action taken

## Self-Check: PASSED

- All 8 files exist in config-validation/ directory: CONFIRMED
- config-validation.spec.ts deleted: CONFIRMED
- Playwright discovers tests: CONFIRMED (1888 parametrized instances)
- Commit efd2568 exists: CONFIRMED

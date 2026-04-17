# Roadmap: QA Repo Improvements

## Overview

Targeted improvements to the YOM QA repo: fix reliability gaps found in codebase audit,
reduce test fragility, and improve execution speed. Three focused phases that each ship independently.

## Phases

- [ ] **Phase 1: Playwright Teardown Fix** - Reliable HTTP server cleanup after every test run
- [ ] **Phase 2: Config Validation Refactor** - Split 1,762-line spec into modular per-feature files
- [x] **Phase 3: B2B Parallel Execution** - Enable parallel client test runs (completed 2026-04-17)
- [x] **Phase 4: Live Reporter Race Condition Fix** - Atomic writes to live.json (completed 2026-04-17)

## Phase Details

### Phase 1: Playwright Teardown Fix
**Goal**: HTTP server started by global-setup always terminates after tests end — no port 8080 leaks
**Depends on**: Nothing
**Requirements**: REQ-01, REQ-02
**Plans:** 1 plan
**Success Criteria** (what must be TRUE):
  1. Running `npm test` twice in a row never fails due to "port already in use"
  2. Killing tests mid-run with Ctrl+C leaves no orphaned http-server process
  3. `global-teardown.ts` successfully kills PID from `.http-server.pid` in all exit scenarios
  4. `.http-server.pid` is cleaned up after each run

Plans:
- [ ] 01-01-PLAN.md — Replace PID-file pattern with Playwright webServer config + belt-and-suspenders port cleanup

### Phase 2: Config Validation Refactor
**Goal**: `config-validation.spec.ts` split into ≤300-line per-feature files with maintainable selectors
**Depends on**: Nothing (parallel to Phase 1)
**Requirements**: REQ-03, REQ-04
**Plans:** 4 plans
**Success Criteria** (what must be TRUE):
  1. No single spec file exceeds 300 lines
  2. All selectors referencing B2B UI text are extracted to a shared `selectors.ts` constants file
  3. All existing test cases still exist (no coverage regression)
  4. Each feature spec is independently runnable with `npx playwright test {spec-name}`

Plans:
- [ ] 02-01-PLAN.md — Create shared helpers.ts and selectors.ts foundation modules
- [ ] 02-02-PLAN.md — Split cv-access (6), cv-catalog (13), cv-cart (14) spec files
- [ ] 02-03-PLAN.md — Split cv-payments (11), cv-orders (9), cv-ui-features (12) spec files
- [ ] 02-04-PLAN.md — Verify test count parity and delete original file

### Phase 3: B2B Parallel Execution
**Goal**: B2B config validation runs across clients in parallel, not sequentially — with >=50% time reduction vs sequential and no test isolation issues
**Depends on**: Phase 2
**Requirements**: REQ-05
**Plans:** 1/1 plans complete
**Success Criteria** (what must be TRUE):
  1. `npx playwright test --workers=4` runs B2B specs without race conditions
  2. Total B2B suite execution time reduced by at least 50% vs. sequential baseline
  3. No test isolation issues between parallel workers

Plans:
- [ ] 03-01-PLAN.md — Measure baseline, add cart isolation fix, verify parallel >=50% reduction

### Phase 4: Live Reporter Race Condition Fix
**Goal**: `tools/live-reporter.js` writes to `public/live.json` atomically — concurrent Playwright workers or overlapping runs never produce invalid JSON or lost updates
**Depends on**: Nothing
**Requirements**: REQ-06
**Plans:** 1/1 plans complete
**Success Criteria** (what must be TRUE):
  1. Writing `live.json` is atomic: a concurrent reader always sees valid JSON (never a partial write)
  2. Overlapping `live-reporter.js` processes do not lose each other's updates
  3. Existing `publish-results.py` and dashboard consumers continue to work unchanged

Plans:
- [ ] 04-01-PLAN.md — Atomic write-then-rename in _save(), .gitignore + run-live.sh cleanup

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Playwright Teardown Fix | 0/1 | Planned | - |
| 2. Config Validation Refactor | 0/4 | Planned | - |
| 3. B2B Parallel Execution | 0/1 | Complete    | 2026-04-17 |
| 4. Live Reporter Race Condition Fix | 1/1 | Complete   | 2026-04-17 |

# Requirements: QA Repo Improvements

## Context

YOM QA repo improvements derived from codebase audit (2026-04-17).
Focus: reliability, maintainability, and test coverage of the QA pipeline.

## Requirements

### REQ-01: Playwright teardown reliability
The HTTP server spawned by `global-setup.ts` must always be cleaned up — even when tests crash or are killed mid-run. Port 8080 must not be left occupied between test runs.

### REQ-02: Playwright teardown — no orphaned processes
After any test run (pass, fail, or interrupt), no `http-server` process should remain running that was started by the QA test suite.

### REQ-03: config-validation.spec.ts split by feature
`tests/e2e/b2b/config-validation.spec.ts` (currently 1,762 lines) must be split into per-feature spec files. Each file must be under 300 lines and independently runnable.

### REQ-04: Brittle selector reduction
Replace inline text-based selectors in config-validation specs with `data-testid` attributes OR extract selectors into a single constants file so one UI change only requires one file edit.

### REQ-05: Parallel test execution for B2B validation
B2B config validation must be runnable in parallel across clients (not sequential 40+ minute runs).

### REQ-06: Live reporter race condition fix
`tools/live-reporter.js` writes to a single `public/live.json`. Concurrent Playwright workers or overlapping test runs must not corrupt the live state file. The fix must be atomic: partial writes must never leave `live.json` in an invalid JSON state.

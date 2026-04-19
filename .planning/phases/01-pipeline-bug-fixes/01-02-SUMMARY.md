---
phase: 01-pipeline-bug-fixes
plan: 02
subsystem: pipeline/live-reporter
tags: [playwright, reporter, dashboard, bugfix, pipeline]
requires:
  - public/live.json contract (running, total, passed, failed, skipped, currentTest, recentTests)
  - Playwright Reporter API (onBegin/onTestEnd/onEnd)
  - POSIX rename(2) atomic write (already implemented in _save)
provides:
  - Clean live.json state on every run start (no prior-run bleed)
  - Defense-in-depth idle sentinel during run-live.sh window before reporter boots
affects:
  - tools/live-reporter.js (onBegin only; other methods untouched)
  - tools/run-live.sh (one new heredoc block before cd tests/e2e)
tech-stack-added: []
patterns:
  - "Full-state replacement on lifecycle hook entry (JS)"
  - "Heredoc sentinel write for pre-process file reset (bash)"
key-files-created: []
key-files-modified:
  - tools/live-reporter.js
  - tools/run-live.sh
decisions:
  - "Chose Option B (onBegin replacement) + Option C (pre-run sentinel) combo per 01-RESEARCH.md — rejected Option A (onEnd reset) because it clobbers the 'run just finished' 3s UX window"
  - "Sentinel written locally only — no extra GitHub Contents API push (matches Open Question 2 resolution)"
  - "endTime intentionally omitted from onBegin replacement (has no meaning at run start); dashboard tolerates missing fields"
metrics:
  duration_seconds: 158
  tasks_completed: 2
  commits: 2
  completed_date: "2026-04-19"
requirements_closed:
  - PIPE-02
---

# Phase 1 Plan 02: Live Reporter Stale State Fix Summary

Replaces `this.state` entirely inside `tools/live-reporter.js` `onBegin()` and writes a clean idle sentinel to `public/live.json` from `tools/run-live.sh` before Playwright boots — eliminating the window where the dashboard polled stale counters (`total: 2932, passed: 0`) between runs.

## Outcome

- **Task 1:** `live-reporter.js` `onBegin()` now performs a full object replacement of `this.state` instead of only setting `.total`. Counters (`passed/failed/skipped`), `recentTests`, and any leftover `endTime` from a prior run are cleared in a single atomic `_save()`.
- **Task 2:** `run-live.sh` writes a deterministic idle sentinel (`{"running":false,"total":0,...}`) to `public/live.json` immediately after starting the HTTP server and opening the browser, before `cd tests/e2e` and the `LIVE=1 npx playwright test` invocation. Closes the ~1s window where a dashboard poll could otherwise hit prior-run data before the reporter's first `onBegin` fires.

## Before / After

### tools/live-reporter.js onBegin() — BEFORE (lines 29-32)

```javascript
onBegin(config, suite) {
  this.state.total = suite.allTests().length;
  this._save();
}
```

### tools/live-reporter.js onBegin() — AFTER (lines 29-44)

```javascript
onBegin(config, suite) {
  // Replace state entirely — clears counters, recentTests, and endTime from any
  // prior run that might otherwise bleed into this run's live.json snapshot.
  // Fixes PIPE-02: stale total/passed/failed/skipped between runs.
  this.state = {
    running: true,
    startTime: new Date().toISOString(),
    total: suite.allTests().length,
    passed: 0,
    failed: 0,
    skipped: 0,
    currentTest: null,
    recentTests: [],
  };
  this._save();
}
```

### tools/run-live.sh — BEFORE (lines 22-26)

```bash
# Open browser (macOS)
sleep 0.5 && open "http://localhost:${PORT}" &

# Run tests with live reporter (capture exit code — don't fail on test failures)
cd tests/e2e
```

### tools/run-live.sh — AFTER (lines 22-34)

```bash
# Open browser (macOS)
sleep 0.5 && open "http://localhost:${PORT}" &

# Reset live.json to clean idle sentinel BEFORE Playwright boots the reporter.
# Without this, the dashboard's 3s pollLive() can observe the prior run's
# counters during the ~1s window before live-reporter.js onBegin() fires.
# Fixes PIPE-02 gap closed by Option C in 01-RESEARCH.md.
cat > public/live.json <<'JSON'
{"running":false,"total":0,"passed":0,"failed":0,"skipped":0,"currentTest":null,"recentTests":[]}
JSON

# Run tests with live reporter (capture exit code — don't fail on test failures)
cd tests/e2e
```

## Verification

### Syntax checks

- `node --check tools/live-reporter.js` → exits 0 (PASS)
- `bash -n tools/run-live.sh` → exits 0 (PASS)

### Task 1 unit behavior check (Node one-liner from plan)

Command:
```
node -e "const R = require('./tools/live-reporter.js'); const r = new R(); r.state.passed = 999; r.state.recentTests = [{title:'stale'}]; r.onBegin({}, { allTests: () => Array(5).fill({}) }); if (r.state.passed !== 0) { console.error('FAIL passed:', r.state.passed); process.exit(1); } if (r.state.total !== 5) { console.error('FAIL total:', r.state.total); process.exit(1); } if (r.state.recentTests.length !== 0) { console.error('FAIL recentTests:', r.state.recentTests.length); process.exit(1); } if (r.state.running !== true) { console.error('FAIL running:', r.state.running); process.exit(1); } console.log('OK');"
```

Output:
```
OK
```

Confirms: stale in-memory `passed=999` and `recentTests=[{...}]` are cleared by `onBegin`, `total` is set from `suite.allTests().length`, `running` is `true`.

### Task 2 sentinel JSON validity

Piped the literal heredoc body into Python and asserted each field:

```
SENTINEL JSON VALID
```

(`running=False, total=0, passed=0, failed=0, skipped=0, currentTest=None, recentTests=[]`)

### Acceptance criteria grep counts

Task 1:
- `grep -c "this.state = {"` → 2 (constructor + onBegin) ✓
- `grep -c "this.state.total = suite.allTests().length;"` → 0 (removed) ✓
- `grep -c "total: suite.allTests().length,"` → 1 ✓
- `grep -c "module.exports = LiveReporter;"` → 1 ✓

Task 2:
- `grep -c "cat > public/live.json <<'JSON'"` → 1 ✓
- Sentinel JSON line → 1 occurrence ✓
- `grep -c "LIVE=1 npx playwright test"` → 1 ✓
- `grep -c "trap.*kill.*SERVER_PID"` → 1 ✓
- `grep -c "python3 tools/publish-results.py"` → 1 ✓
- Sentinel line number (29) < `cd tests/e2e` line number (34) ✓

## What was NOT touched (as required)

**live-reporter.js:**
- `constructor()` — untouched
- `onTestBegin`, `onTestEnd`, `onEnd` — untouched
- `_save()` — body byte-identical (atomic writeFileSync tmp + renameSync)
- `_pushToGitHub()` — body byte-identical (throttled GET/PUT via Contents API)
- Top-level constants (`OUTPUT`, `TMP_OUTPUT`, `GITHUB_REPO`, `GITHUB_FILE`, `PUSH_INTERVAL_MS`) — untouched
- `module.exports = LiveReporter;` — preserved

**run-live.sh:**
- `set -e`, `cd "$(dirname "$0")/.."` — unchanged
- `SPECS="${*:-b2b/}"`, `PORT=8080` — unchanged
- `python3 -m http.server` launch + `SERVER_PID` — unchanged
- `trap ... EXIT` (kills server + cleans live.json + .tmp) — unchanged
- `LIVE=1 npx playwright test ... "$@"` + exit-code capture — unchanged
- `python3 tools/publish-results.py` — unchanged
- Git commit/push block — unchanged
- `exit ${PLAYWRIGHT_EXIT:-0}` — unchanged

**Not touched at all:** `tests/e2e/global-teardown.ts`, `tests/e2e/playwright.config.ts`, dashboard (`public/index.html`).

## Deviations from Plan

None. Plan executed exactly as written. No auto-fixes (Rules 1-3) triggered; no architectural decisions (Rule 4) encountered.

## Commits

| Task | Hash     | Message |
|------|----------|---------|
| 1    | 4ed092c  | fix(01-02): replace state fully in live-reporter onBegin |
| 2    | 974dc08  | fix(01-02): add pre-run sentinel reset in run-live.sh |

## Operator Validation Checklist

Run these commands locally on a dev machine with Playwright installed to confirm end-to-end behavior:

```bash
# 1. Seed a stale live.json (simulates post-run state)
echo '{"running":false,"total":2932,"passed":0,"failed":0,"skipped":0,"currentTest":null,"recentTests":[]}' > public/live.json

# 2. First real run — sentinel from run-live.sh should immediately overwrite the seed,
#    then onBegin should re-write with the run's total and zero counters
./tools/run-live.sh b2b/healthcheck.spec.ts
# Expected: during the run, live.json has running=true with the healthcheck total,
# zero starting counters. After the run, EXIT trap removes live.json.

# 3. Second run in immediate succession — confirm no bleed
./tools/run-live.sh b2b/healthcheck.spec.ts
# Expected: second run also starts from zero counters, with total reflecting
# the healthcheck spec — not any prior state.
```

Manual dashboard check: open `public/index.html` locally after runs end; confirm the live panel does not show stale "Run completado" text between runs when no run is active.

## Known Stubs

None. The fix is a data-freshness improvement to an existing live-state file; no new UI components, no new data sources, no placeholders introduced.

## Deferred Issues

None.

## Threat Flags

No new threat surface introduced. The pre-run sentinel heredoc writes only literal booleans/integers/empty arrays (no secrets, no user input, no network I/O). `_pushToGitHub` cadence and `GITHUB_TOKEN` handling are unchanged. STRIDE register T-01-05 through T-01-09 in the plan remain accurate.

## Self-Check: PASSED

Files verified to exist:
- `tools/live-reporter.js` (FOUND, modified in commit 4ed092c)
- `tools/run-live.sh` (FOUND, modified in commit 974dc08)
- `.planning/phases/01-pipeline-bug-fixes/01-02-SUMMARY.md` (FOUND, this file)

Commits verified in git log:
- `4ed092c` — FOUND (fix(01-02): replace state fully in live-reporter onBegin)
- `974dc08` — FOUND (fix(01-02): add pre-run sentinel reset in run-live.sh)

All success criteria from the plan's `<success_criteria>` block satisfied.

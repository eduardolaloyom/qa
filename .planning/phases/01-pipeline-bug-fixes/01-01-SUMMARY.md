---
phase: 01-pipeline-bug-fixes
plan: 01
subsystem: infra
tags: [bash, python, json, manifest, maestro, dashboard, pipeline]

# Dependency graph
requires: []
provides:
  - tools/run-maestro.sh writes APP manifest entries to the unified public/manifest.json
  - tools/verify-maestro-manifest.sh smoke test for the PIPE-01 write contract
  - orphan public/app-reports/manifest.json removed from repo
affects: [02-live-reporter-sentinel, 03-dashboard-freshness, 04-unified-view, dashboard-app-tab]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Append-dedupe-sort manifest write targeting single source of truth
    - Standalone bash+Python smoke test for embedded-Python contracts (no framework required)

key-files:
  created:
    - tools/verify-maestro-manifest.sh
  modified:
    - tools/run-maestro.sh
  deleted:
    - public/app-reports/manifest.json

key-decisions:
  - "Split PUBLIC_DIR into HTML_DIR (report output) + MANIFEST_FILE (unified public/manifest.json) — preserves HTML location while redirecting manifest writes"
  - "Prefix `file` field with `app-reports/` in the Python append block — dashboard builds links as `<a href=rep.file>` with no prefixing, so the path must resolve relative to public/"
  - "Delete orphan public/app-reports/manifest.json in same plan — its 2 Prinorte entries are already duplicated in public/manifest.json, no audit loss"
  - "Smoke test runs the exact Python append block logic against a scratch temp file — no Android device, no Maestro CLI needed"

patterns-established:
  - "Pipeline scripts write to single source of truth (public/manifest.json); HTML artifacts can live in subdirectories with their path prefix included in the manifest `file` field"
  - "Smoke tests for embedded-Python blocks in shell scripts: seed a tmp manifest, re-run the exact Python block verbatim, assert with inline python3 -c"

requirements-completed: [PIPE-01]

# Metrics
duration: 2min
completed: 2026-04-19
---

# Phase 01 Plan 01: PIPE-01 Maestro Manifest Unification Summary

**Redirected `tools/run-maestro.sh` manifest writes from orphan `public/app-reports/manifest.json` to unified `public/manifest.json`, with `file` prefixed for correct dashboard link resolution, plus a standalone bash+Python smoke test and orphan manifest deletion.**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-04-19T20:17:09Z
- **Completed:** 2026-04-19T20:19:10Z
- **Tasks:** 2
- **Files modified:** 1 (tools/run-maestro.sh)
- **Files created:** 1 (tools/verify-maestro-manifest.sh)
- **Files deleted:** 1 (public/app-reports/manifest.json)

## Accomplishments

- Maestro runs will now appear in the dashboard APP tab because `run-maestro.sh` writes to the same `public/manifest.json` the dashboard reads (PIPE-01 fix)
- `file` field prefixed with `app-reports/` so dashboard `<a href=rep.file>` resolves to `public/app-reports/{cliente}-{date}.html` rather than 404-ing
- Standalone smoke test (`tools/verify-maestro-manifest.sh`) validates the write contract without requiring Maestro CLI or Android device
- Orphan `public/app-reports/manifest.json` removed — future contributors will not confuse it with the live manifest

## Task Commits

Each task was committed atomically with `--no-verify` (parallel executor worktree):

1. **Task 1: Split PUBLIC_DIR into HTML_DIR + unified MANIFEST_FILE in run-maestro.sh** — `3f0bce4` (fix)
2. **Task 2: Smoke-test the manifest write + delete orphan manifest** — `11751f7` (test)

_Plan metadata (SUMMARY.md) commit: created after this write._

## Files Created/Modified

### Modified

**`tools/run-maestro.sh`** — 5 insertions, 5 deletions (net zero; surgical in-place edits):

Before (lines 52-55):
```bash
PUBLIC_DIR="$QA_ROOT/public/app-reports"
MANIFEST_FILE="$PUBLIC_DIR/manifest.json"
REPORT_FILE="${CLIENTE}-${DATE}.html"
REPORT_PATH="$PUBLIC_DIR/${REPORT_FILE}"
```

After:
```bash
HTML_DIR="$QA_ROOT/public/app-reports"
MANIFEST_FILE="$QA_ROOT/public/manifest.json"
REPORT_FILE="${CLIENTE}-${DATE}.html"
REPORT_PATH="$HTML_DIR/${REPORT_FILE}"
```

Before (line 98):
```bash
mkdir -p "$OUTPUT_DIR" "$PUBLIC_DIR"
```

After:
```bash
mkdir -p "$OUTPUT_DIR" "$HTML_DIR"
```

Before (embedded Python, line 463):
```python
'file':         report_file,          # just "prinorte-2026-04-15.html"
```

After:
```python
'file':         f'app-reports/{report_file}',   # "app-reports/prinorte-2026-04-15.html"
```

All other schema fields and the append-dedupe-sort block preserved byte-identical.

### Created

**`tools/verify-maestro-manifest.sh`** (executable) — standalone smoke test that:
1. Seeds a scratch `manifest.json` with one existing b2b entry
2. Re-runs the exact Python append block from `run-maestro.sh` against the scratch file
3. Asserts: `platform == 'app'`, `file == 'app-reports/smoketest-2026-04-19.html'`, pre-existing b2b entry preserved (additive write), entries sorted descending by date
4. Requires only bash + python3 (stdlib); no Maestro, no Android device

### Deleted

**`public/app-reports/manifest.json`** — orphan after Task 1 (no writer, no reader). Its 2 Prinorte entries already duplicated in `public/manifest.json`; git history preserves the deletion.

## Verification Results

Run of `tools/verify-maestro-manifest.sh` after Task 2 completed:

```
✅ manifest schema OK
✅ additive write — b2b entry preserved
✅ sorted descending by date

✅ PIPE-01 smoke test passed
```

Plan-level verification (all pass):

| Check | Command | Result |
|-------|---------|--------|
| Static syntax (run-maestro.sh) | `bash -n tools/run-maestro.sh` | OK |
| Static syntax (verify script) | `bash -n tools/verify-maestro-manifest.sh` | OK |
| Smoke test | `bash tools/verify-maestro-manifest.sh` | PASS |
| Orphan removed | `test ! -f public/app-reports/manifest.json` | PASS |
| HTML dir preserved | `test -d public/app-reports` | PASS |
| Unified manifest shape intact | Python load + field presence check | 5 entries, all valid |
| Unified manifest count unchanged | Count before vs after | 5 → 5 (orphan delete did not touch unified) |

## Decisions Made

- **Plan executed exactly as written** — all 4 open questions in RESEARCH.md were pre-resolved by the planner, so no in-flight decisions were needed.
- The HTML_DIR/MANIFEST_FILE split (vs. keeping a single PUBLIC_DIR and building MANIFEST_FILE off `$QA_ROOT/public` directly) follows the plan's literal instruction and makes the variable names self-documenting.

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

**Scope-leak in initial Task 1 commit (resolved before continuing):**

- The worktree's working tree carried pre-existing uncommitted modifications to `tools/live-reporter.js` (PIPE-02 work, out of scope for this plan) and `public/live.json` (runtime state, gitignored at remote but present locally). The first `git commit` for Task 1 — even after using `git add tools/run-maestro.sh` — picked up `tools/live-reporter.js` because it had been staged by a prior session's index state.
- **Resolution:** `git reset --soft HEAD~1`, `git restore --staged tools/live-reporter.js`, `git checkout -- tools/live-reporter.js`, then re-committed Task 1 with only `tools/run-maestro.sh`. Verified via `git show --stat` that the final Task 1 commit (`3f0bce4`) contains only the one file, 5 insertions + 5 deletions.
- **No impact on plan:** the PIPE-02 work was not written by this executor; it was ambient worktree state. Task 1 commit is now clean and isolated.

## User Setup Required

None — this plan only modifies a pipeline script and adds a smoke test. No new env vars, no external services.

## Next-Run Validation Checklist (for Eduardo)

After the next real Maestro run (`./tools/run-maestro.sh <cliente>`):

- [ ] A new entry appears in `public/manifest.json` with `platform: "app"` and `file: "app-reports/<cliente>-<date>.html"`
- [ ] `public/app-reports/<cliente>-<date>.html` exists (HTML output path unchanged)
- [ ] `public/app-reports/manifest.json` does NOT reappear (would indicate a regression in the Python block)
- [ ] Open `public/index.html` locally → APP tab → the new card appears alongside the existing Prinorte cards
- [ ] Click the new card → opens the HTML report (no 404)
- [ ] Existing b2b entries (Sonrie, Bastien, new-soprole) still render in the B2B/Cowork section unchanged

## Next Phase Readiness

- Unified manifest write contract established and smoke-tested. Ready for Plan 02 (PIPE-02 live.json sentinel reset) to land next.
- No coupling between this plan and PIPE-02 other than both living in the pipeline layer — they can merge in either order.
- Dashboard side requires no changes; the polymorphic schema (b2b + app entries coexisting) was already proven by the two pre-existing Prinorte entries.

## Self-Check: PASSED

Files claimed:
- FOUND: `/Users/lalojimenez/qa/tools/run-maestro.sh` (modified, 5+/5-)
- FOUND: `/Users/lalojimenez/qa/tools/verify-maestro-manifest.sh` (created, executable)
- FOUND: absence of `/Users/lalojimenez/qa/public/app-reports/manifest.json` (deleted)

Commits claimed:
- FOUND: `3f0bce4` — Task 1 (fix)
- FOUND: `11751f7` — Task 2 (test)

Verification claimed:
- `bash -n tools/run-maestro.sh` → exit 0
- `bash tools/verify-maestro-manifest.sh` → prints `✅ PIPE-01 smoke test passed`
- `public/manifest.json` count unchanged at 5 entries

---
*Phase: 01-pipeline-bug-fixes*
*Completed: 2026-04-19*

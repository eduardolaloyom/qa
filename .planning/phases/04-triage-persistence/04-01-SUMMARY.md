---
phase: 04-triage-persistence
plan: 01
subsystem: testing
tags: [python, yaml, pyyaml, pipeline, triage, publish-results, overlay]

# Dependency graph
requires:
  - phase: 03-dashboard-live
    provides: "public/history/{date}.json pipeline with failure_groups schema (category, reason, clients, etc.)"
provides:
  - "Triage overlay helpers (_triage_file_path, _parse_triage_file, _apply_triage_overlay) in tools/publish-results.py"
  - "Runtime detection of QA/{Display|slug}/{date}/triage-{date}.md files during publish"
  - "Optional triage field on failure_groups[] persisted to public/history/{date}.json"
  - "Fail-safe behavior: missing file → no-op (D-15), invalid YAML → warning (D-16), orphan section → warning (D-17)"
  - "Secret redaction via mask_secrets() on rationale + action_taken before JSON embed"
affects:
  - 04-02 (triage-playwright command — writes files consumed by this overlay)
  - 05-qa-listo (may consume failure_groups[].triage for audit / status aggregation)
  - 06-agent-precision (playwright-failure-analyst role may auto-generate triage files)

# Tech tracking
tech-stack:
  added:
    - "PyYAML 6.0.3 (already installed system-wide — only added `import yaml`)"
  patterns:
    - "Overlay (no override): add new 'triage' field to failure_group; preserve auto-classified 'category' untouched"
    - "Display-name-first with slug fallback for QA/ directory lookups (handles lowercase new-soprole dir)"
    - "YAML frontmatter + fenced ```yaml``` section body parsing via yaml.safe_load + re.finditer"
    - "Fail-safe file parsing: warning-to-stderr on any error, never raise"

key-files:
  created: []
  modified:
    - "tools/publish-results.py — +180 lines (import + 3 helpers + 2-line wiring in generate_run_json)"

key-decisions:
  - "Overlay applied INSIDE generate_run_json() before return, so merge_run_json per-client replacement preserves the triage field (Common Pitfall #3 in 04-RESEARCH.md)"
  - "yaml.safe_load exclusively — never yaml.load() (T-04-01 mitigation)"
  - "mask_secrets() called on rationale and action_taken before overlay write (T-04-02 mitigation)"
  - "failure_groups hoisted to named local variable to enable the pre-return overlay mutation"
  - "Display-name lookup via load_staging_urls + strip '(staging)' suffix; falls back to raw slug if display dir missing (handles new-soprole)"

patterns-established:
  - "Helper-triplet pattern: path-resolver → file-parser → overlay-mutator for optional feature flags on pipeline output"
  - "Warning-to-stderr + silent skip for fail-safe parsing (never break the publish pipeline on bad triage file)"
  - "Exact-string matching on reason_match via (slug, reason) dict index for O(1) lookup"

requirements-completed:
  - PROC-02

# Metrics
duration: ~18min
completed: 2026-04-20
---

# Phase 4 Plan 01: Triage Overlay in publish-results.py Summary

**publish-results.py now reads optional `QA/{client}/{date}/triage-{date}.md` files and embeds triage decisions (category, rationale, linear_ticket, action_taken, triaged_at, triaged_by) into `public/history/{date}.json.failure_groups[]` — zero regression when no triage file exists**

## Performance

- **Duration:** ~18 min
- **Started:** 2026-04-20T13:22:30Z
- **Completed:** 2026-04-20T13:40:15Z
- **Tasks:** 2
- **Files modified:** 1 (tools/publish-results.py, +180 lines)

## Accomplishments

- Added `import yaml` (PyYAML 6.0.3, already system-installed)
- Implemented three pure helpers in `tools/publish-results.py`:
  - `_triage_file_path(slug, date, project_root, staging_urls)` — resolves `QA/{Display|slug}/{date}/triage-{date}.md` with fallback
  - `_parse_triage_file(path)` — returns `(frontmatter_dict, [section_dict, ...])`, fail-safe on any YAML / IO error
  - `_apply_triage_overlay(failure_groups, date, project_root)` — mutates groups in place, adds `triage` field where reason_match is exact
- Wired overlay into `generate_run_json()` after `generate_failure_groups()` and before the return dict, ensuring `merge_run_json` preserves triage (Common Pitfall #3)
- Applied `mask_secrets()` to `rationale` and `action_taken` before embedding (T-04-02 mitigation)
- Used `yaml.safe_load` exclusively (T-04-01 mitigation — zero `yaml.load(` in the file)
- Validated D-15 (no file = no regression), D-16 (invalid YAML = warning + skip), D-17 (orphan = warning + skip), D-09 (overlay preserves original `category`), D-14 (re-reads on each publish)

## Task Commits

Each task was committed atomically with `--no-verify` (parallel executor in worktree):

1. **Task 1: Import yaml + 3 triage overlay helpers** — `78e7ba3` (feat)
2. **Task 2: Wire _apply_triage_overlay into generate_run_json** — `6210e40` (feat)

## Files Created/Modified

- `tools/publish-results.py`
  - Added `import yaml` (line 22)
  - Added `_triage_file_path()` (lines 509-529) — display-name-first path resolver with slug fallback
  - Added `_parse_triage_file()` (lines 532-593) — YAML frontmatter + fenced section parser
  - Added `_apply_triage_overlay()` (lines 596-677) — in-place overlay mutator with orphan warnings and mask_secrets integration
  - Refactored `generate_run_json()` return block (lines 792-813) — hoisted `failure_groups` to named variable, inserted overlay call before return

## Decisions Made

- **Overlay runs inside `generate_run_json()` before return** — consistent with Common Pitfall #3 research finding. `merge_run_json` replaces failure_groups per client, so the overlay must stamp `triage` onto the new run's groups before merge.
- **Display-name fallback via `load_staging_urls`** — reused existing mechanism rather than creating a new slug→display map. Fallback to raw slug when `QA/{Display}/` missing (covers new-soprole lowercase dir).
- **mask_secrets on `rationale` and `action_taken` only** — `linear_ticket` is structured (YOM-NNN), `category` is enum (bug/flaky/ambiente), `triaged_at`/`triaged_by` are controlled. Only free-text fields need redaction.
- **`_title` attached to each parsed section** — used for orphan warning messages so Eduardo can locate the bad section in the triage file quickly.

## Deviations from Plan

None — plan executed exactly as written.

### Verification Performed

All verification gates from the plan passed:

**Task 1 (helper unit tests):**
- Parse happy path with 1 valid section → `(fm_dict, [section_dict])` with correct fields
- Invalid YAML → `({}, [])` + warning to stderr (D-16)
- Overlay on matched reason → `triage` dict with 6 subcampos, mask_secrets redacted `token=abc123defghi` → `token=[REDACTED]`
- Missing file → no-op, no `triage` added (D-15)
- Orphan section (no reason_match) → warning, no mutation (D-17)
- Display-vs-slug fallback → `QA/Bastien/` found via display name lookup

**Task 2 (integration / regression):**
- Static checks: overlay call is AFTER `failure_groups = generate_failure_groups(...)` and BEFORE `return {`
- `yaml.load(` unsafe occurrences: 0. `yaml.safe_load(` usages: 2.
- `mask_secrets(rationale)` and `mask_secrets(action_taken)` present inside `_apply_triage_overlay`
- **Zero-regression gate:** ran overlay on real `public/history/2026-04-17.json.failure_groups` with no triage files → `json.dumps(fg_before, sort_keys=True) == json.dumps(fg_after, sort_keys=True)`. Confirmed 0 triage fields added to 3 pre-existing failure_groups.
- **Positive integration gate:** created `QA/Sonrie/2026-04-17/triage-2026-04-17.md` with exact `reason_match` for the first failure_group → overlay applied `triage` dict with `category=bug`, `linear_ticket=YOM-234`, `triaged_by=Claude`, `triaged_at=2026-04-17`, rationale with `[REDACTED]` replacing the embedded test token. Other two groups remained untouched.
- End-to-end run `python3 tools/publish-results.py --date 2026-04-17` completed without errors; produced history JSON structurally identical to pre-run (only `timestamp` field changed — expected).

## Issues Encountered

- **First verification script had wrong assertion for unsafe YAML detection** — used `assert bad_count == safe_count` where it should have been `assert bad_count == 0`. Fixed and re-ran; gate passes with 0 unsafe uses.

## User Setup Required

None — PyYAML 6.0.3 is already installed system-wide (verified via `python3 -c "import yaml; print(yaml.__version__)"`). No new dependencies, no config changes.

## Next Phase Readiness

- **Plan 04-02 can proceed:** `/triage-playwright` command can now write `QA/{CLIENT}/{DATE}/triage-{date}.md` files knowing that the publish pipeline will pick them up on the next run.
- **No dashboard changes required** — D-11 explicitly defers UI to Phase 5 or later. `public/history/{date}.json.failure_groups[].triage` is metadata that any future consumer can read.
- **Manual positive validation path for Eduardo:** create `QA/Codelpa/2026-04-17/triage-2026-04-17.md` with a real failure reason_match → run `python3 tools/publish-results.py --date 2026-04-17` → inspect `public/history/2026-04-17.json` for the `triage` field.

## Self-Check: PASSED

- `tools/publish-results.py` exists and contains `import yaml`, `_triage_file_path`, `_parse_triage_file`, `_apply_triage_overlay`
- Commit `78e7ba3` present (feat 04-01: helpers)
- Commit `6210e40` present (feat 04-01: wiring)
- `mask_secrets(rationale)` + `mask_secrets(action_taken)` verified in overlay source
- `yaml.load(` unsafe call count: 0
- `yaml.safe_load(` safe call count: 2
- D-15 regression test: no-op confirmed on real 2026-04-17.json (3 failure_groups, 0 triage fields)
- D-17 orphan test: warning logged, no mutation
- Positive integration test: triage field applied with mask_secrets redaction

---
*Phase: 04-triage-persistence*
*Completed: 2026-04-20*

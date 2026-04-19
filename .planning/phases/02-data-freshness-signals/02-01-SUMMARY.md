---
phase: 2
plan: 01
subsystem: dashboard-ui
tags: [css, html, vanilla-js, dashboard, freshness-signals]
requires: []
provides: [css-classes-freshness, html-skeleton-run-nav]
affects: [public/index.html]
tech_stack_added: []
tech_stack_patterns: [inline-css-style-block, additive-html-insertion]
key_files_created: []
key_files_modified:
  - public/index.html
decisions:
  - "D-07: Two separate visual elements per card — .client-last-tested always visible + .freshness-badge only when diffDays > 2."
  - "D-02: Run-nav placed immediately before #clientsContainer inside the B2B card, not in the card header or tab bar."
  - "Empty <select> skeleton in plan 01; plan 02-02 wires JS populate + change listener."
metrics:
  tasks_completed: 2
  total_tasks: 2
  duration_minutes: 2
  files_changed: 1
  lines_added: 47
  commits: 3
completed: 2026-04-19
---

# Phase 2 Plan 01: CSS + HTML Skeleton Summary

Foundation layer for data freshness signals: six new CSS classes and an empty run-nav HTML container wired into the B2B card, leaving the JS logic for plan 02-02.

## What Was Built

### CSS additions (`public/index.html` lines 573–615)

Inserted after the existing `.client-url` rule, before `.pass-rate-badge`:

- `.client-last-tested` — 11px / weight 400 / color `#9ca3af` / margin-top 4px. Metadata line for "Testeado: YYYY-MM-DD" or "Sin datos de test".
- `.freshness-badge` — base pill: inline-flex, 4px 8px padding, 9999px border-radius, 11px / weight 700, no wrap, no shrink.
- `.freshness-badge.freshness-stale` — amber variant: background `#fef3c7`, text `#92400e`.
- `.run-nav` — flex container, 8px gap, 8px bottom margin.
- `.run-nav-label` — 12px / weight 400 / color `#6b7280`, no wrap.
- `.run-select` — native `<select>` styling: 4px 8px padding, 1.5px border `#d1d5db`, 8px radius, 12px font, inherited font-family, color `#374151`, white background, pointer cursor.
- `.run-select:focus` — outline none, border `#667eea` (matches the existing accent color).

All six classes follow the token scale defined in `02-UI-SPEC.md` (spacing 4/8, typography 11/12px, color palette dominant/accent/amber).

### HTML additions (`public/index.html` lines 1263–1266)

Inside the B2B `<div class="card">`, directly between the card-title and `#clientsContainer`:

```html
<div class="run-nav">
    <span class="run-nav-label">Run:</span>
    <select id="runSelector" class="run-select"></select>
</div>
```

The `<select>` is intentionally empty — plan 02-02 handles `populateRunSelector()` from `allRuns` and the `change` event listener. At this point the dashboard renders a visible but non-functional "Run:" label with an empty dropdown; functionality lands when plan 02-02 merges.

## Files Modified

| File | Change |
|------|--------|
| `public/index.html` | +47 lines total (43 CSS, 4 HTML). No existing selector or element mutated. |
| `.planning/phases/02-data-freshness-signals/02-01-PLAN.md` | New — task specification for this plan. |
| `.planning/phases/02-data-freshness-signals/02-01-SUMMARY.md` | New — this file. |

## Commits

| Hash | Message |
|------|---------|
| `c9bacfa` | docs(02-01): add plan for CSS + HTML skeleton |
| `6378ca3` | feat(02-01): add CSS classes for freshness signals and run nav |
| `9457fe9` | feat(02-01): insert run-nav HTML skeleton before clients grid |

## Verification

- `grep -n 'client-last-tested' public/index.html` → line 573 (CSS only, no JS consumer yet — expected in this plan).
- `grep -n 'freshness-badge' public/index.html` → lines 579, 589 (base + stale variant).
- `grep -n 'run-select' public/index.html` → lines 605, 615, 1265 (CSS + focus + HTML).
- `grep -n 'id="runSelector"' public/index.html` → single match at line 1265.
- `grep -n '.client-card-header' public/index.html` → existing rule at line 561 unchanged.
- `grep -n 'clientsContainer' public/index.html` → two matches (HTML 1267, JS 1864 — both unchanged apart from line shift from added CSS/HTML above).

## Key Decisions

- **Empty `<select>` skeleton** — rather than duplicating plan 02-02's populate logic here, we ship a dead but valid HTML container. This keeps plan 02-01 strictly "CSS + HTML skeleton" and plan 02-02 strictly "JS logic" with zero overlap in the edit surface. Backward-compatible because there are no existing consumers of `#runSelector`.
- **CSS placement after `.client-url`** — keeps all client-card styling clustered together in the stylesheet, matching the existing `.client-name` → `.client-url` → `.pass-rate-badge` grouping.
- **Run-nav HTML placement inside the B2B card** — honors D-02 (ubicación = inmediatamente antes del `clientsContainer` div, dentro de la sección B2B). The label/select sit above the grid so users see the context before the content.

## Deviations from Plan

None — plan executed exactly as written. No Rule 1/2/3 fixes triggered. No auth gates. No out-of-scope discoveries.

## Known Stubs

- `<select id="runSelector">` is empty until plan 02-02 populates it via `populateRunSelector()`. This is intentional and documented — plan 02-02 (wave 2) completes the functionality. Not a blocker because the B2B card continues to render its grid via the existing `updateClients()` call path.

## Dependencies Downstream

Plan 02-02 will:
1. Populate `#runSelector` from `allRuns` (respecting the ≤10/>10 rule from D-04).
2. Add a `change` listener that calls `loadRunDetails(date)` and then `updateClients(selectedRun)`.
3. Refactor `updateClients()` into `updateClients(run = latestRun)` and replace the `lastTestedBadge` inline-style block with the CSS classes shipped in this plan.

All three CSS class groups and the HTML `<select>` anchor are now available for plan 02-02 to consume.

## Self-Check: PASSED

- [x] CSS classes present — verified via Grep (6 classes + focus state).
- [x] HTML skeleton present — verified via Grep (run-nav + runSelector).
- [x] No existing rules modified — `.client-card-header`, `.client-url`, `.pass-rate-badge` unchanged.
- [x] Commits exist — `c9bacfa`, `6378ca3`, `9457fe9` all in `git log`.
- [x] No unintended deletions — `git diff --diff-filter=D HEAD~2 HEAD` returned empty.

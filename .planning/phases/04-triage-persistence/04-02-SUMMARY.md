---
phase: 04-triage-persistence
plan: 02
subsystem: claude-command-triage
tags:
  - claude-command
  - triage
  - persistence
  - git-flow
  - phase-4
dependency_graph:
  requires:
    - ai-specs/.commands/triage-playwright.md (existing Steps 1-4)
    - data/qa-matrix-staging.json (slug → display name)
    - CLAUDE.md (global push-a-main policy)
  provides:
    - Step 5 "Persistir decisiones" in /triage-playwright
    - YAML frontmatter + fenced yaml section template
    - QA/{CLIENT}/{DATE}/triage-{date}.md artifact generation
    - Immediate commit+push flow with pull --rebase fallback
  affects:
    - QA/{CLIENT}/{DATE}/ directory (new file per triage session)
    - git history (chore(triage): ... commits)
    - tools/publish-results.py (consumer — will be wired in Plan 04-01)
tech_stack:
  added: []
  patterns:
    - YAML frontmatter (delimited by ---) + markdown body with ## sections
    - Fenced ```yaml``` blocks per section for structured fields
    - Double-quoted YAML strings for reason_match (escapes \\ and $)
    - Block scalar (|) for multi-line rationale
    - Commit+push atomic flow with rebase fallback
key_files:
  created: []
  modified:
    - ai-specs/.commands/triage-playwright.md
decisions:
  - D-01..D-05 honored: YAML frontmatter + section ## + fenced yaml body with 5 fields
  - D-06: granularity = one section per failure_group (not per test)
  - D-07: one triage-{date}.md per client
  - D-08: multi-client failure_group → replicate same section in each client's file
  - D-12: commit+push immediate at end of Step 5, single commit for all clients
  - D-14: re-run overwrites file (manual edits lost on next triage session)
  - Step 5 Resumen renumbered to Step 6 (preserves flow 1→2→3→4→5→6)
  - Display-name resolver with QA/{Display}/ → QA/{slug}/ → create default order
metrics:
  duration_minutes: 6
  completed_date: "2026-04-20"
  tasks_completed: 1
  tasks_total: 1
  files_modified: 1
  files_created: 0
  commits: 1
---

# Phase 4 Plan 02: Triage Command Persistence — Summary

Extend `/triage-playwright` with a mandatory Step 5 that writes a `QA/{CLIENT}/{DATE}/triage-{date}.md` file per affected client (YAML frontmatter + ## section per failure_group + fenced yaml body) and commits+pushes the result to main in a single atomic flow — closing PROC-01 (triage artifacts auditable via git history).

## What Was Built

### Step 5 "Persistir decisiones" in `/triage-playwright`

Inserted a new Step 5 between existing Step 4 (triage interactivo) and the previously-numbered "### 5. Resumen final" (renumbered to Step 6). The new step has five sub-steps:

- **5a. Agrupar decisiones por cliente** — build `decisions_by_client` dict; replicate per D-08 when a failure_group affects multiple clients.
- **5b. Resolver ruta del archivo** — try `QA/{Display}/{DATE}/` first, fallback to `QA/{slug}/{DATE}/` (lowercase), else create `QA/{Display}/{DATE}/`. Handles the `new-soprole` capitalization inconsistency.
- **5c. Generar contenido del archivo** — exact template with YAML frontmatter (`client`, `date`, `total_failures`, `triaged_count`, `triaged_by`) + `# Triage — {Display} — {DATE}` title + one `##` section per failure_group with a fenced ```yaml``` block containing `reason_match`, `category`, `rationale` (block scalar `|`), `linear_ticket`, `action_taken`.
- **5d. Escribir archivos** — `mkdir -p` + Write tool per client (no heredoc).
- **5e. Commit + push inmediato** — single commit for all generated files with message `chore(triage): {CLIENTES} {FECHA} — {N} failure_groups classified`. Fallback `git pull --rebase origin main && git push origin main` on rejection (CLAUDE.md global policy).

### Step 6 Resumen final (renumbered from Step 5)

Enhanced with a new "Persistencia" block that reports number of files written, exact commit message, and push target — giving Eduardo explicit confirmation the artifacts reached the remote.

### Reglas section — 6 new rules added

1. Persistir es obligatorio (Step 5 not optional).
2. `reason_match` debe copiarse EXACTAMENTE desde `failure_group.reason`.
3. Una sección por `failure_group`, no por test individual (D-06).
4. Un archivo por cliente afectado; replicar sección para multi-client groups (D-08).
5. Re-run del mismo día sobreescribe el archivo (D-14).
6. Commit+push inmediato, sin preguntar (consistente con CLAUDE.md global).

### Archivos clave section — 2 new entries

- `QA/{CLIENT}/{DATE}/triage-{date}.md` — output of the command, committed to git.
- `tools/publish-results.py` — consumer of the triage file (auto-reads on each publish if the file exists, wired in Plan 04-01).

## Verification

All 8 structural checks of the plan's `<verify><automated>` block passed:

1. Step 5 heading with "Persistir" present.
2. Step 5 precedes Step 6.
3. All 5 frontmatter keys present (`client:`, `date:`, `total_failures:`, `triaged_count:`, `triaged_by:`).
4. All 5 section yaml fields present (`reason_match:`, `category:`, `rationale:`, `linear_ticket:`, `action_taken:`).
5. Git flow commands present (`git add QA/`, `git commit -m`, `chore(triage):`, `git push`, `pull --rebase`).
6. Reglas updated with required snippets (`reason_match debe copiarse EXACTAMENTE`, `double-quoted`, `D-06`, `D-08`, `Commit+push es inmediato`).
7. QA path pattern present in Archivos clave (`QA/{CLIENT}/{DATE}/triage-{date}.md` + `tools/publish-results.py`).
8. No duplicate heading numbering — exactly one `### 5.` and one `### 6.` top-level heading.

Semantic coherence: Steps 1 (adopt role) → 2 (load results) → 3 (initial summary) → 4 (triage each) → 5 (persist) → 6 (final summary). Template uses `|` block scalar for multi-line rationale. Multi-client replication rule documented in both 5a and the Reglas section (two reinforcing mentions).

## Deviations from Plan

None — plan executed exactly as written. The action block specified insertion points and exact text literally; no gap required improvisation.

## Commits

- `7701b6d` feat(04-02): add Step 5 persistir decisiones to /triage-playwright

## Interop with Plan 04-01

The `reason_match` field generated by this step is consumed by `_apply_triage_overlay` in `publish-results.py` (Plan 04-01). Both sides use exact `==` comparison — success depends on the command copying `failure_group.reason` verbatim into the YAML double-quoted string. The Step 5 template enforces this explicitly via the "reason_match DEBE ser idéntico a `failure_group.reason`" rule and by instructing Claude to copy the string without truncation.

Escape handling: YAML double-quoted strings tolerate `\\` (backslash), `\"` (quote), `` ` `` (backtick), `$`, `*`, `.` — covering the verified failure reasons in `public/history/2026-04-17.json` (e.g., `"Elemento no encontrado: \`text=/\\\\$\\\\s*[\\\\d.,]+/\`"`).

## Requirements Closed

- **PROC-01** — `/triage-playwright` genera `QA/{CLIENT}/{DATE}/triage-{date}.md` con decisiones por fallo (bug|flaky|ambiente) + rationale.

## Decisions Honored

D-01, D-02, D-03, D-04, D-05, D-06, D-07, D-08, D-12, D-14.

## Deferred / Out of Scope

- Update of `ai-specs/.agents/playwright-failure-analyst.md` to auto-generate the archive (deferred to Phase 6 per CONTEXT.md Deferred Ideas).
- Badge visual de triage en dashboard (Phase 5+ per D-11).
- Integración Linear auto-create tickets from `bug` triages (post-MVP).

## Known Stubs

None — the command is a pure markdown specification that Claude interprets at runtime. The template literals (`{CLIENT}`, `{DATE}`, `{YOM-NNN}`) are intentional placeholders interpreted by Claude during session execution, not stub data.

## Threat Flags

None — Phase 4 Plan 02 only modifies a Claude command specification. No new network endpoints, auth paths, file access patterns, or schema changes at trust boundaries were introduced. The documented threat register (T-04-06..T-04-09) is fully covered: Reglas and action text instruct against leaking credentials in `rationale`/`action_taken`, the rebase fallback addresses race conditions, `triaged_by` provides repudiation traceability.

## Self-Check: PASSED

- File `ai-specs/.commands/triage-playwright.md` exists and contains Step 5 + Step 6 + updated Reglas + updated Archivos clave — VERIFIED
- Commit `7701b6d` exists in `git log` — VERIFIED
- Automated 8-check structural verification passes — VERIFIED

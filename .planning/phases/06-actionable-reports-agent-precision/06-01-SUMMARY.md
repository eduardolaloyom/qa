---
phase: 06-actionable-reports-agent-precision
plan: 01
subsystem: ai-specs/commands
tags: [report-qa, accionables, executive-summary, stakeholder-readiness]
dependency_graph:
  requires: []
  provides: [PROC-05, PROC-06]
  affects: [ai-specs/.commands/report-qa.md]
tech_stack:
  added: []
  patterns: [markdown-instructions, 4-col-table, veredicto-pattern]
key_files:
  modified:
    - ai-specs/.commands/report-qa.md
decisions:
  - "Resumen ejecutivo va en ambos formatos (.md y .html) con mismo contenido"
  - "Accionables limita a P0/P1; P2/P3 permanecen en Issues detallados"
  - "Sección Accionables reemplaza Recommendations en Report Structure template"
  - "Plazos relativos: P0=0-1 dias, P1=2-5 dias — sin fechas absolutas para evitar staleness"
  - "Dueños: Tech (bug app/API), QA (selector/flaky/cobertura), PM (config/precio/dato visible)"
metrics:
  duration: "88 seconds"
  completed: "2026-04-20"
  tasks_completed: 2
  tasks_total: 2
  files_modified: 1
---

# Phase 6 Plan 01: Report QA — Actionable Reports Summary

Actualizacion de `/report-qa` command con resumen ejecutivo 3 lineas + seccion Accionables con tabla 4 columnas (Issue | Severidad | Dueno | Plazo) limitada a P0/P1, en ambos formatos .md y .html.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Agregar instruccion de resumen ejecutivo 3 lineas en Step 6 y Report Structure | 0e8345d | ai-specs/.commands/report-qa.md |
| 2 | Reemplazar seccion Recommendations por seccion Accionables con tabla 4 cols y logica P0/P1-only | 67b4cbb | ai-specs/.commands/report-qa.md |

## What Was Built

`ai-specs/.commands/report-qa.md` actualizado en 5 puntos:

1. **Step 6a — Resumen ejecutivo** (Task 1): Reemplaza el item generico "Resumen ejecutivo: modos completados..." por instruccion exacta con formato `{VEREDICTO} | Score {N}/100 | {X} issues criticos (P0: {N}, P1: {M})`, valores posibles de veredicto, y separador `---`.

2. **Step 6b — HTML executive-summary div** (Task 1): Agrega instruccion para incluir el resumen ejecutivo como `<div class="executive-summary">` antes del primer `<section>` en el HTML.

3. **Report Structure template — header** (Task 1): Agrega las 3 lineas de resumen ejecutivo inmediatamente bajo `# QA Report: {CLIENT} — {DATE}` en el template markdown de referencia.

4. **Step 6a — Accionables** (Task 2): Agrega bloque completo con tabla 4 columnas, logica de asignacion de Dueno (Tech/QA/PM), plazos relativos P0/P1, exclusion explicita de P2/P3, y ejemplo con fila real.

5. **Report Structure template — Accionables** (Task 2): Reemplaza la seccion `## Recommendations` (columnas Issue|Priority|Owner|Action) por `## Accionables` (columnas Issue|Severidad|Dueno|Plazo) con nota explicita de scope P0/P1.

## Deviations from Plan

None — plan executed exactly as written.

## Success Criteria Verification

1. `ai-specs/.commands/report-qa.md` contiene instruccion de resumen ejecutivo en Step 6 para ambos formatos (.md y .html) — PASS
2. Template en `## Report Structure` muestra `{VEREDICTO} | Score {N}/100 | {X} issues criticos (P0: {N}, P1: {M})` bajo el titulo — PASS
3. Existe seccion `## Accionables` con tabla `Issue | Severidad | Dueno | Plazo` en Step 6 y en el template — PASS
4. La instruccion especifica explicitamente que solo P0 y P1 entran en Accionables — PASS
5. Los plazos relativos P0 → "0-1 dias (urgente)" y P1 → "2-5 dias (esta semana)" estan documentados — PASS
6. Los duenos posibles (Tech / QA / PM) estan documentados con criterio de asignacion — PASS

## Known Stubs

None.

## Threat Flags

None — cambios son solo texto Markdown en instrucciones de agente. No hay nuevas superficies de red, auth, ni endpoints.

## Self-Check: PASSED

- File exists: `/Users/lalojimenez/qa/ai-specs/.commands/report-qa.md` — FOUND
- Commit 0e8345d exists — FOUND
- Commit 67b4cbb exists — FOUND

---
phase: 2
plan: 02
subsystem: dashboard-ui
tags: [vanilla-js, dashboard, freshness-signals, run-selector, dash-01, dash-02]
requires: [css-classes-freshness, html-skeleton-run-nav]
provides: [freshness-rendering, historical-run-navigation]
affects: [public/index.html]
tech_stack_added: []
tech_stack_patterns: [default-parameter-backward-compat, inline-template-literal, promise-then-chain]
key_files_created: []
key_files_modified:
  - public/index.html
decisions:
  - "D-04: Dropdown range = allRuns.length > 10 ? slice(0, 14) : all."
  - "D-05: latestRun NO muta; el change listener solo re-renderiza el grid via updateClients(run)."
  - "D-06: Reemplazo completo del bloque lastTestedBadge (no extensión)."
  - "D-07: Dos elementos separados — .client-last-tested siempre + .freshness-badge solo cuando stale."
  - "D-08: referenceDate = run.date (nunca new Date() / todayStr)."
  - "D-09: Threshold exclusivo diffDays > 2 (0, 1, 2 sin badge; 3+ ámbar)."
  - "D-10: Orden DOM = freshness-badge → pass-rate-badge → expand-icon."
  - "D-11: last_tested === null → 'Sin datos de test', sin badge."
  - "D-13: allRuns vacío → .run-nav display:none."
metrics:
  tasks_completed: 2
  total_tasks: 2
  duration_minutes: 4
  files_changed: 1
  lines_added: 53
  lines_removed: 9
  commits: 3
completed: 2026-04-19
---

# Phase 2 Plan 02: updateClients Refactor + Run Selector Wiring Summary

Cableado JS sobre el esqueleto CSS+HTML que Wave 1 dejó en `public/index.html`: refactor de `updateClients()` con parámetro `run = latestRun` y clases CSS, nueva función `populateRunSelector()` con listener `change`, e invocación única desde `initDashboard`. Cierra DASH-01 y DASH-02.

## What Was Built

### Task 1 — Refactor `updateClients(run = latestRun)` (commit `046bc5c`)

`public/index.html` líneas 1862–1942. Cambios sobre el bloque anterior de 62 líneas:

- **Firma:** `function updateClients()` → `function updateClients(run = latestRun)`. Parámetro con default preserva backward compat con los 3 call-sites existentes (`initDashboard`, `enterEnv`, `backToLanding`), ninguno modificado.
- **Guard inicial:** early return con mensaje "Sin datos de clientes en este run" cuando `run` es null (Pitfall 3 defense).
- **Referencia de fecha:** `const referenceDate = run.date` — la variable `todayStr = new Date().toISOString().slice(0,10)` del código anterior se eliminó por completo del bloque (D-08).
- **Fecha siempre visible (DASH-02):** `<div class="client-last-tested">Testeado: ${c.last_tested}</div>` si hay dato, `<div class="client-last-tested">Sin datos de test</div>` si es null (D-07, D-11). Se renderiza debajo de `.client-name`, antes de `.client-url`.
- **Badge ámbar (DASH-01):** `<span class="freshness-badge freshness-stale">Hace N días</span>` solo cuando `c.last_tested` existe, `referenceDate` existe, y `diffDays > 2`. Date math: `Math.round((new Date(referenceDate) - new Date(c.last_tested)) / 86400000)` — ambos operandos son strings `"YYYY-MM-DD"` → parse UTC-midnight → delta exacto múltiplo de 86400000 (Pitfall 1 defense). Pluralización defensiva: `diffDays === 1 ? 'Hace 1 día' : \`Hace ${diffDays} días\``.
- **Orden DOM (D-10):** en el `div style="display:flex..."` del card header, ahora es `${freshnessBadge}` → `pass-rate-badge` → `expand-icon`. Pass rate sigue siendo visual primario; badge ámbar es secundario solo cuando aparece.
- **Identificador viejo eliminado:** `lastTestedBadge` (variable inline-style del código anterior) ya no existe en el archivo. El sufijo `${lastTestedBadge}` se eliminó del template literal de `.client-name`.
- **No muta `latestRun`:** ninguna asignación a `latestRun` dentro del body.

### Task 2 — `populateRunSelector()` + change listener + invocación (commit `d0d6bb2`)

`public/index.html` líneas 1945–1967 (nueva función, insertada entre `updateClients` y `toggleCard`) + 1496 (nueva línea en `initDashboard`).

- **Función `populateRunSelector()`:**
  - Early return + `nav.style.display = 'none'` cuando `allRuns.length === 0` (D-13).
  - `const runs = allRuns.length > 10 ? allRuns.slice(0, 14) : allRuns` — variable local, NO reasigna `allRuns` (Pitfall 2 defense, D-04).
  - `sel.innerHTML` con opciones `<option value="${r.date}" selected>${r.date} (más reciente)</option>` para `i === 0`, `<option value="${r.date}">${r.date}</option>` para el resto.
  - Listener `change`: `loadRunDetails(e.target.value).then(run => { if (run) updateClients(run); else console.warn(...) })`. El patrón `.then(run =>` es el requerido por el must_have key_link 2. NO escribe a `latestRun` (D-05).
- **Invocación:** una línea agregada dentro de `initDashboard()`, justo después de `updateClients();` y antes de `updateTrendChart();` (Pitfall 5 defense — el grid ya está renderizado con `latestRun` cuando el `<option selected>` se marca como la opción más reciente).
- **NO se llama desde `enterEnv` / `backToLanding` / `pollLive`** — Open Question 3 RESOLVED: cambiar ambiente mientras ves un run histórico regresa a `latestRun` por el default param; regresión UX menor aceptada como trade-off de scope.

## Files Modified

| File | Change |
|------|--------|
| `public/index.html` | Refactor de `updateClients` (+19 / -9 líneas netas) + nueva función `populateRunSelector` (+23 líneas) + 1 línea de invocación en `initDashboard`. Total: +53 líneas, -9 líneas. |

## Commits

| Hash | Message |
|------|---------|
| `046bc5c` | refactor(02-02): updateClients accepts run param and uses class-based freshness rendering |
| `d0d6bb2` | feat(02-02): add populateRunSelector with change listener for historical run navigation |

(El commit docs del plan — `8b667e9` — ya existía antes del worktree desde Wave 2 planning y no se duplica.)

## Verification — must_haves checklist

### Truths (7/7)

- [x] **Cada card renderiza `.client-last-tested` siempre** — template literal produce `<div class="client-last-tested">Testeado: ${c.last_tested}</div>` o `<div class="client-last-tested">Sin datos de test</div>` para todo cliente activo.
- [x] **Cuando `diffDays > 2` la card muestra `<span class="freshness-badge freshness-stale">`** con "Hace 1 día" o "Hace N días" — verificado en líneas 1890–1899.
- [x] **Cuando `diffDays <= 2` o `last_tested` null NO se renderiza `.freshness-badge`** — la variable `freshnessBadge` queda `''` y se interpola vacía.
- [x] **`diffDays` se calcula contra `run.date` nunca `new Date()`** — `const referenceDate = run.date`, luego `new Date(referenceDate) - new Date(c.last_tested)`. Verificado con `grep -c "new Date()" awk-slice-updateClients` → 0.
- [x] **`updateClients` acepta `run` opcional con default `latestRun`** — firma exacta `function updateClients(run = latestRun)`. Los 3 call-sites existentes (initDashboard línea 1495, enterEnv, backToLanding) no se modifican.
- [x] **`populateRunSelector` popula `#runSelector` con `slice(0,14)` cuando `length > 10`** — expresión `allRuns.length > 10 ? allRuns.slice(0, 14) : allRuns`. Si `allRuns` está vacío oculta `.run-nav` via `nav.style.display = 'none'`.
- [x] **Change listener llama `loadRunDetails(date).then(run => updateClients(run))`; `latestRun` NO se muta** — patrón exacto en líneas 1958–1965. `awk` slice de `populateRunSelector` body no contiene `latestRun = `.

### Artifacts (2/2)

- [x] `public/index.html` provee `updateClients` refactorizada + `populateRunSelector` + change listener — contiene `function updateClients(run = latestRun)` (línea 1862).
- [x] `public/index.html` provee `populateRunSelector` invocada una vez desde `initDashboard` después de `loadHistoryIndex` y después del primer `updateClients` — contiene `function populateRunSelector()` (línea 1945) e invocación en línea 1496.

### Key Links (3/3)

- [x] `updateClients(run)` → `run.date + c.last_tested` via `Math.round((new Date(run.date) - new Date(c.last_tested)) / 86400000)` — patrón `referenceDate = run.date` presente (línea 1869).
- [x] `#runSelector change event` → `loadRunDetails(date) -> updateClients(run)` via `addEventListener('change', ...)` — patrón `loadRunDetails\(e\.target\.value\)\.then\(run =>` presente (línea 1959).
- [x] `initDashboard()` → `populateRunSelector()` via llamada directa después de `loadHistoryIndex` y del primer `updateClients` — patrón `populateRunSelector()` presente (línea 1496).

### Success criteria (5/5)

- [x] **DASH-01** — badge ámbar con "Hace N días" cuando `diffDays > 2` vs `run.date`.
- [x] **DASH-02** — `.client-last-tested` con "Testeado: YYYY-MM-DD" o "Sin datos de test" siempre presente.
- [x] **Backward compatibility** — 3 call-sites sin modificar; default param los cubre.
- [x] **Reference date correcta** — `new Date()` eliminado del body de `updateClients` (grep-verified count=0).
- [x] **Run selector funcional** — populate + change listener + hide cuando vacío, sin mutar `latestRun`.

### Phase 2 Roadmap criterion 4

"Changing the selected run date via the dashboard history navigation re-evaluates freshness against the new reference date" — satisfecho: el listener llama `updateClients(selectedRun)` con el run cargado, y `referenceDate = run.date` garantiza que `diffDays` se recalcule contra la fecha del run histórico.

## Key Decisions Applied

- **D-04 (dropdown range):** `allRuns.length > 10 ? slice(0, 14) : all`. Funciona para cualquier length; para 11–14 runs es equivalente a "todos" (slice excede el array).
- **D-05 (no mutar latestRun):** variable local via parámetro `run`, sin reasignación global.
- **D-06 (reemplazo completo):** el bloque `lastTestedBadge` de 5 líneas fue eliminado; clases CSS reemplazan inline styles.
- **D-07 (dos elementos):** `.client-last-tested` siempre + `.freshness-badge` condicional.
- **D-08 (referenceDate):** `run.date`, nunca `new Date()`.
- **D-09 (threshold exclusivo):** `diffDays > 2`.
- **D-10 (orden DOM):** freshness-badge antes de pass-rate-badge.
- **D-11 (null last_tested):** "Sin datos de test", sin badge.
- **D-13 (allRuns vacío):** `.run-nav` se oculta con `display:none`.

## Deviations from Plan

Ninguna. El plan se ejecutó exactamente como estaba escrito:

- No se disparó Rule 1 (auto-fix de bug): el código anterior no estaba roto, solo usaba la referencia de fecha incorrecta por diseño previo.
- No se disparó Rule 2 (missing critical functionality): todas las defensas (null guard, Pitfall 1/2/3/5) ya estaban especificadas en el action block.
- No se disparó Rule 3 (blocking issues): no hubo errores de sintaxis, dependencias faltantes, o conflictos.
- No se disparó Rule 4 (architectural change): el refactor quedó confinado al edit surface previsto.

## Known Stubs / Follow-ups

Ninguno. Todo el contrato de DASH-01 y DASH-02 está satisfecho. Open Question 3 (change de ambiente mientras ves run histórico → regresa a latestRun) está documentada como regresión UX aceptada en el RESEARCH; no es un stub sino una decisión explícita.

## Threat Flags

Ninguno. Phase 2 no introduce nuevos vectores: el único input controlado por el usuario (`#runSelector.value`) proviene de `allRuns.map(r => r.date)` que a su vez viene del pipeline interno. No hay nuevos endpoints, auth paths, ni escrituras a trust boundaries.

## Self-Check: PASSED

- [x] `public/index.html` existe y contiene ambos cambios — verificado con Read y Grep.
- [x] Commit `046bc5c` existe — verificado con `git log --oneline`.
- [x] Commit `d0d6bb2` existe — verificado con `git log --oneline`.
- [x] JS válido — ambos bloques `<script>` parsean sin errores (`new Function(body)` exitoso).
- [x] No deleciones no intencionales — `git diff --diff-filter=D HEAD~2 HEAD` devuelve vacío.
- [x] Wave 1 artifacts siguen intactos — `.client-last-tested`, `.freshness-badge`, `.run-nav`, `#runSelector` siguen en sus líneas originales (573, 579, 593, 1265).

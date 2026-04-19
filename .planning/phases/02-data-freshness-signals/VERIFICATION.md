---
phase: 02-data-freshness-signals
verified: 2026-04-19T00:00:00Z
status: human_needed
score: 7/7 must-haves verified
overrides_applied: 0
human_verification:
  - test: "Abrir public/index.html en navegador (file:// o http-server) — tab B2B"
    expected: "Cada card de cliente muestra 'Testeado: YYYY-MM-DD' debajo del nombre. Clientes con last_tested > 2 días (ej. codelpa/surtiventas en run 2026-04-17) muestran badge ámbar '#fef3c7/#92400e' con texto 'Hace N días'. Clientes recientes (bastien, sonrie) no muestran badge."
    why_human: "Validación visual de color ámbar, legibilidad, orden DOM (freshness-badge → pass-rate-badge → expand-icon), y que no hay errores de layout CSS. Requiere render real de navegador."
  - test: "Cambiar el <select id='runSelector'> a un run histórico (ej. 2026-04-09)"
    expected: "El grid se re-renderiza con clientes de ese run. Los badges ámbar aparecen/desaparecen según la nueva referenceDate (con run 2026-04-09, un cliente con last_tested 2026-04-06 debe mostrar 'Hace 3 días'). Summary row, trend chart y failure groups NO cambian (siguen mostrando latestRun)."
    why_human: "Requiere interacción UI en vivo + verificación de que latestRun no muta y que summary/trend mantienen referencia original. Grep-only no puede validar el comportamiento dinámico del event listener."
  - test: "Consola del navegador durante la interacción"
    expected: "Sin errores JS (TypeError, ReferenceError). console.warn solo si loadRunDetails devuelve null para alguna fecha."
    why_human: "Errores runtime solo aparecen al ejecutar el código en un motor JS real."
---

# Phase 2: Data Freshness Signals — Verification Report

**Phase Goal:** Users can tell at a glance whether a client card reflects today's run or data seeded from previous days.
**Verified:** 2026-04-19
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Cada card renderiza `.client-last-tested` siempre (texto "Testeado: YYYY-MM-DD" o "Sin datos de test") | VERIFIED | `public/index.html:1907` emite `<div class="client-last-tested">${lastTestedText}</div>` incondicionalmente. `lastTestedText` se computa en 1886–1888 con ternario que cubre ambos casos (`c.last_tested` truthy → "Testeado: …"; falsy → "Sin datos de test"). |
| 2 | Cuando `diffDays > 2` vs run seleccionado, la card muestra `<span class="freshness-badge freshness-stale">` con "Hace N días" | VERIFIED | `public/index.html:1896–1899`: `if (diffDays > 2)` guarda la asignación; template exacto `<span class="freshness-badge freshness-stale">${label}</span>` con pluralización defensiva (`diffDays === 1 ? 'Hace 1 día' : 'Hace N días'`). |
| 3 | Cuando `diffDays <= 2` o `last_tested` es null, NO se renderiza `.freshness-badge` | VERIFIED | `freshnessBadge` inicializa en `''` (línea 1891). El bloque `if (c.last_tested && referenceDate)` + `if (diffDays > 2)` garantiza que permanece vacío en ambos casos. El string vacío se interpola sin producir nodo DOM. |
| 4 | La referencia para `diffDays` es `run.date`, nunca `new Date() / todayStr` | VERIFIED | `public/index.html:1870` `const referenceDate = run.date`. `grep -c "todayStr\|lastTestedBadge"` dentro de `updateClients` devuelve `0`. `new Date()` sin argumentos solo aparece en líneas 2607/2685 (completamente fuera de `updateClients`). |
| 5 | `updateClients(run = latestRun)` preserva los 3 call-sites originales | VERIFIED | Firma en 1863. Call-sites `updateClients()` sin args: línea 1440 (`enterEnv`), 1460 (`backToLanding`), 1495 (`initDashboard`), 2068 (`pollLive` post-run). El default param `run = latestRun` garantiza backward-compat. |
| 6 | `populateRunSelector` puebla `#runSelector` con `slice(0,14)` cuando `length > 10`; oculta `.run-nav` si `allRuns` vacío | VERIFIED | Función en 1945–1967. Línea 1952 `const runs = allRuns.length > 10 ? allRuns.slice(0, 14) : allRuns`. Líneas 1948–1951 guard: `if (!sel || allRuns.length === 0) { if (nav) nav.style.display = 'none'; return; }`. NO reasigna `allRuns` (Pitfall 2 evitado). |
| 7 | Cambiar `#runSelector` invoca `loadRunDetails(date) → updateClients(run)` sin mutar `latestRun` | VERIFIED | Listener en 1958–1966: `sel.addEventListener('change', (e) => { loadRunDetails(e.target.value).then(run => { if (run) updateClients(run); else console.warn(...) }); })`. `grep "latestRun =" public/index.html` confirma que solo hay 2 asignaciones (1488 initDashboard, 2066 pollLive) — ninguna dentro del body de `populateRunSelector` ni del change callback. |

**Score:** 7/7 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `public/index.html` | `updateClients` refactorizada con parámetro `run` + clases CSS | VERIFIED | Función en línea 1863 con firma exacta `function updateClients(run = latestRun)`. Template usa `.client-last-tested` y `.freshness-badge freshness-stale`. 62 líneas de implementación limpias. |
| `public/index.html` | `populateRunSelector` + invocación en `initDashboard` | VERIFIED | Función en línea 1945. Invocación en línea 1496 dentro de `initDashboard` (después de `updateClients()`, antes de `updateTrendChart()`). Secuencia correcta — grid ya renderizado antes de marcar `<option selected>`. |
| `public/index.html` (CSS) | `.client-last-tested`, `.freshness-badge`, `.freshness-stale`, `.run-nav`, `.run-nav-label`, `.run-select`, `.run-select:focus` | VERIFIED | Líneas 573–615: todas presentes con los valores exactos de UI-SPEC (11px/400/#9ca3af; #fef3c7/#92400e; border-color #667eea en focus). No hay duplicados de selectores existentes. |
| `public/index.html` (HTML) | Skeleton `<div class="run-nav">` con `<select id="runSelector">` vacío antes de `#clientsContainer` | VERIFIED | Líneas 1263–1266 dentro del card `🏪 Clientes B2B`, precede a `<div class="clients-grid" id="clientsContainer">` en 1267. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `updateClients(run)` | `run.date + c.last_tested` | `Math.round((new Date(run.date) - new Date(c.last_tested)) / 86400000)` | WIRED | Líneas 1893–1895. Operandos son strings ISO `YYYY-MM-DD` → UTC-midnight parse → delta múltiplo exacto de 86400000 (sin off-by-one por timezone). |
| `#runSelector change event` | `loadRunDetails(date) → updateClients(run)` | `addEventListener('change', ...)` con `.then(run => updateClients(run))` | WIRED | Líneas 1958–1966. Patrón regex exacto encontrado. `loadRunDetails` existe en línea 1475 como función async. |
| `initDashboard()` | `populateRunSelector()` | llamada directa después de `updateClients()` | WIRED | Línea 1496 — después de `updateClients();` (1495) y antes de `updateTrendChart();` (1497). Orden correcto garantiza que el grid ya está renderizado con `latestRun` cuando se marca `<option selected>`. |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|--------------|--------|--------------------|--------|
| `updateClients` → `.client-card` DOM | `run.clients` | `loadRunDetails(date)` → `fetch('history/{date}.json')` | YES — `public/history/2026-04-17.json` contiene 15+ clientes con `last_tested` poblado (`codelpa: 2026-04-07`, `surtiventas: 2026-04-07`, `bastien: 2026-04-16`, `sonrie: 2026-04-17`) | FLOWING |
| `populateRunSelector` → `<option>` list | `allRuns` | `loadHistoryIndex()` → `fetch('history/index.json')` | YES — `public/history/index.json` lista 9 runs reales con `date`/`total`/`passed`/`failed` | FLOWING |
| `initDashboard` → `latestRun` | `allRuns[0].date` | `loadRunDetails(allRuns[0].date)` | YES — 2026-04-17.json existe (run más reciente) | FLOWING |

### Behavioral Spot-Checks

Comprobaciones ejecutadas con Node.js contra los datos reales de `public/history/`:

| Behavior | Ref Date | last_tested | diffDays | Badge Esperado | Resultado | Status |
|----------|---------|-------------|----------|----------------|-----------|--------|
| Cliente testeado hoy | 2026-04-17 | 2026-04-17 | 0 | sin badge | sin badge | PASS |
| Cliente testeado ayer | 2026-04-17 | 2026-04-16 | 1 | sin badge (≤2) | sin badge | PASS |
| Cliente testeado hace 2 días | 2026-04-17 | 2026-04-15 | 2 | sin badge (boundary exclusiva) | sin badge | PASS |
| Cliente testeado hace 3 días | 2026-04-17 | 2026-04-14 | 3 | "Hace 3 días" | "Hace 3 días" | PASS |
| Codelpa en run actual | 2026-04-17 | 2026-04-07 | 10 | "Hace 10 días" | "Hace 10 días" | PASS |
| Reference histórica: run 2026-04-09 con last_tested 2026-04-07 | 2026-04-09 | 2026-04-07 | 2 | sin badge (NO debe basarse en hoy) | sin badge | PASS (SC 4) |
| Reference histórica con stale | 2026-04-09 | 2026-04-06 | 3 | "Hace 3 días" | "Hace 3 días" | PASS (SC 4) |

Todos los casos matemáticos confirman que `referenceDate = run.date` recalcula correctamente cuando cambia el run seleccionado — esto es exactamente lo que pide Success Criterion 4.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| DASH-01 | 02-01, 02-02 | Badge ámbar cuando `last_tested` >2 días respecto al run seleccionado (texto "Hace N días") | SATISFIED | Truths 2 + 4 + 7 verifican render condicional, referencia correcta, y recálculo dinámico. Lógica matemática validada con 7 casos. |
| DASH-02 | 02-01, 02-02 | `last_tested` siempre visible (no en hover) | SATISFIED | Truth 1 verifica render incondicional. El elemento `.client-last-tested` se emite dentro del `.client-card-header` visible (no dentro de `.client-card-body` que está collapsed por default). |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `public/index.html` | 1328, 2487, 2490, 2494 | `placeholder="…"` en `<input>` / `<textarea>` | Info | Atributos HTML legítimos de forms — NO son stubs. Descartados. |
| `public/index.html` | 2607, 2685 | `new Date().toISOString()` | Info | Fuera del scope de Phase 2 (están en funciones de QA manual y download de reporte). No afectan `updateClients`. |

No hay TODO/FIXME/XXX/HACK, ni `return null`/`return []` sin justificación, ni console.log stubs dentro del código de Phase 2. `lastTestedBadge` y `todayStr` (identificadores obsoletos del pre-refactor) fueron completamente eliminados (`grep -c lastTestedBadge` → 0).

### Success Criteria from ROADMAP

| # | Criterio | Status | Evidencia |
|---|----------|--------|-----------|
| 1 | Todas las cards del B2B tab muestran `last_tested` explícito (siempre visible, no hover) | VERIFIED | `.client-last-tested` se renderiza dentro de `.client-card-header` — siempre visible. |
| 2 | Cuando `last_tested` >2 días vs run seleccionado, aparece badge ámbar "Hace N días" | VERIFIED | `diffDays > 2` exclusivo; CSS `#fef3c7` background, `#92400e` color; label pluralizado. |
| 3 | Cards dentro de 2 días renderizan con color normal — no false positives | VERIFIED | Behavioral spot-checks confirman: diffDays ∈ {0, 1, 2} → `freshnessBadge = ''` → no span emitido. |
| 4 | Cambiar el run seleccionado re-evalúa freshness contra la nueva fecha | VERIFIED (código) + HUMAN (interacción UI) | El listener `change` llama `updateClients(run)` donde `referenceDate = run.date`. Matemáticamente correcto en los 7 casos. La interacción UI real requiere verificación humana. |

### Human Verification Required

3 items requieren validación visual/interactiva (ver frontmatter `human_verification`):

1. **Render visual en navegador** — confirmar color ámbar, layout, orden DOM de badges
2. **Interacción con runSelector** — cambiar a run histórico y confirmar re-render + que summary/trend no mutan
3. **Consola sin errores** — durante carga inicial y cambios de selector

### Gaps Summary

**No gaps.** Los 2 planes ejecutaron al 100%:

- CSS foundations (plan 02-01): 6 clases agregadas, 0 modificadas, HTML skeleton insertado correctamente.
- JS wiring (plan 02-02): `updateClients` refactorizada con firma backward-compat, `populateRunSelector` funcional con guard de `allRuns` vacío, listener registrado sin mutar `latestRun`, invocación desde `initDashboard` en el orden correcto.

Los 7 truths del `must_haves.truths`, los 2 artifacts, y los 3 key_links están verificados con evidencia directa del código. Los 4 success criteria del ROADMAP están cubiertos:

- SC 1 (fecha siempre visible) — código lo garantiza incondicionalmente.
- SC 2 (badge >2 días) — lógica matemática confirmada con datos reales.
- SC 3 (no false positives dentro de 2 días) — boundary exclusivo `diffDays > 2` probado.
- SC 4 (cambiar run re-evalúa freshness) — `referenceDate = run.date` propaga correctamente; behavioral check con run histórico PASS.

El único motivo de status `human_needed` (no `passed`) es que SC 4 y el render visual (ámbar, orden DOM, ausencia de errores runtime) no se pueden validar 100% sin abrir el dashboard en un navegador real. La lógica subyacente está correcta — solo falta la confirmación visual.

---

_Verified: 2026-04-19_
_Verifier: Claude (gsd-verifier)_

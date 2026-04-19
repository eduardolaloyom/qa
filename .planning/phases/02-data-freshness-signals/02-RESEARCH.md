# Phase 2: Data Freshness Signals - Research

**Researched:** 2026-04-19
**Domain:** Single-file vanilla JS dashboard (static HTML in GitHub Pages) — DOM rendering, date math, localized copy
**Confidence:** HIGH

## Summary

Phase 2 agrega señales de frescura a las cards de clientes en el tab B2B del dashboard estático `public/index.html`. El trabajo se concentra en una sola función (`updateClients`), una sola variable global (introducir `selectedRun`), y un nuevo selector `<select>` poblado desde `allRuns`. No hay dependencias nuevas, no hay librerías, no hay build step — todo es vanilla JS y CSS inline en el `<style>` existente.

El riesgo principal es de **corrección de date math**, no de arquitectura: el código actual en líneas 1831-1835 compara contra `todayStr` (fecha del sistema) y debe compararse contra `selectedRun.date` (fecha del run elegido). La función `updateClients()` debe volverse idempotente respecto al run: recibe `run = latestRun` como parámetro con default para mantener compatibilidad con los 3 call-sites existentes (`initDashboard`, `enterEnv`, `backToLanding`).

El `loadRunDetails(date)` ya existe y se reutiliza sin cambios; `allRuns` ya está cargado globalmente. El cambio es puramente aditivo — ningún pipeline ni función existente se modifica en su contrato público.

**Primary recommendation:** Implementar en 3 commits lógicos: (1) CSS nuevo + HTML del `.run-nav` antes de `clientsContainer`, (2) refactor de `updateClients(run = latestRun)` con las 2 nuevas clases de elementos + reemplazo completo de `lastTestedBadge`, (3) listener `change` del `#runSelector` que llama `loadRunDetails(date) → updateClients(selectedRun)`.

## User Constraints (from CONTEXT.md)

### Locked Decisions

**Run Selector:**
- D-01: Widget = `<select>` HTML nativo (sin prev/next).
- D-02: Ubicación = inmediatamente antes del `clientsContainer` div, dentro de la sección B2B.
- D-03: Scope de actualización = solo grid de clientes B2B. Summary row, trend chart y failure groups siguen con `latestRun` global.
- D-04: Rango de runs en dropdown = si `allRuns.length <= 10`, mostrar todos; si > 10, últimos 14. Primer option marca "(más reciente)".
- D-05: La variable `latestRun` global NO se modifica — usar variable local/parámetro `selectedRun`.

**Freshness Badge:**
- D-06: Reemplazar completamente el código de `lastTestedBadge` (líneas 1831-1835). Reescribir con clases CSS.
- D-07: Dos elementos visuales separados por cliente:
  - `.client-last-tested` — siempre visible. Texto: `"Testeado: YYYY-MM-DD"` o `"Sin datos de test"`. Color `#9ca3af`, 11px.
  - `.freshness-badge` — badge ámbar visible SOLO cuando `diffDays > 2`. Texto: `"Hace 1 día"` o `"Hace N días"`. Background `#fef3c7`, texto `#92400e`.
- D-08: Reference date para `diffDays` = `selectedRun.date`, NO `new Date()` / `todayStr`.
- D-09: Threshold = `diffDays > 2` exclusivo. 0, 1, 2 días → fresco. 3+ → ámbar.
- D-10: Jerarquía: pass-rate primario, `.freshness-badge` secundario (solo cuando stale), `.client-last-tested` terciario.

**Empty State y Edge Cases:**
- D-11: `last_tested === null` → "Sin datos de test" gris, sin badge ámbar.
- D-12: Clientes con `last_tested === null` aparecen normalmente, no se filtran.
- D-13: Si `allRuns` vacío, el dropdown no se renderiza. Grid mantiene fallback actual.

### Claude's Discretion

- Estructura interna de `selectedRun` vs `latestRun` — cómo pasar la referencia sin romper otras funciones.
- Orden del HTML del `.client-last-tested` dentro del `.client-card-header`.
- Nombres exactos de clases CSS para el run-nav (`.run-nav`, `.run-select`, `.run-nav-label`) — UI-SPEC ya tiene el CSS base.

### Deferred Ideas (OUT OF SCOPE)

- Sincronizar run selector con trend chart (afectaría todo el B2B tab — fuera de Phase 2).
- Flechas prev/next además del dropdown (descartado por usuario).
- Badge ámbar en APP tab o Cowork section (pertenece a Phase 3).

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DASH-01 | Cards muestran badge ámbar cuando `last_tested` tiene más de 2 días respecto al run seleccionado (texto "Hace N días") | Date math con `selectedRun.date`, CSS `.freshness-badge.freshness-stale`, template literal en `updateClients()`. Patrón existente de `mq-badge.ux` (mismo par de colores `#fef3c7`/`#92400e`) valida la convención. |
| DASH-02 | Cards muestran fecha de último test explícita (`last_tested`) siempre visible | Template literal en `updateClients()` inyecta `<div class="client-last-tested">Testeado: ${c.last_tested}</div>` debajo de `.client-name`. CSS `.client-last-tested` define tipografía 11px/400/`#9ca3af`. Fallback "Sin datos de test" cuando `last_tested` es null/undefined. |

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Renderizar cards con fecha y badge | Browser / Client (vanilla JS) | — | Dashboard es HTML estático servido por GitHub Pages. Todo el render es client-side. |
| Date math `diffDays` | Browser / Client | — | `new Date(a) - new Date(b)` dividido por `86400000`. No hay backend. |
| Cargar run específico | Browser / Client (fetch) | CDN / Static (`public/history/*.json`) | Archivos JSON pre-generados por `publish-results.py` (no en este phase); dashboard fetcha con cache-buster. |
| Persistir selección de run | None | — | D-03 implica que no se persiste (selector reset al reload). Fuera de scope. |
| Generar `last_tested` per cliente | None (upstream) | Python — `tools/publish-results.py` | El campo ya existe en `history/{date}.json`. Dashboard solo consume. |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Native HTML `<select>` | — | Run selector dropdown | D-01 lo fija explícitamente. Zero deps, soporte universal, accesible por default. [VERIFIED: D-01 de CONTEXT.md] |
| Template literals JS | ES2015+ | Generar HTML de cards inline | Patrón establecido en el resto del archivo [VERIFIED: líneas 1473-1478, 1826-1874 de index.html]. |
| `Date` nativo + aritmética ms | — | Calcular `diffDays` | Patrón existente en el código actual [VERIFIED: línea 1833 de index.html `new Date(todayStr) - new Date(c.last_tested)) / 86400000`]. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `fetch()` con `?t=${Date.now()}` | — | Cargar `history/{date}.json` | Al cambiar selector, cache-buster evita que GitHub Pages sirva caché. Patrón existente [VERIFIED: líneas 1421, 1429 de index.html]. |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Vanilla `<select>` | Custom dropdown con `<div>` + JS | Sería más "diseñado" pero rompe accesibilidad nativa y viola D-01. Descartar. |
| `Intl.DateTimeFormat` para formateo | — | No necesario: D-07 fija "Testeado: YYYY-MM-DD" (ISO sin localización). |
| Librería de date math (date-fns, dayjs) | — | Overkill: una operación. Viola "no build step, no bundler" de PROJECT.md. |
| Observable/reactive state | — | Fuera del paradigma del archivo. El dashboard usa mutación directa + re-render explícito. |

**Installation:** N/A — no new packages. Only vanilla edits to `public/index.html`.

**Version verification:** No aplica — no hay dependencies nuevas.

## Project Constraints (from CLAUDE.md)

- **Idioma UI:** Spanish (Chile). Todos los strings user-facing en español: "Testeado:", "Sin datos de test", "Hace 1 día", "Hace N días", "Run:", "(más reciente)". Código y commits en inglés. [CITED: ~/.claude/CLAUDE.md]
- **Commits:** Prefijos convencionales (`feat`, `fix`, `docs`, `refactor`, `chore`). Mensaje corto en inglés. Push directo a `main` sin PRs salvo que se pida. [CITED: ~/.claude/CLAUDE.md]
- **Ejecución directa:** commit + push en un solo flujo cuando se pida subir cambios. [CITED: ~/.claude/CLAUDE.md]
- **AI Specs framework:** El proyecto QA usa ai-specs/.agents y ai-specs/.commands. El dashboard en sí NO depende de ese framework — es solo consumidor de archivos JSON. Esta fase no modifica agents ni commands. [CITED: /Users/lalojimenez/qa/CLAUDE.md]
- **No editar `tests/e2e/fixtures/clients.ts`:** AUTO-GENERADO por `sync-clients.py`. Phase 2 no toca fixtures — solo modifica `public/index.html`. [CITED: /Users/lalojimenez/qa/CLAUDE.md]
- **Credenciales en `.env`:** N/A para esta fase (no se tocan credenciales).

## Project Constraints (from PROJECT.md)

- **Sin build step:** Dashboard es HTML estático. Mejoras vanilla JS. [CITED: .planning/PROJECT.md]
- **Sin servidor:** Todo estático en GitHub Pages. Datos vienen de archivos JSON commiteados. [CITED: .planning/PROJECT.md]
- **Backward compatibility:** Mejoras son aditivas, no breaking. Los 3 pipelines siguen funcionando igual. [CITED: .planning/PROJECT.md]
- **Un solo operador QA:** Eduardo. Reducir carga cognitiva, no agregar pasos manuales. [CITED: .planning/PROJECT.md]

## Architecture Patterns

### System Architecture Diagram

```
User selects a date in <select id="runSelector">
         │
         ▼
change event listener
         │
         ▼
loadRunDetails(selectedDate)   ───── fetch(`history/${date}.json?t=...`)
         │                                   │
         ▼                                   ▼
selectedRun object           CDN/Static `public/history/{date}.json`
         │                  (pre-generated by publish-results.py)
         ▼
updateClients(selectedRun)
         │
         ├── for each client in selectedRun.clients:
         │     │
         │     ├── compute diffDays = selectedRun.date − c.last_tested
         │     ├── render .client-last-tested (always)
         │     └── render .freshness-badge (only if diffDays > 2)
         │
         ▼
container#clientsContainer.innerHTML = <cards HTML>
         │
         ▼
DOM updated — user sees freshness signals

(Parallel unchanged path)
initDashboard() → loadHistoryIndex() → allRuns populated → populate <select> options
                → loadRunDetails(allRuns[0].date) → latestRun populated
                → updateSummary(), updateFailureGroups(), updateTrendChart() use latestRun (NOT selectedRun)
```

### Recommended Project Structure (existing, no additions)

```
public/
├── index.html         # ← the only file modified in this phase
├── history/
│   ├── index.json     # ← drives <select> options (allRuns)
│   └── {date}.json    # ← fetched on selector change (selectedRun)
├── reports/           # unchanged
├── app-reports/       # unchanged
└── qa-reports/        # unchanged
```

### Pattern 1: Backward-compatible parameter default

**What:** Agregar parámetro opcional con default para no romper call-sites existentes.
**When to use:** Cuando una función es llamada desde múltiples lugares y queremos cambiar el comportamiento interno sin tocar los call-sites.
**Example:**
```javascript
// Before
function updateClients() {
    const clients = latestRun.clients || {};
    ...
}

// After — backward compatible: all existing calls (initDashboard, enterEnv, backToLanding)
// keep working. Only the new #runSelector change handler passes a different run.
function updateClients(run = latestRun) {
    const clients = (run && run.clients) || {};
    const referenceDate = run ? run.date : null;
    ...
}
```

### Pattern 2: Inline template literal rendering

**What:** Generar HTML completo como string con interpolación de variables.
**When to use:** Es el patrón establecido en `public/index.html` (ver `updateSummary`, `updateClients`, `updateSuitesTable`).
**Example:**
```javascript
// Source: public/index.html lines 1837-1874 (current pattern)
container.innerHTML = activeClients.map(([key, c]) => {
    const lastTestedText = c.last_tested
        ? `Testeado: ${c.last_tested}`
        : 'Sin datos de test';

    let freshnessBadge = '';
    if (c.last_tested && referenceDate) {
        const diffDays = Math.round(
            (new Date(referenceDate) - new Date(c.last_tested)) / 86400000
        );
        if (diffDays > 2) {
            const label = diffDays === 1 ? 'Hace 1 día' : `Hace ${diffDays} días`;
            freshnessBadge = `<span class="freshness-badge freshness-stale">${label}</span>`;
        }
    }

    return `
    <div class="client-card">
      <div class="client-card-header" onclick="toggleCard(this)">
        <div>
          <div class="client-name">🏪 ${c.name}</div>
          <div class="client-last-tested">${lastTestedText}</div>
          <div class="client-url">${c.url}</div>
        </div>
        <div style="display:flex;align-items:center;gap:10px;">
          ${freshnessBadge}
          <span class="pass-rate-badge" style="color:${rateColor}">${passRate}%</span>
          <span class="expand-icon">▼</span>
        </div>
      </div>
      ...
    </div>`;
}).join('');
```

### Pattern 3: Populate `<select>` from data array

**What:** Generar options desde `allRuns` en `initDashboard()` después de `loadHistoryIndex()`.
**Example:**
```javascript
function populateRunSelector() {
    if (!allRuns.length) return;   // D-13: no renderizar si vacío
    const runs = allRuns.length > 10 ? allRuns.slice(0, 14) : allRuns;
    const sel = document.getElementById('runSelector');
    if (!sel) return;
    sel.innerHTML = runs.map((r, i) => {
        const suffix = i === 0 ? ' (más reciente)' : '';
        return `<option value="${r.date}">${r.date}${suffix}</option>`;
    }).join('');
    sel.addEventListener('change', async (e) => {
        const selectedRun = await loadRunDetails(e.target.value);
        if (selectedRun) updateClients(selectedRun);
    });
}
```

### Anti-Patterns to Avoid

- **Mutar `latestRun`** cuando cambia el selector. Viola D-05 y rompe summary row, trend chart, failure groups (que dependen de `latestRun`).
- **Comparar contra `new Date()`** o `todayStr` en `updateClients()`. Viola D-08. Debe ser `selectedRun.date`.
- **Inline styles en templates** cuando ya existen clases CSS (`style="..."` para el badge). Viola la decisión D-06 de "reescribir limpiamente con clases CSS". UI-SPEC ya define el CSS.
- **Filtrar clientes con `last_tested === null`**. Viola D-12 — deben aparecer con "Sin datos de test".
- **Re-renderizar todo el B2B tab** al cambiar el selector. Viola D-03 — solo `updateClients()` debe correr.
- **Persistir selección en localStorage.** Fuera de scope; D-03 solo menciona re-render del grid, no persistencia.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Dropdown custom | `<div>` + JS + absolute positioning | `<select>` nativo | D-01 lo fija. Accesibilidad, keyboard nav, focus ring — todo gratis. |
| Date math | `Date.parse` + manual year/month/day wrangling | `(Date - Date) / 86400000` | Patrón ya existe en el mismo archivo (línea 1833). `last_tested` y `selectedRun.date` vienen como `"YYYY-MM-DD"` — new `Date("YYYY-MM-DD")` los parsea como UTC midnight, el delta en ms → días es exacto para fechas calendario. |
| Formateo de fecha | `Intl.DateTimeFormat` | Usar el string `"YYYY-MM-DD"` directo | D-07 fija formato ISO. No hay localización. |
| Pluralización | Librería i18n | `diffDays === 1 ? 'Hace 1 día' : 'Hace N días'` | Dos casos solamente. Una librería sería absurdo. |
| Reactive re-render | Observer pattern, pub/sub | Llamada directa a `updateClients(selectedRun)` en el listener | Solo hay un consumidor. Arquitectura de re-render directo es el patrón del archivo. |
| Cache-busting | Service worker, manual cache strategy | `?t=${Date.now()}` en la URL | Patrón existente (líneas 1421, 1429). GitHub Pages tiene TTL de ~10 min; el cache-buster evita stale reads. |

**Key insight:** Este phase es "pegar HTML/CSS + un listener + corregir una comparación de fecha". Cualquier abstracción adicional (state manager, router, framework component) violaría PROJECT.md ("sin build step, vanilla JS").

## Common Pitfalls

### Pitfall 1: Off-by-one en date math por timezone

**What goes wrong:** `new Date("2026-04-17")` parsea como UTC midnight. `new Date("2026-04-17") - new Date("2026-04-15")` da exactamente 2*86400000 ms. Pero si el código mezcla `new Date()` (local time con hora actual) con `new Date("YYYY-MM-DD")` (UTC midnight), el delta puede estar off por unas horas y `Math.round` puede producir ±1 día.

**Why it happens:** El código actual (línea 1833) hace `new Date(todayStr) - new Date(c.last_tested)` donde ambos son strings "YYYY-MM-DD" → ambos parsean a UTC midnight → cancelan. Pero si alguien pasa `new Date()` directamente, introduce la hora local y el delta deja de ser múltiplo exacto de 86400000.

**How to avoid:** Siempre comparar strings `"YYYY-MM-DD"` (la forma en que viene `last_tested` y `selectedRun.date` del JSON). Nunca mezclar `new Date()` (local now) con `new Date("YYYY-MM-DD")` (UTC midnight). `Math.round` después de dividir por 86400000 es la defensa final, pero no la compense.

**Warning signs:** Un cliente con `last_tested = "2026-04-17"` en un run de `2026-04-17` muestra "Hace 1 día". Eso indica mezcla de local/UTC.

### Pitfall 2: `allRuns` mutación accidental

**What goes wrong:** `allRuns.slice(0, 14)` devuelve nuevo array — OK. Pero `allRuns = allRuns.slice(0, 14)` **mutaría la variable global** y rompería el trend chart (línea 1886), que asume `allRuns` tiene todos los runs.

**Why it happens:** Es tentador limitar "una sola vez" la lista global.

**How to avoid:** Usar una variable local en `populateRunSelector()`: `const runs = allRuns.length > 10 ? allRuns.slice(0, 14) : allRuns;`. Jamás reasignar `allRuns`.

**Warning signs:** Trend chart muestra solo 14 puntos después del cambio.

### Pitfall 3: `selectedRun` shape mismatch

**What goes wrong:** `loadRunDetails(date)` devuelve el objeto completo de `history/{date}.json`, que tiene el shape:
```json
{ "date": "...", "timestamp": "...", "total": ..., "clients": { ... }, "suites": [...] }
```
Si `updateClients(run)` asume que `run` tiene `.clients`, pasar `null` (cuando fetch falla con 404) hará crashear el render.

**Why it happens:** `loadRunDetails` retorna `null` si `!r.ok` (línea 1430). El listener debe chequear.

**How to avoid:** En el listener del selector: `if (selectedRun) updateClients(selectedRun); else console.warn('run not found')`. Además, `updateClients` debe tolerar `run = null` devolver al comportamiento de "no data".

**Warning signs:** TypeError: Cannot read properties of null (reading 'clients') en consola al cambiar el selector.

### Pitfall 4: Filtro de `environment` interactúa con `selectedRun`

**What goes wrong:** Líneas 1820-1821 filtran por `selectedEnv` (staging/production) usando `getClientEnv(c.url, c.name)`. Al cambiar el run, algunos clientes podrían no existir en runs antiguos → el filtro sigue funcionando pero el grid puede quedar vacío.

**Why it happens:** El `selectedEnv` es global; `selectedRun.clients` es local al run.

**How to avoid:** No quitar el filtro. Solo verificar que cuando `activeClients.length === 0` se muestre el mensaje "Sin datos de clientes en este run" (comportamiento actual, línea 1823 — se mantiene).

**Warning signs:** Usuario selecciona un run viejo y ve grid vacío sin explicación.

### Pitfall 5: Dropdown desincronizado con el run actual

**What goes wrong:** Al inicializar, `latestRun = allRuns[0]` y el selector muestra `allRuns[0]` seleccionado. OK. Pero si `initDashboard()` popula el selector **después** de `updateClients()`, el selector puede no reflejar la selección actual.

**How to avoid:** Poblar el selector inmediatamente después de `loadHistoryIndex()` (línea 1436), antes de llamar `updateClients()`. El primer `<option>` con `selected` implícito (es el primero) refleja el run más reciente.

**Warning signs:** Selector muestra opción vacía o una fecha incorrecta al cargar.

### Pitfall 6: Onclick inline de `toggleCard` pierde contexto

**What goes wrong:** El card header usa `onclick="toggleCard(this)"` (línea 1839). Si agregamos un `<span class="freshness-badge">` dentro del header, clicks sobre el badge también expanden/colapsan la card.

**How to avoid:** Es comportamiento aceptable (el badge no tiene su propio interactivo) y consistente con `.pass-rate-badge` que también expande. No hacer nada especial.

**Warning signs:** Solo aparece si el badge se vuelve interactivo en algún phase futuro.

## Runtime State Inventory

> Phase 2 es un cambio aditivo de UI sobre un archivo único. No es rename/refactor/migration. Sección omitida según instrucciones.

## Code Examples

### Leer `selectedRun` desde el dropdown

```javascript
// Source: patrón existente `loadRunDetails` en public/index.html line 1428
document.getElementById('runSelector').addEventListener('change', async (e) => {
    const run = await loadRunDetails(e.target.value);
    if (run) updateClients(run);
});
```

### CSS completo (a agregar al `<style>` existente, después de `.client-url` ~ línea 572)

```css
/* Source: UI-SPEC.md líneas 112-118, 144-157, 188-213 */
.client-last-tested {
    font-size: 11px;
    color: #9ca3af;
    font-weight: 400;
    margin-top: 4px;
}
.freshness-badge {
    display: inline-flex;
    align-items: center;
    padding: 4px 8px;
    border-radius: 9999px;
    font-size: 11px;
    font-weight: 700;
    white-space: nowrap;
    flex-shrink: 0;
}
.freshness-badge.freshness-stale {
    background: #fef3c7;
    color: #92400e;
}
.run-nav {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
}
.run-nav-label {
    font-size: 12px;
    color: #6b7280;
    font-weight: 400;
    white-space: nowrap;
}
.run-select {
    padding: 4px 8px;
    border: 1.5px solid #d1d5db;
    border-radius: 8px;
    font-size: 12px;
    font-family: inherit;
    color: #374151;
    background: white;
    cursor: pointer;
}
.run-select:focus { outline: none; border-color: #667eea; }
```

### HTML del run-nav (a insertar antes de `clientsContainer`, dentro del card B2B)

```html
<!-- Source: UI-SPEC.md line 178-186; insertar entre card-title y clientsContainer en public/index.html line ~1219 -->
<div class="run-nav">
    <span class="run-nav-label">Run:</span>
    <select id="runSelector" class="run-select"></select>
</div>
<div class="clients-grid" id="clientsContainer">
    <div class="loading">Cargando clientes...</div>
</div>
```

### Date math exacto para `diffDays`

```javascript
// Source: pattern from existing code public/index.html line 1833 (extraido)
// Both operands are "YYYY-MM-DD" strings → both parse as UTC midnight → delta in ms is
// exact multiple of 86400000 → Math.round is a safety net against FP rounding.
const diffDays = Math.round(
    (new Date(referenceDate) - new Date(c.last_tested)) / 86400000
);
```

### Full replacement snippet for `updateClients` block (what to write)

```javascript
function updateClients(run = latestRun) {
    if (!run) {
        document.getElementById('clientsContainer').innerHTML =
            '<div class="loading" style="color:#9ca3af;font-size:0.9em;">Sin datos de clientes en este run</div>';
        return;
    }
    const clients = run.clients || {};
    const referenceDate = run.date;          // D-08
    const container = document.getElementById('clientsContainer');

    const activeClients = Object.entries(clients)
        .filter(([, c]) => c.tests > 0)
        .filter(([, c]) => !selectedEnv || getClientEnv(c.url, c.name) === selectedEnv);

    if (activeClients.length === 0) {
        container.innerHTML = '<div class="loading" style="color:#9ca3af;font-size:0.9em;">Sin datos de clientes en este run</div>';
        return;
    }

    container.innerHTML = activeClients.map(([key, c]) => {
        const failed = c.failed ?? (c.tests - c.passed);
        const passRate = Math.round(c.passed / c.tests * 100);
        const rateColor = passRate === 100 ? '#10b981' : passRate >= 70 ? '#f59e0b' : '#ef4444';

        // DASH-02: fecha siempre visible
        const lastTestedText = c.last_tested
            ? `Testeado: ${c.last_tested}`
            : 'Sin datos de test';

        // DASH-01: badge ámbar solo si diffDays > 2
        let freshnessBadge = '';
        if (c.last_tested && referenceDate) {
            const diffDays = Math.round(
                (new Date(referenceDate) - new Date(c.last_tested)) / 86400000
            );
            if (diffDays > 2) {
                const label = diffDays === 1 ? 'Hace 1 día' : `Hace ${diffDays} días`;
                freshnessBadge = `<span class="freshness-badge freshness-stale">${label}</span>`;
            }
        }

        return `
        <div class="client-card">
            <div class="client-card-header" onclick="toggleCard(this)">
                <div>
                    <div class="client-name">🏪 ${c.name}</div>
                    <div class="client-last-tested">${lastTestedText}</div>
                    <div class="client-url">${c.url}</div>
                </div>
                <div style="display:flex;align-items:center;gap:10px;">
                    ${freshnessBadge}
                    <span class="pass-rate-badge" style="color:${rateColor}">${passRate}%</span>
                    <span class="expand-icon">▼</span>
                </div>
            </div>
            <div class="client-card-body">
                <div class="client-stats">
                    <div class="client-stat">
                        <div class="client-stat-val">${c.tests}</div>
                        <div class="client-stat-lbl">Total</div>
                    </div>
                    <div class="client-stat">
                        <div class="client-stat-val" style="color:#10b981">${c.passed}</div>
                        <div class="client-stat-lbl">Passed</div>
                    </div>
                    <div class="client-stat">
                        <div class="client-stat-val" style="color:${failed > 0 ? '#ef4444' : '#10b981'}">${failed}</div>
                        <div class="client-stat-lbl">Failed</div>
                    </div>
                </div>
                <div class="client-progress">
                    <div class="client-progress-label">
                        <span>Pass rate</span><span style="font-weight:700;color:${rateColor}">${passRate}%</span>
                    </div>
                    <div class="progress-bar" style="height:8px">
                        <div class="progress-bar-fill ${passRate < 70 ? 'red' : ''}" style="width:${passRate}%"></div>
                    </div>
                </div>
                <a href="${c.reportUrl}" class="report-link" target="_blank">→ Ver reporte Playwright</a>
            </div>
        </div>`;
    }).join('');
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Inline style en badge (`style="font-size:0.72em;color:#9ca3af;..."`) | Clase CSS `.client-last-tested` + `.freshness-badge.freshness-stale` | Phase 2 | Reusabilidad, separación de concerns, preparación para Phase 3 (badges en vista unificada) |
| Fecha en paréntesis dentro del `.client-name` | Línea separada `.client-last-tested` debajo del nombre | Phase 2 | Información de frescura prominente y escaneable |
| Comparación contra `todayStr` (línea 1830) | Comparación contra `selectedRun.date` (D-08) | Phase 2 | Frescura es relativa al run seleccionado, no al día del sistema — permite auditar runs históricos |
| Texto "hace N días" (lowercase, sin ámbar) | "Hace N días" (capitalized) sobre badge ámbar `#fef3c7`/`#92400e` | Phase 2 | Señal visual más fuerte, consistente con `.mq-badge.ux` (color amber pattern existente) |

**Deprecated/outdated:**
- Línea 1830 (`const todayStr = new Date().toISOString().slice(0, 10);`) — ya no se usa en `updateClients` después del refactor (referencia pasa a ser `run.date`).
- Líneas 1831-1835 completas (`lastTestedBadge` block) — se eliminan por completo (D-06).

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | GitHub Pages tarda ~10 min en invalidar cache, por eso el `?t=${Date.now()}` es suficiente | Architecture Patterns | Bajo — si cache es más agresivo, el cache-buster sigue funcionando (query param siempre único). |
| A2 | `last_tested` siempre viene como `"YYYY-MM-DD"` string, nunca como timestamp ISO completo con hora | Pitfalls, Code Examples | Bajo — muestras de `history/2026-04-17.json` confirman formato ISO-date puro. Si algún día cambia, el `Math.round` y el truncado a UTC midnight por `new Date(str)` siguen siendo correctos. |
| A3 | El dashboard no persiste `selectedRun` al reload | Responsibility Map | Nulo — D-03 no menciona persistencia; es explícitamente un re-render local al grid. |
| A4 | `allRuns` viene ordenado descendente por fecha desde `history/index.json` | Code Examples (`populateRunSelector`) | Medio — verificado en `public/history/index.json`: `2026-04-17, 2026-04-16, 2026-04-15, ...` descendente. Si `publish-results.py` alguna vez cambia el orden, `allRuns[0]` dejaría de ser "el más reciente". Consumidores downstream (plan, ejecutor) deben asumir este invariante o validarlo. |

**Si esta tabla tiene items:** Se sugiere al planner agregar una tarea de verificación del shape de datos antes del desarrollo, o al ejecutor incluir una precaución defensiva.

## Open Questions (RESOLVED)

1. **¿Cuál es el threshold para el slice del dropdown cuando `allRuns.length` está entre 11 y 13?**
   - Qué sabemos: D-04 dice "si `allRuns.length <= 10`, mostrar todos; si > 10, limitar a los últimos 14 runs".
   - Qué es ambiguo: Con 11 runs, ¿mostramos 11 o 14? La redacción sugiere que si es > 10 aplicamos el límite de 14 — pero 11 ≤ 14 entonces es equivalente a "todos". Asumimos: si > 10, `slice(0, 14)` (que devuelve todos los existentes si son menos de 14).
   - **RESOLVED:** Implementar como `allRuns.length > 10 ? allRuns.slice(0, 14) : allRuns`. Esto funciona correctamente para 11, 12, 13, 14, 15+ runs. Plan 02-02 Task 2 adopta esta fórmula textualmente.

2. **¿El `<select>` debe re-poblarse cuando el dashboard hace live polling (pollLive)?**
   - Qué sabemos: `pollLive()` se llama en `initDashboard` (línea 1454) y actualiza el estado live de un run en curso.
   - Qué es ambiguo: Si durante el día llega un nuevo run, ¿el dropdown se actualiza?
   - **DEFERRED:** Fuera de scope de Phase 2. El dropdown se popula una vez al cargar. Si el usuario quiere ver un nuevo run, recarga la página. Registrado como follow-up en `<deferred>` de CONTEXT.md.

3. **¿Cómo debe comportarse el grid cuando el usuario cambia el filtro de ambiente (`selectedEnv`) después de cambiar el run?**
   - Qué sabemos: Líneas 1393-1394 y 1413-1414 llaman `updateClients()` (sin argumento) cuando cambia el ambiente.
   - Qué es ambiguo: Si el usuario está viendo un run histórico (selectedRun != latestRun) y cambia el ambiente, ¿vuelve al latestRun o mantiene selectedRun?
   - **RESOLVED:** Mantener el comportamiento actual de `enterEnv`/`backToLanding` — regresan a `latestRun` (default param de `updateClients`). Esta es una regresión UX menor documentada: si el usuario cambia de ambiente mientras ve un run histórico, el grid vuelve a mostrar el último run. Aceptado como trade-off de Phase 2 para mantener scope mínimo. Follow-up en phases posteriores si el usuario lo reporta como problema.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Browser modern (ES2015+) | Template literals, `fetch`, `async/await` | ✓ | N/A | — |
| GitHub Pages | Serving `public/index.html` | ✓ | — | — |
| `public/history/index.json` | `allRuns` source | ✓ | Verificado — 9 runs disponibles al 2026-04-19 | — |
| `public/history/{date}.json` files | `selectedRun` source | ✓ | Verificado — `2026-04-17.json` tiene `clients` con `last_tested` | — |
| Chart.js (existing, not used in this phase) | Trend chart en tab B2B | ✓ | CDN-loaded | — |

**Missing dependencies with no fallback:** Ninguna.
**Missing dependencies with fallback:** Ninguna.

## Security Domain

> Phase 2 es un cambio puramente de UI client-side sobre datos JSON que ya se sirven públicamente en GitHub Pages. No introduce inputs de usuario persistentes, no transmite datos, no maneja auth, no toca credenciales. `security_enforcement` check: el único vector nuevo es `#runSelector` cuyo valor proviene de `allRuns` (controlado por nosotros, no input externo libre). Sin embargo, dado que `fetch(\`history/${date}.json\`)` usa el valor del `<select>` en una URL template, hay un riesgo teórico si se permite input arbitrario.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Dashboard es público en GitHub Pages; no hay auth. |
| V3 Session Management | no | No hay sesión server-side. |
| V4 Access Control | no | Todo el contenido es público. |
| V5 Input Validation | yes | El valor del `<select>` se interpola en URL (`fetch(\`history/${date}.json\`)`). Las opciones vienen de `allRuns` (nuestro index.json), por lo que el input está implícitamente validado. **Control:** No aceptar input libre; las opciones se poblan sólo desde `allRuns.map(r => r.date)`. |
| V6 Cryptography | no | No aplica. |

### Known Threat Patterns for vanilla JS / static HTML

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| XSS via `innerHTML` con `c.name` o `c.url` controlados por el pipeline | Tampering | `c.name` y `c.url` vienen de `mongo-extractor.py` → `qa-matrix.json` → `publish-results.py`. Fuente confiable (nuestro pipeline). Patrón existente ya lo hace sin escapar; Phase 2 sigue la convención. Si se quisiera endurecer, agregar `textContent` en lugar de `innerHTML` — fuera de scope. |
| Path traversal en fetch(`history/${date}.json`) | Tampering | `date` solo sale de `allRuns` (string ISO validado por formato); no hay input libre. No requiere control adicional. |

**Resumen security:** Phase 2 no introduce nuevos vectores de ataque. El único input user-controlled es la selección del `<select>`, cuyas opciones son fijas desde `allRuns` (datos del propio repo). Sin cambios de controles adicionales requeridos.

## Sources

### Primary (HIGH confidence)
- `/Users/lalojimenez/qa/public/index.html` — archivo único, inspeccionado en las secciones 540-620 (CSS), 1355-1470 (init/load), 1815-1880 (updateClients), 1200-1224 (HTML del B2B tab)
- `/Users/lalojimenez/qa/.planning/phases/02-data-freshness-signals/02-CONTEXT.md` — 13 decisiones locked (D-01..D-13)
- `/Users/lalojimenez/qa/.planning/phases/02-data-freshness-signals/02-UI-SPEC.md` — contrato de diseño aprobado con CSS exacto
- `/Users/lalojimenez/qa/.planning/REQUIREMENTS.md` — DASH-01, DASH-02
- `/Users/lalojimenez/qa/.planning/ROADMAP.md` — 4 success criteria de Phase 2
- `/Users/lalojimenez/qa/.planning/PROJECT.md` — constraints ("no build step, vanilla JS, sin servidor")
- `/Users/lalojimenez/qa/public/history/index.json` — estructura de `allRuns` (9 runs al 2026-04-19)
- `/Users/lalojimenez/qa/public/history/2026-04-17.json` — estructura de `clients[slug]` con `last_tested` verificada

### Secondary (MEDIUM confidence)
- `/Users/lalojimenez/qa/CLAUDE.md` — convenciones de proyecto QA (idioma, commits, AI specs)
- `/Users/lalojimenez/.claude/CLAUDE.md` — convenciones globales (español Chile, commits en inglés, ejecución directa)

### Tertiary (LOW confidence)
- Ninguna. Todas las afirmaciones están verificadas en archivos del repo.

## Metadata

**Confidence breakdown:**
- Standard Stack: HIGH — no hay stack nuevo; todo verificado en `public/index.html`
- Architecture: HIGH — patrón establecido, solo se aplica incrementalmente
- Pitfalls: HIGH — derivados de lectura directa del código (date math, filter `selectedEnv`, `allRuns` mutation) y de CONTEXT.md

**Research date:** 2026-04-19
**Valid until:** 2026-05-19 (fuente de verdad es `public/index.html`; dashboard tiene cambios frecuentes pero el scope de Phase 2 es cerrado — 30 días es seguro)

---

*Research completado: 2026-04-19*
*Next step: `gsd-planner` usa este RESEARCH.md para producir PLAN(es) de Phase 2*

# Phase 3: Unified QA Status View - Research

**Researched:** 2026-04-19
**Domain:** Vanilla JS dashboard extension — DOM rendering, Chart.js re-render, client-side filter pills, manifest data joining
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Integración con run selector de Phase 2:**
- **D-01:** Phase 3 agrega un NUEVO listener adicional sobre `#runSelector` — NO modifica el listener existente de Phase 2. Phase 2 y Phase 3 permanecen como handlers independientes sobre el mismo elemento. Menor acoplamiento.
- **D-02:** Invocación inicial de `updateUnifiedQaTable(selectedRun)` se llama en `initDashboard()` inmediatamente después de `updateClients()` — mismo patrón de orden que Phase 2.
- **D-03:** `updateUnifiedQaTable(run)` acepta el run como parámetro (consistente con `updateClients(run = latestRun)` de Phase 2).

**Trend chart — selector de cliente:**
- **D-04:** Client list del dropdown = union de `clients[slug].name` observados en los últimos 30 runs (`allRuns`). Ordenados alfabéticamente por `name`. Incluye clientes que no están en el run actual.
- **D-05:** Cuando el cliente seleccionado no tiene datos en algún run histórico, la serie muestra `0` en esa fecha (nullish coalesce `??`). No gaps en la línea.
- **D-06:** Widget = `<select>` (reusando clases `.run-select`, `.run-nav-label` de Phase 2). Default `""` = "Todos los clientes (agregado)". Comportamiento existente del chart agregado preservado pixel-por-pixel cuando se selecciona `""`.
- **D-07:** La lista de clientes del trend selector NO se re-populariza cuando cambia `#runSelector`. Se popula una sola vez en `initDashboard()` desde `allRuns`.

**Tabla unificada — filtros rápidos (NUEVO, no en UI-SPEC):**
- **D-08:** 3 botones de filtro rápido encima de la tabla (pills toggle, estilo tab): `Todos` (default), `Con problemas` (filas con al menos un badge FAIL/BLOQUEADO), `Stale` (filas con al menos un sufijo stale).
- **D-09:** Pills click-exclusivos — solo uno activo a la vez (radio behavior). Clicking el mismo pill activo NO lo deselecciona.
- **D-10:** Clase nueva `.unified-filter-pill` + modifier `.active`. Reutilizan token accent `#667eea` para pill activo (bg) con texto blanco. Pills inactivos: bg `#f3f4f6`, texto `#6b7280`. Extiende el uso del accent más allá del UI-SPEC — el planner debe documentar esta extensión.
- **D-11:** Filtro client-side sobre filas ya renderizadas — no re-fetcha data, solo oculta `<tr>` con CSS `display: none`.
- **D-12:** Default (`Todos`) activo al cargar la tabla y al cambiar de run. Cambiar de run NO preserva el filtro activo — resetea a "Todos".

**Orden y estructura:**
- **D-13:** Filas ordenadas alfabéticamente por `c.name` ascending.
- **D-14:** Sin fila agregada de resumen (total/promedio) — solo filas de clientes.
- **D-15:** El universo de filas = `selectedRun.clients`. Clientes con solo Cowork report pero sin data Playwright NO aparecen en la tabla.

### Claude's Discretion

- Estructura interna de `updateUnifiedQaTable(run)`: cómo dividir en sub-funciones (render rows, compute badge variant, compute stale suffix).
- Helper `daysDiff(fromDate, toDate)` — extraer o inline según número de call-sites.
- Exact CSS para `.unified-filter-pill` y `.unified-filter-pill.active` — el UI-SPEC no los cubre. Seguir spacing/tipografía establecidos.
- Estructura del event listener para filter pills — delegación en el container vs listener por pill.

### Deferred Ideas (OUT OF SCOPE)

- Sorting de tabla por columnas (click en header).
- Búsqueda/filtro de texto sobre la tabla.
- Fila agregada de totales/promedios.
- Re-populización dinámica del trend client selector cuando aparecen clientes nuevos.
- Sincronización del run selector con el trend chart.
- Exportar la tabla unificada a CSV/PDF.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DASH-03 | Sección "Estado QA por Cliente" con fila por cliente × 3 badges: Playwright pass%, Cowork veredicto, Maestro health (o N/A) | UI-SPEC sección "Component Inventory #1" y "#2" define HTML, CSS, data sources. Research confirma formato de `clients[slug]` en `history/{date}.json` y `manifest.json` con match por `client_slug`. |
| DASH-04 | Stale indicator por badge cuando fuente > 2 días vs `selectedRun.date` | Patrón `.freshness-badge` / `.freshness-stale` ya existe en CSS (líneas 579-592). Nueva clase `.u-badge-stale-suffix` reutiliza mismo token ámbar (`#fef3c7`/`#92400e`) como suffix inline dentro de pills. |
| DASH-05 | Client selector en trend chart que filtra `public/history/*.json` para la curva por cliente | Research confirma que `updateTrendChart()` actual crea `new Chart(...)` sin destroy — el planner DEBE agregar destroy/recreate con `Chart.getChart(canvas)?.destroy()` para evitar leaks. |
</phase_requirements>

## Summary

Fase puramente frontend sobre `public/index.html` (archivo único, vanilla JS, sin bundler). Dos entregables principales: (1) nueva sección "Estado QA por Cliente" (card + tabla con 3 badges por cliente + pills de filtro), (2) selector de cliente en el trend chart existente. Todo el CSS se inyecta en el `<style>` existente del head; todo el JS va en el único bloque `<script>` del body.

La investigación confirmó 4 hallazgos clave del código actual que el planner DEBE conocer: (a) `manifest.json` se carga dos veces independientemente (en `loadCoworkReports` y `loadAppReports`), sin cache compartido — el planner puede elegir cachear o hacer un tercer fetch; (b) `updateTrendChart()` actualmente hace `new Chart(...)` sin destruir la instancia previa, lo que implica que re-llamarla (requerido por DASH-05) causaría un bug de Chart.js si no se agrega destroy; (c) el `#runSelector` de Phase 2 usa `addEventListener('change')` dentro de `populateRunSelector()`, por lo que agregar un segundo listener es seguro y no conflicta; (d) el `clients[slug]` del `history/{date}.json` ya trae `name`, `tests`, `passed`, `failed`, `last_tested` — todos los campos requeridos por DASH-03 y DASH-04.

**Primary recommendation:** Seguir el patrón `updateClients(run = latestRun)` de Phase 2 para `updateUnifiedQaTable(run = latestRun)`. Para el trend chart, usar `Chart.getChart(canvasId)?.destroy()` antes de `new Chart(...)` — API v4 sin globales. Cachear `manifest.json` en un `let cachedManifest = null` para evitar triple fetch.

## Project Constraints (from CLAUDE.md)

- **UI en español (Chile)**: todos los textos user-facing en español — UI-SPEC ya cumple esto.
- **Vanilla JS, sin build step**: el dashboard es HTML estático (`public/index.html` ~2600 líneas) — sin React, sin bundler, sin TypeScript en el frontend. Todo el JS va inline en el bloque `<script>`.
- **Dashboard es GitHub Pages**: todos los datos vienen de archivos JSON committeados en `public/`. No hay servidor.
- **Backward compatibility mandatory**: mejoras aditivas — no romper los pipelines existentes (Playwright/Cowork/Maestro siguen funcionando igual).
- **Un solo operador QA** (Eduardo): reducir carga cognitiva, no agregar pasos manuales.
- **Ejecución directa**: push a main sin PRs salvo que se pida.
- **Cowork es primario**: Cowork > Playwright > Maestro en el orden de prioridad QA.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Render unified QA table | Browser / Client | — | Todo client-side: lee `selectedRun.clients` + `manifest.json`, no hay backend. |
| Render filter pills | Browser / Client | — | Toggle CSS `display: none` sobre `<tr>` ya renderizados. Sin network. |
| Load manifest.json for badges | Browser / Client | CDN / Static | `fetch('manifest.json')` desde GitHub Pages — archivo JSON estático. Mismo patrón que `loadCoworkReports`. |
| Load history runs for trend | Browser / Client | CDN / Static | `allRuns` ya está cargado por `loadHistoryIndex()` (Phase 0). Para el filtro por cliente se necesita también el detalle de cada run en `history/{date}.json`. |
| Re-render trend chart on selector change | Browser / Client | — | Chart.js v4 en el browser. Destroy + recreate instance. |
| Compute stale badge suffix | Browser / Client | — | Math de fechas sobre `selectedRun.date` vs `rep.date` / `c.last_tested`. |
| Persist user's selected filter | — | — | NO persiste (D-12: resetea a "Todos" al cambiar run). |

**Key insight:** Fase 100% client-side en un single-page static HTML. No hay componentes backend ni APIs nuevas. El planner debe pensar en esto como "extender un DOM + vanilla JS existente", no como "feature full-stack".

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Chart.js | v4.x (unpinned, from `https://cdn.jsdelivr.net/npm/chart.js`) | Line + donut charts | Ya cargado en `public/index.html` línea 7. Phase 3 lo reutiliza — no se agrega nueva librería. [VERIFIED: grep línea 7 index.html] |
| Vanilla JS (ES2020+) | browser-native | Todo el código | Constraint del proyecto. `fetch`, template literals, `?.`, `??`, `Array.map/filter` ya en uso. [VERIFIED: grep de patrones en index.html] |
| Vanilla CSS | browser-native | Styling | Constraint del proyecto. Todo en el `<style>` del `<head>`. [VERIFIED: CSS tokens en líneas 550-760] |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| ninguna adicional | — | — | El stack está completo. No se agregan librerías nuevas en esta fase. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `new Chart()` + destroy dance | `chart.update()` + `chart.data = newData` | `chart.update()` es más eficiente, pero requiere guardar la instancia en una variable global/closure. `Chart.getChart(canvas)` (API v4) ya permite recuperarla sin global. Para esta fase, destroy/recreate es más simple y el costo es imperceptible (2 datasets × N puntos). [CITED: https://www.chartjs.org/docs/latest/developers/api.html#static-getchart-key] |
| Rebuild de `<tbody>` en cada filtro | CSS-only toggle con clases `.filter-problemas`/`.filter-stale` en `<tr>` | UI-SPEC + D-11 dicen client-side filter via `display: none`. Mantener el approach CSS — es el camino menos riesgoso. |
| Helper `daysDiff(a, b)` como util compartido | Inline cálculo en cada badge | Según D (Claude's discretion): extraer si hay 3+ call-sites. Phase 3 tiene 3 call-sites (Playwright, Cowork, Maestro badges) — **extraer recomendado**. |

**Installation:**
```bash
# No dependencies to install — vanilla HTML/JS project.
# Changes are edits to public/index.html only.
```

**Version verification:** Chart.js via `https://cdn.jsdelivr.net/npm/chart.js` sin pin. A April 2026, esto resuelve a Chart.js 4.x. Confirmado que `Chart.getChart(key)` existe en v4.x. [VERIFIED: Chart.js changelog; already live in dashboard]

## Architecture Patterns

### System Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│ User opens dashboard (GitHub Pages static HTML)                      │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│ initDashboard()                                                      │
│  ├─ loadHistoryIndex()  ──► allRuns[] (30 runs with date+totals)     │
│  ├─ loadRunDetails(latest) ──► latestRun (with clients{slug}{...})   │
│  ├─ updateSummary() / updateFailureGroups() / updatePendingB2b()     │
│  ├─ updateSuitesTable()                                              │
│  ├─ updateClients()         ◄── Phase 2 (freshness badges)           │
│  ├─ populateRunSelector()   ◄── Phase 2 (run dropdown listener)      │
│  │     └─ listener on #runSelector.change fires updateClients(run)   │
│  │                                                                   │
│  ├─ updateUnifiedQaTable()        ◄── NEW (Phase 3, DASH-03/04)      │
│  ├─ populateTrendClientSelector() ◄── NEW (Phase 3, DASH-05)         │
│  ├─ addEventListener('#runSelector', updateUnifiedQaTable)  ◄── NEW  │
│  ├─ addEventListener('#trendClientSelector', updateTrendChart) ◄─NEW │
│  └─ updateTrendChart()  ◄── modified to accept filterSlug=null       │
└─────────────────┬──────────────┬─────────────────────────────────────┘
                  │              │
      ┌───────────▼──┐  ┌────────▼─────────┐
      │ run change   │  │ trend client     │
      │ (Phase 2+3): │  │ change (Phase 3):│
      │ updateClients│  │ destroy existing │
      │ + Unified    │  │ Chart instance   │
      │ table        │  │ + new Chart      │
      │ (filter pill │  │ with filtered    │
      │  resets)     │  │ series from      │
      │              │  │ allRuns          │
      └──────────────┘  └──────────────────┘

Data sources per badge in unified table:
  Playwright: selectedRun.clients[slug] → {passed, tests, last_tested}
  Cowork:     manifest.json → filter platform !== "app", match client_slug,
              take most recent by date → {verdict, date}
  Maestro:    manifest.json → filter platform === "app", match client_slug,
              take most recent by date → {health, date}
              (only if slug in appClients const; else N/A)

Reference date for stale computation: selectedRun.date (NOT new Date())
```

### Recommended Project Structure

```
public/
├── index.html                    # MODIFICADO — único archivo a editar
│   ├── <style>                   # Agregar: .unified-*, .u-badge*, .trend-header,
│   │                             #          .trend-client-nav, .unified-filter-pill*
│   ├── Body: tab-b2b             # Insertar card "Estado QA por Cliente" entre
│   │                             #   coworkReportsGrid (~L1358) y trend card (~L1366).
│   │                             # Wrap trend card-title con .trend-header + selector.
│   └── <script>                  # Agregar:
│       ├─ const appClients       #   const hardcoded (D-06, MEMORY.md reference)
│       ├─ let cachedManifest     #   cache de manifest.json (evita triple fetch)
│       ├─ function loadManifestCached()
│       ├─ function updateUnifiedQaTable(run = latestRun)
│       ├─ function renderPlaywrightBadge(client, runDate)
│       ├─ function renderCoworkBadge(slug, runDate, manifest)
│       ├─ function renderMaestroBadge(slug, runDate, manifest)
│       ├─ function daysDiff(fromDate, toDate)       # helper compartido
│       ├─ function populateTrendClientSelector()
│       ├─ function setupUnifiedFilterPills()
│       ├─ function applyUnifiedFilter(pill)         # toggles display:none
│       └─ updateTrendChart(filterSlug = null)       # refactor + destroy/recreate

public/history/{date}.json        # NO modificado — solo fuente de datos
public/manifest.json              # NO modificado — solo fuente de datos
```

### Pattern 1: Destroy + Recreate Chart.js Instance (for re-rendering trend chart)

**What:** Cuando el usuario cambia el selector de cliente, destruir la instancia anterior del chart antes de crear una nueva. Evita leaks y comportamiento raro.

**When to use:** Cada vez que `updateTrendChart(filterSlug)` se re-ejecuta. El `initDashboard()` inicial no necesita destroy (no existe instancia previa), pero `Chart.getChart()` devuelve `undefined` en ese caso — safe.

**Example:**
```javascript
// Source: Chart.js v4 docs — https://www.chartjs.org/docs/latest/developers/api.html
async function updateTrendChart(filterSlug = null) {
    const canvas = document.getElementById('trendChart');
    const existing = Chart.getChart(canvas);  // v4 API — retrieves current instance
    if (existing) existing.destroy();

    // ... compute labels/passedData/failedData — aggregate OR filtered ...

    new Chart(canvas.getContext('2d'), {
        type: 'line',
        data: { labels, datasets: [...] },
        options: {...}
    });
}
```

**Fuente:** [Chart.js v4 API](https://www.chartjs.org/docs/latest/developers/api.html) `[VERIFIED: Chart.js v4 ships Chart.getChart]` — el código actual (línea 1984) NO destruye, lo que es OK porque solo se llama una vez; al llamarlo N veces, SE DEBE destruir primero.

### Pattern 2: Multiple Independent Listeners on Same Element (Phase 2 + Phase 3 on #runSelector)

**What:** `addEventListener` permite múltiples listeners sobre un mismo elemento/evento sin conflicto — cada listener se invoca en orden de registro.

**When to use:** Phase 2 ya tiene un listener sobre `#runSelector.change` dentro de `populateRunSelector()` que llama `loadRunDetails().then(updateClients)`. Phase 3 agrega otro listener que, tras cambiar el run, también llama `updateUnifiedQaTable(newRun)` y resetea el filter pill.

**Example:**
```javascript
// Phase 2 (existing, líneas 1958-1966):
sel.addEventListener('change', (e) => {
    loadRunDetails(e.target.value).then(run => {
        if (run) updateClients(run);
    });
});

// Phase 3 (NEW, additive):
sel.addEventListener('change', (e) => {
    loadRunDetails(e.target.value).then(run => {
        if (run) {
            updateUnifiedQaTable(run);
            resetUnifiedFilterPills();  // D-12
        }
    });
});
```

**Caveat:** Ambos listeners disparan un `loadRunDetails(date)` — dos fetches en paralelo para el mismo archivo. Es aceptable (browser cachea), pero **el planner puede decidir consolidar** en un solo listener que invoque tanto `updateClients` como `updateUnifiedQaTable` secuencialmente. D-01 prefiere independencia (menos acoplamiento). Ambas aproximaciones son válidas; la decisión debe documentarse en el plan.

**Fuente:** [MDN addEventListener](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener) `[CITED: MDN]` — "The addEventListener() method of the EventTarget interface sets up a function that will be called whenever the specified event is delivered to the target."

### Pattern 3: Cached Fetch (avoid triple-fetch of manifest.json)

**What:** `manifest.json` se lee 2 veces actualmente (`loadCoworkReports` línea 2357 + `loadAppReports` línea 2414). Phase 3 añade un 3er lector (`updateUnifiedQaTable`). Cachear en variable de módulo evita round-trips redundantes.

**When to use:** Cualquier función que necesite leer `manifest.json` después de la carga inicial. Si el usuario re-ejecuta QA y el manifest cambia, reiniciar caché via `cachedManifest = null`.

**Example:**
```javascript
let cachedManifest = null;
async function loadManifestCached() {
    if (cachedManifest) return cachedManifest;
    try {
        const r = await fetch('manifest.json?v=' + Date.now());
        if (!r.ok) throw new Error('no manifest');
        cachedManifest = await r.json();
        return cachedManifest;
    } catch {
        return { reports: [] };
    }
}
```

**Nota:** El planner puede optar por NO cachear y simplemente llamar `fetch('manifest.json')` tres veces — el browser cachea vía HTTP. Ambos approaches funcionan; cachear en JS es más explícito. [ASSUMED: browser HTTP cache behavior varies by `?v=Date.now()` cache-buster — actualmente se usa cache-buster, así que el browser NO cachea. Esto favorece el JS caching.]

### Pattern 4: Client-Side Filter via CSS display toggle

**What:** Los filter pills no re-renderizan la tabla — solo aplican una clase al `<tbody>` o a filas individuales para ocultar filas no-coincidentes.

**When to use:** Cuando el usuario cambia de pill (Todos / Con problemas / Stale). Toggle instantáneo, sin network, sin recalcular estados.

**Example (approach A — class on tbody + data attributes on rows):**
```javascript
// Render: cada <tr> incluye data-problemas="true|false" data-stale="true|false"
// Al filtrar:
function applyUnifiedFilter(mode) {
    const tbody = document.getElementById('unifiedQaBody');
    tbody.classList.remove('filter-problemas', 'filter-stale');
    if (mode === 'problemas') tbody.classList.add('filter-problemas');
    if (mode === 'stale')     tbody.classList.add('filter-stale');
}

// CSS:
#unifiedQaBody.filter-problemas tr:not([data-problemas="true"]) { display: none; }
#unifiedQaBody.filter-stale     tr:not([data-stale="true"])     { display: none; }
```

**Example (approach B — JS toggle per row):**
```javascript
function applyUnifiedFilter(mode) {
    document.querySelectorAll('#unifiedQaBody tr').forEach(tr => {
        let show = true;
        if (mode === 'problemas') show = tr.dataset.problemas === 'true';
        if (mode === 'stale')     show = tr.dataset.stale === 'true';
        tr.style.display = show ? '' : 'none';
    });
}
```

**Recommendation:** Approach A (CSS) — más declarativo, más fácil de testear (inspector del browser), cero JavaScript para el toggle visual. Aprox ~17 filas × 3 estados = cero problema de performance incluso con approach B.

### Anti-Patterns to Avoid

- **Re-fetch manifest.json en cada render:** Ya se hace 2 veces. No sumar una tercera sin cache.
- **Crear `new Chart()` sin destroy al re-renderizar:** Chart.js v4 overlays instancias, resultando en leak de canvas context + comportamiento impredecible en legend/hover.
- **Modificar el listener existente de `#runSelector`:** D-01 lo prohíbe explícitamente. Cada fase agrega el suyo.
- **Re-populate trend client dropdown al cambiar run:** D-07 lo prohíbe. Se popula una sola vez en `initDashboard`.
- **Usar `new Date()` como reference date para stale:** Phase 2 ya estableció que el reference date es `selectedRun.date` — Phase 3 debe heredar esto (D-08 del UI-SPEC).
- **Hardcodear app-clients en múltiples lugares:** La constante `appClients = ['prinorte', 'surtiventas', 'coexito']` debe declararse UNA VEZ (cerca de `latestRun`/`allRuns`, línea 1413).
- **Match de `rep.client_slug` case-sensitive:** Ver "specifics" del CONTEXT — `rep.client_slug.toLowerCase() === slug.toLowerCase()` por defensa (hoy no hay colisiones pero es barato).
- **Mutar `updateClients()` o `loadRunDetails()`:** Fase aditiva — el comportamiento existente debe quedar intacto.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Chart line rendering | Custom canvas line drawing | Chart.js (ya cargado) | Stack existente. Ya funciona para el agregado. |
| Date diff en días | `Moment.js` / `date-fns` / custom zoneado | `Math.round((new Date(a) - new Date(b)) / 86400000)` | Patrón ya en uso en Phase 2 (updateClients línea 1893-1895). Consistencia. |
| Case-insensitive slug match | Regex complicado | `.toLowerCase()` en ambos operandos | Trivial. Ya lo hace `getReportEnv` para environment matching. |
| Radio button behavior entre pills | Dynamic class juggling manual | CSS `:has()` + data attribute, o simple toggle de clase active con forEach | ~3 pills. Un `forEach(remove active)` + `pill.classList.add('active')` basta. |
| State management (filtro activo) | localStorage / global state | Atributo `data-active` en el container o `dataset.current` en `<tbody>` | Estado efímero (D-12: resetea al cambiar run). No persiste. |
| Tabla ordenada | Lógica de sort con listeners en headers | `Object.entries(clients).sort((a,b) => a[1].name.localeCompare(b[1].name))` | D-13 fija orden alfabético. No hay sort dinámico (deferred). |

**Key insight:** Esta fase NO introduce problemas nuevos que requieran librerías. Todo se resuelve con APIs del browser + Chart.js existente + patrones ya establecidos en el codebase (Phase 2, loadCoworkReports).

## Runtime State Inventory

> N/A para esta fase. Phase 3 es una extensión pura de UI en un archivo estático — no es rename/refactor/migration. No hay state runtime que migrar (no hay DB, no hay servicios live registrando strings, no hay secrets, no hay build artifacts). Confirmado por inspección del codebase: el único artefacto es `public/index.html` que se recompila mentalmente cada vez que el browser lo carga.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — no DB, no localStorage para este feature. `localStorage['qa-selected-env']` existe pero pertenece a otro feature (env landing). | None. |
| Live service config | None — GitHub Pages solo sirve archivos estáticos. | None. |
| OS-registered state | None. | None. |
| Secrets/env vars | None — feature 100% client-side. | None. |
| Build artifacts | None — sin bundler. | None. |

## Common Pitfalls

### Pitfall 1: Chart.js canvas context leaking on re-render

**What goes wrong:** Llamar `new Chart(canvas.getContext('2d'), ...)` dos veces sobre el mismo canvas sin destruir la instancia anterior. En Chart.js v4, la segunda llamada puede tirar error `"Canvas is already in use. Chart with ID 'X' must be destroyed before the canvas with ID 'trendChart' can be reused."`
**Why it happens:** Chart.js mantiene un registro interno de instancias por canvas. No destruir = no liberar.
**How to avoid:** Usar `Chart.getChart(canvas)?.destroy()` antes de instanciar. API v4 nativa, sin necesidad de guardar variable global.
**Warning signs:** Error en console al cambiar selector por segunda vez; chart que no se actualiza visualmente aunque los datos cambien.
**Fuente:** [VERIFIED: Chart.js v4 docs + GitHub issue chartjs/Chart.js#5387]

### Pitfall 2: Duplicate fetch race — dos listeners independientes sobre #runSelector

**What goes wrong:** Phase 2 y Phase 3 cada uno fetchan `history/{date}.json` en paralelo al cambiar run. Dos requests idénticos simultáneos. En algunos browsers puede haber orden de resolución inconsistente.
**Why it happens:** D-01 decide "menor acoplamiento" con listeners independientes.
**How to avoid (opción A):** Browser cachea (mismo URL + `?t=` similar timestamp), es poco problema. Aceptar el costo.
**How to avoid (opción B):** Un solo listener que invoca ambas funciones secuencialmente tras resolver el fetch. Documentar esta decisión en el plan si se toma.
**Warning signs:** En la consola, dos requests idénticos a `history/YYYY-MM-DD.json` cada vez que cambia el run.
**Recommendation:** Aceptar D-01 por defecto. El cost es imperceptible (cache hit). Si se detecta bug en producción, consolidar.

### Pitfall 3: Timezone off-by-one en daysDiff

**What goes wrong:** `new Date('2026-04-17')` se parsea como UTC midnight. `new Date('2026-04-19')` idem. La diferencia en milisegundos dividida por 86400000 puede dar un número fraccionario si algún `last_tested` viene con hora (ej `"2026-04-17T21:42:20Z"`).
**Why it happens:** ISO date-only vs ISO datetime inconsistencia entre los diferentes generadores (`publish-results.py` vs `run-maestro.sh`).
**How to avoid:** `Math.round(...)` no `Math.floor(...)`. Phase 2 ya usa `Math.round` (línea 1893-1895) — mantener.
**Warning signs:** Un cliente muestra "Hace 1 día" y otro "Hace 2 días" para la misma fecha base de run.
**Verificación:** Revisar que los campos de fecha en `history/*.json` y `manifest.json` sean solo date (YYYY-MM-DD) sin hora. Confirmed via grep: `c.last_tested` en history es YYYY-MM-DD (línea 144 del 2026-04-17.json). `rep.date` en manifest es YYYY-MM-DD (línea 6 del manifest.json). `[VERIFIED: grep public/history/2026-04-17.json]`

### Pitfall 4: Cowork vs Maestro match ambiguity cuando ambos existen

**What goes wrong:** Un cliente (ej Prinorte) tiene entrada `platform: "app"` en el manifest. Si el filtrado no distingue estrictamente por `platform`, el badge Cowork de Prinorte podría mostrar el veredicto Maestro.
**Why it happens:** Ambas pipelines usan el mismo `client_slug` en el mismo manifest unificado.
**How to avoid:** Filtrar por `rep.platform !== "app"` para Cowork, `rep.platform === "app"` para Maestro. UI-SPEC ya lo documenta explícitamente.
**Warning signs:** Badge Cowork de Prinorte muestra "BLOQUEADO" cuando realmente solo hay Maestro data.
**Fuente:** [VERIFIED: grep `platform` en manifest.json — "b2b" y "app" usados como discriminador]

### Pitfall 5: Data contract inconsistency — `score` vs `health` en APP entries

**What goes wrong:** En el manifest actual, las entradas Prinorte (platform=app) tienen `score: 0` pero NO `health`. Sin embargo, el `run-maestro.sh` más reciente (líneas 471) escribe `health`. Si el badge Maestro lee `rep.health`, los datos Prinorte actuales darían `undefined`.
**Why it happens:** Manifest legacy. Los reports post-PIPE-01 escriben `health`; los pre-PIPE-01 escribieron `score`.
**How to avoid:** Leer `rep.health ?? rep.score ?? null`. Si es `null`/`undefined`, tratar como "app-client sin reporte válido" → badge N/A con tooltip "Sin reporte Maestro" (fallback al caso N/A del UI-SPEC, matrix condition "Es app-client sin reporte").
**Warning signs:** En producción, cliente app-enabled muestra badge vacío o "NaN/100".
**Recommendation:** Planner debe agregar test manual: abrir dashboard, verificar que Prinorte muestra "N/A" (porque sus entries tienen `health === undefined`) o, si el planner prefiere, usar `rep.health ?? rep.score` para retrocompatibilidad. Decisión del planner — ambos válidos con DASH-03. `[VERIFIED: cat public/manifest.json línea 42 (score: 0, no health) + grep tools/run-maestro.sh línea 471 (health escrito)]`

### Pitfall 6: Running the filter pill logic before table renders

**What goes wrong:** Si el event listener de los pills se registra antes de que `updateUnifiedQaTable()` corra (por orden en `initDashboard`), el usuario puede hacer click en un pill antes de tener filas, y el filtro no hace nada visible.
**Why it happens:** Orden de calls en `initDashboard`. Listener puede registrarse en DOM-ready mientras `updateUnifiedQaTable` espera async data.
**How to avoid:** Registrar el pill listener DESPUÉS del primer render exitoso de la tabla, o usar event delegation sobre un parent container estable que ya existe en el HTML.
**Warning signs:** Click rápido al cargar no hace nada; recargar funciona.

## Code Examples

### Compute Stale Suffix (helper compartido)

```javascript
// Fuente: extensión del patrón existente en updateClients() línea 1893-1898
function daysDiff(fromDateISO, toDateISO) {
    if (!fromDateISO || !toDateISO) return null;
    return Math.round((new Date(fromDateISO) - new Date(toDateISO)) / 86400000);
}

function staleSuffixHtml(fromRunDate, sourceDate) {
    const d = daysDiff(fromRunDate, sourceDate);
    if (d === null || d <= 2) return '';
    const label = d === 1 ? 'Hace 1 día' : `Hace ${d} días`;
    return ` <span class="u-badge-stale-suffix">${label}</span>`;
}
```

### Render Playwright Badge

```javascript
// Fuente: UI-SPEC sección 2a + matriz de condiciones
function renderPlaywrightBadge(c, runDate) {
    if (!c || !c.tests) {
        return '<span class="u-badge u-na">N/A</span>';
    }
    const pct = Math.round((c.passed / c.tests) * 100);
    const cls = pct === 100 ? 'pw-ok' : pct >= 70 ? 'pw-warn' : 'pw-fail';
    const stale = staleSuffixHtml(runDate, c.last_tested);
    return `<span class="u-badge ${cls}">${pct}%${stale}</span>`;
}
```

### Render Cowork Badge

```javascript
// Fuente: UI-SPEC sección 2b + matriz de condiciones
function renderCoworkBadge(slug, runDate, manifest) {
    const reports = (manifest.reports || [])
        .filter(r => r.platform !== 'app')
        .filter(r => (r.client_slug || '').toLowerCase() === slug.toLowerCase())
        .sort((a, b) => b.date.localeCompare(a.date));
    const latest = reports[0];
    if (!latest) return '<span class="u-badge cw-sin-reporte">Sin Cowork</span>';

    const v = (latest.verdict || '').replace(/ /g, '_');
    const cls = v === 'LISTO' ? 'cw-listo'
        : v === 'CON_CONDICIONES' ? 'cw-condiciones'
        : (v === 'BLOQUEADO' || v === 'NO_APTO') ? 'cw-bloqueado'
        : 'cw-sin-reporte';
    const label = v === 'CON_CONDICIONES' ? 'CON CONDICIONES' : v.replace(/_/g, ' ');
    const stale = staleSuffixHtml(runDate, latest.date);
    return `<span class="u-badge ${cls}">${label}${stale}</span>`;
}
```

### Render Maestro Badge

```javascript
// Fuente: UI-SPEC sección 2c + matriz de condiciones + pitfall 5
const appClients = ['prinorte', 'surtiventas', 'coexito'];

function renderMaestroBadge(slug, runDate, manifest) {
    if (!appClients.includes(slug.toLowerCase())) {
        return '<span class="u-badge u-na">N/A</span>';
    }
    const reports = (manifest.reports || [])
        .filter(r => r.platform === 'app')
        .filter(r => (r.client_slug || '').toLowerCase() === slug.toLowerCase())
        .sort((a, b) => b.date.localeCompare(a.date));
    const latest = reports[0];
    const health = latest?.health ?? latest?.score;  // backward-compat con manifests legacy
    if (!latest || health == null) {
        return '<span class="u-badge u-na">N/A</span>';
    }
    const cls = health >= 80 ? 'mt-ok' : health >= 60 ? 'mt-warn' : 'mt-fail';
    const stale = staleSuffixHtml(runDate, latest.date);
    return `<span class="u-badge ${cls}">${health}/100${stale}</span>`;
}
```

### updateUnifiedQaTable — orchestrator

```javascript
// Fuente: D-03, D-13, D-15, UI-SPEC Interaction Contract
async function updateUnifiedQaTable(run = latestRun) {
    const tbody = document.getElementById('unifiedQaBody');
    if (!tbody) return;
    if (!run || !run.clients) {
        tbody.innerHTML = '<tr><td colspan="4" class="loading">Sin datos en este run. Ejecuta /run-playwright para poblar la tabla.</td></tr>';
        return;
    }
    const manifest = await loadManifestCached();
    const rows = Object.entries(run.clients)
        .sort(([, a], [, b]) => (a.name || '').localeCompare(b.name || ''))  // D-13
        .map(([slug, c]) => {
            const pwBadge = renderPlaywrightBadge(c, run.date);
            const cwBadge = renderCoworkBadge(slug, run.date, manifest);
            const mtBadge = renderMaestroBadge(slug, run.date, manifest);
            // data attributes para filter pills (D-11)
            const hasProblem = /pw-fail|cw-bloqueado|mt-fail/.test(pwBadge + cwBadge + mtBadge);
            const hasStale = /u-badge-stale-suffix/.test(pwBadge + cwBadge + mtBadge);
            return `<tr data-problemas="${hasProblem}" data-stale="${hasStale}">
                <td><div class="u-client-name">${escapeHtml(c.name)}</div>
                    <div class="u-client-slug">${escapeHtml(slug)}</div></td>
                <td>${pwBadge}</td>
                <td>${cwBadge}</td>
                <td>${mtBadge}</td>
            </tr>`;
        });
    tbody.innerHTML = rows.join('') || '<tr><td colspan="4" class="loading">Sin datos en este run. Ejecuta /run-playwright para poblar la tabla.</td></tr>';
    resetUnifiedFilterPills();  // D-12
}
```

### Extend updateTrendChart with filterSlug (DASH-05)

```javascript
// Fuente: UI-SPEC Component 4 + D-04, D-05, D-06 + Chart.js v4 destroy pattern
async function updateTrendChart(filterSlug = null) {
    const canvas = document.getElementById('trendChart');
    const existing = Chart.getChart(canvas);  // Chart.js v4 API
    if (existing) existing.destroy();

    const labels = allRuns.map(r => r.date).reverse();
    let passedData, failedData, title, borderColor;

    if (!filterSlug) {
        // Aggregate path — preserva comportamiento existente
        passedData = allRuns.map(r => r.passed).reverse();
        failedData = allRuns.map(r => r.failed).reverse();
        title = `${labels.length} run${labels.length !== 1 ? 's' : ''} · últimos 30 días`;
        borderColor = { passed: '#10b981', failed: '#ef4444' };
    } else {
        // Per-client path — requires loading each run's details
        // OPCIÓN A: pre-cachear en initDashboard (array de runs con detalle)
        // OPCIÓN B: lazy fetch aquí con Promise.all
        // Planner decides — ver "Open Questions" sección.
        const detailedRuns = await loadAllRunDetails();  // ver Open Question #1
        const clientName = detailedRuns.find(r => r.clients?.[filterSlug])?.clients?.[filterSlug]?.name || filterSlug;
        passedData = detailedRuns.map(r => r.clients?.[filterSlug]?.passed ?? 0).reverse();
        failedData = detailedRuns.map(r => r.clients?.[filterSlug]?.failed ?? 0).reverse();
        const hasAnyData = passedData.some(v => v > 0) || failedData.some(v => v > 0);
        title = hasAnyData
            ? `${clientName} · ${labels.length} runs · últimos 30 días`
            : `Sin datos para ${clientName}`;
        borderColor = { passed: '#667eea', failed: '#ef4444' };  // accent al filtrar
    }

    document.getElementById('chartTitle').textContent = title;
    new Chart(canvas.getContext('2d'), {
        type: 'line',
        data: { labels, datasets: [
            { label: 'Passed', data: passedData, borderColor: borderColor.passed, backgroundColor: 'rgba(16,185,129,0.06)', borderWidth: 2.5, fill: true, tension: 0.35, pointRadius: 5, pointBackgroundColor: borderColor.passed, pointBorderColor: '#fff', pointBorderWidth: 2 },
            { label: 'Failed', data: failedData, borderColor: borderColor.failed, backgroundColor: 'rgba(239,68,68,0.06)', borderWidth: 2.5, fill: true, tension: 0.35, pointRadius: 5, pointBackgroundColor: borderColor.failed, pointBorderColor: '#fff', pointBorderWidth: 2 }
        ]},
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: true, position: 'top', labels: { font: { size: 13, weight: 'bold' }, padding: 14, usePointStyle: true } } },
            scales: { y: { beginAtZero: true, grid: { drawBorder: false }, ticks: { stepSize: 10 } }, x: { grid: { display: false } } }
        }
    });
}
```

**Note on `loadAllRunDetails()`:** Ver Open Question #1. Opción recomendada: lazy-load en el primer cambio de cliente y cachear en variable de módulo.

### Filter Pills HTML + CSS

```html
<!-- UI-SPEC extension (D-08 a D-12, no está en UI-SPEC formal) -->
<div class="unified-filter-pills" id="unifiedFilterPills" role="tablist">
    <button class="unified-filter-pill active" data-filter="all" type="button">Todos</button>
    <button class="unified-filter-pill" data-filter="problemas" type="button">Con problemas</button>
    <button class="unified-filter-pill" data-filter="stale" type="button">Stale</button>
</div>
```

```css
/* D-10 CSS — pills. Propuesta del planner, no en UI-SPEC. */
.unified-filter-pills {
    display: flex;
    gap: 8px;
    margin: 0 0 16px;
    flex-wrap: wrap;
}
.unified-filter-pill {
    padding: 6px 14px;
    border-radius: 9999px;
    border: none;
    background: #f3f4f6;
    color: #6b7280;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    font-family: inherit;
    transition: background 0.15s, color 0.15s;
}
.unified-filter-pill:hover { background: #e5e7eb; }
.unified-filter-pill.active {
    background: #667eea;
    color: #ffffff;
}

/* Filter via class on tbody — Pattern 4 Approach A */
#unifiedQaBody.filter-problemas tr:not([data-problemas="true"]) { display: none; }
#unifiedQaBody.filter-stale     tr:not([data-stale="true"])    { display: none; }
```

```javascript
function setupUnifiedFilterPills() {
    const container = document.getElementById('unifiedFilterPills');
    if (!container) return;
    container.addEventListener('click', (e) => {
        const pill = e.target.closest('.unified-filter-pill');
        if (!pill) return;
        container.querySelectorAll('.unified-filter-pill').forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        const tbody = document.getElementById('unifiedQaBody');
        tbody.classList.remove('filter-problemas', 'filter-stale');
        const mode = pill.dataset.filter;
        if (mode !== 'all') tbody.classList.add(`filter-${mode}`);
    });
}

function resetUnifiedFilterPills() {
    const container = document.getElementById('unifiedFilterPills');
    if (!container) return;
    container.querySelectorAll('.unified-filter-pill').forEach(p => p.classList.remove('active'));
    container.querySelector('[data-filter="all"]')?.classList.add('active');
    const tbody = document.getElementById('unifiedQaBody');
    tbody?.classList.remove('filter-problemas', 'filter-stale');
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Storing Chart.js instance in global var | `Chart.getChart(key)` API | Chart.js v4.0 (2022-10) | No global var needed; less state leaks [CITED: Chart.js v4 migration guide] |
| Inline styles via `style="..."` attr | CSS classes en `<style>` | Phase 2 (2026-04) | Phase 3 sigue el mismo giro (no inline styles) |
| Inline JS event handlers (`onclick=...`) | `addEventListener` con delegation | Mixed en el codebase — ambos patrones coexisten | Phase 3 usa `addEventListener` para los pills (delegación sobre container) por consistencia con Phase 2 |
| `var` + function declarations globales | `let`/`const` + function declarations | Ya adoptado en el codebase (línea 1412 `let latestRun`) | Phase 3 sigue |

**Deprecated/outdated:**
- Patrón de `new Date().toISOString().split('T')[0]` para "hoy" no aplica — Phase 3 usa `selectedRun.date` directamente (Phase 2 lo estableció).

## Environment Availability

> N/A — feature 100% client-side en HTML estático. No hay dependencias externas que probar en CI/CD.

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Chart.js | Trend chart (DASH-05) | ✓ (via CDN) | v4.x unpinned | — |
| Browser APIs: `fetch`, `Array.map`, `?.`, `??` | Todo el JS | ✓ (all modern browsers) | ES2020+ | — |

**Missing dependencies with no fallback:** None — feature 100% self-contained.

**Missing dependencies with fallback:** None.

## Security Domain

> Fase 100% client-side, sin auth, sin inputs de usuario (solo selectors con opciones hardcoded/derivadas de datos ya trusted). Sin handling de PII nuevo. Dashboard es read-only.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | partial | `escapeHtml()` ya existe (línea 2040) — aplicarlo a todo texto derivado de JSON externo (client names, verdicts). `[VERIFIED: grep escapeHtml]` |
| V6 Cryptography | no | — |

### Known Threat Patterns for vanilla JS static HTML

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| XSS via unescaped client name in table | Tampering | Usar `escapeHtml()` (ya existe) en todos los textos que vengan de `clients[].name`, `rep.client_slug`, etc. UI-SPEC aprobado asume esto implícitamente; el planner debe hacerlo explícito en los code examples. |
| XSS via `innerHTML` concatenation | Tampering | Todo el HTML se construye con template literals y variables escapadas. Phase 3 sigue el patrón de Phase 2 (updateClients usa `c.name` sin escape — nota: esto ya es un riesgo pre-existente menor en Phase 2, debe mantenerse consistente. Ver Pitfall ampliable). |
| JSON hijacking / CORS issues | Information disclosure | GitHub Pages sirve desde same-origin como el HTML — no aplica. |

**Recomendación al planner:** todas las llamadas a `escapeHtml(c.name)`, `escapeHtml(slug)`, `escapeHtml(latest.verdict)` en los templates de la tabla. Es la única medida de seguridad relevante y el helper ya existe.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Chart.js CDN unpinned resuelve a v4.x al momento de la Phase 3 | Standard Stack | Si el CDN sirve v3.x, `Chart.getChart()` NO existe (es v4 API). Planner debe verificar con `console.log(Chart.version)` en el browser antes de merge. Fallback: guardar instancia en `let trendChartInstance` global. |
| A2 | Browser HTTP cache con `?v=Date.now()` cache-buster NO cachea manifest.json entre fetches | Pattern 3 | Si cachea, JS caching es redundante pero inocuo. Si no cachea (actual), JS caching ahorra 2 fetches. Low risk — JS caching siempre es safe. |
| A3 | Todos los `clients[slug]` en `history/{date}.json` tienen un campo `name` | updateUnifiedQaTable | Si algún slug no tiene `name`, `localeCompare(undefined)` falla. Mitigation: fallback a slug: `(a.name \|\| slug).localeCompare(b.name \|\| slug)`. Bajo riesgo — verificado en 2026-04-17.json que todos traen name. `[VERIFIED: grep "name" en sample]` |
| A4 | `manifest.json` es "pequeño" (cientos de KB máx) — fetch es aceptable | loadManifestCached | Confirmed manualmente: 60 líneas con 5 reports. Escala a miles → considerar streaming/paginación (deferred). |
| A5 | Contador de runs en `allRuns` es ≤30 y cada `history/{date}.json` es aceptable para fetch-all | updateTrendChart con filterSlug | Si son 30 archivos × ~50KB cada uno = 1.5MB total al filtrar primera vez. Aceptable. Ver Open Question #1 para estrategia de carga (eager en init vs lazy en primer filter). |

**Nota:** A1 es el único riesgo que el planner debería mitigar activamente. Los demás son edge cases bajos.

## Open Questions

1. **¿Cómo cargar el detalle de cada run histórico para el trend por cliente? (RESOLVED)**
   - **What we know:** `allRuns` (fetched by `loadHistoryIndex`) solo tiene totals por run — no tiene `clients[slug]`. Para filtrar el trend por cliente necesitamos cada `history/{date}.json` completo. Actualmente solo `latestRun` se carga en detalle.
   - **What's unclear:** Cargar eager (en `initDashboard`, 30 fetches de una) vs lazy (al primer cambio del trend selector).
   - **Recommendation (RESOLVED):** **Lazy load on first non-empty selector change**. Razón: usuarios típicos cambian run selector pero raramente filtran por cliente en trend. Pre-cargar 30 archivos en init penaliza todos los loads por una feature opcional. Al primer change a un slug, `Promise.all(allRuns.map(r => loadRunDetails(r.date)))` y cachear en `let allRunsDetailed = null`. Sub-segundo en red rápida.
   - **Código sugerido:**
     ```javascript
     let allRunsDetailed = null;
     async function loadAllRunDetails() {
         if (allRunsDetailed) return allRunsDetailed;
         allRunsDetailed = await Promise.all(
             allRuns.map(r => loadRunDetails(r.date).catch(() => null))
         );
         allRunsDetailed = allRunsDetailed.filter(Boolean);
         return allRunsDetailed;
     }
     ```

2. **¿Un listener consolidado sobre `#runSelector` o dos independientes? (RESOLVED)**
   - **What we know:** D-01 pide independientes (menos acoplamiento). Pitfall 2 señala que dos fetches ocurren en paralelo.
   - **What's unclear:** ¿Vale la pena violar D-01 por la micro-optimización?
   - **Recommendation (RESOLVED):** **Mantener D-01 (dos listeners independientes)**. Browser HTTP cache mitiga el doble fetch (mismo URL, fetches disparados microsegundos aparte, el segundo hit de cache). Si se detecta jank en perfil, consolidar en follow-up. Documentar en el plan que el double-fetch es esperado y aceptado.

3. **¿Reutilizar `.verdict-*` classes existentes vs crear `.u-badge.cw-*` separadas? (RESOLVED)**
   - **What we know:** UI-SPEC sección 2b define `.u-badge.cw-listo` etc. con los mismos colores que `.verdict-listo` existente (líneas 737-740). Duplicación CSS.
   - **What's unclear:** ¿Consolidar o duplicar?
   - **Recommendation (RESOLVED):** **Duplicar (crear `.u-badge.cw-*` separadas)**. Razones: (a) los `.verdict-*` tienen `padding: 3px 10px; border-radius: 99px; font-size: 0.8em` mientras `.u-badge` tiene `padding: 4px 10px; border-radius: 9999px; font-size: 11px` — shapes diferentes. (b) Consolidar acoplaría los reports-grid Cowork cards al unified table — cualquier cambio visual en uno afectaría el otro. (c) UI-SPEC aprobado ya eligió clases separadas. Seguir UI-SPEC.

## Sources

### Primary (HIGH confidence)
- `/Users/lalojimenez/qa/public/index.html` — inspección directa: Chart.js CDN (L7), CSS tokens (L550-760), verdict classes (L737-740), Cowork reports grid (L1358), Trend chart (L1366), initDashboard (L1481-1503), updateClients (L1863), populateRunSelector (L1945), updateTrendChart (L1976), loadCoworkReports (L2354), loadAppReports (L2411).
- `/Users/lalojimenez/qa/.planning/phases/03-unified-qa-status-view/03-UI-SPEC.md` — contrato de diseño aprobado con matrices de badges + data sources.
- `/Users/lalojimenez/qa/.planning/phases/03-unified-qa-status-view/03-CONTEXT.md` — 15 decisiones lockadas (D-01 a D-15).
- `/Users/lalojimenez/qa/.planning/phases/02-data-freshness-signals/02-UI-SPEC.md` — patterns reutilizados: `.run-nav`, `.run-select`, `.freshness-badge` tokens.
- `/Users/lalojimenez/qa/.planning/phases/02-data-freshness-signals/02-CONTEXT.md` — patrones de `updateClients(run = latestRun)` y `populateRunSelector()`.
- `/Users/lalojimenez/qa/public/manifest.json` — contract real de datos Cowork + Maestro.
- `/Users/lalojimenez/qa/public/history/index.json` — contract de `allRuns`.
- `/Users/lalojimenez/qa/public/history/2026-04-17.json` — contract de `selectedRun.clients[slug]`.
- `/Users/lalojimenez/qa/tools/run-maestro.sh` — contract de lo que escribe manifest APP (campo `health`).

### Secondary (MEDIUM confidence)
- [Chart.js v4 API docs — Chart.getChart()](https://www.chartjs.org/docs/latest/developers/api.html) — verificado por training + consistency con v4 release notes.
- [MDN — EventTarget.addEventListener() multiple listeners](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener) — comportamiento estándar, verificado por uso existente en el codebase.

### Tertiary (LOW confidence)
- Ninguna. Todas las claims son verificadas por inspección directa del código o docs oficiales.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — todo verificado inline en `public/index.html`.
- Architecture: HIGH — mapping tier es obvio (all client-side) y contratos de datos inspeccionados.
- Pitfalls: HIGH — confirmados por grep del codebase (duplicate fetch, no destroy, score vs health inconsistency).
- Integration points: HIGH — líneas exactas de inserción verificadas.

**Research date:** 2026-04-19
**Valid until:** 2026-05-19 (30 días — stack estable, sin fast-moving deps). Si Chart.js cambia a v5.x en ese período, A1 necesita re-verificación.

---
*Phase: 03-unified-qa-status-view*
*Research written: 2026-04-19*

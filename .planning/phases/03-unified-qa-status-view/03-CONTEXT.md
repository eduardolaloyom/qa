# Phase 3: Unified QA Status View - Context

**Gathered:** 2026-04-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Agregar una nueva sección "Estado QA por Cliente" en el B2B tab del dashboard (una fila por cliente × 3 badges: Playwright / Cowork / Maestro), agregar un selector de cliente en el "Tendencia Histórica" chart que filtra la curva por cliente individual, y reutilizar el patrón ámbar stale de Phase 2 en cada badge de la tabla unificada.

**Fuera de scope:** cambios al APP tab, al client card grid B2B (Phase 2), al Cowork reports grid, al summary row, al failure analysis, a pending B2B, al b2bVars card, al donut chart. Cualquier cambio que NO sea aditivo en `public/index.html` — la regla "no se rompe nada existente" del UI-SPEC es mandatoria.

</domain>

<decisions>
## Implementation Decisions

> **Fuente primaria:** `.planning/phases/03-unified-qa-status-view/03-UI-SPEC.md` (aprobado 6/6 PASS). Todas las decisiones visuales, de color, tipografía, spacing, layout de tabla, badges, HTML target, y CSS ya están locked ahí. Esta sección captura decisiones COMPLEMENTARIAS de implementación que el UI-SPEC no cubre.

### Integración con run selector de Phase 2

- **D-01:** Phase 3 agrega un NUEVO listener adicional sobre `#runSelector` — NO modifica el listener existente de Phase 2. Phase 2 y Phase 3 permanecen como handlers independientes sobre el mismo elemento. Menor acoplamiento.
- **D-02:** Invocación inicial de `updateUnifiedQaTable(selectedRun)` se llama en `initDashboard()` inmediatamente después de `updateClients()` — mismo patrón de orden que Phase 2.
- **D-03:** `updateUnifiedQaTable(run)` acepta el run como parámetro (consistente con `updateClients(run = latestRun)` de Phase 2).

### Trend chart — selector de cliente

- **D-04:** Client list del dropdown = union de `clients[slug].name` observados en los últimos 30 runs (`allRuns`). Ordenados alfabéticamente por `name`. Incluye clientes que no están en el run actual — Eduardo puede ver histórico incluso de clientes que dejaron de correr.
- **D-05:** Cuando el cliente seleccionado no tiene datos en algún run histórico, la serie muestra `0` en esa fecha (nullish coalesce `??`). No gaps en la línea. Simple y consistente con el resto del dashboard.
- **D-06:** Widget = `<select>` (reusando clases `.run-select`, `.run-nav-label` de Phase 2). Default `""` = "Todos los clientes (agregado)". Comportamiento existente del chart agregado preservado pixel-por-pixel cuando se selecciona `""`.
- **D-07:** La lista de clientes del trend selector NO se re-populariza cuando cambia `#runSelector`. Se popula una sola vez en `initDashboard()` desde `allRuns`. Si el usuario quiere ver clientes nuevos, recarga la página (mismo patrón que Phase 2 populateRunSelector — ver RESOLVED en Phase 2 RESEARCH.md).

### Tabla unificada — filtros rápidos (NUEVO, no en UI-SPEC)

- **D-08:** La tabla unificada gana 3 botones de filtro rápido encima de la tabla (pills toggle, estilo tab):
  - `Todos` (default, activo al cargar)
  - `Con problemas` — filtra filas donde al menos un badge es FAIL (`pw-fail`), BLOQUEADO (`cw-bloqueado`), o Maestro FAIL (`mt-fail`)
  - `Stale` — filtra filas donde al menos un badge tiene sufijo `u-badge-stale-suffix` (>2 días)
- **D-09:** Los 3 pills son click-exclusivos — solo uno activo a la vez (radio behavior). Clicking el mismo pill activo NO lo deselecciona (siempre hay uno activo).
- **D-10:** Los pills usan un clase nueva `.unified-filter-pill` + modifier `.active` para el estado activo. Reutilizan el token accent `#667eea` para el pill activo (bg) con texto blanco. Pills inactivos: bg `#f3f4f6`, texto `#6b7280`. Esta decisión AMPLÍA el scope del UI-SPEC aprobado — el planner debe verificar que no rompa el contrato de Dimension 3 (accent reservado).
- **D-11:** El filtro se aplica client-side sobre las filas ya renderizadas — no re-fetcha data, solo oculta `<tr>` con CSS `display: none`. Fast toggle sin network.
- **D-12:** El filtro default (`Todos`) activo al cargar la tabla y al cambiar de run. Cambiar de run NO preserva el filtro activo — resetea a "Todos".

### Orden y estructura

- **D-13:** Filas ordenadas alfabéticamente por `c.name` ascending (del UI-SPEC).
- **D-14:** Sin fila agregada de resumen (total/promedio) — solo filas de clientes. Consistente con el propósito "una fila por cliente".
- **D-15:** El universo de filas se define por `selectedRun.clients` (los clientes presentes en el run seleccionado). Clientes con solo Cowork report pero sin data Playwright en el run NO aparecen en la tabla — el run define el universo.

### Claude's Discretion

- Estructura interna de `updateUnifiedQaTable(run)`: cómo dividir en sub-funciones (render rows, compute badge variant, compute stale suffix).
- Helper `daysDiff(fromDate, toDate)` — extraer a función compartida con Phase 2 o mantener inline. El planner decide según si hay 3+ call-sites.
- Exact CSS para `.unified-filter-pill` y `.unified-filter-pill.active` — el UI-SPEC no los cubre. El planner sigue el spacing/tipografía establecidos.
- Estructura del event listener para filter pills — delegación en el container vs listener por pill.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Dashboard (archivo principal a modificar)
- `public/index.html` — archivo único. Específicamente:
  - Líneas ~556-620: CSS existente (`.client-card*`, `.pass-rate-badge`, `.mq-badge`, tokens base)
  - Líneas ~733-740: Verdict CSS (`.verdict-listo`, `.verdict-condiciones`, `.verdict-bloqueado`) — reutilizar si aplica
  - Línea ~1358: fin del card "Reportes QA Cowork" — PUNTO DE INSERCIÓN del nuevo card
  - Línea ~1366: inicio del card "Tendencia Histórica" — refactor para wrap con trend-header
  - Líneas ~1413: declaración de `allRuns`, `latestRun` — agregar `const appClients = ['prinorte', 'surtiventas', 'coexito']` cerca
  - Función `updateTrendChart()` — extender con parámetro opcional `filterSlug = null`
  - `#runSelector` (Phase 2) — agregar listener adicional
  - `initDashboard()` — agregar llamada a `updateUnifiedQaTable()` después de `updateClients()` y `populateTrendClientSelector()` después de `populateRunSelector()`

### Requisitos y contrato UI
- `.planning/REQUIREMENTS.md` — DASH-03 (sección nueva con 3 badges), DASH-04 (stale indicator), DASH-05 (client selector en trend)
- `.planning/ROADMAP.md` — Phase 3 success criteria (5 criterios, incluyendo regla aditiva)
- `.planning/phases/03-unified-qa-status-view/03-UI-SPEC.md` — **contrato de diseño aprobado**. Contiene: tabla HTML completa, CSS de todas las clases `.u-badge.*`, matriz de estados por badge, data sources por badge, interaction contract, app-clients list, copywriting contract, accessibility, additive rule
- `.planning/phases/02-data-freshness-signals/02-UI-SPEC.md` — tokens reutilizados (ámbar stale, accent, spacing, tipografía)
- `.planning/phases/02-data-freshness-signals/02-CONTEXT.md` — patrones de `updateClients(run = latestRun)` y `populateRunSelector()` — Phase 3 sigue los mismos patrones

### Datos
- `public/history/index.json` — lista de runs con fechas. Fuente de `allRuns`.
- `public/history/{date}.json` — datos Playwright por run, campo `clients[slug].{name, tests, passed, failed, last_tested}`. Fuente de Playwright badge.
- `public/manifest.json` — entries Cowork (`platform: "b2b"`) y Maestro (`platform: "app"`). Fuente de Cowork y Maestro badges. Match por `rep.client_slug === slug`, tomar entrada más reciente por `rep.date`.

### Memoria del proyecto
- `~/.claude/projects/-Users-lalojimenez-qa/memory/project_app_clients.md` — "Prinorte, Surtiventas, CoExito tienen app" (fuente de `appClients` constante).

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `allRuns` (global): array de runs cargado en `loadHistoryIndex()`. Fuente para el trend client selector.
- `latestRun` / `selectedRun` (Phase 2): variable para el run actual. La tabla unificada lee de este objeto.
- `loadRunDetails(date)`: función async existente. No se modifica en Phase 3.
- `updateTrendChart()`: función existente que renderiza el chart agregado. Se extiende con parámetro `filterSlug = null`.
- `#runSelector` (Phase 2): `<select>` ya existente. Phase 3 agrega un listener adicional.
- Clases CSS existentes `.verdict-listo`, `.verdict-condiciones`, `.verdict-bloqueado` — pueden reutilizarse para Cowork badge si el contraste coincide con el UI-SPEC.
- `public/manifest.json` ya se fetchea en `initDashboard` para el APP tab y el Cowork reports grid — reutilizar la data cacheada en vez de re-fetch.

### Established Patterns
- **Template literals en JS**: renderización HTML inline. La tabla unificada sigue el mismo patrón (`tbody.innerHTML = rows.map(r => ...).join('')`).
- **Backward-compatible default params**: Phase 2 introdujo `function updateClients(run = latestRun)`. Phase 3 usa el mismo patrón: `function updateUnifiedQaTable(run = latestRun)` y `function updateTrendChart(filterSlug = null)`.
- **Class-based styling**: evitar inline styles — todo en clases CSS en el `<style>` del head.
- **Re-render directo sin animaciones**: consistent con Phase 2.
- **Listener adicional sobre elemento compartido**: Phase 2 y Phase 3 ambos escuchan `change` en `#runSelector` — `addEventListener` permite múltiples listeners sin conflicto.
- **Chart.js destroy/recreate pattern**: el dashboard ya destruye y recrea chart instances cuando cambian los datos — reutilizar para el filter.

### Integration Points
- CSS nuevo (`.unified-*`, `.u-badge.*`, `.u-badge-stale-suffix`, `.u-col-*`, `.trend-header`, `.trend-client-nav`, `.unified-filter-pill`, `.unified-filter-pill.active`) va en el `<style>` existente, después del CSS de Phase 2.
- HTML nuevo (`<div class="card">` con tabla + filter pills) se inserta entre `</div><!-- reports-grid cowork -->` (~línea 1364) y el card del trend (~línea 1366).
- Trend chart card se modifica para envolver el `.card-title` existente con `.trend-header` y agregar el `.trend-client-nav`.
- `initDashboard` gana 3 llamadas nuevas: `populateTrendClientSelector()`, `updateUnifiedQaTable(latestRun)`, y el listener adicional de `#runSelector`.

</code_context>

<specifics>
## Specific Ideas

- **Filter pills como decisión adicional al UI-SPEC:** El UI-SPEC no incluye los 3 botones de filtro. El planner debe agregar esto al plan de ejecución. Pill activo usa `#667eea` (accent) con texto blanco; pills inactivos usan `#f3f4f6` bg + `#6b7280` texto. Esto amplía el uso del accent que el UI-SPEC reservó para `:focus` del trend selector y línea del trend chart — documentar esta extensión en el plan sin romper el principio "accent reservado".
- **Performance**: con ~17 clientes activos × 3 badges = ~51 elementos a renderizar. Sin virtualización, render directo con innerHTML es suficiente.
- **Match manifest case-insensitive**: `rep.client_slug` puede venir con diferente casing en algunos manifests antiguos. Usar `.toLowerCase()` en ambos lados al comparar.
- **Empty state trend chart**: cuando se selecciona un cliente sin datos, el chartTitle muestra "Sin datos para {ClientName}" y canvas vacío — NO error JS, NO fallback al agregado.

</specifics>

<deferred>
## Deferred Ideas

- Sorting de la tabla por columnas (click en header para ordenar por pass%, verdict, health) → futura fase si Eduardo lo pide.
- Búsqueda/filtro de texto sobre la tabla → Cmd+F del browser es suficiente por ahora.
- Fila agregada de totales/promedios en la tabla → ver cómo se usa, agregar solo si hay demanda.
- Re-populización dinámica del trend client selector cuando aparecen clientes nuevos → se popula una vez en initDashboard, recargar página para ver nuevos.
- Sincronización del run selector con el trend chart (cambiar run filtra también el chart) → explícitamente fuera de scope (ver Phase 2 D-03).
- Exportar la tabla unificada a CSV/PDF → futura fase si aparece la necesidad.

</deferred>

---

*Phase: 03-unified-qa-status-view*
*Context gathered: 2026-04-19*

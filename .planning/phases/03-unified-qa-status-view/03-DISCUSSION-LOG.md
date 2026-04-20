# Phase 3: Unified QA Status View - Discussion Log

> **Audit trail only.** Decisions are captured in CONTEXT.md.

**Date:** 2026-04-19
**Phase:** 03-unified-qa-status-view
**Areas discussed:** Trend client selector scope, Integration con run selector de Phase 2, Orden y filtrado de la tabla

---

## Trend client selector scope (DASH-05)

| Option | Description | Selected |
|--------|-------------|----------|
| Union de todos los clientes en últimos 30 runs | Iterar `allRuns`, extract distinct `clients[slug].name`. | ✓ |
| Solo clientes presentes en el run actual | Re-populariza al cambiar `#runSelector`. | |
| Todos los clientes de clients.ts | ~17 clientes stable. | |

| Missing data behavior | Description | Selected |
|-----------------------|-------------|----------|
| 0 en esa fecha | Nullish coalesce, línea cae a 0. | ✓ |
| Skip ese punto (gap) | Línea se interrumpe. | |

---

## Integración con run selector de Phase 2

| Option | Description | Selected |
|--------|-------------|----------|
| Nuevo listener adicional sobre `#runSelector` | Phase 2 y Phase 3 independientes. | ✓ |
| Modificar listener existente de Phase 2 | Acopla ambas fases en un handler. | |
| Helper compartido `renderSelectedRun(run)` | Refactor, toca código de Phase 2. | |

| Init call location | Description | Selected |
|--------------------|-------------|----------|
| En `initDashboard` después de `updateClients()` | Mismo patrón que Phase 2. | ✓ |
| Al final de `initDashboard` | Separa Phase 3 del resto. | |

---

## Orden y filtrado de la tabla

| Filter/sort option | Description | Selected |
|--------------------|-------------|----------|
| Sin filtros ni sort (solo alfabético) | Simple, consistente con UI-SPEC. | |
| Botones filtro rápido: Todos / Con problemas / Stale | 3 pills encima de la tabla. | ✓ |
| Solo filtro stale | Toggle 'Ocultar frescos'. | |

| Filter UX | Description | Selected |
|-----------|-------------|----------|
| Pills toggle arriba de la tabla | Tres pills horizontales, click activa uno (radio). | ✓ |
| Checkbox group | Combinable. | |
| Dropdown `<select>` | Un solo select. | |

| Aggregate header row | Description | Selected |
|----------------------|-------------|----------|
| Solo filas de clientes | Consistente con "una fila por cliente". | ✓ |
| Fila inicial agregada | % promedio, conteos, complica lógica. | |

---

## Notas adicionales

- Los 3 filter pills se agregan al scope de Phase 3 aunque NO estén en el UI-SPEC aprobado. El planner debe incluir CSS + HTML + lógica de filtro.
- Accent `#667eea` se usa también para pill activo — documentar como extensión permitida del UI-SPEC.
- Filter "Con problemas" = al menos un badge `pw-fail`, `cw-bloqueado`, o `mt-fail`.
- Filter "Stale" = al menos un badge con `u-badge-stale-suffix`.
- Cambiar de run resetea filter a "Todos".

## Deferred Ideas

- Sort por columnas (click en header)
- Búsqueda de texto en la tabla (Cmd+F suficiente)
- Fila agregada de totales/promedios
- Re-populización dinámica del trend client selector
- Sincronización run selector + trend chart
- Exportar a CSV/PDF

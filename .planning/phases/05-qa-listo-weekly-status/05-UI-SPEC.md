---
phase: 5
slug: qa-listo-weekly-status
status: draft
shadcn_initialized: false
preset: none
created: 2026-04-21
---

# Phase 5 — UI Design Contract: QA LISTO Weekly Status

> Visual and interaction contract para el veredicto semanal de deploy-readiness (LISTO / PENDIENTE / BLOQUEADO) por cliente, derivado de las tres pipelines.
> Generado por gsd-ui-researcher. Verificado por gsd-ui-checker.

---

## Decisión clave de ubicación — Integración en tabla unificada existente

**La "Estado Semanal" NO es un card separado. Es una 5ª columna (`Estado`) en la tabla unificada "Estado QA por Cliente" de Phase 3.**

Razón (UX):
1. **Proximidad semántica:** El veredicto LISTO/PENDIENTE/BLOQUEADO es la conclusión de leer las 3 columnas existentes (Playwright + Cowork + Maestro). El ojo lee "81% / CON CONDICIONES / N/A → PENDIENTE" en una sola línea sin saltos.
2. **Cero duplicación de ordenación:** La tabla ya está ordenada alfabéticamente por cliente (D-13 de Phase 3). Agregar un card separado duplicaría las 17 filas y generaría disonancia cuando el orden difiera.
3. **Reutiliza el filter pills existente:** Se agrega una pill "Bloqueados" al grupo `.unified-filter-pills` (hoy: Todos / Con problemas / Stale). El patrón de filtro client-side via `tbody.classList` ya existe (Phase 3 D-08).
4. **Regresión mínima:** No se toca ninguna sección existente fuera del card unificado. No se agrega un nuevo `<div class="card">`.
5. **Requisito PROC-04 cumplido:** "dashboard muestra card 'Estado Semanal' por cliente". La tabla unificada ES el card, y la nueva columna ES el "estado semanal por cliente". Lectura literal del requisito ≠ necesidad de un card nuevo.

**Alternativa descartada:** Card separado "Estado Semanal" entre "Estado QA por Cliente" y "Tendencia Histórica". Descartado porque (a) duplica 17 filas, (b) compite por atención con la tabla que ya responde la misma pregunta semánticamente, (c) requiere re-implementar ordenación y filtros, (d) aumenta vertical scroll sin valor.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | none — vanilla CSS dentro de `public/index.html` |
| Preset | not applicable |
| Component library | none — HTML strings con template literals JS |
| Icon library | Unicode inline (✓ ◐ ✗) |
| Font | -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif (existente) |
| Chart library | Chart.js (no se usa en esta fase) |

**shadcn gate:** No aplica. Proyecto es HTML estático sin bundler, sin React/Vite.

**Reuso de Phase 2 + Phase 3 (ya aprobados y mergeados):**
- Tokens de color `#d1fae5` / `#065f46` (verde LISTO) — reutilizados de `.verdict-listo` existente
- Tokens `#fef3c7` / `#92400e` (ámbar PENDIENTE) — reutilizados del sufijo stale Phase 2
- Tokens `#fee2e2` / `#991b1b` (rojo BLOQUEADO) — reutilizados de `.verdict-bloqueado` existente
- Clase `.u-badge` (Phase 3) — base para el nuevo `.u-badge-estado-*`
- `.unified-filter-pill` (Phase 3) — se extiende con un nuevo pill `data-filter="bloqueado"`
- Patrón `tbody.classList.add('filter-*')` — se extiende con `filter-bloqueado`

**Fuente:** PROJECT.md "Sin build step"; Phase 2 y Phase 3 UI-SPEC mergeados.

---

## Spacing Scale

Heredada de Phase 2/3. Sin cambios.

| Token | Value | Usage en esta fase |
|-------|-------|--------------------|
| xs | 4px | Padding interno de pill, gap entre ícono y texto del estado |
| sm | 8px | Gap entre filter pills del grupo (existente) |
| md | 16px | Padding horizontal de la columna `Estado` (heredado de `.unified-qa-table td`) |
| lg | 24px | No se usa en esta fase |
| xl | 32px | No se usa en esta fase |
| 2xl | 48px | No se usa en esta fase |
| 3xl | 64px | No se usa en esta fase |

Excepciones: ninguna.

**Fuente:** Phase 3 UI-SPEC + inspección directa de `public/index.html` líneas 623–724 (CSS de `.unified-qa-table` y `.u-badge`).

---

## Typography

Heredada de Phase 2/3. Sin nuevos tamaños ni pesos.

| Role | Size | Weight | Line Height | Uso en esta fase |
|------|------|--------|-------------|-------------------|
| Body | 14px | 400 | 1.5 | (no se usa — la celda ya hereda del `td`) |
| Badge text | 11px | 700 | 1.2 | Texto "LISTO" / "PENDIENTE" / "BLOQUEADO" |
| Column header | 11px | 700 | 1 | Header `Estado` (hereda `.unified-qa-table th` con uppercase) |

> El pill "Bloqueados" reusa `.unified-filter-pill` sin modificar estilos (peso 600 heredado de Phase 3 CSS existente). Phase 5 solo declara pesos 400 y 700.

No se declaran tamaños nuevos. La fase es aditiva al contrato tipográfico de Phase 3.

**Fuente:** Phase 3 UI-SPEC + `public/index.html` líneas 634–696.

---

## Color

Sistema de color existente. La columna "Estado" reutiliza los tres tokens semánticos ya en uso (verde / ámbar / rojo) — esto es crítico porque el ojo los entrenó a lo largo de Phase 2 y Phase 3 con el mismo significado ("OK / advertencia / bloqueo"). Introducir colores nuevos rompería la memoria muscular del usuario.

| Role | Value | Usage |
|------|-------|-------|
| Dominant (60%) | `#ffffff` | Fondo de fila de la tabla (sin cambios) |
| Secondary (30%) | `#f9fafb` / `#f3f4f6` | Hover de fila, header de tabla (sin cambios) |
| Accent (10%) | `#667eea` | EXCLUSIVO: pill activo `.unified-filter-pill.active` (sin cambios — no se extiende) |
| Estado LISTO | `#d1fae5` bg + `#065f46` text | Badge "LISTO" columna Estado |
| Estado PENDIENTE | `#fef3c7` bg + `#92400e` text | Badge "PENDIENTE" columna Estado |
| Estado BLOQUEADO | `#fee2e2` bg + `#991b1b` text | Badge "BLOQUEADO" columna Estado |
| Estado sin dato | `#f3f4f6` bg + `#9ca3af` text + `#e5e7eb` border 1px | Badge "Sin evaluar" cuando `weekly-status.json` no incluye al cliente |

**Reglas de uso:**
- **No se introduce un 4º color semántico.** Los 3 estados (LISTO/PENDIENTE/BLOQUEADO) mapean 1-a-1 con los 3 colores existentes (verde/ámbar/rojo). Mantener este mapeo es un contrato visual que el usuario ya sabe leer de Phase 2 y Phase 3.
- **Accent morado `#667eea` NO se usa en la columna Estado.** Queda reservado EXCLUSIVAMENTE para: pill de filter activo, borde `:focus` de `#trendClientSelector` (Phase 3), borde `:focus` de `#runSelector` (Phase 2), y línea del trend chart cuando se filtra por cliente (Phase 3). No se extiende en Phase 5.
- **Estado "Sin evaluar" (neutro gris) requiere border 1px** para distinguirlo visualmente del fondo de la celda — mismo patrón que el badge N/A de Phase 3 (`.u-badge.u-na`).

**Accent reserved for:** `.unified-filter-pill.active` (bg morado), `#trendClientSelector:focus` border, `#runSelector:focus` border, línea del trend chart filtrado. Nada más. La columna Estado no usa accent.

**Fuente:** `public/index.html` líneas 686–696 (tokens `.u-badge.pw-ok/warn/fail`, `.cw-listo/condiciones/bloqueado`, `.u-na`), líneas 705–721 (`.unified-filter-pill.active`).

---

## Visual Hierarchy

La columna "Estado" es el **segundo focal point de la fila**, después del nombre del cliente. El orden de lectura izquierda-a-derecha de la fila:

1. **Primario:** Nombre del cliente (columna 1, 14px/700, `#111827`).
2. **Terciario (lectura detallada):** Tres badges Playwright / Cowork / Maestro (columnas 2-4, 11px/700). Estos son los *datos*.
3. **Secundario (conclusión):** Badge Estado LISTO/PENDIENTE/BLOQUEADO (columna 5, 11px/700). Esta es la *decisión*.

Paradoja aparente: "la conclusión es más importante que los datos, pero está más a la derecha que ellos". Se resuelve visualmente: el badge Estado tiene **un prefijo ícono** (`✓ ◐ ✗`) que lo hace escaneable a distancia como un "resumen" — el usuario puede recorrer toda la columna 5 con el ojo verticalmente y ver "todos los ✓" o "un ✗" sin leer las tres columnas de datos. El ícono actúa como ancla visual.

No se hace el badge Estado más grande ni de color más saturado que los demás, porque eso rompería el contrato 60/30/10 (Phase 3 ya usa los 3 tokens semánticos; saturar esta columna generaría 4 niveles competitivos).

El filter pill "Bloqueados" (nueva entrada) es un control UI secundario que vive arriba de la tabla — no compite con la columna Estado.

---

## Component Inventory — Nuevos elementos

### 1. Columna `Estado` en la tabla unificada (PROC-04)

**Ubicación:** 5ª columna de la tabla unificada existente (`#unifiedQaBody` dentro de `<div class="card">` en línea ~1491 de `public/index.html`).

**HTML target — header de la tabla:**
```html
<thead>
    <tr>
        <th class="u-col-client">Cliente</th>
        <th class="u-col-badge">Playwright</th>
        <th class="u-col-badge">Cowork</th>
        <th class="u-col-badge">Maestro</th>
        <th class="u-col-estado">Estado</th>  <!-- nueva columna -->
    </tr>
</thead>
```

**HTML target — fila de datos:**
```html
<tr data-problemas="true" data-stale="false" data-estado="pendiente">
    <td><div class="u-client-name">Codelpa</div>
        <div class="u-client-slug">codelpa</div></td>
    <td><span class="u-badge pw-warn">81%</span></td>
    <td><span class="u-badge cw-sin-reporte">Sin Cowork</span></td>
    <td><span class="u-badge u-na">N/A</span></td>
    <td><span class="u-badge estado-pendiente">◐ PENDIENTE</span></td>
</tr>
```

**CSS a agregar:**
```css
.u-col-estado { width: 14%; }  /* ajusta anchos: client 24%, 3 badges × 17%, estado 14% = 89% + scrollbar */
.u-badge.estado-listo      { background: #d1fae5; color: #065f46; }
.u-badge.estado-pendiente  { background: #fef3c7; color: #92400e; }
.u-badge.estado-bloqueado  { background: #fee2e2; color: #991b1b; }
.u-badge.estado-sin-dato   { background: #f3f4f6; color: #9ca3af; border: 1px solid #e5e7eb; }
```

**Ajuste de anchos de columnas existentes:**
```css
/* ANTES (Phase 3): client 30%, cada badge 23.33% — suma 100% */
/* DESPUÉS (Phase 5): client 24%, cada badge 18%, estado 14% — suma 92% (resto: table layout auto) */
.u-col-client { width: 24%; }   /* era 30% */
.u-col-badge  { width: 18%; }   /* era 23.33% */
.u-col-estado { width: 14%; }   /* nuevo */
```

**Data source:** `public/weekly-status.json`. Estructura esperada (definida por PROC-03):
```json
{
  "generated_at": "2026-04-21T10:00:00Z",
  "reference_date": "2026-04-21",
  "thresholds": {
    "playwright_min_pass_pct": 70,
    "maestro_min_health": 60
  },
  "clients": {
    "codelpa": { "status": "PENDIENTE", "reason": "Playwright 81% below 85% threshold" },
    "prinorte": { "status": "BLOQUEADO", "reason": "Maestro health 0/100 < 60" },
    "surtiventas": { "status": "LISTO" }
  }
}
```

**Contrato de consumo:** La UI lee EXCLUSIVAMENTE `clients[slug].status` y `clients[slug].reason`. **La UI NO calcula el estado** — eso es responsabilidad del script (PROC-03). Si `weekly-status.json` no existe o el cliente no está en `clients`, el badge es `"Sin evaluar"` (neutro).

**Fuente decisión:** REQUIREMENTS.md PROC-04 ("dashboard lee `public/weekly-status.json`"), ROADMAP.md Phase 5 criterio 2 y 4 ("Re-running the script … changes the card state without manual dashboard edits" — confirma que UI es solo lectora).

---

### 2. Badge Estado — cuatro variantes

Cada badge es un pill con ícono Unicode + etiqueta en mayúsculas. El ícono refuerza el color y permite lectura rápida vertical.

**Clase base: `.u-badge` existente** (Phase 3) + modifier `.estado-*`.

| Variante | Condición (status en JSON) | Fondo | Texto | Ícono | Label |
|----------|---------------------------|-------|-------|-------|-------|
| LISTO | `status === "LISTO"` | `#d1fae5` | `#065f46` | `✓` | `✓ LISTO` |
| PENDIENTE | `status === "PENDIENTE"` | `#fef3c7` | `#92400e` | `◐` | `◐ PENDIENTE` |
| BLOQUEADO | `status === "BLOQUEADO"` | `#fee2e2` | `#991b1b` | `✗` | `✗ BLOQUEADO` |
| Sin evaluar | cliente no está en `weekly-status.json.clients` o archivo no existe | `#f3f4f6` con border | `#9ca3af` | (sin ícono) | `Sin evaluar` |

**Decisión de íconos:** Unicode inline (`✓` U+2713, `◐` U+25D0, `✗` U+2717). No se introduce librería de íconos — consistente con Phase 2/3 (Unicode-only) y con la constraint "Sin build step" de PROJECT.md. Los tres caracteres tienen soporte universal en fuentes del sistema macOS/Windows/Linux.

**Justificación del ícono por variante:**
- `✓` (check): señal universal de aprobación.
- `◐` (círculo medio-lleno): comunica "parcial/en progreso" mejor que un signo de advertencia `⚠` (que semánticamente es "peligro", no "pendiente"). El glyph medio-lleno está visualmente entre `○` (vacío / rechazo) y `●` (lleno / aprobado) — lectura semántica inmediata.
- `✗` (cruz): señal universal de bloqueo/rechazo.

**Tooltip (hover nativo):** Cada badge tiene atributo `title="{reason}"` cuando `reason` existe en el JSON. Ejemplo: `<span class="u-badge estado-pendiente" title="Playwright 81% below 85% threshold">◐ PENDIENTE</span>`. Esto cumple PROC-04 sin agregar UI nueva — el tooltip es nativo del browser.

**Fuente decisión:** REQUIREMENTS.md PROC-04 (enumera literalmente "LISTO, PENDIENTE, BLOQUEADO"), principio de consistencia con Phase 2/3 (íconos Unicode, tokens de color reutilizados).

---

### 3. Filter pill "Bloqueados" (extensión del grupo existente)

**Ubicación:** Dentro de `<div class="unified-filter-pills" id="unifiedFilterPills">` (línea ~1494 de `public/index.html`), agregado al final del grupo existente. Orden final: `Todos | Con problemas | Stale | Bloqueados`.

**HTML target:**
```html
<div class="unified-filter-pills" id="unifiedFilterPills" role="tablist">
    <button class="unified-filter-pill active" data-filter="all" type="button">Todos</button>
    <button class="unified-filter-pill" data-filter="problemas" type="button">Con problemas</button>
    <button class="unified-filter-pill" data-filter="stale" type="button">Stale</button>
    <button class="unified-filter-pill" data-filter="bloqueado" type="button">Bloqueados</button>  <!-- nuevo -->
</div>
```

**CSS a agregar (extiende el patrón Phase 3 D-08):**
```css
#unifiedQaBody.filter-bloqueado tr:not([data-estado="bloqueado"]) { display: none; }
```

**Comportamiento:**
- Click en "Bloqueados" → oculta todas las filas excepto las que tienen `data-estado="bloqueado"`.
- Se comporta idéntico a los pills existentes (único activo a la vez, toggle via clase `active`).
- El handler JS existente en `setupUnifiedFilterPills()` (línea ~1731) ya maneja el patrón genérico `tbody.classList.add('filter-{mode}')` — solo hay que extender el bloque `if/else` con la rama `bloqueado`.

**Nota de UX:** NO se agrega pill "Listos" ni "Pendientes". Razón: el usuario normal quiere ver **todo** (pill por defecto) o **acotar problemas** ("Con problemas", "Stale", "Bloqueados"). Ver "solo los LISTOS" no es un caso de uso — para celebrar no se necesita filter. Mantener el grupo en 4 pills (vs 6) reduce carga cognitiva.

**Fuente decisión:** Extensión natural del filter pattern de Phase 3 (D-08). REQUIREMENTS.md PROC-04 sugiere que BLOQUEADO es el estado más accionable — facilitar verlo aislado es directo.

---

### 4. Atributo `data-estado` en `<tr>` (selector para filter)

**Contrato:** Cada `<tr>` del `#unifiedQaBody` debe tener `data-estado="listo|pendiente|bloqueado|sin-dato"` (lowercase, slug del status).

**Mapping:**
| status en JSON | data-estado |
|----------------|-------------|
| `"LISTO"` | `"listo"` |
| `"PENDIENTE"` | `"pendiente"` |
| `"BLOQUEADO"` | `"bloqueado"` |
| (cliente no en JSON) | `"sin-dato"` |

Consistente con los atributos existentes `data-problemas` y `data-stale` de Phase 3 (boolean string). En este caso es enum string.

---

## Copywriting Contract

| Element | Copy |
|---------|------|
| Column header nueva | `"Estado"` |
| Badge Estado LISTO | `"✓ LISTO"` |
| Badge Estado PENDIENTE | `"◐ PENDIENTE"` |
| Badge Estado BLOQUEADO | `"✗ BLOQUEADO"` |
| Badge Estado sin dato | `"Sin evaluar"` |
| Filter pill nuevo | `"Bloqueados"` |
| Tooltip (sobre badge estado) | `"{reason}"` (texto libre desde `weekly-status.json[clients][slug].reason`) |
| Tooltip cuando no hay reason | (sin atributo `title`) |
| Subtitle de la sección | `"Resumen de las tres pipelines por cliente. N/A = pipeline no aplica a este cliente."` (existente — SIN CAMBIOS) |
| Empty state tabla | `"Sin datos en este run. Ejecuta /run-playwright para poblar la tabla."` (existente — SIN CAMBIOS) |
| Empty state columna cuando JSON no existe | Todas las filas muestran `"Sin evaluar"` en la columna Estado. No hay toast ni banner de error. |

**Decisión de lenguaje — mayúsculas para los 3 estados:**
El requisito dice literalmente "LISTO / PENDIENTE / BLOQUEADO" en mayúsculas. Se respeta porque:
1. Son etiquetas-estado, no frases — mayúsculas comunican "categoría discreta" (vs oraciones).
2. 11px en weight 700 es pequeño — las mayúsculas mejoran legibilidad a ese tamaño.
3. Es consistente con la columna Cowork ("LISTO", "CON CONDICIONES", "BLOQUEADO") ya renderizada con el mismo patrón (`.u-badge.cw-listo`) — el usuario no tiene que aprender dos convenciones.

**Decisión "Sin evaluar" vs "N/A" vs "Sin dato":**
Se usa `"Sin evaluar"` (no `"N/A"`) porque:
- `"N/A"` (Phase 3) significa "esta pipeline no aplica a este cliente" — estructural (Maestro no aplica a clientes web-only). Es un estado *permanente*.
- `"Sin evaluar"` significa "el script PROC-03 aún no corrió o el JSON no tiene este cliente" — es un estado *transitorio* que el usuario puede resolver corriendo el script.
- El tercer candidato `"Sin datos"` es ambiguo (podría ser ausencia de datos de fuente). `"Sin evaluar"` es más preciso: "los datos existen, pero el veredicto no se calculó".

**Destructive actions:** Ninguna en esta fase. No hay delete/reset/edit — solo lectura.

**Fuente:** REQUIREMENTS.md PROC-04 (enumera los 3 estados en mayúsculas), MEMORY.md `feedback_qa_report_format.md` ("No testeado" como patrón para estados no-evaluados).

---

## Estado — Matriz de condiciones

| Condición | `weekly-status.json` | `clients[slug].status` | Render | `data-estado` | tooltip |
|-----------|----------------------|------------------------|--------|----------------|---------|
| Archivo no existe | 404 al fetch | — | `Sin evaluar` (neutro) | `sin-dato` | — |
| Archivo existe, slug no está | OK | `undefined` | `Sin evaluar` (neutro) | `sin-dato` | — |
| LISTO sin reason | OK | `"LISTO"` sin `reason` | `✓ LISTO` (verde) | `listo` | — |
| LISTO con reason | OK | `"LISTO"` + `reason: "…"` | `✓ LISTO` (verde) | `listo` | texto de `reason` |
| PENDIENTE | OK | `"PENDIENTE"` | `◐ PENDIENTE` (ámbar) | `pendiente` | texto de `reason` (o vacío) |
| BLOQUEADO | OK | `"BLOQUEADO"` | `✗ BLOQUEADO` (rojo) | `bloqueado` | texto de `reason` (o vacío) |
| status inválido | OK | cualquier otro string | `Sin evaluar` (neutro) + `console.warn` | `sin-dato` | — |

**Fallback robusto:** El renderer JS debe tratar cualquier status fuera del enum `{LISTO, PENDIENTE, BLOQUEADO}` como "Sin evaluar" (neutro) y emitir `console.warn('weekly-status: unknown status "{X}" for client "{slug}"')`. No debe lanzar excepción ni romper la tabla.

---

## Interaction Contract

### Carga inicial

1. Al cargar el dashboard, se invoca `loadWeeklyStatus()` (nueva función) que hace `fetch('weekly-status.json?t={timestamp}')` con cache-bust.
2. El resultado se cachea en variable global `weeklyStatusCache` (patrón consistente con `manifestCache` de Phase 3).
3. `updateUnifiedQaTable(run)` (función existente línea ~1699) se extiende para incluir la nueva columna — lee `weeklyStatusCache?.clients?.[slug]` al renderizar cada fila.
4. Si el fetch falla (404, JSON inválido, red caída), la tabla renderiza con columna Estado poblada de `"Sin evaluar"` neutro. **No se bloquea el render de las otras columnas.**

### Re-render al cambiar run (selector de Phase 2)

1. Usuario cambia `#runSelector` → evento `change`.
2. `loadRunDetails(selectedDate)` → actualiza `selectedRun`.
3. `updateClients(selectedRun)` → Phase 2.
4. `updateUnifiedQaTable(selectedRun)` → Phase 3 + **Phase 5**: re-renderiza incluyendo columna Estado.
5. **`weeklyStatusCache` NO se re-consulta.** La columna Estado refleja el veredicto que el script PROC-03 escribió la última vez, no el run histórico seleccionado. Esto es correcto porque `weekly-status.json` tiene su propio `reference_date` (generado por el script) y NO se indexa por run individual.
6. El pill "Bloqueados" mantiene su estado activo o se resetea a "Todos" (comportamiento idéntico a Phase 3 `resetUnifiedFilterPills()`).

### Click en filter pill "Bloqueados"

1. Usuario click en `.unified-filter-pill[data-filter="bloqueado"]`.
2. `setupUnifiedFilterPills()` (existente) captura el click delegado.
3. Remueve `.active` de todos los pills, agrega `.active` al clickeado.
4. `tbody.classList.remove('filter-problemas', 'filter-stale', 'filter-bloqueado')`.
5. `tbody.classList.add('filter-bloqueado')`.
6. CSS hace el resto: solo `tr[data-estado="bloqueado"]` quedan visibles.
7. **Sin animación.** Toggle directo — consistente con Phase 3.

### Hover sobre badge estado

1. Usuario hover sobre `.u-badge.estado-*`.
2. Si el `<span>` tiene atributo `title`, el browser muestra tooltip nativo después de ~1s.
3. Contenido del tooltip: `reason` literal desde el JSON (ej: "Playwright 81% below 85% threshold").
4. Si no hay `reason`, no hay tooltip. Sin fallback de texto genérico.

### Re-render cuando `weekly-status.json` cambia en el servidor

El dashboard NO hace polling de `weekly-status.json`. Se lee UNA vez al cargar. Para refrescar, el usuario recarga la página (F5). Esto es consistente con el patrón del dashboard:
- `manifest.json` se lee una vez al cargar.
- `history/*.json` se re-lee al cambiar de run, no automáticamente.
- Solo `live.json` se polea (cada 3s) porque es live state.

**Weekly status NO es live** — se actualiza manualmente cuando alguien corre el script PROC-03 (típicamente una vez al día o por semana). Polling agregaría ruido de red sin valor.

### Additive rule — NO se rompe nada existente

- El card "Estado QA por Cliente" gana una columna. Las 4 columnas existentes (Cliente, Playwright, Cowork, Maestro) NO cambian de contenido ni renderer.
- Los 3 badges existentes (`.u-badge.pw-*`, `.cw-*`, `.mt-*`) NO se modifican.
- `updateUnifiedQaTable(run)` se extiende con una llamada adicional al nuevo helper `renderEstadoBadge(slug)`. Firma pública sin cambios.
- `setupUnifiedFilterPills()` gana una rama `if (mode === 'bloqueado')` — no reemplaza la lógica existente.
- `resetUnifiedFilterPills()` se extiende para limpiar también `filter-bloqueado`.
- Tab APP, grid B2B de Phase 2, card Cowork reports, trend chart de Phase 3 — cero modificaciones.
- `loadWeeklyStatus()` es una función nueva, no reemplaza ninguna existente.
- Nada cambia si `weekly-status.json` no existe — backward compatible con versiones previas del dashboard.

### Empty states

| Estado | UI |
|--------|----|
| `weekly-status.json` no existe aún (404) | Columna Estado muestra `"Sin evaluar"` en todas las filas. Sin banner de error. Pill "Bloqueados" queda habilitado pero al clickearlo muestra 0 filas. |
| `weekly-status.json` existe pero vacío (`clients: {}`) | Igual que 404. |
| Un cliente no está en `clients` | Esa fila muestra `"Sin evaluar"` en columna Estado. Las otras columnas (Playwright/Cowork/Maestro) renderizan normalmente. |
| `selectedRun.clients` está vacío (Phase 3 existing empty state) | Tabla completa muestra `"Sin datos en este run"` (single cell colspan=5 — ajustar de 4 a 5 por la nueva columna). |

### No animations

Consistente con Phase 2/3: re-render directo, sin transitions en el badge Estado. El pill "Bloqueados" hereda la transition existente de `.unified-filter-pill` (`transition: background 0.15s, color 0.15s`) — sin cambios.

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| ninguno | n/a — vanilla CSS/JS | not applicable |

No se usa shadcn, no hay registros de terceros, no se importan librerías nuevas. Todos los estilos nuevos se agregan inline en `public/index.html`. Los íconos son Unicode del sistema — sin dependencia externa.

---

## Accessibility

- La nueva columna `Estado` se renderiza como `<th>` semántico, igual que las 4 columnas existentes. Screen readers la identifican como header de columna.
- **Contraste WCAG AA validado para los badges Estado:**
  - Verde `#d1fae5` bg + `#065f46` texto: contrast 7.8:1 ✓ (AA)
  - Ámbar `#fef3c7` bg + `#92400e` texto: contrast 5.2:1 ✓ (AA)
  - Rojo `#fee2e2` bg + `#991b1b` texto: contrast 6.4:1 ✓ (AA)
  - Neutro `#f3f4f6` bg + `#9ca3af` texto: contrast 3.1:1 — marginal. Mitigado con `border: 1px solid #e5e7eb` (refuerza forma) y con el texto "Sin evaluar" siendo secundario (usuario no necesita decidir nada con él).
- **Información no depende solo del color:** Los íconos `✓ ◐ ✗` comunican el estado de forma redundante al color. Un usuario daltónico puede distinguir LISTO/PENDIENTE/BLOQUEADO por ícono sin ver el color (el test visual: imprimir en blanco y negro y confirmar que el ícono es leíble).
- **Tooltip nativo vs custom:** Se usa el atributo `title` (tooltip nativo del browser) en vez de un tooltip custom. Ventajas: funciona sin JS, accesible por keyboard (focus + tooltip en screen readers modernos), cero código. Desventaja: formato limitado (solo texto plano) — aceptable porque `reason` es texto corto.
- **Filter pill "Bloqueados":** Hereda `role` implícito de `<button>` y `aria-pressed` no se agrega (consistente con Phase 3 donde los pills existentes tampoco lo tienen — podría ser una mejora cross-cutting futura, no de esta fase).
- **Keyboard navigation:** La tabla es scrolleable con Tab/arrow keys nativamente. No se agregan shortcut keys custom.

---

## Threshold visibility — fuera del scope UI

Los umbrales (Playwright ≥ N%, Maestro ≥ N%) son una **decisión de CONFIG, no de UI**. Viven en:

1. **Primario:** El script PROC-03 (python o shell en `tools/` — planner decide ubicación exacta).
2. **Documentación espejo:** `ai-specs/specs/qa-listo-criteria.mdc` o similar (planner decide).
3. **Visibilidad en el JSON:** `weekly-status.json.thresholds` es un sub-objeto que el script escribe para trazabilidad (ver ejemplo en sección 1).

**La UI NO muestra los umbrales.** Razones:
- El dashboard es para consumo diario; agregar "70% ≥ threshold" en la UI sería ruido (los umbrales cambian raramente).
- El tooltip `reason` ya comunica el umbral de forma contextual: `"Playwright 81% below 85% threshold"` — el usuario ve el umbral solo cuando importa (cuando el cliente NO pasó).
- Si se necesitara exponer los umbrales en la UI, sería una feature futura (ej: card "Configuración QA LISTO" en tab de admin) — fuera del scope de Phase 5.

**Fuente:** ROADMAP.md Phase 5 criterio 3 ("thresholds used for classification are documented (in the script and/or in `ai-specs/`) so the team can adjust them without reverse-engineering the code") — explícitamente dice "script y/o ai-specs", no "UI".

---

## Notas de implementación para el executor

1. **CSS a agregar:** Bloque nuevo después de la definición de `.u-badge.u-na` (línea ~696). Grupos:
   - `.u-col-estado { width: 14%; }`
   - 4 clases `.u-badge.estado-{listo|pendiente|bloqueado|sin-dato}`
   - 1 selector para el filter: `#unifiedQaBody.filter-bloqueado tr:not([data-estado="bloqueado"]) { display: none; }`
   - **Ajuste de anchos existentes:** `.u-col-client` y `.u-col-badge` deben actualizarse (24% / 18% / 18% / 18% / 14% ≈ 92% + auto).

2. **HTML a modificar:**
   - Línea ~1507: agregar `<th class="u-col-estado">Estado</th>` al `<thead>`.
   - Línea ~1510: cambiar `colspan="4"` a `colspan="5"` en el empty state del `<tr>` inicial.
   - Línea ~1497: agregar `<button class="unified-filter-pill" data-filter="bloqueado" type="button">Bloqueados</button>` al grupo de pills.

3. **JS a agregar:**
   - Nueva función `loadWeeklyStatus()` — async, hace `fetch('weekly-status.json?t={ts}')`, cachea en `weeklyStatusCache`, maneja 404 silenciosamente.
   - Nueva función `renderEstadoBadge(slug)` — retorna el HTML del span con clase correcta, ícono, label, atributo `title` condicional.
   - Invocar `loadWeeklyStatus()` en el init del dashboard, antes de la primera llamada a `updateUnifiedQaTable()`.
   - Extender `updateUnifiedQaTable(run)` (línea ~1699):
     - Antes del `.map`: `const weeklyStatus = weeklyStatusCache || { clients: {} };`
     - Dentro del `.map`: `const estadoBadge = renderEstadoBadge(slug, weeklyStatus); const estadoStatus = weeklyStatus.clients?.[slug]?.status?.toLowerCase() || 'sin-dato';`
     - Agregar al `<tr>`: `data-estado="${estadoStatus}"`.
     - Agregar 5ª columna: `<td>${estadoBadge}</td>`.
   - Extender `setupUnifiedFilterPills()` (línea ~1731) bloque `if/else` con: `else if (mode === 'bloqueado') tbody.classList.add('filter-bloqueado');`
   - Extender `resetUnifiedFilterPills()` (línea ~1749) para remover también `filter-bloqueado`.

4. **XSS safety:** El campo `reason` viene de `weekly-status.json` (archivo local, generado por script del equipo) pero aún así debe pasarse por `escapeHtml()` antes de insertarlo como atributo `title`. Consistente con cómo Phase 3 escapa nombres de cliente.

5. **Backward compat:** Si `public/weekly-status.json` no existe (primera ejecución del dashboard tras merge de Phase 5 pero antes de correr PROC-03), la tabla renderiza con "Sin evaluar" en todas las filas. Sin error visible, sin toast, sin console.error — solo `console.info('weekly-status.json not found — showing "Sin evaluar"')` para debug.

6. **NO cambiar:**
   - Los 3 renderers existentes `renderPlaywrightBadge`, `renderCoworkBadge`, `renderMaestroBadge`.
   - Las clases `.u-badge.pw-*`, `.cw-*`, `.mt-*`, `.u-na`.
   - `data-problemas` y `data-stale` de `<tr>` (se agrega `data-estado` adicional).
   - Filter pills existentes "Todos", "Con problemas", "Stale".
   - Nada del tab APP, grid B2B (Phase 2), card Cowork reports, trend chart (Phase 3), donut chart.

7. **Ordenación:** No cambia. Sigue siendo alfabética por `c.name` (D-13 Phase 3). Se descarta "ordenar por estado" porque desacopla el orden de la tabla de otras vistas y rompe la memoria muscular.

8. **Test visual:** Con 17 clientes y distribución esperada (ej: 5 LISTO, 8 PENDIENTE, 2 BLOQUEADO, 2 Sin evaluar), la columna Estado debe ser escaneable verticalmente en menos de 3 segundos. Si el usuario lee todos los íconos `✓` y ve solo uno `✗`, la tarea "¿quién está bloqueado hoy?" se resuelve sin filter.

---

## Checker Sign-Off

- [ ] Dimension 1 Copywriting: PASS
- [ ] Dimension 2 Visuals: PASS
- [ ] Dimension 3 Color: PASS
- [ ] Dimension 4 Typography: PASS
- [ ] Dimension 5 Spacing: PASS
- [ ] Dimension 6 Registry Safety: PASS

**Approval:** pending

---

## Appendix — Mockup textual (layout final)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🎯 Estado QA por Cliente                                                                         │
│ Resumen de las tres pipelines por cliente. N/A = pipeline no aplica a este cliente.              │
│ [ Todos ● ]  [ Con problemas ]  [ Stale ]  [ Bloqueados ]                                        │
│ ┌─────────────────────────────────────────────────────────────────────────────────────────┐     │
│ │ CLIENTE       │ PLAYWRIGHT       │ COWORK           │ MAESTRO   │ ESTADO                 │     │
│ ├───────────────┼──────────────────┼──────────────────┼───────────┼────────────────────────┤     │
│ │ Bastien       │ [100%]           │ [CON CONDICIONES]│ [N/A]     │ [◐ PENDIENTE]          │     │
│ │ bastien       │                  │                  │           │                        │     │
│ ├───────────────┼──────────────────┼──────────────────┼───────────┼────────────────────────┤     │
│ │ Codelpa       │ [81% · Hace 4d]  │ [Sin Cowork]     │ [N/A]     │ [◐ PENDIENTE]          │     │
│ │ codelpa       │                  │                  │           │                        │     │
│ ├───────────────┼──────────────────┼──────────────────┼───────────┼────────────────────────┤     │
│ │ Prinorte      │ [95%]            │ [LISTO]          │ [0/100]   │ [✗ BLOQUEADO]          │     │
│ │ prinorte      │                  │                  │           │                        │     │
│ ├───────────────┼──────────────────┼──────────────────┼───────────┼────────────────────────┤     │
│ │ Sonrie        │ [100%]           │ [LISTO]          │ [N/A]     │ [✓ LISTO]              │     │
│ │ sonrie        │                  │                  │           │                        │     │
│ ├───────────────┼──────────────────┼──────────────────┼───────────┼────────────────────────┤     │
│ │ Surtiventas   │ [98%]            │ [CON CONDICIONES]│ [85/100]  │ [◐ PENDIENTE]          │     │
│ │ surtiventas   │                  │                  │           │                        │     │
│ ├───────────────┼──────────────────┼──────────────────┼───────────┼────────────────────────┤     │
│ │ NewClient     │ [N/A]            │ [Sin Cowork]     │ [N/A]     │ [Sin evaluar]          │     │
│ │ newclient     │                  │                  │           │                        │     │
│ └─────────────────────────────────────────────────────────────────────────────────────────┘     │
└────────────────────────────────────────────────────────────────────────────────────────────────┘

Al hover sobre [✗ BLOQUEADO] de Prinorte → tooltip nativo: "Maestro health 0/100 < 60"
Al click en pill [ Bloqueados ] → solo queda visible la fila de Prinorte
```

---

*UI-SPEC creado: 2026-04-21*
*Fuentes: REQUIREMENTS.md (PROC-03, PROC-04), ROADMAP.md (Phase 5 success criteria), Phase 3 UI-SPEC (tokens y patrón de tabla reutilizados), Phase 2 UI-SPEC (tokens de color), public/index.html (estructura existente líneas 623–1514, 1699–1757), MEMORY.md (project_app_clients.md para contexto de app-clients en badge Maestro — sin cambios en Phase 5)*

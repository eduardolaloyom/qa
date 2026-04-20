# Phase 5: QA LISTO Weekly Status - Context

**Gathered:** 2026-04-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Implementar: (1) script Python `tools/evaluate-qa-listo.py` que evalúa criterios de deploy-readiness por cliente y escribe `public/weekly-status.json` (PROC-03), y (2) la columna "Estado" en la tabla unificada del dashboard que lee ese JSON y muestra LISTO/PENDIENTE/BLOQUEADO por cliente (PROC-04).

**Fuera de scope:** notificaciones automáticas (Slack), integración Linear, cálculo de status en el JS del cliente (la UI solo lee el JSON), polling de weekly-status.json, argumentos de fecha específica para el script.

</domain>

<decisions>
## Implementation Decisions

### Thresholds del script (PROC-03)

- **D-01:** Playwright threshold = **80%** (`PLAYWRIGHT_MIN_PASS_PCT = 80`). Rationale: un cliente con más del 20% de tests fallando no debería deployarse. Los runs recientes muestran 95-100% para clientes estables, por lo que 80% es exigente pero alcanzable.
- **D-02:** Maestro threshold = **60%** (`MAESTRO_MIN_HEALTH = 60`). Rationale: Maestro tiene menos flows que Playwright — bajo 60% implica que el flujo principal de la APP está comprometido.
- **D-03:** Los thresholds se documentan en **tres lugares**: (a) constantes al inicio del script (`PLAYWRIGHT_MIN_PASS_PCT = 80`, `MAESTRO_MIN_HEALTH = 60`), (b) en `weekly-status.json` bajo la clave `thresholds` (trazabilidad), y (c) en `ai-specs/specs/qa-listo-criteria.mdc` (lenguaje natural para el equipo). Cumple literalmente el criterio 3 del ROADMAP Phase 5.

### Lógica de clasificación (PROC-03)

- **D-04:** Clasificación por cliente — orden de evaluación (BLOQUEADO primero, LISTO último):
  1. **BLOQUEADO** si cualquiera de:
     - Playwright data existe AND `passed/tests * 100 < PLAYWRIGHT_MIN_PASS_PCT`
     - Cowork veredicto = `BLOQUEADO`
     - Maestro data existe (cliente tiene entradas `platform:app` en manifest) AND `score < MAESTRO_MIN_HEALTH`
  2. **LISTO** si todas:
     - Playwright data existe AND `passed/tests * 100 >= PLAYWRIGHT_MIN_PASS_PCT`
     - Cowork veredicto = `LISTO`
     - Maestro data no existe (N/A) OR `score >= MAESTRO_MIN_HEALTH`
  3. **PENDIENTE** en todos los demás casos (condición por defecto):
     - Playwright sin datos aún, OR
     - Cowork = `CON_CONDICIONES`, OR
     - Cowork sin reporte aún, OR
     - Mix de signals insuficiente para LISTO pero sin bloqueo explícito

- **D-05:** `CON_CONDICIONES` de Cowork → mapea a **PENDIENTE**, no a BLOQUEADO. Rationale: CON_CONDICIONES significa "QA aprobó con observaciones" — el cliente puede deployar con conciencia de las condiciones. Solo `BLOQUEADO` del veredicto Cowork impide el deploy.

- **D-06:** Cowork **sin reporte** (ninguna entrada `platform:b2b` en manifest para el cliente) → **PENDIENTE**. Rationale: falta de evidencia no es evidencia de falla. El `reason` debe decir `"Cowork: sin reporte"`.

- **D-07:** Playwright **sin datos** (cliente no aparece en ningún history JSON) → **PENDIENTE**, no BLOQUEADO. El `reason` debe decir `"Playwright: sin datos recientes"`.

- **D-08:** Maestro **N/A** = el cliente no tiene ninguna entrada `platform:app` en `public/manifest.json`. Se determina **dinámicamente por el script** — no hay lista hardcodeada de "app clients". Self-correcting: si un cliente obtiene flows Maestro, automáticamente deja de ser N/A en el próximo run del script.

### Fuente de datos y referencia temporal (PROC-03)

- **D-09:** El script evalúa el **estado más reciente por cliente**, no un run de fecha específica. Para Playwright: history JSON más reciente donde el cliente tiene datos (`passed > 0` OR `failed > 0`). Para Cowork y Maestro: entrada más reciente en `manifest.json` por `client_slug`, ordenando por `date` DESC.
- **D-10:** No se pasa argumento de fecha — el script siempre trabaja con los datos más recientes disponibles. Idempotente: puede re-correrse en cualquier momento, sobreescribe `weekly-status.json`.
- **D-11:** `reference_date` en `weekly-status.json` = fecha ISO en que corrió el script (hoy). `generated_at` = timestamp ISO completo. Consistente con UI-SPEC Component Inventory.

### Estructura del script (PROC-03)

- **D-12:** Script = `tools/evaluate-qa-listo.py`. Mirror del patrón `tools/publish-results.py`: Python 3, sin dependencias externas nuevas, ejecutable directo (`python3 tools/evaluate-qa-listo.py`).
- **D-13:** El script lee: `public/manifest.json` (Cowork + Maestro, campos `client_slug`, `platform`, `verdict`, `score`, `date`) y los `public/history/*.json` individuales (Playwright por cliente, campos `tests`, `passed`, `failed`). No lee `history/index.json` como lookup — enumera los archivos directamente con `glob("public/history/*.json")`.
- **D-14:** Output: `public/weekly-status.json`. El script termina con `git add public/weekly-status.json && git commit -m "chore(weekly-status): ..."  && git push origin main` (consistente con CLAUDE.md "commit + push en un solo flujo"). Si git push rechaza → `git pull --rebase && git push`.
- **D-15:** El script imprime un resumen por consola (tabla: cliente | status | reason) ordenado: BLOQUEADOs primero, PENDIENTEs segundo, LISTOs último. Permite validación visual sin abrir el dashboard.

### Dashboard (PROC-04)

- **D-16:** Todo el contrato de UI está en `05-UI-SPEC.md`. Puntos clave para el executor:
  - Nueva función `loadWeeklyStatus()` — fetch una vez al init, cachea en `weeklyStatusCache`
  - Nueva función `renderEstadoBadge(slug, weeklyStatus)` — helper puro que retorna `<span>` HTML con clase, ícono, label, y atributo `title` condicional
  - `updateUnifiedQaTable(run)` — extender para incluir columna 5 y `data-estado` en cada `<tr>`
  - `setupUnifiedFilterPills()` / `resetUnifiedFilterPills()` — extender con rama `bloqueado`
  - Colspan del empty state: 4 → 5
  - Ajuste de anchos: `.u-col-client` 30% → 24%, `.u-col-badge` 23.33% → 18%, nueva `.u-col-estado` 14%
- **D-17:** XSS safety: el campo `reason` se pasa por `escapeHtml()` antes de insertarlo como atributo `title`. Función ya existe en el dashboard.
- **D-18:** `weeklyStatusCache` NO se invalida al cambiar el `#runSelector`. La columna Estado es la evaluación más reciente del script, no indexada por run histórico. Esto es correcto: `weekly-status.json` tiene su propio `reference_date`.

### Claude's Discretion

- Nombres internos de funciones auxiliares del script (e.g., `load_manifest`, `load_playwright_data`, `classify_client`, `build_reason`)
- Si el script acepta `--dry-run` para preview sin escribir (útil para debugging)
- Logging a stderr vs stdout en el script
- Estructura exacta del nuevo archivo `ai-specs/specs/qa-listo-criteria.mdc`

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requisitos y criterios de fase
- `.planning/REQUIREMENTS.md` — PROC-03 (script evaluación + weekly-status.json), PROC-04 (dashboard card Estado)
- `.planning/ROADMAP.md` — Phase 5 success criteria (4 criterios: script, dashboard, documentación thresholds, re-run)
- `.planning/phases/05-qa-listo-weekly-status/05-UI-SPEC.md` — Contrato visual completo PROC-04: HTML target, CSS, atributos data, filter pill, interaction contract, empty states, matrix de condiciones

### Fuentes de datos del script
- `public/manifest.json` — estructura: `reports[]` con campos `client_slug`, `platform` (`b2b` = Cowork, `app` = Maestro), `verdict`, `score`, `date`
- `public/history/2026-04-17.json` — muestra de history JSON: `clients[slug]` con `tests`, `passed`, `failed`, `last_tested`
- `public/history/index.json` — índice de runs disponibles (referencia de estructura)

### Código a modificar (PROC-04)
- `public/index.html` líneas 623–724 — CSS de `.unified-qa-table`, `.u-badge` (agregar `.u-col-estado`, `.u-badge.estado-*`, filtro CSS `filter-bloqueado`)
- `public/index.html` líneas ~1491–1514 — HTML: `<thead>` (nuevo `<th>`), empty state (`colspan` 4→5), filter pills (nuevo pill "Bloqueados")
- `public/index.html` líneas ~1699–1757 — JS: `updateUnifiedQaTable`, `setupUnifiedFilterPills`, `resetUnifiedFilterPills`
- `public/index.html` bloque init — invocar `loadWeeklyStatus()` al cargar

### Código de referencia (patrón para el script nuevo)
- `tools/publish-results.py` — patrón de script Python: argparse, Path, json.load/dump, glob de history files, escribir a public/ y git push
- `.planning/codebase/CONVENTIONS.md` — convenciones del repo

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `public/manifest.json` — ya presente; campos `client_slug`, `platform`, `verdict`, `score`, `date` disponibles para el script.
- `public/history/{date}.json` — ya presente; campos `tests`, `passed`, `failed` calculados por `publish-results.py`.
- `escapeHtml()` en `public/index.html` — función de sanitización ya existente; usar para el campo `reason` en atributo `title`.
- `manifestCache` / `loadManifestCached()` — patrón de cache de fetch ya en el dashboard; replicar con `weeklyStatusCache` / `loadWeeklyStatus()`.
- `setupUnifiedFilterPills()` / `resetUnifiedFilterPills()` — handlers de pills en líneas ~1731/1749; extender (no reemplazar).

### Established Patterns
- **Script Python en tools/**: argparse + pathlib.Path + json.load/dump + git commit+push al final (ver `publish-results.py`)
- **Fetch con cache-bust**: `fetch('file.json?t={timestamp}')` — patrón existente en el dashboard para manifest y history
- **data-* attributes en `<tr>`**: `data-problemas`, `data-stale` ya en uso; agregar `data-estado` con mismo patrón
- **Modo fail-safe**: usar `.get()` defensivo en todos los campos del manifest/history — patrón de `publish-results.py`
- **Commit+push inmediato**: consistente con CLAUDE.md y Phase 4 (triage file)

### Integration Points
- `updateUnifiedQaTable(run)` (línea ~1699) — punto de extensión principal para la columna Estado
- `public/weekly-status.json` → se escribe a `public/` y se commitea vía git, igual que `manifest.json`
- El script de evaluación es independiente del pipeline Playwright — se corre manualmente cuando hay datos frescos de las 3 pipelines

</code_context>

<specifics>
## Specific Ideas

**Ejemplo de weekly-status.json esperado:**
```json
{
  "generated_at": "2026-04-21T10:00:00Z",
  "reference_date": "2026-04-21",
  "thresholds": {
    "playwright_min_pass_pct": 80,
    "maestro_min_health": 60
  },
  "clients": {
    "bastien": { "status": "PENDIENTE", "reason": "Cowork: CON_CONDICIONES" },
    "codelpa": { "status": "PENDIENTE", "reason": "Cowork: sin reporte" },
    "prinorte": { "status": "BLOQUEADO", "reason": "Maestro score 0 < 60" },
    "sonrie": { "status": "LISTO" },
    "surtiventas": { "status": "PENDIENTE", "reason": "Cowork: CON_CONDICIONES" }
  }
}
```

**Verificación de coherencia con UI-SPEC mockup:**
- Bastien: PW 100% ✓, CW CON_CONDICIONES → PENDIENTE ✓
- Codelpa: PW 81% ≥ 80% ✓ (pasa threshold), CW Sin Cowork → PENDIENTE ✓
- Prinorte: PW 95% ✓, CW LISTO ✓, MT 0/100 < 60 → BLOQUEADO ✓
- Sonrie: PW 100% ✓, CW LISTO ✓, MT N/A → LISTO ✓
- Surtiventas: PW 98% ✓, CW CON_CONDICIONES → PENDIENTE ✓ (MT 85/100 ≥ 60 ✓ pero CW condiciona)

**Ejemplo de output de consola al correr el script:**
```
Estado QA LISTO — 2026-04-21
─────────────────────────────────────────
BLOQUEADO  prinorte      Maestro score 0 < 60
PENDIENTE  bastien       Cowork: CON_CONDICIONES
PENDIENTE  codelpa       Cowork: sin reporte
PENDIENTE  surtiventas   Cowork: CON_CONDICIONES
LISTO      sonrie
...
─────────────────────────────────────────
1 BLOQUEADO · 8 PENDIENTES · 8 LISTOS
→ public/weekly-status.json updated
```

**Nota sobre `qa-listo-criteria.mdc`:** Debe describir los criterios en lenguaje natural: "Un cliente está LISTO cuando Playwright pasa el 80% de sus tests, Cowork entregó veredicto LISTO, y Maestro (si aplica) supera el 60%". Sin código. Para que el equipo pueda ajustar thresholds sin leer el script.

</specifics>

<deferred>
## Deferred Ideas

- Notificaciones automáticas a Slack cuando un cliente queda BLOQUEADO → NOTIF-V2-01 en REQUIREMENTS.md (v2)
- Integración Linear para auto-crear tickets desde BLOQUEADO → LINEAR-V2-01 (v2)
- Ordenar la tabla por estado (BLOQUEADOs primero) — cambia orden que el usuario ya memorizó; sería sort-on-demand, no default
- Filter pills adicionales "Listos" y "Pendientes" — ver LISTOS no es accionable; BLOQUEADO es el caso de acción
- Argumento `--date YYYY-MM-DD` para evaluar un día específico en retrospectiva — útil para auditorías; mejora futura del script

</deferred>

---

*Phase: 05-qa-listo-weekly-status*
*Context gathered: 2026-04-21*

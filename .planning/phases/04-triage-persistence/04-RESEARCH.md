# Phase 4: Triage Persistence - Research

**Researched:** 2026-04-20
**Domain:** Python file I/O + YAML parsing + markdown section scanning; integration into existing publish pipeline (`tools/publish-results.py`)
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions (17 total — D-01..D-17)

**Formato del archivo triage-{date}.md**

- **D-01:** Formato = YAML frontmatter (metadata global) + una sección `##` por `failure_group` triaged. Parseable por publish-results.py con `yaml.safe_load()` + `re.findall` de secciones.
- **D-02:** Frontmatter contiene: `client` (slug), `date` (YYYY-MM-DD), `total_failures` (int), `triaged_count` (int), `triaged_by` ("Claude" o usuario). Fields informativos — publish-results.py no falla si alguno falta.
- **D-03:** Cada sección `##` representa UN failure_group (granularidad decidida). Título de la sección = el `reason` del failure_group truncado a ~80 chars (suficiente para disambiguar). Claude incluye el `reason` completo como campo dentro de la sección para matching exacto contra `history/{date}.json`.
- **D-04:** Cada sección tiene 4 campos en un bloque YAML inline (fenced):
  - `category`: `bug` | `flaky` | `ambiente` (los 3 valores canónicos de REQUIREMENTS.md PROC-01)
  - `rationale`: string libre, multilínea permitida (por qué se clasificó así)
  - `linear_ticket`: `YOM-NNN` si es bug con ticket, `null` si no
  - `action_taken`: string libre (ej: "ticket creado", "patch aplicado a spec", "monitorear", "ignorado — error de staging conocido")
- **D-05:** El `reason` completo del failure_group se incluye como campo `reason_match` dentro de la sección — usado por publish-results.py para hacer match exacto con `failure_groups[].reason`. Evita ambigüedad cuando reasons son similares.

**Granularidad**

- **D-06:** Una decisión por `failure_group`, no por test individual.
- **D-07:** Un `triage-{date}.md` por cliente. Ubicación: `QA/{CLIENT}/{DATE}/triage-{date}.md`.
- **D-08:** Si un failure_group afecta a múltiples clientes (`failure_group.clients` >1), Claude genera la misma entrada en el triage.md de cada cliente afectado.

**Override vs Overlay**

- **D-09:** Estrategia = **overlay**. Campo `category` original NO se modifica. Se agrega campo `triage` al failure_group con subcampos `category`, `rationale`, `linear_ticket`, `action_taken`, `triaged_at`.
- **D-10:** Cuando triage.category === category (confirmación), el field `triage` SIGUE agregándose.
- **D-11:** Sin cambios visuales en el dashboard en esta fase.

**Git flow**

- **D-12:** `/triage-playwright` termina con `git add QA/{CLIENT}/{DATE}/triage-{date}.md` + commit + push inmediato. Commit message: `chore(triage): {CLIENTE} {FECHA} — {N} failure_groups classified`.
- **D-13:** `publish-results.py` re-lee el triage file en CADA publish (determinístico).
- **D-14:** Triage file se puede editar manualmente — próxima corrida re-integra.

**Fallback / edge cases**

- **D-15:** Sin triage file → no se agrega campo `triage` (comportamiento actual preservado).
- **D-16:** YAML inválido → warning + continuar SIN triage (fail-safe).
- **D-17:** Sección huérfana (no match con ningún reason) → warning + ignore.

### Claude's Discretion

- Nombres exactos de funciones Python internas (`load_triage_file`, `parse_triage_sections`, `merge_triage_into_failure_groups`).
- Estructura del YAML inline dentro de las secciones — bloque fenced ```yaml ... ``` o lista de `key: value` líneas.
- Ubicación exacta del nuevo código en `publish-results.py` (cerca de `generate_run_json` o como función separada).
- Si usar `pyyaml` (ya instalado — ver Standard Stack) o parser manual con regex.

### Deferred Ideas (OUT OF SCOPE)

- Badge visual de triage en el dashboard → Phase 5 o posterior.
- Integración Linear: auto-crear tickets desde `bug` triages → post-MVP.
- Update de `playwright-failure-analyst.md` para auto-generar archivo → puede caber aquí o deferir a Phase 6.
- Historial cross-run: "este reason apareció en 3 runs previos, triaged flaky" → requiere nueva agregación.
- Parser más robusto (múltiples reason_match por sección) → post-Phase 4 si aparece necesidad.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PROC-01 | `/triage-playwright` genera `QA/{CLIENT}/{DATE}/triage-{date}.md` con decisiones por fallo (bug/flaky/ambiente) | Sección "Triage File Format", "Code Examples" (frontmatter + fenced YAML sections). `/triage-playwright` (líneas 102-107) ya ejecuta acciones; solo necesita step 5 "escribir archivo + commit+push" (D-12). |
| PROC-02 | `publish-results.py` detecta y incorpora triage en `public/history/{date}.json` | Sección "Integration Points", "Architecture Patterns": nueva función `load_triage_for_run(date, clients)` + merge overlay ANTES de `merge_run_json`. Claves de matching D-05. Fallbacks D-15/16/17. |
</phase_requirements>

## Summary

Phase 4 entrega **persistencia de decisiones de triage** mediante dos cambios coordinados: (1) `/triage-playwright` escribe un archivo markdown por cliente en `QA/{CLIENT}/{DATE}/triage-{date}.md` con una sección por `failure_group` (YAML frontmatter + secciones ##), y (2) `tools/publish-results.py` lee opcionalmente estos archivos y agrega un campo `triage` (overlay, no override) a los `failure_group` correspondientes en `public/history/{date}.json`.

El stack es mínimo: Python stdlib (`pathlib`, `re`, `json`) + PyYAML 6.0.3 (ya instalado en el sistema, solo falta el `import yaml`). No hay dependencias nuevas ni cambios en la UI. El patrón de archivo sigue `cowork-session.md` en el mismo directorio `QA/{CLIENTE}/{FECHA}/`. La integración en `publish-results.py` se hace en `generate_run_json()` después de `generate_failure_groups()` y ANTES de `merge_run_json()`, para que el triage quede embedded en el run nuevo antes del merge con el history existente.

**Primary recommendation:** Agregar `import yaml` en `publish-results.py`, crear 3 helpers puros (`_triage_file_path`, `_parse_triage_file`, `_apply_triage_overlay`), invocarlos desde `generate_run_json()` justo después de construir `failure_groups`. El comando `/triage-playwright` se extiende con un Step 5 "Write triage file" que genera el markdown usando el template exacto de D-01..D-05 y hace commit+push inmediato por D-12.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Capturar decisiones de triage por failure_group | Comando Claude (`/triage-playwright`) | — | Claude ya conduce el triage interactivamente; agregar escritura de archivo al final es el mínimo cambio. |
| Persistir decisiones en filesystem + git | Comando Claude + git CLI | — | Patrón ya establecido en `cowork-session.md` / `qa-report-*.md`. Commit+push inmediato consistente con CLAUDE.md. |
| Leer archivos triage y fusionarlos en history JSON | `tools/publish-results.py` | — | Single entry point para publish (invocado por global-teardown + run-live.sh). Centralizar la integración evita duplicación. |
| Parsear YAML frontmatter + secciones markdown | Python stdlib + PyYAML | — | PyYAML 6.0.3 instalado; `re.findall` maneja secciones `##`. No amerita librería nueva. |
| Mapear slug → display name (QA/Codelpa/) | `data/qa-matrix-staging.json` | — | Source of truth ya existente; `load_staging_urls()` ya hace el lookup. |
| Visualizar triage en dashboard | — (Phase 5+) | — | Decisión D-11: sin UI en esta fase. Campo `triage` es metadata auditiva. |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib (`pathlib`, `re`, `json`, `sys`) | 3.9.6 | File I/O, regex, JSON | [VERIFIED: `python3 --version` local → 3.9.6]. Mismo stack que el resto de `publish-results.py`. |
| PyYAML | 6.0.3 | Parse YAML frontmatter + fenced YAML blocks | [VERIFIED: `python3 -c "import yaml; print(yaml.__version__)"` → 6.0.3]. Instalado system-wide; `yaml.safe_load()` es el estándar para YAML no confiable. |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| — | — | — | No hace falta agregar dependencies. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| PyYAML | Regex-only parser (split por `---` + split por `##` + regex `key: value`) | Elimina dep, pero no maneja bien multilínea ni quoting. **Rechazado**: PyYAML ya instalado, D-16 requiere warning limpio en YAML inválido (difícil sin parser real). |
| PyYAML para frontmatter + PyYAML para bloques | `python-frontmatter` | Otra dep, azúcar sintáctico. No justifica. |
| Fenced ```yaml block``` per section | Lista de `key: value` lines directamente bajo `##` | Ambas son parseables; fenced block es más explícito y tolerante a texto libre alrededor. **Recomendación del planner**: fenced (consistente con D-01 "un bloque YAML inline fenced"). |

**Installation:**
```bash
# Nada que instalar — PyYAML ya está en el sistema.
python3 -c "import yaml; print(yaml.__version__)"  # Expected: 6.0.3
```

**Version verification:** [VERIFIED 2026-04-20 via local Python]: `yaml` module version 6.0.3 accessible from `python3` (/Library/Developer/CommandLineTools/...). Publicado 2025-03-25 según el changelog de pyyaml — versión estable y activa.

## Architecture Patterns

### System Architecture Diagram

```
/triage-playwright (Claude)
  │
  │ 1. Lee public/history/{date}.json.failure_groups
  │ 2. Para cada group: usuario decide category/rationale/linear_ticket/action_taken
  │ 3. Agrupa decisiones por cliente (D-08: si group.clients = [c1,c2] → aparece en ambos triage.md)
  │
  ▼
Write QA/{CLIENT}/{DATE}/triage-{date}.md  ─────┐
  (frontmatter + una sección ## por group)     │
  │                                             │
  ▼                                             │
git add + commit + push (D-12, inmediato)       │
                                                │
                                                │  (archivo queda en git)
                                                │
────────────────────────────────────────────────┘

Luego (o en paralelo), cuando corre Playwright:
  │
  ▼
npx playwright test → global-teardown.ts
  │
  ▼
python3 tools/publish-results.py [--date D]
  │
  │ ┌────────────────────────────────────────────┐
  │ │ main()                                     │
  │ │   ↓                                        │
  │ │ generate_run_json(results, date)           │
  │ │   ↓                                        │
  │ │ failure_groups = generate_failure_groups() │
  │ │   ↓                                        │
  │ │ ░░ NEW: apply triage overlay ░░            │
  │ │   for slug in set(g.clients for g in      │
  │ │                   failure_groups):         │
  │ │     path = QA/{Display(slug)}/{date}/      │
  │ │            triage-{date}.md                │
  │ │     if not path.exists(): continue         │
  │ │     sections = parse_triage_file(path)     │
  │ │     for section in sections:               │
  │ │       group = find_by_reason_match(        │
  │ │                 failure_groups, section)   │
  │ │       if group: group["triage"] = ...      │
  │ │       else: warn(orphan)                   │
  │ │   ↓                                        │
  │ │ return run_json                            │
  │ │   ↓                                        │
  │ │ merge_run_json(existing, new_run_json)     │
  │ │   — triage field survives merge because    │
  │ │   new failure_groups replace old for same  │
  │ │   client set (see line 728-733 existing)   │
  │ │   ↓                                        │
  │ │ write history/{date}.json                  │
  │ └────────────────────────────────────────────┘
  ▼
public/history/{date}.json (ahora con failure_groups[].triage cuando aplica)
  ▼
Dashboard (sin cambios — lee el JSON como siempre, ignora campo desconocido)
```

### Recommended Project Structure

```
QA/
├── {CLIENTE}/                           # Display name (Bastien, Codelpa, new-soprole)
│   └── {YYYY-MM-DD}/
│       ├── cowork-session.md            # EXISTENTE
│       ├── qa-report-{date}.md          # EXISTENTE
│       └── triage-{date}.md             # NUEVO — Phase 4
└── ...

tools/
└── publish-results.py                   # MODIFICAR
    ├── import yaml                      # NUEVO (línea ~15)
    ├── def _slug_to_display_name()      # NUEVO helper (opcional; reusar load_staging_urls)
    ├── def _triage_file_path(slug, date, project_root) -> Path   # NUEVO
    ├── def _parse_triage_file(path) -> list[dict]                # NUEVO
    ├── def _apply_triage_overlay(failure_groups, date, root)     # NUEVO
    └── generate_run_json()              # MODIFICAR: invocar overlay antes del return

ai-specs/.commands/
└── triage-playwright.md                 # MODIFICAR: step 5 write file + commit+push
```

### Pattern 1: YAML Frontmatter + Fenced Section Body

**What:** Un archivo markdown con metadata YAML al principio (entre `---`), seguido de secciones `##` cada una con un bloque fenced ```yaml``` que contiene los campos estructurados.

**When to use:** Cuando el archivo necesita ser legible por humanos (Eduardo puede editarlo manualmente — D-14) Y parseable por máquina (publish-results.py — D-13).

**Example** (template a generar por `/triage-playwright`):

```markdown
---
client: codelpa
date: 2026-04-17
total_failures: 3
triaged_count: 3
triaged_by: Claude
---

# Triage — Codelpa — 2026-04-17

## Redirección incorrecta en Pipeline API catálogo

```yaml
reason_match: "Redirección incorrecta en: Pipeline API catálogo devuelve productos con nombre y pricing @catalog @critico"
category: bug
rationale: "Endpoint API retorna 302 en lugar de 200 con payload. Reproducible en staging."
linear_ticket: YOM-234
action_taken: "Ticket creado, asignado a @dev-backend"
```

## Elemento no encontrado — selector de precios

```yaml
reason_match: "Elemento no encontrado: `text=/\\\\$\\\\s*[\\\\d.,]+/`"
category: ambiente
rationale: "Selector text-regex frágil. Cambió la estructura del componente de precio en YOMCL."
linear_ticket: null
action_taken: "Patch aplicado a prices.spec.ts — usa [data-testid=price]"
```
```

**Parsing recipe** (Python):

```python
# Source: PyYAML 6.0.3 docs (yaml.safe_load) + re stdlib
import yaml, re
from pathlib import Path

def _parse_triage_file(path: Path) -> tuple[dict, list[dict]]:
    """Return (frontmatter_dict, [section_dict, ...]).
    On any YAML error, returns ({}, []) and caller logs a warning."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"⚠️  No se pudo leer {path}: {e}", file=sys.stderr)
        return ({}, [])

    # Split frontmatter (between first two '---' on their own lines)
    fm_match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not fm_match:
        print(f"⚠️  {path}: falta YAML frontmatter — skip triage file", file=sys.stderr)
        return ({}, [])

    try:
        frontmatter = yaml.safe_load(fm_match.group(1)) or {}
    except yaml.YAMLError as e:
        print(f"⚠️  {path}: YAML frontmatter inválido ({e}) — skip triage file", file=sys.stderr)
        return ({}, [])

    body = fm_match.group(2)

    # Find each "## Title\n\n```yaml\n...\n```" block
    sections = []
    # Matches: section header line, then optional blank, then ```yaml fenced block
    pattern = re.compile(
        r"^##\s+(?P<title>.+?)\n\s*```yaml\n(?P<body>.*?)\n```",
        re.MULTILINE | re.DOTALL,
    )
    for m in pattern.finditer(body):
        try:
            data = yaml.safe_load(m.group("body")) or {}
        except yaml.YAMLError as e:
            print(f"⚠️  {path}: sección '{m.group('title')[:50]}' con YAML inválido "
                  f"({e}) — skip section", file=sys.stderr)
            continue
        if not isinstance(data, dict):
            continue
        data["_title"] = m.group("title").strip()
        sections.append(data)

    return (frontmatter, sections)
```

### Pattern 2: Overlay (No Override) on failure_group

**What:** Agregar un nuevo campo (`triage`) al failure_group dict sin modificar los campos existentes (`category`, `reason`, `owner`, `action`, `count`, `tests`, `clients`, etc.).

**When to use:** Siempre que se quiera preservar auditabilidad de la decisión automática Y registrar la decisión humana (D-09, D-10).

**Example:**

```python
# Antes del overlay:
{"category": "bug", "reason": "...", "owner": "dev", ...}

# Después del overlay:
{
    "category": "bug",                   # intocado
    "reason": "...",
    "owner": "dev",
    "triage": {                          # NUEVO
        "category": "flaky",             # puede coincidir con category o no
        "rationale": "Pasó 3/4 retries",
        "linear_ticket": None,
        "action_taken": "Monitorear",
        "triaged_at": "2026-04-17",      # leído del frontmatter date
        "triaged_by": "Claude"           # leído del frontmatter triaged_by (opcional)
    },
    ...
}
```

**Implementation:**

```python
def _apply_triage_overlay(failure_groups: list[dict], date: str,
                          project_root: Path) -> None:
    """Mutate failure_groups in place: add 'triage' field where matching
    triage-{date}.md section exists. Missing files are silently ignored (D-15).
    Invalid YAML logs a warning (D-16). Orphan sections log a warning (D-17)."""

    # Collect unique (slug → display) pairs that appear in failure_groups
    staging_urls = load_staging_urls(project_root)  # already exists
    slugs = {c for g in failure_groups for c in g.get("clients", [])}

    # Index failure_groups by (client_slug, reason) for O(1) lookup
    index: dict[tuple[str, str], dict] = {}
    for g in failure_groups:
        for slug in g.get("clients", []):
            index[(slug, g.get("reason", ""))] = g

    for slug in slugs:
        path = _triage_file_path(slug, date, project_root, staging_urls)
        if not path.exists():
            continue  # D-15

        frontmatter, sections = _parse_triage_file(path)
        if not sections:
            continue  # D-16 already logged inside parser

        triaged_at = (frontmatter.get("date") or date)
        triaged_by = frontmatter.get("triaged_by", "Claude")

        for section in sections:
            reason_match = section.get("reason_match", "").strip()
            if not reason_match:
                print(f"⚠️  {path}: sección '{section.get('_title','?')}' "
                      f"sin reason_match — skip", file=sys.stderr)
                continue
            key = (slug, reason_match)
            group = index.get(key)
            if not group:
                print(f"⚠️  {path}: reason_match '{reason_match[:60]}...' "
                      f"no coincide con ningún failure_group para {slug} — skip",
                      file=sys.stderr)  # D-17
                continue

            group["triage"] = {
                "category": section.get("category"),
                "rationale": section.get("rationale"),
                "linear_ticket": section.get("linear_ticket"),
                "action_taken": section.get("action_taken"),
                "triaged_at": str(triaged_at),
                "triaged_by": str(triaged_by),
            }
```

### Pattern 3: slug → display name for QA/ directory path

**What:** El directorio `QA/` usa el display name del cliente (stripped de " (staging)"), no el slug. Para `new-soprole` el display cae a la forma del slug (cap inconsistente).

**Implementation** (reusable de `load_staging_urls`):

```python
def _triage_file_path(slug: str, date: str, project_root: Path,
                      staging_urls: dict) -> Path:
    """Return QA/{DisplayName}/{date}/triage-{date}.md for the client.
    DisplayName comes from qa-matrix-staging.json name field, stripped of
    ' (staging)' suffix. Fallback to slug.capitalize() if not found."""
    info = staging_urls.get(slug, {})
    raw_name = info.get("name", slug.capitalize())
    display = re.sub(r"\s*\(staging\)\s*$", "", raw_name).strip() or slug.capitalize()
    return project_root / "QA" / display / date / f"triage-{date}.md"
```

**⚠ Gotcha verified locally (2026-04-20):**

```
ls QA/ → Bastien, Codelpa, Prinorte, Sonrie, Soprole, Surtiventas, Tienda, new-soprole
```

`new-soprole` does NOT capitalize. This happens because the display name for `new-soprole-staging` in qa-matrix is "New Soprole (staging)" → "New Soprole" after strip, but the directory was created as `new-soprole` by `/report-qa` following a different convention. **Fallback strategy**: if `QA/{Display}/` doesn't exist but `QA/{slug}/` does, prefer the one that exists. Or simply check both.

### Anti-Patterns to Avoid

- **Override de `category` en vez de agregar `triage`**: Rompe auditabilidad — se pierde la decisión automática original. D-09 lo prohíbe explícitamente.
- **Matching por substring o fuzzy en reason**: Ambiguo cuando dos groups comparten palabras. D-05 exige match exacto con `==`.
- **Romper publish si triage file no existe**: Viola D-15 (no regresión). Siempre usar `.get()` defensivo y `if path.exists()`.
- **Levantar excepción en YAML inválido**: Viola D-16 (fail-safe). Capturar `yaml.YAMLError` + print warning + continuar sin triage.
- **Hacer merge de triage DESPUÉS de `merge_run_json`**: El merge ya reemplaza failure_groups para clientes del run nuevo (línea 728-733). Si haces overlay post-merge, tienes que preocuparte por re-aplicar a las que se mantuvieron de runs previos. **Correcto**: aplicar overlay en `generate_run_json()` ANTES del merge; así cada run tiene su propio overlay y `merge_run_json` maneja el reemplazo atómicamente.
- **Usar `eval()` o `json.loads()` sobre el YAML body**: Inseguro y no funciona. Siempre `yaml.safe_load()`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Parse YAML frontmatter | Custom splitter por `---` y `key: value` regex | `yaml.safe_load()` | Maneja quoting, listas, multilínea, nested dicts, escaping — todos edge cases que PyYAML ya resuelve. PyYAML 6.0.3 ya instalado. |
| Detect section boundaries | Iteración línea a línea con estado | `re.finditer(r"^##\\s+...\\n```yaml\\n(...)\\n```", ..., re.MULTILINE)` | Una sola regex captura exactamente el bloque fenced. Reduce bugs de parsing. |
| slug → display name | Construir desde cero | `load_staging_urls(project_root)` (existente línea 487) + strip " (staging)" | Ya hay una función que lee qa-matrix-staging.json. Reusarla. |
| Merge triage con history | Re-escribir `merge_run_json` | Aplicar overlay ANTES de `merge_run_json` | La lógica de merge existente (línea 728-733) ya reemplaza failure_groups por cliente del run nuevo. Si el triage ya está embedded en el run nuevo, sobrevive el merge sin tocar nada. |
| Command flow triage | Reescribir `/triage-playwright` | Agregar Step 5 "Write file + commit + push" al final | El flujo interactivo (líneas 44-106) ya funciona. Solo falta persistir la decisión. |

**Key insight:** El valor de Phase 4 está en **conectar dos piezas existentes** (comando triage + publish pipeline), no en construir lógica nueva. Cada función nueva debe ser pequeña (< 40 líneas), pura y testeable en aislamiento.

## Runtime State Inventory

*(Phase 4 es un cambio aditivo — no rename/refactor/migration. No hay stored data que renombrar ni state OS-registered que actualizar. Sección incluida para disciplina.)*

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | **None** — el history/{date}.json existente NO contiene campo `triage` hoy. Los nuevos runs agregarán el campo; runs pasados permanecen sin él (comportamiento aceptable: los archivos existentes quedan inalterados hasta que alguien corra triage + re-publish). | Ninguna migración de data retroactiva. |
| Live service config | **None** — sin servicios externos (Datadog, Tailscale, etc.) involucrados. | Ninguna. |
| OS-registered state | **None** — no hay Task Scheduler / launchd / systemd que embeba el nombre del archivo. | Ninguna. |
| Secrets/env vars | **None** — el triage no requiere credenciales nuevas. Linear API (ya opcional en `.env` como `LINEAR_API_KEY`) se mantiene sin cambio. | Ninguna. |
| Build artifacts | **None** — no hay egg-info, compiled binaries, ni Docker images con el nombre del archivo. | Ninguna. |

**Canonical question answer:** *Después de que cada archivo en el repo se actualice, ¿qué sistemas de runtime siguen con el nombre viejo?* → **Ninguno.** Este es un feature aditivo: nuevos archivos se crean, código nuevo los lee, campo nuevo aparece en JSON. Nada anterior requiere migración.

## Common Pitfalls

### Pitfall 1: `reason` con caracteres especiales (backticks, $, regex) rompe el matching

**What goes wrong:** El `reason` de un failure_group puede contener backticks, slashes, dollar signs (ejemplo verificado en `2026-04-17.json`: `"Elemento no encontrado: \`text=/\\\\$\\\\s*[\\\\d.,]+/\`"`). Si Claude genera `reason_match` en el triage file con escaping incorrecto, el match falla.

**Why it happens:** JSON escaping vs YAML escaping vs markdown escaping son distintos. Al copiar el reason desde history JSON al triage.md, si se decide no-quotear en YAML, los backticks y backslashes se malinterpretan.

**How to avoid:**
- El plan DEBE mandar a `/triage-playwright` que genere `reason_match` usando YAML double-quoted string (`"..."`), que soporta escape de `\\` y `\"`. No usar single-quoted (no soporta `\\`).
- En el parser Python, comparar con `==` directamente — no hacer ningún pre-procesamiento del `reason_match` antes de la comparación.

**Warning signs:** Ver warnings `"reason_match '...' no coincide con ningún failure_group para {slug}"` durante publish cuando Eduardo sabe que acaba de triaged el group.

### Pitfall 2: `/report-qa` y `/triage-playwright` crean directorios con capitalizaciones diferentes

**What goes wrong:** `/report-qa` puede crear `QA/new-soprole/2026-04-17/` (lowercase) mientras que `publish-results.py` espera `QA/New Soprole/2026-04-17/triage-2026-04-17.md` si deriva display name ingenuamente.

**Why it happens:** Verificado empíricamente: `ls QA/` devuelve `Bastien, Codelpa, ..., new-soprole` (mixed case). La lógica que crea el directorio varía entre comandos.

**How to avoid:**
- `_triage_file_path()` debe probar en orden: `QA/{Display}/{date}/` primero, `QA/{slug}/{date}/` como fallback. Usar el primero que contenga el archivo.
- `/triage-playwright` al escribir: replicar la convención que ya usó `cowork-session.md` para ese cliente. Si existe `QA/{slug}/` pero no `QA/{Display}/`, seguir usando `QA/{slug}/`. Si no existe ninguno, preferir `QA/{Display}/`.

**Warning signs:** Triage file creado en un directorio, publish busca en otro → warning "no existe triage file" pese a que sí se creó.

### Pitfall 3: `merge_run_json` borra triage de runs previos por el filtro en línea 731

**What goes wrong:** Revisar `publish-results.py` línea 728-733:

```python
new_clients = set(c for g in new.get("failure_groups", []) for c in g.get("clients", []))
kept = [g for g in existing.get("failure_groups", [])
        if not any(c in new_clients for c in g.get("clients", []))]
merged["failure_groups"] = kept + new.get("failure_groups", [])
```

Si el run nuevo contiene clientes A y B, los failure_groups existentes de A o B se descartan. Si el run nuevo NO tenía triage aplicado pero el existente SÍ, se pierde el triage.

**Why it happens:** El merge asume que un re-run de los mismos clientes reemplaza completamente sus groups. Esto es correcto para data Playwright pero problemático para triage si el overlay no se aplica en el run nuevo.

**How to avoid:**
- El overlay debe aplicarse DENTRO de `generate_run_json()` (antes de retornar el dict nuevo) — así cuando `merge_run_json` lo combina con el existente, el triage ya está en el new run_json.
- D-13: publish-results.py re-lee el triage file en CADA publish. Siempre que el archivo exista en disco, el campo se regenera. Si el archivo fue borrado, el triage desaparece (comportamiento correcto — el archivo es la fuente de verdad).

**Warning signs:** Un triage aparecía en el JSON, se corrió un test de un solo cliente, desapareció el triage de otros clientes. → confirmar que el overlay se está aplicando en `generate_run_json`, no post-merge.

### Pitfall 4: YAML `null` vs `~` vs campo ausente

**What goes wrong:** D-04 dice `linear_ticket: null` cuando no hay ticket. En YAML: `null`, `~`, y `Null` son equivalentes, pero ausencia del campo también se parsea como `None` con `.get()`. Claude puede generar cualquiera; el parser debe aceptar las variantes.

**How to avoid:**
- En `_apply_triage_overlay`, usar `section.get("linear_ticket")` — retorna `None` tanto si está ausente como si es explícitamente `null`.
- Preservar el valor tal cual como `None` en el output (no stringify).
- El dashboard (si eventualmente lee el campo) debe interpretar `None` como "sin ticket".

**Warning signs:** Ver `linear_ticket: "null"` (string) en el JSON → el parser convirtió incorrectamente.

### Pitfall 5: Triage file committed pero publish-results.py corre ANTES del pull

**What goes wrong:** Eduardo tiene una máquina con el repo local. Triage fue pusheado desde una Claude session en otra máquina. Cuando corre Playwright local, el trigger de `publish-results.py` no ve el archivo porque no hizo `git pull`.

**Why it happens:** Pipeline actual no hace pull automático antes de publish. `global-teardown.ts` y `run-live.sh` ejecutan publish-results sin sincronizar.

**How to avoid:**
- No es responsabilidad de Phase 4 resolver sync git automático. D-13 es determinístico: "si el archivo existe, integra; si no, comportamiento actual".
- Documentar en `/triage-playwright` que el commit+push hace el archivo disponible globalmente; el próximo publish en cualquier máquina lo usa.
- Si hay desincronización, la siguiente publish (con archivo pulled) re-integra correctamente.

**Warning signs:** Triage que "debería estar" ausente del history.json → Eduardo hace `git pull` y re-publica.

## Code Examples

### Example 1: Template de triage-{date}.md que debe generar `/triage-playwright`

```markdown
---
client: codelpa
date: 2026-04-17
total_failures: 3
triaged_count: 3
triaged_by: Claude
---

# Triage — Codelpa — 2026-04-17

## Redirección incorrecta en Pipeline API catálogo

```yaml
reason_match: "Redirección incorrecta en: Pipeline API catálogo devuelve productos con nombre y pricing @catalog @critico"
category: bug
rationale: |
  Endpoint API retorna 302 en lugar de 200 con payload.
  Reproducible en staging desde `/pipeline/catalog`.
linear_ticket: YOM-234
action_taken: "Ticket creado, asignado a @dev-backend"
```

## Elemento no encontrado selector de precios

```yaml
reason_match: "Elemento no encontrado: `text=/\\\\$\\\\s*[\\\\d.,]+/`"
category: ambiente
rationale: "Selector text-regex frágil. Cambió la estructura del componente de precio en YOMCL v2.3."
linear_ticket: null
action_taken: "Patch aplicado a prices.spec.ts — ahora usa [data-testid=price]"
```

## Pasaron en retry

```yaml
reason_match: "Pasaron en retry — no son bugs confirmados"
category: flaky
rationale: "1 test flaky en cv-ui-features. Pasa 3/4 retries. No es bug."
linear_ticket: null
action_taken: "Monitorear. Si persiste 3 runs consecutivos, investigar."
```
```

### Example 2: Diff esperado en `public/history/2026-04-17.json` después del overlay

```diff
 {
   "failure_groups": [
     {
       "category": "bug",
       "label": "🔴 Bug",
       "reason": "Redirección incorrecta en: Pipeline API catálogo devuelve productos con nombre y pricing @catalog @critico",
       "owner": "dev",
       "action": "Revisar el routing — la app quedó en la misma URL en lugar de avanzar al paso siguiente.",
       "count": 1,
       "tests": [...],
       "clients": ["sonrie"],
       "error_sample": "...",
       "annotations_sample": [],
-      "spec_file": "mongo-data.spec.ts"
+      "spec_file": "mongo-data.spec.ts",
+      "triage": {
+        "category": "bug",
+        "rationale": "Endpoint API retorna 302 en lugar de 200 con payload.\nReproducible en staging desde `/pipeline/catalog`.\n",
+        "linear_ticket": "YOM-234",
+        "action_taken": "Ticket creado, asignado a @dev-backend",
+        "triaged_at": "2026-04-17",
+        "triaged_by": "Claude"
+      }
     }
   ]
 }
```

### Example 3: Invocación desde `generate_run_json()`

```python
# En publish-results.py, dentro de generate_run_json(), justo antes del return:

def generate_run_json(results: dict, date: str, project_root: Path = None) -> dict:
    # ... código existente ...

    failure_groups = generate_failure_groups(results)

    # ░░ NUEVO — Phase 4: overlay triage decisions ░░
    _apply_triage_overlay(failure_groups, date, project_root)

    return {
        "date": date,
        # ... demás campos ...
        "failure_groups": failure_groups,
        # ...
    }
```

### Example 4: Commit+push flow en `/triage-playwright` Step 5

```bash
# Después de generar todos los archivos triage-{date}.md:

FILES=$(find QA -name "triage-${DATE}.md" -newer /tmp/triage-start 2>/dev/null)
CLIENTS=$(echo "$FILES" | sed -E 's|QA/([^/]+)/.*|\1|' | sort -u | paste -sd '+')
COUNT=$(echo "$FILES" | wc -l | tr -d ' ')

git add QA/*/"${DATE}"/triage-"${DATE}".md
git commit -m "chore(triage): ${CLIENTS} ${DATE} — ${COUNT} failure_groups classified"
git push || (git pull --rebase && git push)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Triage decisions se pierden en el chat | Archivo markdown committeado + overlay en history JSON | Phase 4 (esta) | Auditabilidad total; ejemplo visible en el JSON del run. |
| `category` auto-classified = decisión final | `category` auto + `triage.category` manual (overlay) | D-09 en Phase 4 | Permite mostrar tanto la clasificación del algoritmo como la decisión humana. |
| Parse markdown ad-hoc | YAML frontmatter + fenced YAML secciones + PyYAML | D-01 en Phase 4 | Formato parseable robusto y legible por humanos. |

**Deprecated/outdated:**
- *(Nada obsoleto — Phase 4 agrega sin reemplazar.)*

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Claude puede genera consistentemente YAML double-quoted strings con escaping correcto para `reason_match` | Common Pitfalls #1 | Medio — si falla, warnings "no coincide" durante publish. No rompe pipeline. El planner debe mandar a `/triage-playwright` probar el matching antes del commit (dry-run). |
| A2 | `new-soprole` es el único cliente con inconsistencia de capitalización | Common Pitfalls #2 | Bajo — la estrategia de "probar display, fallback a slug" maneja el caso genéricamente. |
| A3 | El merge de `merge_run_json` (línea 728-733) siempre descarta failure_groups de clientes del run nuevo. | Common Pitfalls #3 | Bajo — código verificado. Triage aplicado pre-merge sobrevive. |
| A4 | PyYAML 6.0.3 estará disponible en todos los ambientes donde corre publish-results (developer local, CI) | Standard Stack | Bajo — verificado local. Si CI no lo tiene, agregar `pip install pyyaml` al workflow o usar `pyyaml` como system package. Ninguna mención de CI actual en el pipeline (global-teardown salta git push en CI). |
| A5 | Eduardo no edita triage files manualmente en formatos no-estándar | D-14 + Common Pitfalls #4 | Medio — si hace copypaste de otro formato, YAML puede quebrar. D-16 (fail-safe) mitiga. |

**If this table is empty:** No aplica — hay 5 assumptions explícitos.

## Open Questions

1. **¿El `/triage-playwright` command debe actualizar también `ai-specs/.agents/playwright-failure-analyst.md`? (RESOLVED)**
   - CONTEXT.md "Deferred Ideas" lo marca explícitamente como "puede incluirse en Phase 4 si cabe en scope, o deferir a Phase 6". Recomendación: **deferir a Phase 6** (Agent Precision ya incluye AGENT-01/02/03 que tocan ese agent). Phase 4 enfoca solo en el flujo de comando + publish pipeline.

2. **¿Debe `/triage-playwright` recibir parámetro de fecha opcional o siempre usar la del run que cargó? (RESOLVED)**
   - El comando ya acepta `[FECHA]` como argumento (línea 8 de triage-playwright.md). Recomendación: reusar ese mismo argumento para el nombre del archivo (`triage-{FECHA}.md`). Si no se pasa fecha → usar la del `history/{latest}.json` leído. Consistente con el patrón existente.

3. **¿El commit+push debe hacerse una sola vez al final o un commit por cliente? (RESOLVED)**
   - D-12 dice "commit + push inmediato" con commit message que lista múltiples clientes si aplica (`chore(triage): Codelpa+Bastien 2026-04-17 — 5 failure_groups classified`). Un solo commit al final del comando. Claude agrupa todos los archivos generados en una sesión de triage.

4. **¿Qué pasa si `/triage-playwright` se corre dos veces el mismo día para el mismo cliente? (RESOLVED)**
   - D-14: "el triage file se puede editar manualmente" implica que el archivo sobrevive entre corridas. Recomendación: la segunda corrida **sobreescribe** el archivo completo (no hace append). Si Eduardo hizo edits manuales, los pierde — pero la segunda corrida es explícita, así que es aceptable. Alternativa más segura: leer archivo existente, mergear por `reason_match`, escribir result. El planner decide; recomendación es **sobreescribir** por simplicidad (matching el mental model "triage session = nueva decisión").

5. **¿Debe `publish-results.py` listar en el log qué triage files encontró y cuántas secciones aplicó? (RESOLVED)**
   - No está en CONTEXT pero es útil para debugging. Recomendación: **sí**, agregar un print al final del overlay: `ℹ️  Triage aplicado: {n_files} archivo(s), {n_sections} sección(es) matched, {n_orphans} huérfana(s)`. Consistent con el estilo de prints existente en `publish-results.py` (líneas 890-901).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3 | publish-results.py | ✓ | 3.9.6 | — |
| PyYAML | _parse_triage_file | ✓ | 6.0.3 | Regex-only parser (peor, no recomendado) |
| git | /triage-playwright commit+push | ✓ (asumido — repo activo) | — | — |
| `QA/` directory tree | triage file destination | ✓ (existente, 8 clientes con carpetas) | — | `mkdir -p` on write |
| `data/qa-matrix-staging.json` | slug → display name | ✓ (existente, usado por `load_staging_urls`) | — | fallback a `slug.capitalize()` |

**Missing dependencies with no fallback:** Ninguna.

**Missing dependencies with fallback:** Ninguna (PyYAML fallback existe pero no es necesario activarlo).

## Security Domain

> Included per research discipline. Phase 4 tiene superficie de seguridad mínima (file parsing de archivos propios del repo), pero dos patrones aplican.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | — |
| V3 Session Management | no | — |
| V4 Access Control | no | — |
| V5 Input Validation | **yes** | Usar `yaml.safe_load()` (NUNCA `yaml.load()` sin Loader). Validar tipos esperados tras parse (`isinstance(data, dict)`). |
| V6 Cryptography | no | — |

### Known Threat Patterns for Python + YAML + local file parsing

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Arbitrary code execution via `yaml.load()` con untrusted input | Elevation of Privilege | **Siempre** `yaml.safe_load()`. Nunca `yaml.load(stream)` o `Loader=yaml.Loader`. |
| Path traversal via `reason_match` o `slug` controlados | Tampering | Los slugs vienen de `failure_groups[].clients` que a su vez vienen de parsing de titles en tests — son strings safe. Display name se construye desde `qa-matrix-staging.json` controlado por el repo. No hay user input externo. Aún así, `_triage_file_path()` debe usar `Path` + `/` (no `os.path.join` con strings concatenadas). |
| Credenciales en `reason` o `rationale` accidentalmente leaked a public/history/ | Information Disclosure | `_SECRET_PATTERNS` ya existente en publish-results.py (líneas 123-140) redacta tokens del `error_sample`. **El campo `rationale` del triage NO pasa por este filtro hoy.** Recomendación: plan DEBE aplicar `mask_secrets()` al `rationale` y `action_taken` antes de embedder en el JSON publicado. |

## Sources

### Primary (HIGH confidence)
- `tools/publish-results.py` lines 1-907 — código completo de la pipeline (leído íntegro)
- `public/history/2026-04-17.json` — estructura real de failure_groups (leído íntegro)
- `.planning/phases/04-triage-persistence/04-CONTEXT.md` — 17 decisiones locked (leído íntegro)
- `.planning/REQUIREMENTS.md` — PROC-01, PROC-02 (leído íntegro)
- `.planning/ROADMAP.md` — Phase 4 success criteria (leído íntegro)
- `ai-specs/.commands/triage-playwright.md` — flujo actual del comando (leído íntegro)
- `ai-specs/.agents/playwright-failure-analyst.md` — rol actual (leído íntegro)
- `.planning/codebase/CONVENTIONS.md` — QA/{CLIENTE}/{FECHA}/ pattern (leído íntegro)
- `QA/Sonrie/2026-04-16/cowork-session.md` — ejemplo real del patrón paralelo
- Local CLI `python3 --version` → 3.9.6 [VERIFIED 2026-04-20]
- Local CLI `python3 -c "import yaml; print(yaml.__version__)"` → 6.0.3 [VERIFIED 2026-04-20]
- Local CLI `ls QA/` → 8 client dirs verified [VERIFIED 2026-04-20]
- `data/qa-matrix-staging.json` — estructura de clients[] con name/domain [VERIFIED 2026-04-20]

### Secondary (MEDIUM confidence)
- PyYAML 6.0.3 changelog (published 2025-03-25): [CITED: pypi.org/project/PyYAML/#history] — versión estable con mantenimiento activo

### Tertiary (LOW confidence)
- *(Ninguno — todas las claims verificadas contra código local o docs oficiales.)*

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — Python stdlib + PyYAML verificados localmente con versiones exactas
- Architecture: HIGH — código fuente leído íntegro; integration point identificado línea por línea
- Pitfalls: HIGH — pitfalls #1, #2, #3, #4 verificados contra archivos reales; #5 es operacional, standard
- Code examples: HIGH — todos derivados de patrones existentes en el codebase o de template en CONTEXT.md

**Research date:** 2026-04-20
**Valid until:** 2026-05-20 (30 días — stack estable, no framework cambios inminentes)

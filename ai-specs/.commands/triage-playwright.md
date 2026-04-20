# Triage Playwright

Analiza los fallos del último run de Playwright, corrobora cada uno y actúa: crea ticket en Linear, parchea el spec, o descarta.

## Usage

```
/triage-playwright
/triage-playwright 2026-04-16
/triage-playwright bastien
```

## Pasos

### 1. Adoptar rol
Adoptar el rol `playwright-failure-analyst` (ver `ai-specs/.agents/playwright-failure-analyst.md`).

### 2. Cargar resultados
- Si se pasa fecha → leer `public/history/{FECHA}.json`
- Si no → leer el archivo más reciente en `public/history/`
- Si se pasa cliente → filtrar `failure_groups` por ese cliente

Extraer:
- `failure_groups` → lista de fallos clasificados
- `stats`: total, passed, failed
- Fecha del run

Si no hay fallos (`failed == 0`) → responder "✅ Sin fallos en el último run de {FECHA}" y terminar.

### 3. Mostrar resumen inicial

```
🔍 Triage Playwright — {FECHA}
{total} tests · {passed} ✅ · {failed} ❌ · {flaky} ⚠️

Fallos a triagear:
1. [bug]      {razón} — {clientes afectados}
2. [ambiente] {razón} — {clientes afectados}
3. [flaky]    {razón} — {clientes afectados}
```

### 4. Triagear cada fallo (uno por uno)

Para cada grupo en `failure_groups` (orden: bug → ux → ambiente → flaky):

#### 4a. Mostrar contexto del fallo
```
─────────────────────────────────────────
Fallo {N}/{total}: [{CATEGORÍA}]
Razón: {reason}
Tests afectados: {count} ({tests[0]}, ...)
Clientes: {clients}
Acción sugerida: {action}
Screenshot: public/data/{screenshot si existe}
─────────────────────────────────────────
```

Si hay screenshot → mostrarlo con Read tool.

#### 4b. Decidir acción según categoría

**Si `bug` o `ux` (owner: dev):**
- Leer el spec afectado para confirmar que el test es correcto
- Si el test es correcto → proponer crear ticket Linear:
  ```
  Crear ticket Linear:
  Título: [QA] {razón corta} — {cliente}
  Descripción: {action} | Run: {fecha} | Tests: {lista}
  ¿Crear? (sí/no/skip)
  ```
- Si el test es incorrecto → ir a flujo "reescribir"

**Si `ambiente` (owner: qa):**
- Leer el spec afectado
- Identificar selector o timeout problemático
- Evaluar si el método es el problema o si hay una forma más robusta de validar lo mismo
- Proponer las opciones disponibles:
  ```
  Opciones para {test}:

  A) Parchear selector actual:
     - {línea actual}
     + {línea corregida}

  B) Método alternativo (más robusto):
     {descripción del método alternativo}
     Ej: interceptar /api/coupon en vez de buscar botón en UI

  C) Derivar a Cowork — feature visual que Playwright no captura bien

  ¿Qué hacemos? (a/b/c/skip)
  ```

**Si `flaky`:**
- Mostrar lista de tests flaky
- No crear ticket ni parchear
- Proponer annotation `.info()` para monitoreo:
  ```
  ⚠️ {count} tests flaky — pasaron en retry, no son bugs confirmados
  Monitorear en próximos runs. ¿Agregar annotation? (sí/no/skip)
  ```

#### 4c. Ejecutar acción aprobada
- **Crear ticket**: usar Linear API con `LINEAR_API_KEY` del `.env`
- **Parchear spec**: editar el archivo directamente con Edit tool
- **Skip**: pasar al siguiente fallo

### 5. Persistir decisiones — escribir triage file + commit+push

Al completar la iteración del Step 4 (o después de cada sí/no/skip final), agrupar las decisiones por cliente y escribir un archivo markdown por cliente. Este paso es OBLIGATORIO — sin él, el triage se pierde al cerrar la sesión.

#### 5a. Agrupar decisiones por cliente (D-06, D-08)

Para cada `failure_group` donde el usuario decidió (no skip):
- Si `group.clients = [c1, c2, c3]` → esa decisión se replica en el archivo de c1, c2 y c3.
- Si `group.clients = [c1]` → solo en el archivo de c1.
- Granularidad: una decisión por `failure_group`, no por test individual.

Construir un dict `decisions_by_client = { slug: [ {reason_match, category, rationale, linear_ticket, action_taken}, ... ] }`.

#### 5b. Resolver ruta del archivo (maneja capitalización mixta)

Para cada slug en `decisions_by_client`:
- `{Display}` = leer `data/qa-matrix-staging.json` → `clients[{slug}-staging].name` → strip ` (staging)` → ej "Codelpa"
- Probar orden:
  1. Si existe `QA/{Display}/{DATE}/` → usar ese directorio
  2. Si existe `QA/{slug}/{DATE}/` (lowercase) → usar ese
  3. Si no existe ninguno → crear `QA/{Display}/{DATE}/` (preferir capitalizado por default)

Esto cubre el caso `new-soprole` (directorio en lowercase) sin romper los demás.

El nombre del archivo es siempre `triage-{DATE}.md` donde `{DATE}` = la fecha del run (el argumento pasado al comando, o la extraída de `public/history/{latest}.json`).

#### 5c. Generar contenido del archivo (template exacto)

Para cada cliente, el archivo sigue este template **exacto** (D-01..D-05):

````markdown
---
client: {slug}
date: {YYYY-MM-DD}
total_failures: {total_failures_del_run}
triaged_count: {count_de_decisions_para_ese_cliente}
triaged_by: Claude
---

# Triage — {Display} — {YYYY-MM-DD}

## {título_sección_1: reason truncado a ~80 chars}

```yaml
reason_match: "{reason completo del failure_group — copiado EXACTAMENTE}"
category: {bug|flaky|ambiente}
rationale: |
  {rationale multi-línea explicando la decisión}
linear_ticket: {YOM-NNN | null}
action_taken: "{acción tomada}"
```

## {título_sección_2}

```yaml
reason_match: "..."
category: ...
rationale: |
  ...
linear_ticket: ...
action_taken: "..."
```
````

**Reglas críticas del template:**

- **reason_match DEBE ser idéntico a `failure_group.reason`**. No truncar, no editar. Usar YAML double-quoted string para permitir escape de backticks (`` ` ``), backslashes (`\\`), y símbolos regex (`$`, `*`, `.`). NUNCA usar single-quoted (no soporta `\\`).
- **El título de la sección `##`** es el `reason` truncado a ~80 chars (solo para legibilidad humana). La identidad real es `reason_match` dentro del bloque yaml.
- **Si el failure_group afecta varios clientes**, la misma sección (con el mismo reason_match) se escribe en cada archivo del cliente. `rationale` y `action_taken` son iguales por default; Eduardo puede editarlos manualmente post-commit si quiere granularidad por cliente.
- **Si `linear_ticket` es null**, escribir literalmente `linear_ticket: null` (sin comillas). El parser acepta null, ~, o ausencia.
- **Usar `rationale: |` (block scalar YAML)** para multi-línea. Indentar 2 espacios cada línea del contenido.
- **Si se re-ejecuta `/triage-playwright` el mismo día para el mismo cliente**: sobreescribir el archivo completo. Eduardo puede editarlo manualmente después; el próximo re-run lo pisa (aceptable — triage session = nueva decisión, mental model explícito).

#### 5d. Escribir archivos

```bash
mkdir -p "QA/{Display_o_slug}/{DATE}"
# Usar Write tool (no heredoc) para crear "QA/{Display_o_slug}/{DATE}/triage-{DATE}.md" con el contenido generado
```

Repetir por cada cliente en `decisions_by_client`.

#### 5e. Commit + push inmediato (D-12, CLAUDE.md global)

Después de escribir TODOS los archivos (un solo commit para todos los clientes del run):

```bash
cd /Users/lalojimenez/qa  # project root
git add QA/*/{DATE}/triage-{DATE}.md

# Derivar lista de clientes para el commit message
CLIENTS_STR=$(git diff --cached --name-only | sed -nE 's|QA/([^/]+)/.+|\1|p' | sort -u | paste -sd '+' -)
COUNT=$(git diff --cached --name-only | grep -c "triage-${DATE}.md")

git commit -m "chore(triage): ${CLIENTS_STR} ${DATE} — ${COUNT} failure_groups classified"
git push origin main || (git pull --rebase origin main && git push origin main)
```

**Ejemplos de commit message final:**
- Un solo cliente: `chore(triage): Codelpa 2026-04-17 — 3 failure_groups classified`
- Múltiples clientes: `chore(triage): Codelpa+Bastien+Sonrie 2026-04-17 — 7 failure_groups classified`

Si no hay decisiones que persistir (usuario dijo skip a todo) → omitir el Step 5 completo y saltar al Step 6 con nota "0 decisiones persistidas".

### 6. Resumen final

```
─────────────────────────────────────────
Triage completado — {FECHA}

Acciones tomadas:
✓ Ticket Linear creado: {título} → {url}
✓ Spec parcheado: {archivo} — {descripción del cambio}
⏭ Saltado: {razón}
⚠️ Flaky monitoreados: {count}

Persistencia:
✓ {N} archivo(s) triage-{FECHA}.md escrito(s) en QA/
✓ Commit: chore(triage): {CLIENTES} {FECHA} — {N} failure_groups classified
✓ Push: origin main

Próximo paso: correr los tests parcheados para verificar
npx playwright test --grep "{tests parcheados}"
─────────────────────────────────────────
```

## Reglas

- **Máximo 1 ticket por grupo de fallo** — no crear duplicados por cada test del grupo
- **Buscar primero en Linear** si ya existe un ticket abierto para el mismo fallo antes de crear uno nuevo
- **No parchear specs flaky** — solo bugs confirmados (unexpected, no flaky)
- **Siempre leer el spec** antes de proponer un patch — no asumir qué hay que cambiar
- Si hay más de 5 fallos → priorizar los de categoría `bug` primero
- **Persistir = obligatorio** — el Step 5 no es opcional. Sin archivo committeado, el triage no es auditable y no se integra al history JSON.
- **reason_match debe copiarse EXACTAMENTE** desde `failure_group.reason` — sin truncar, sin editar. Usar YAML double-quoted string para permitir escape correcto.
- **Una sección por `failure_group`, no por test individual** — el failure_group ya agrupa tests con misma causa raíz (D-06).
- **Un archivo por cliente afectado** — si un failure_group afecta a 3 clientes, la misma sección (mismo reason_match) va en los 3 archivos (D-08).
- **Re-run del mismo día sobreescribe el archivo** — edits manuales del usuario se pierden en el próximo triage session. Eduardo puede editar después del triage; los edits sobreviven hasta el próximo `/triage-playwright` del mismo cliente+fecha.
- **Commit+push es inmediato** — al final del Step 5, sin preguntar. Consistente con CLAUDE.md global.

## Archivos clave

- `public/history/` — resultados clasificados post-run
- `public/data/` — screenshots de fallos
- `tests/e2e/b2b/` — specs a parchear
- `ai-specs/.agents/playwright-failure-analyst.md` — rol a adoptar
- `QA/{CLIENT}/{DATE}/triage-{date}.md` — output del comando, committeado a git
- `tools/publish-results.py` — consumer del triage file (auto-lee en cada publish si el archivo existe)

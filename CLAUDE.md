# QA — Plataforma YOM

Suite de QA para YOM (You Order Me): B2B web, APP mobile, Admin.  
Framework: **AI Specs** — roles IA estándar, workflows automatizados, specs reutilizables.

## Lenguaje del dominio

Antes de cualquier tarea, tener presente el glosario de términos exactos de YOM:  
**`/Users/lalojimenez/Claude Context/ubiquitous-language-yom.md`**

Términos clave: Cliente ≠ Comercio ≠ Usuario. PeM, Segmento, Override, externalId, precio trampa, Staging vs Production.

## Estrategia de testing

**Cowork (Claude) es la herramienta primaria de QA.** Simula interacción humana real con la app, valida que la configuración del cliente se vea correctamente (banners, fechas, datos, flujos completos). Playwright es **obligatorio** por cliente: corre regresión automatizada y detecta roturas conocidas (post-mortems).

Orden de ejecución: Playwright (regresión E2E, corre solo) → Cowork (validación visual) → Maestro (APP mobile) → Checklists manuales (servicios backend)

Si Playwright encuentra un P0 (auth roto, checkout imposible), no continuar con Cowork hasta que esté resuelto. Cowork valida lo que Playwright no puede ver: UX, textos, banners, flujos multi-paso.

## Cuándo usar cada comando

Comandos activos como slash commands en Claude Code (vía `.claude/commands/` → `ai-specs/.commands/`):

| Situación | Comando |
|-----------|---------|
| Onboarding cliente nuevo | `/qa-plan-client {CLIENTE}` |
| Correr regresión B2B | `/run-playwright b2b` |
| Triagear fallos post-run Playwright | `/triage-playwright` o `/triage-playwright {FECHA}` |
| Suite completa (MongoDB→tests→reporte) | `/qa-client-validation {CLIENTE} staging` |
| Generar reporte desde sesión Cowork | `/report-qa {CLIENTE} {FECHA}` |
| Extraer mejoras al proceso QA | `/qa-improve {CLIENTE} {FECHA}` |
| Ver gaps de cobertura | `/qa-coverage-analysis` |
| Auditar flow APP Maestro | `/audit-maestro {FLOW}` |
| Review de PR/cambio de código | "grillame este PR desde perspectiva QA" (inline) |
| Guardar hallazgos Cowork | `agrega modo {X} al archivo de sesión de {CLIENTE}` |
| Sincronizar datos MongoDB → clients.ts | `/sync-qa-data` o `/sync-qa-data staging --client {slug}` |
| Resumen QA semanal de todos los clientes | `/weekly-qa-pulse` o `/weekly-qa-pulse {FECHA}` |
| Limpiar repo (DS_Store, PNGs viejos, dirs vacíos) | `/cleanup-repo` o `/cleanup-repo deep` |

**Cuándo NO re-extraer MongoDB:** si `data/qa-matrix-staging.json` tiene menos de 7 días y no hubo cambios de config en el cliente, saltarse extracción y correr directo `/run-playwright`.

**Cuándo reportar vs solo ver resultados:** generar reporte solo cuando hay una sesión Cowork completa o al cierre de una semana QA. Para debugging rápido, leer el HTML de Playwright directamente.

## Guardado de HANDOFFs Cowork

Cuando el usuario diga **"agrega modo X al archivo de sesión de {CLIENTE}"** o **"guarda el handoff modo X para {CLIENTE}"**:
1. Determinar la fecha: usar `YYYY-MM-DD` de hoy si no se especifica
2. Archivo destino: `QA/{CLIENTE}/{FECHA}/cowork-session.md`
3. Si el archivo no existe → crearlo con header `# Sesión Cowork — {CLIENTE} — {FECHA}`
4. Si ya existe → agregar el nuevo bloque al final (no reemplazar)
5. Si el usuario no pegó el bloque HANDOFF, pedirlo

Al final de todos los modos, `/report-qa {CLIENTE} {FECHA}` lee `cowork-session.md` y genera el reporte consolidado.

## Estructura

```
ai-specs/
├── .agents/                  # Roles IA (qa-coordinator, playwright-specialist, etc)
├── .commands/               # Workflows QA (plan-qa-client, run-playwright, etc)
├── specs/                   # Standards QA (testing, fixtures, conventions)
└── changes/                 # Planes generados por fase/cliente

checklists/                  # Casos de prueba (regresion, deuda-tecnica, servicios, funcional)
tests/e2e/b2b/              # Playwright specs B2B (tienda.youorder.me)
tests/e2e/admin/            # Playwright specs Admin (admin.youorder.me)
tests/e2e/fixtures/         # Auth y datos de clientes parametrizados
tests/app/flows/            # Maestro flows APP Android
tests/app/config/           # Config de ambiente Maestro
tools/                      # run-qa.sh, checklist-generator.py, sync-clients.py
data/                       # mongo-extractor.py, qa-matrix.json, features CSV
QA/{CLIENTE}/{FECHA}/       # Resultados por cliente y fecha
```

## Pipeline QA — Cómo funciona

```
MongoDB STAGING (solopide.me)          MongoDB PROD (youorder.me)
    ↓ mongo-extractor.py                   ↓ mongo-extractor.py
      --env staging                           --env production
      --output data/qa-matrix-staging.json    (→ data/qa-matrix.json, gitignored)
data/qa-matrix-staging.json  ←── day-to-day QA
    ↓ sync-clients.py --input data/qa-matrix-staging.json
tests/e2e/fixtures/clients.ts (AUTO-GENERADO)
    ↓
Playwright E2E (--project=b2b) → luego Cowork → luego Maestro
    ↓
QA/{CLIENTE}/{FECHA}/ (reporte HTML)
```

**Puntos clave:**
- `clients.ts` es **AUTO-GENERADO** — NO EDITAR MANUALMENTE
- Staging: `mongo-extractor.py --env staging --output data/qa-matrix-staging.json`
- Prod:    `mongo-extractor.py --env production` (escribe a `qa-matrix.json`, gitignored)
- Sync:    `sync-clients.py --input data/qa-matrix-staging.json` (staging) / `sync-clients.py` (prod)
- Credenciales en `.env`, nunca en código
- Cada cliente tiene su propia rama de staging (`{slug}.solopide.me`)

## Convenciones de nombres

- E2E specs: `{feature}.spec.ts` (ej: `cart.spec.ts`, `prices.spec.ts`)
- Maestro flows: `{cliente}-session.yaml` → `{cliente}/NN-{feature}.yaml` + `helpers/`
- Checklists: `checklist-{categoría}-{área}.md`
- Test case IDs: `{PREFIX}-{NN}` (ej: PM1, ERP-01, CART-01)
- Issue IDs: `{CLIENTE}-QA-{NNN}` (ej: Soprole-QA-001)

## Roles IA (via ai-specs/.agents/)

Los roles se aplican inline — no son sub-agentes separados. Claude adopta el rol según el contexto:

- **QA Coordinator** (`ai-specs/.agents/qa-coordinator.md`): planificación, cobertura, gaps
- **Playwright Specialist** (`ai-specs/.agents/playwright-specialist.md`): specs E2E, fixtures
- **Maestro Specialist** (`ai-specs/.agents/maestro-specialist.md`): flows APP Android
- **Data Pipeline Specialist** (`ai-specs/.agents/data-pipeline-specialist.md`): sincronización MongoDB → clients.ts, KEY_ALIASES, cuándo re-extraer
- **Weekly QA Pulse** (`ai-specs/.agents/weekly-qa-pulse.md`): síntesis semanal de estado QA por cliente (scores, trends, issues Linear)
- **Repo Cleanup Specialist** (`ai-specs/.agents/repo-cleanup-specialist.md`): qué archivos son seguros eliminar vs. protegidos

## Reglas para Claude

- `clients.ts` es AUTO-GENERADO — nunca editar manualmente
- Antes de test nuevo, verificar `checklists/INDICE.md` para evitar duplicados
- Credenciales en `.env`, nunca en código
- Para reportes usar `templates/qa-report-template.md`
- Post-mortems (PM1-PM7) en `checklists/regresion/checklist-regresion-postmortems.md`
- IDs de issues secuenciales por cliente (no saltar)

## Fuentes de verdad

- **Linear**: deuda técnica, features en desarrollo, bugs asignados
- **Notion**: features por cliente, post-mortems, wiki (lag hasta 2 semanas)
- **Slack #engineering/#tech**: bugs en producción, coordinación

## Archivos por herramienta

| Herramienta | Archivo de instrucciones |
|-------------|--------------------------|
| **Claude Code** (este) | `CLAUDE.md` — instrucciones para desarrollo, tests, automatización |
| **Cowork** (claude.ai) | `COWORK.md` — flujos QA con pasos UI, formato de reporte, escalamiento |

## Documentos principales

| Documento | Propósito |
|-----------|-----------|
| `qa-master-guide.md` | Fuente única: filosofía, responsabilidades, casos Tier 1-3, fixtures |
| `B2B_REFERENCE.md` | Referencia UI B2B: selectores, componentes, código Playwright |
| `playbook-qa-cliente-nuevo.md` | Onboarding QA completo (6 fases) |
| `qa-app-strategy.md` | Estrategia APP mobile |
| `checklists/INDICE.md` | Mapa de cobertura |
| `ai-specs/specs/qa-standards.mdc` | Estándares de testing: naming, cobertura, fixtures |
| `ai-specs/specs/maestro-standards.mdc` | Estándares Maestro flows APP |
| `ai-specs/specs/admin-testing-standards.mdc` | Estándares testing Admin |
| `ai-specs/specs/qa-coverage-mapping.mdc` | Cómo usar y mantener el mapa de cobertura |

## Patrones de prompting efectivos

- **"/qa-plan-client {CLIENTE}"** → Planificar QA completo para un cliente
- **"/run-playwright b2b"** → Ejecutar tests B2B y generar reporte
- **"grillame este PR desde perspectiva QA"** → Revisión exhaustiva de edge cases
- **"genera reporte QA para {CLIENTE}"** → Usa template + datos de sesión

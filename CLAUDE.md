# QA — Plataforma YOM

Suite de QA para YOM (You Order Me): B2B web, APP mobile, Admin.  
Framework: **AI Specs** — roles IA estándar, workflows automatizados, specs reutilizables.

## Estrategia de testing

**Cowork (Claude) es la herramienta primaria de QA.** Simula interacción humana real con la app, valida que la configuración del cliente se vea correctamente (banners, fechas, datos, flujos completos). Playwright es complementario: corre regresión automatizada y detecta roturas conocidas (post-mortems).

Prioridad: Cowork (validación visual + config) > Playwright (regresión E2E) > Maestro (APP mobile) > Checklists manuales (servicios backend)

## Comandos QA disponibles

| Comando | Propósito |
|---------|-----------|
| `/qa-plan-client {CLIENTE}` | Planificar QA para un cliente: config validation, specs, checklists |
| `/qa-client-validation {CLIENTE} {ENV}` | Ejecutar suite QA completa para un cliente (MongoDB→Playwright→Maestro→reporte) |
| `/qa-coverage-analysis` | Comparar casos esperados vs. tests existentes — identificar gaps |
| `/run-playwright {PROJECT}` | Ejecutar tests Playwright (b2b, admin, staging) |
| `/report-qa {CLIENTE} {FECHA}` | Generar reporte QA completo con hallazgos |
| `/audit-maestro {FLOW}` | Auditar flow Maestro en APP |

Usa `/qa-plan-client Codelpa` para ver ejemplo completo.

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
MongoDB (yom-stores, yom-production, yom-promotions, b2b-marketing)
    ↓ (mongo-extractor.py)
data/qa-matrix.json
    ↓ (sync-clients.py)
tests/e2e/fixtures/clients.ts (AUTO-GENERADO)
    ↓ (loginHelper + tests multi-cliente)
Playwright E2E + Maestro flows
    ↓
QA/{CLIENTE}/{FECHA}/ (reporte HTML)
```

**Puntos clave:**
- `clients.ts` es **AUTO-GENERADO** — NO EDITAR MANUALMENTE
- Siempre correr `sync-clients.py` después de cambios en `qa-matrix.json`
- Credenciales en `.env`, nunca en código
- Cada cliente tiene su propia rama de staging (`{slug}.solopide.me`)

## Convenciones de nombres

- E2E specs: `{feature}.spec.ts` (ej: `cart.spec.ts`, `prices.spec.ts`)
- Maestro flows: `{NN}-{feature}.yaml` (ej: `05-pedido.yaml`)
- Checklists: `checklist-{categoría}-{área}.md`
- Test case IDs: `{PREFIX}-{NN}` (ej: PM1, ERP-01, CART-01)
- Issue IDs: `{CLIENTE}-QA-{NNN}` (ej: Soprole-QA-001)

## Roles IA definidos

- **QA Coordinator**: Orquesta planes, mapea cobertura, identifica gaps
- **Playwright Specialist**: Escribe/audita specs E2E, config validation, fixtures
- **Maestro Specialist**: Audita flows APP, crea nuevos flows, resuelve sincronización
- **Test Validator**: Corre tests, interpreta fallos, propone fixes

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

# QA — Plataforma YOM

Suite de QA para YOM (You Order Me): B2B web, APP mobile, Admin.
11 checklists (~280 casos), 15 Playwright specs, 12 Maestro flows, herramientas Python.

## Estrategia de testing

**Cowork (Claude) es la herramienta primaria de QA.** Simula interacción humana real con la app, valida que la configuración del cliente se vea correctamente (banners, fechas, datos, flujos completos). Playwright es complementario: corre regresión automatizada y detecta roturas conocidas (post-mortems). Los tests unitarios no son foco de QA.

Prioridad: Cowork (validación visual + config) > Playwright (regresión E2E) > Maestro (APP mobile) > Checklists manuales (servicios backend)

## Estructura

```
checklists/                     — Casos de prueba por categoría (regresion, deuda-tecnica, servicios, funcional)
tests/e2e/b2b/                  — Playwright specs B2B (tienda.youorder.me)
tests/e2e/admin/                — Playwright specs Admin (admin.youorder.me)
tests/e2e/fixtures/             — Auth y datos de clientes parametrizados
tests/app/flows/                — Maestro flows APP Android (numerados)
tests/app/config/               — Config de ambiente Maestro
tools/                          — run-qa.sh, checklist-generator.py, generate_features_csv.py
data/                           — mongo-extractor.py, features CSV, qa-matrix.json
templates/                      — Reportes QA y templates de escalamiento
references/                     — Taxonomía de issues (severidad, categoría, escalamiento)
QA/{CLIENTE}/{FECHA}/           — Resultados por cliente y fecha
```

## Convenciones de nombres

- E2E specs: `{feature}.spec.ts` (ej: `cart.spec.ts`, `prices.spec.ts`)
- Maestro flows: `{NN}-{feature}.yaml` (ej: `05-pedido.yaml`, `09-concurrencia.yaml`)
- Checklists: `checklist-{categoría}-{área}.md` (ej: `checklist-deuda-tecnica-pagos.md`)
- Test case IDs: `{PREFIX}-{NN}` en checklists (ej: PM1, ERP-01, KHP-01, CART-01)
- Issue IDs: `{CLIENTE}-QA-{NNN}` en reportes (ej: Soprole-QA-001)
- Resultados: `QA/{CLIENTE}/{YYYY-MM-DD}/`

## Multi-tenant

Mismo código, distintos subdominios: `{slug}.youorder.me`

- E2E: `BASE_URL=https://{slug}.youorder.me npx playwright test`
- Maestro: editar `tests/app/config/env.yaml`
- Checklists: `python3 tools/checklist-generator.py --cliente {NOMBRE}`

## Herramientas clave

| Comando | Qué hace |
|---------|----------|
| `./tools/run-qa.sh {CLIENTE}` | Orquesta el pipeline completo: **1)** extrae de MongoDB con mongo-extractor.py **2)** regenera clients.ts con sync-clients.py **3)** genera checklist **4)** corre Playwright |
| `python3 data/mongo-extractor.py` | Extrae config de clientes desde MongoDB → `data/qa-matrix.json` |
| `python3 tools/sync-clients.py` | Genera `tests/e2e/fixtures/clients.ts` desde `data/qa-matrix.json` (AUTO-GENERADO, no editar manualmente) |
| `python3 tools/checklist-generator.py` | Genera checklist personalizado por cliente desde CSV |
| `npx playwright test --project=b2b` | Corre E2E B2B contra clientes en `clients.ts` |
| `npx playwright test --project=admin` | Corre E2E Admin |
| `maestro test tests/app/flows/` | Corre todos los flows APP |

## Fuentes de verdad

- **Linear**: deuda técnica, features en desarrollo, bugs asignados
- **Notion**: features por cliente, post-mortems, wiki técnica (puede tener lag — cruzar con Slack/git si el status importa)
- **Slack #engineering/#tech**: bugs en producción, coordinación con Diego y Rodrigo

## Documentos principales

| Documento | Propósito |
|-----------|-----------|
| `GUIA-OPERACIONAL-QA.md` | Quién hace qué, cuándo usar cada checklist |
| `qa-master-prompt.md` | ~80 casos madre (Tier 1-3), fixtures, esquemas |
| `playbook-qa-cliente-nuevo.md` | Proceso completo onboarding QA (6 fases) |
| `plan-qa-b2b.md` | Estrategia 3 capas para QA B2B |
| `qa-app-strategy.md` | Estrategia APP mobile (post-reunión con Rodrigo) |
| `checklists/INDICE.md` | Mapa de cobertura: checklist → test → estado |
| `SKILL.md` | Documento operacional del flujo QA PeM (NO es un skill de Claude) |

## Pipeline QA — Cómo funciona

El pipeline de QA está basado en MongoDB como fuente de verdad:

```
MongoDB (yom-stores, yom-production, yom-promotions, b2b-marketing)
    ↓ (mongo-extractor.py)
data/qa-matrix.json
    ↓ (sync-clients.py)
tests/e2e/fixtures/clients.ts (AUTO-GENERADO)
    ↓ (loginHelper + tests multi-cliente)
Playwright E2E
    ↓
grouped-report.html en public/
```

**Puntos clave:**
- `clients.ts` es **AUTO-GENERADO** por `sync-clients.py` desde `qa-matrix.json` — **NO EDITAR MANUALMENTE**
- Si editas datos de clientes, SIEMPRE correr: `python3 tools/sync-clients.py` para sincronizar
- Los specs multi-cliente (config-validation.spec.ts, mongo-data.spec.ts, codelpa.spec.ts, etc.) usan `clients.ts` importado directamente
- El fixture `auth.ts` está ELIMINADO — fue reemplazado por `loginHelper` + `clients.ts`

## Reglas para Claude en este repo

- Credenciales NUNCA en código — usar `.env`, `tests/e2e/.env`, `tests/app/config/env.yaml`
- `clients.ts` es AUTO-GENERADO — no editar, correr sync-clients.py si hay cambios en qa-matrix.json
- Antes de crear un test nuevo, verificar `checklists/INDICE.md` para no duplicar
- Para reportes QA usar `templates/qa-report-template.md`
- Para escalar issues usar `templates/escalation-templates.md`
- IDs de issues son secuenciales por cliente (no saltar números)
- Si se agrega un checklist o test nuevo, actualizar `checklists/INDICE.md`
- Post-mortems (PM1-PM7) están en `checklists/regresion/checklist-regresion-postmortems.md`

## Patrones de prompting efectivos

- **"grillame este PR/cambio desde perspectiva QA"** → revisión exhaustiva de edge cases
- **"usa subagents para X"** → paralelizar investigación + ejecución
- **"sabiendo todo lo que sabes del repo, rehaz esto bien"** → forzar solución elegante con contexto completo
- **"fix"** (con bug pegado de Slack/Linear) → dejar que Claude resuelva sin micromanagear
- **"genera reporte QA para {CLIENTE}"** → usa template + datos de la sesión
- **"entra en plan mode"** → antes de cualquier tarea multi-paso

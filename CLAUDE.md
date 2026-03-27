# QA — Plataforma YOM

Suite de QA para YOM (You Order Me): B2B web, APP mobile, Admin.
11 checklists (~280 casos), 15 Playwright specs, 12 Maestro flows, herramientas Python.

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
| `./tools/run-qa.sh {CLIENTE}` | Extrae MongoDB + genera checklist + corre Playwright |
| `python3 tools/checklist-generator.py` | Genera checklist personalizado por cliente desde CSV |
| `python3 data/mongo-extractor.py` | Extrae config de clientes desde MongoDB |
| `npx playwright test --project=b2b` | Corre E2E B2B |
| `npx playwright test --project=admin` | Corre E2E Admin |
| `maestro test tests/app/flows/` | Corre todos los flows APP |

## Fuentes de verdad

- **Linear**: deuda técnica, features en desarrollo, bugs asignados
- **Notion**: estado de clientes, features por cliente, post-mortems, wiki técnica
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

## Reglas para Claude en este repo

- Credenciales NUNCA en código — usar `.env`, `tests/e2e/.env`, `tests/app/config/env.yaml`
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

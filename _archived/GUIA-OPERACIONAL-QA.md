# Guia Operacional QA — YOM

> Este documento explica **qué**, **cuándo**, **quién** y **cómo** se aplica cada artefacto QA.
> Audiencia: Lalo (QA lead) + equipo Dev (Diego, Rodrigo, Daniel)

---

## Resumen del repo

El repo QA contiene **3 tipos de artefactos** que se complementan:

| Tipo | Qué es | Quién lo ejecuta | Cuántos hay |
|------|--------|-------------------|-------------|
| **Checklists** | Casos de prueba documentados para validación manual o guiada | QA (Lalo) | 11 checklists, ~280 casos |
| **E2E Playwright** | Tests automatizados que corren en browser contra B2B y Admin | Devs (en CI) + QA (manual) | 13 specs |
| **Maestro flows** | Tests automatizados de la APP mobile en emulador Android | QA (Lalo) | 10 flows |

---

## Origen de cada checklist

Cada checklist fue extraída de fuentes reales de Notion del equipo Engineering. No son casos inventados — son problemas que ya pasaron o riesgos documentados por el mismo equipo.

| Checklist | Fuente en Notion | Qué cubre |
|-----------|-----------------|-----------|
| [Regresión post-mortems](checklists/regresion/checklist-regresion-postmortems.md) | [Post-mortems](https://www.notion.so/915bf7626ea141879a941f45b2e2ec57) | 7 incidentes reales: cupones, pricing, API caída, promotions |
| [Deuda técnica — Pagos](checklists/deuda-tecnica/checklist-deuda-tecnica-pagos.md) | [Deuda Técnica](https://www.notion.so/19ad8139ba4e8061bb86cfd8db6f46fe) | paymentDocuments vs paymentItems, notas de crédito negativas |
| [Deuda técnica — General](checklists/deuda-tecnica/checklist-deuda-tecnica-general.md) | [Deuda Técnica](https://www.notion.so/19ad8139ba4e8061bb86cfd8db6f46fe) | Race conditions, migración MongoDB/Node/SSR |
| [Pricing engine](checklists/funcional/checklist-pricing-engine.md) | [Pricing — Tech Wiki](https://www.notion.so/27b1bef354734c8aa97414ca9944cee8) | Pipeline de 4 descuentos + impuestos, campos en BD |
| [Carrito B2B](checklists/funcional/checklist-carrito-b2b.md) | [Tareas de carrito](https://www.notion.so/294d8139ba4e8067b628f5af1d37e6a9) | Refresh, migración, historial, triggers |
| [Eventos GA4](checklists/funcional/checklist-eventos-ga4-b2b.md) | [[B2B] Eventos registrados](https://www.notion.so/2bdd8139ba4e80d0aeddc9f861d92b79) | 62 eventos GA4, funnel de conversión |
| [Puesta en marcha APP](checklists/funcional/checklist-puesta-en-marcha-app.md) | Proceso interno | Login, sync, pedidos, precios en app móvil |
| [Integraciones ERP](checklists/servicios/checklist-integraciones-erp.md) | [Cronjob reintento](https://www.notion.so/24fd8139ba4e80438aa0e71412c0721e) + [Hooks pedidos](https://www.notion.so/24fd8139ba4e807594c7e4f16c375c82) | Hooks, cronjob cada 30min, transformaciones por cliente |
| [Webhooks](checklists/servicios/checklist-webhooks.md) | [Webhooks — Tech Wiki](https://www.notion.so/222d8139ba4e805a9d1fd8c35d51d9c4) + [Integración estados](https://www.notion.so/17dd8139ba4e807f8b06ddfb85343c01) | 13 hooks, integración de estados, statuschangelog |
| [Fintech / Khipu](checklists/servicios/checklist-fintech-khipu.md) | [Fintech](https://www.notion.so/2dad8139ba4e801c9005f2f5f1bebcbd) | Pagos Khipu multi-tenant, onboarding nuevo cliente |
| [Integration Validator](checklists/servicios/checklist-integration-validator.md) | [Integration Validator](https://www.notion.so/320d8139ba4e80cc80d9c413e092ab2e) | Lambda de validación CSV/JSON/Excel |

---

## Quién hace qué

### QA (Lalo)

| Actividad | Herramienta | Frecuencia |
|-----------|-------------|-----------|
| Validar B2B de clientes nuevos | Playwright E2E + checklists funcionales | Cada onboarding |
| Validar APP en puesta en marcha | Maestro flows + checklist app | Cada onboarding |
| Revisar post-deploy a producción | Checklists de regresión (según área afectada) | Cada release |
| Documentar issues encontrados | Templates de escalamiento | Continuo |
| Mantener checklists actualizadas | Agregar casos cuando aparezcan bugs nuevos | Continuo |

### Devs (Diego, Rodrigo)

| Actividad | Herramienta | Frecuencia |
|-----------|-------------|-----------|
| Correr E2E antes de merge a main | `npx playwright test --project=b2b` | Cada PR |
| Agregar tests cuando fixen un bug | Nuevo `.spec.ts` o caso en spec existente | Cada fix |
| Validar integraciones ERP post-cambio | Checklist integraciones + logs erpIntegrations | Cada cambio en hooks |
| Revisar pricing post-cambio | `prices.spec.ts` + `step-pricing.spec.ts` | Cada cambio en pricing |
| Verificar que tests no estén desactivados | No dejar `describe.only` / `test.only` en código | Siempre (lección PM1) |

---

## Cuándo usar cada checklist

### En cada deploy a producción

```
Siempre:
  ✓ Correr E2E B2B completo (Playwright)
  ✓ Revisar checklist regresión post-mortems (los 7 incidentes)

Si el cambio toca pricing/promociones:
  ✓ checklist-pricing-engine.md
  ✓ step-pricing.spec.ts + promotions.spec.ts

Si el cambio toca cupones:
  ✓ coupons.spec.ts
  ✓ Sección PM1/PM2 de regresión post-mortems

Si el cambio toca pagos/cobranza:
  ✓ checklist-deuda-tecnica-pagos.md
  ✓ payments.spec.ts + flow 08-pagos.yaml

Si el cambio toca carrito:
  ✓ checklist-carrito-b2b.md
  ✓ cart.spec.ts + checkout.spec.ts

Si el cambio toca integraciones/hooks:
  ✓ checklist-integraciones-erp.md
  ✓ checklist-webhooks.md
```

### En onboarding de cliente nuevo

```
1. playbook-qa-cliente-nuevo.md (proceso completo)
2. checklist-puesta-en-marcha-app.md (si usa APP)
3. Playwright multi-cliente:
   BASE_URL=https://{nuevo-cliente}.youorder.me npx playwright test --project=b2b
4. Si usa Khipu → checklist-fintech-khipu.md (sección onboarding)
5. Si tiene hooks ERP → checklist-webhooks.md + checklist-integraciones-erp.md
```

### En migraciones de infraestructura

```
Migración MongoDB:
  ✓ checklist-deuda-tecnica-general.md → sección MG-01 a MG-06
  ✓ E2E completo pre y post migración
  ✓ Comparar datos de muestra

Upgrade Node.js:
  ✓ checklist-deuda-tecnica-general.md → sección ND-01 a ND-05

Migración a SSR (Admin o B2B):
  ✓ checklist-deuda-tecnica-general.md → sección SSR-01 a SSR-07
  ✓ E2E completo post-migración (los tests pueden necesitar ajuste)
```

### Post-incidente

```
1. Identificar qué post-mortem es más similar al incidente
2. Ejecutar la sección correspondiente de checklist-regresion-postmortems.md
3. Si no hay test automatizado para ese caso → crear uno
4. Agregar el nuevo caso a la checklist para futuros deploys
```

---

## Cómo correr los tests

### Pipeline QA Completo (MongoDB → Playwright)

El pipeline QA está integrado con MongoDB. El flujo es:

```
1. MongoDB (yom-stores, yom-production, yom-promotions, b2b-marketing)
    ↓
2. python3 data/mongo-extractor.py    → data/qa-matrix.json (config, coupons, banners, promotions)
    ↓
3. python3 tools/sync-clients.py      → tests/e2e/fixtures/clients.ts (AUTO-GENERADO)
    ↓
4. Playwright tests (multi-cliente: Codelpa, Surtiventas automáticamente)
    ↓
5. Reportes en public/ y GitHub Pages
```

**Script conveniente: `./tools/run-qa.sh`**
```bash
# Ejecuta el pipeline completo: extrae Mongo → regenera clients.ts → corre Playwright → genera reporte
./tools/run-qa.sh Codelpa          # O "Surtiventas" o sin parámetros para ambos
```

**IMPORTANTE**: 
- `clients.ts` es **AUTO-GENERADO** por `sync-clients.py` — no editar manualmente
- Cada vez que hay cambios en MongoDB, correr `mongo-extractor.py` + `sync-clients.py` antes de ejecutar tests
- Las credenciales de cada cliente se definen en `tests/e2e/.env` (no en el código)

### Playwright (B2B + Admin)

```bash
cd tests/e2e
npm install                                    # Primera vez
npx playwright install chromium                # Primera vez

# ═══════════════════════════════════════════════════════════════
# SETUP: Regenerar clients.ts desde MongoDB (requiere cada vez que cambie MongoDB)
# ═══════════════════════════════════════════════════════════════
python3 ../../data/mongo-extractor.py          # Extrae 4 DBs MongoDB → qa-matrix.json
python3 ../../tools/sync-clients.py            # qa-matrix.json → clients.ts (auto-generado)

# ═══════════════════════════════════════════════════════════════
# EJECUCIÓN: Tests multi-cliente (Codelpa, Surtiventas automáticamente)
# ═══════════════════════════════════════════════════════════════

# TODOS LOS TESTS B2B (todos los clientes en clients.ts)
npx playwright test --project=b2b

# TODOS LOS TESTS ADMIN
npx playwright test --project=admin

# UN SPEC ESPECÍFICO (corre para cada cliente)
npx playwright test --project=b2b checkout     # Todos los clientes

# SOLO UN CLIENTE (filtrar por nombre en la salida)
npx playwright test --project=b2b -g "codelpa"         # Solo tests de Codelpa
npx playwright test --project=b2b -g "surtiventas"     # Solo tests de Surtiventas

# ═══════════════════════════════════════════════════════════════
# DEBUG / MODO VISUAL
# ═══════════════════════════════════════════════════════════════
npx playwright test --project=b2b --headed             # Navegador visible
npx playwright test --project=b2b --debug              # Con debugger de Playwright
npx playwright test --project=b2b --view-report        # Abrir reporte HTML automáticamente
npx playwright show-report                             # Ver último reporte generado

# ═══════════════════════════════════════════════════════════════
# CREDENCIALES POR CLIENTE
# ═══════════════════════════════════════════════════════════════
# Archivo: tests/e2e/.env (copiar de .env.example)
# Variables requeridas por cliente activo:
CODELPA_EMAIL=user@codelpa.example
CODELPA_PASSWORD=password123
SURTIVENTAS_EMAIL=user@surtiventas.example
SURTIVENTAS_PASSWORD=password456

# Nota: Las credenciales son opcionales para algunos tests (ej: config-validation)
# pero requeridas para tests que necesitan login (ej: cart, checkout, prices)

# ═══════════════════════════════════════════════════════════════
# AGREGAR UN CLIENTE NUEVO (por defecto es cada cliente en qa-matrix.json)
# ═══════════════════════════════════════════════════════════════
# 1. Agregar cliente a MongoDB (colecciones yom-stores, yom-production, etc.)
# 2. Ejecutar: python3 ../../data/mongo-extractor.py
# 3. Ejecutar: python3 ../../tools/sync-clients.py
# 4. Verificar: cat fixtures/clients.ts | grep -i nuevocliente
# 5. Agregar credenciales: NUEVOCLIENTE_EMAIL, NUEVOCLIENTE_PASSWORD en .env
# 6. Ejecutar tests del nuevo cliente: npx playwright test --project=b2b -g "nuevocliente"
```

### Maestro (APP mobile)

```bash
# Requisito: emulador Android corriendo o dispositivo conectado

# Todos los flows
maestro test tests/app/flows/

# Un flow específico
maestro test tests/app/flows/08-pagos.yaml

# Con grabación de video
maestro record tests/app/flows/05-pedido.yaml
```

### Checklists manuales

1. Abrir el archivo `.md` correspondiente
2. Ejecutar cada caso según la columna "Cómo validar"
3. Cambiar el estado de `PENDIENTE` a `PASS` o `FAIL`
4. Si es FAIL → escalar usando templates de `templates/escalation-templates.md`

---

## Estructura de carpetas

```
qa/
├── checklists/                          ← CHECKLISTS ORGANIZADAS
│   ├── INDICE.md                        ← Mapa maestro: checklist → test → cobertura
│   ├── regresion/                       ← Post-mortems (incidentes reales)
│   │   └── checklist-regresion-postmortems.md
│   ├── deuda-tecnica/                   ← Deuda técnica documentada por el equipo
│   │   ├── checklist-deuda-tecnica-pagos.md
│   │   └── checklist-deuda-tecnica-general.md
│   ├── servicios/                       ← Backend: ERP, Khipu, Validator, Webhooks
│   │   ├── checklist-integraciones-erp.md
│   │   ├── checklist-webhooks.md
│   │   ├── checklist-fintech-khipu.md
│   │   └── checklist-integration-validator.md
│   └── funcional/                       ← Producto: pricing, carrito, GA4, app
│       ├── checklist-pricing-engine.md
│       ├── checklist-carrito-b2b.md
│       ├── checklist-eventos-ga4-b2b.md
│       └── checklist-puesta-en-marcha-app.md
│
├── tests/                               ← TESTS AUTOMATIZADOS
│   ├── e2e/                             ← Playwright (browser)
│   │   ├── b2b/                         ← 13 specs B2B
│   │   │   ├── login.spec.ts
│   │   │   ├── catalog.spec.ts
│   │   │   ├── cart.spec.ts
│   │   │   ├── checkout.spec.ts
│   │   │   ├── prices.spec.ts
│   │   │   ├── coupons.spec.ts          ← Regresión PM1/PM2
│   │   │   ├── step-pricing.spec.ts     ← Regresión PM4
│   │   │   ├── promotions.spec.ts       ← Regresión PM5
│   │   │   ├── payments.spec.ts         ← Deuda técnica
│   │   │   ├── config-validation.spec.ts
│   │   │   └── multi-client.spec.ts
│   │   ├── admin/                       ← 2 specs Admin
│   │   │   ├── login.spec.ts
│   │   │   └── orders.spec.ts
│   │   └── playwright.config.ts
│   └── app/                             ← Maestro (Android)
│       └── flows/
│           ├── 01-login.yaml
│           ├── 02-sync.yaml
│           ├── 03-comercios.yaml
│           ├── 04-catalogo.yaml
│           ├── 05-pedido.yaml
│           ├── 06-precios.yaml
│           ├── 07-offline.yaml
│           ├── 08-pagos.yaml            ← Deuda técnica
│           ├── 09-concurrencia.yaml     ← Deuda técnica
│           └── 10-descuentos.yaml       ← Regresión PM3
│
├── GUIA-OPERACIONAL-QA.md              ← ESTE DOCUMENTO
├── playbook-qa-cliente-nuevo.md         ← Paso a paso onboarding
├── qa-master-prompt.md                  ← Casos de prueba madre (~80 casos)
├── plan-qa-b2b.md                       ← Estrategia QA B2B
└── qa-app-strategy.md                   ← Estrategia QA APP
```

---

## Mantenimiento

### Agregar un caso nuevo

1. Identificar a qué checklist pertenece (regresión, deuda técnica, servicios, funcional)
2. Agregar el caso con ID secuencial al final de la tabla correspondiente
3. Si es automatizable → crear o extender el `.spec.ts` o `.yaml`
4. Actualizar `checklists/INDICE.md` si se creó una checklist nueva

### Después de un incidente en producción

1. Documentar el incidente en `checklists/regresion/checklist-regresion-postmortems.md`
2. Crear test automatizado si el caso es reproducible en E2E
3. Agregar a la lista de "siempre correr pre-deploy"

### Fuentes a revisar periódicamente

| Fuente | Qué buscar | Frecuencia |
|--------|-----------|-----------|
| [Post-mortems (Notion)](https://www.notion.so/915bf7626ea141879a941f45b2e2ec57) | Incidentes nuevos → casos de regresión | Semanal |
| [Deuda Técnica (Notion)](https://www.notion.so/19ad8139ba4e8061bb86cfd8db6f46fe) | Items nuevos o resueltos | Quincenal |
| [Tareas de carrito (Notion)](https://www.notion.so/294d8139ba4e8067b628f5af1d37e6a9) | Progreso del refactor → ajustar tests | Según avance |
| Slack #tech | Bugs reportados, cambios de último minuto | Diario |
| GitHub PRs | Qué áreas están siendo modificadas | Diario |

# Índice QA — Cobertura de tests

> Mapeo entre checklists, tests automatizados y fuentes.
> Última actualización: 2026-04-19

---

## Estructura del repo

```
qa/
├── checklists/                    # Checklists por categoría
│   ├── regresion/                 # Basadas en incidentes reales
│   ├── deuda-tecnica/             # Basadas en deuda técnica documentada
│   ├── servicios/                 # Servicios backend (ERP, Fintech, Validator)
│   └── funcional/                 # Funcionalidad de producto (carrito, app)
├── tests/
│   ├── e2e/
│   │   ├── b2b/                   # Playwright — B2B (tienda.youorder.me)
│   │   └── admin/                 # Playwright — Admin (admin.youorder.me)
│   └── app/
│       └── flows/                 # Maestro — App móvil (Android)
└── *.md                           # Planes, estrategias, reportes
```

---

## Mapa de cobertura

### Regresión (post-mortems)

| ID | Incidente | Checklist | Test automatizado | Cobertura |
|---|-----------|-----------|-------------------|-----------|
| PM1 | Error al ordenar con cupones | [postmortems](regresion/checklist-regresion-postmortems.md#pm-1) | [coupons.spec.ts](../tests/e2e/b2b/coupons.spec.ts) | E2E B2B |
| PM2 | Cupones de orden no soportados B2B | [postmortems](regresion/checklist-regresion-postmortems.md#pm-2) | [coupons.spec.ts](../tests/e2e/b2b/coupons.spec.ts) | E2E B2B |
| PM3 | Crash descuentos App Móvil | [postmortems](regresion/checklist-regresion-postmortems.md#pm-3) | [10-descuentos.yaml](../tests/app/flows/10-descuentos.yaml) | Maestro App |
| PM4 | Step pricing Soprole | [postmortems](regresion/checklist-regresion-postmortems.md#pm-4) | [step-pricing.spec.ts](../tests/e2e/b2b/step-pricing.spec.ts) | E2E B2B |
| PM5 | Promotions colapsado | [postmortems](regresion/checklist-regresion-postmortems.md#pm-5) | [promotions.spec.ts](../tests/e2e/b2b/promotions.spec.ts) | E2E B2B |
| PM6 | Índices MongoDB faltantes | [postmortems](regresion/checklist-regresion-postmortems.md#pm-6) | — | Manual/API |
| PM7 | Cheerio sin pinear | [postmortems](regresion/checklist-regresion-postmortems.md#pm-7) | — | Manual/CI |

### Deuda técnica

| Área | Checklist | Test automatizado | Cobertura |
|------|-----------|-------------------|-----------|
| Pagos (paymentDocuments/Items) | [pagos](deuda-tecnica/checklist-deuda-tecnica-pagos.md) | [payments.spec.ts](../tests/e2e/b2b/payments.spec.ts) + [08-pagos.yaml](../tests/app/flows/08-pagos.yaml) | E2E B2B + Maestro App |
| Race conditions (background thread) | [general](deuda-tecnica/checklist-deuda-tecnica-general.md#1) | [09-concurrencia.yaml](../tests/app/flows/09-concurrencia.yaml) | Maestro App |
| Migración MongoDB | [general](deuda-tecnica/checklist-deuda-tecnica-general.md#2) | — | Manual (al migrar) |
| Upgrade Node.js | [general](deuda-tecnica/checklist-deuda-tecnica-general.md#3) | — | Manual (al migrar) |
| Migración SSR | [general](deuda-tecnica/checklist-deuda-tecnica-general.md#4) | — | Manual (al migrar) |

### Pre-producción (integraciones de cliente)

| Checklist | Cuándo usar | Cobertura |
|-----------|-------------|-----------|
| [Pre-producción cliente](integraciones/checklist-preproduccion-cliente.md) | Cliente nuevo + re-validación por deuda técnica | Config MongoDB, catálogo, usuarios, ERP, docs tributarios |

### Servicios backend

| Servicio | Checklist | Test automatizado | Cobertura |
|----------|-----------|-------------------|-----------|
| Integraciones ERP + Reintento | [integraciones](servicios/checklist-integraciones-erp.md) | — | Manual/API |
| Webhooks (13 hooks) | [webhooks](servicios/checklist-webhooks.md) | — | Manual/API |
| Fintech / Khipu | [khipu](servicios/checklist-fintech-khipu.md) | — | Manual/API |
| Integration Validator (Lambda) | [validator](servicios/checklist-integration-validator.md) | — | Manual/API |

### Funcional

| Área | Checklist | Test automatizado | Cobertura |
|------|-----------|-------------------|-----------|
| Motor de Pricing | [pricing](funcional/checklist-pricing-engine.md) | [prices.spec.ts](../tests/e2e/b2b/prices.spec.ts) | E2E B2B (parcial) |
| Carrito B2B | [carrito](funcional/checklist-carrito-b2b.md) | [cart.spec.ts](../tests/e2e/b2b/cart.spec.ts) | E2E B2B (parcial) |
| Eventos GA4 B2B (62 eventos) | [ga4](funcional/checklist-eventos-ga4-b2b.md) | — | Pendiente E2E |
| Puesta en marcha App | [app](funcional/checklist-puesta-en-marcha-app.md) | [01-07 flows](../tests/app/flows/) | Maestro App |
| Login Admin | — | [admin/login.spec.ts](../tests/e2e/admin/login.spec.ts) | E2E Admin |
| Órdenes Admin | — | [admin/orders.spec.ts](../tests/e2e/admin/orders.spec.ts) | E2E Admin |

---

## Tests automatizados por plataforma

### Playwright E2E — B2B (`npx playwright test --project=b2b`)

| Spec | Casos | Origen |
|------|-------|--------|
| catalog.spec.ts | Catálogo, búsqueda, categorías | Flujo C2 |
| cart.spec.ts | Carrito, cantidades, monto mínimo | Flujo C2 |
| checkout.spec.ts | Checkout, doble click, historial | Flujo C2 |
| prices.spec.ts | Precios, descuentos, impuestos, cupón field | Flujo C3 |
| orders.spec.ts | Historial de pedidos, carga de órdenes | Flujo C2 |
| **coupons.spec.ts** | Cupón inválido, orden sin cupón, loading | **Post-mortem PM1/PM2** |
| **step-pricing.spec.ts** | Escalones, cambio cantidad, precios rotos | **Post-mortem PM4** |
| **promotions.spec.ts** | Catálogo con promos, totales, timeout | **Post-mortem PM5** |
| **payments.spec.ts** | Historial pagos, montos negativos, tributarios | **Deuda técnica** |
| **payment-documents.spec.ts** | Documentos tributarios (C7): acceso y bloqueo | Config condicional |
| **mongo-data.spec.ts** | Cupones, banners y promotions desde MongoDB | Datos operacionales |
| **config-validation/** | Config multi-tenant (65 tests en 6 archivos) | Validación |
| ↳ cv-access.spec.ts | Acceso: anónimo, login, maintenance | Validación |
| ↳ cv-catalog.spec.ts | Catálogo: filtros, categorías, búsqueda | Validación |
| ↳ cv-cart.spec.ts | Carrito: monto mínimo, unidades, cupones | Validación |
| ↳ cv-payments.spec.ts | Pagos: métodos, OC, historial | Validación |
| ↳ cv-orders.spec.ts | Órdenes: confirmación, despacho, tracking | Validación |
| ↳ cv-ui-features.spec.ts | UI: banners, descuentos, precios, idioma | Validación |
| multi-client.spec.ts | Múltiples clientes paralelos | Multi-tenant |

### Playwright E2E — Admin (`npx playwright test --project=admin`)

| Spec | Casos | Checklist | Origen |
|------|-------|-----------|--------|
| **login.spec.ts** | Login, error, ruta protegida | [checklist-admin-acceso.md](../checklists/funcional/checklist-admin-acceso.md) | **Deuda técnica** |
| **orders.spec.ts** | Listado, detalle, pagos | [checklist-admin-ordenes.md](../checklists/funcional/checklist-admin-ordenes.md) | **Deuda técnica** |
| **stores.spec.ts** | Config admin → reflejo en B2B | [checklist-admin-reportes.md](../checklists/funcional/checklist-admin-reportes.md) | **Deuda técnica** |
| *(pendiente)* | Reportes y exportación | [checklist-admin-reportes.md](../checklists/funcional/checklist-admin-reportes.md) | Manual |

### Maestro — App móvil (`./tools/run-maestro.sh <cliente>`)

Patrón de flows desde 2026-04-17: cada cliente usa un `{cliente}-session.yaml` que orquesta subflows en `{cliente}/NN-*.yaml` + helpers compartidos.

**Helpers compartidos** (`tests/app/flows/helpers/`)

| Helper | Propósito |
|--------|-----------|
| login.yaml | Login vendedor (Samsung Pass, popup nueva versión) |
| sync.yaml | Sincronización + dismiss popups |

**Prinorte** (`tests/app/flows/prinorte-session.yaml` → `prinorte/`)

| Flow | Casos | Origen |
|------|-------|--------|
| helpers/login.yaml | Login vendedor | Flujo base |
| helpers/sync.yaml | Sincronización | Flujo base |
| prinorte/01-comercios.yaml | Selección comercio | Flujo base |
| prinorte/02-catalogo.yaml | Catálogo productos | Flujo base |
| prinorte/03-pedido.yaml | Toma de pedido completa | Flujo crítico |
| prinorte/04-filtros.yaml | Filtros y búsqueda | Flujo base |
| prinorte/05-multi-unidad.yaml | Múltiples unidades de venta | Config |
| prinorte/06-stock-limite.yaml | Límite de stock | Config |
| prinorte/07-sin-filtro-venta.yaml | Sin filtro de venta | Config |
| prinorte/08-crear-comercio.yaml | Crear nuevo comercio | Flujo avanzado |
| prinorte/09-promociones.yaml | Promociones en pedido | **Post-mortem PM3** |
| prinorte/10-descuentos-vendedor.yaml | Descuentos de vendedor | Config |
| prinorte/11-crear-comercio-region.yaml | Comercio con región | Flujo avanzado |
| prinorte/12-precios-fotos.yaml | Precios + fotos productos | Config |

**Flows legacy** (`tests/app/flows/_legacy/` — no ejecutables con setup actual):

Movidos a `_legacy/` el 2026-04-19. Requieren `env.yaml` genérico que no existe.
Útiles como referencia de casos de prueba al crear flows de nuevos clientes.

| Flow | Casos | Origen |
|------|-------|--------|
| 08-pagos.yaml | Cobranza y pagos | **Deuda técnica** |
| 09-concurrencia.yaml | Race conditions | **Deuda técnica** |
| 10-descuentos.yaml | Descuentos en pedido | **Post-mortem PM3** |
| 11-guion-comercial.yaml | Guión comercial | Growth |
| 12-contacto-cliente.yaml | Contacto vía chat/teléfono | Growth |
| 13-tareas-growth.yaml | Gestión de tareas | Growth |

---

## Pendientes de automatizar (requieren acceso API)

Estos items están documentados en checklists pero necesitan tests de API (no E2E de UI):

- [ ] ERP-01 a ERP-42: Integraciones ERP — requiere endpoint `/orders/admin/` con auth
- [ ] KHP-01 a KHP-47: Fintech Khipu — requiere acceso a servicio NestJS
- [ ] IV-01 a IV-53: Integration Validator — requiere acceso a Lambda/Gateway
- [ ] PM6-01 a PM6-03: Performance queries MongoDB — requiere acceso a BD

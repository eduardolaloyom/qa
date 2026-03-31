# Índice QA — Cobertura de tests

> Mapeo entre checklists, tests automatizados y fuentes.
> Última actualización: 2026-03-27

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
| login.spec.ts | Login, acceso anónimo, sesión | Flujo C1 |
| catalog.spec.ts | Catálogo, búsqueda, categorías | Flujo C2 |
| cart.spec.ts | Carrito, cantidades, monto mínimo | Flujo C2 |
| checkout.spec.ts | Checkout, doble click, historial | Flujo C2 |
| prices.spec.ts | Precios, descuentos, impuestos, cupón field | Flujo C3 |
| **coupons.spec.ts** | Cupón inválido, orden sin cupón, loading | **Post-mortem PM1/PM2** |
| **step-pricing.spec.ts** | Escalones, cambio cantidad, precios rotos | **Post-mortem PM4** |
| **promotions.spec.ts** | Catálogo con promos, totales, timeout | **Post-mortem PM5** |
| **payments.spec.ts** | Historial pagos, montos negativos, tributarios | **Deuda técnica** |
| config-validation.spec.ts | Config multi-tenant | Validación |
| multi-client.spec.ts | Múltiples clientes | Multi-tenant |

### Playwright E2E — Admin (`npx playwright test --project=admin`)

| Spec | Casos | Origen |
|------|-------|--------|
| **login.spec.ts** | Login, error, ruta protegida | **Deuda técnica (Test en admin)** |
| **orders.spec.ts** | Listado, detalle, pagos | **Deuda técnica (Test en admin)** |

### Maestro — App móvil (`maestro test tests/app/flows/`)

| Flow | Casos | Origen |
|------|-------|--------|
| 01-login.yaml | Login vendedor | Flujo base |
| 02-sync.yaml | Sincronización | Flujo base |
| 03-comercios.yaml | Selección comercio | Flujo base |
| 04-catalogo.yaml | Catálogo productos | Flujo base |
| 05-pedido.yaml | Toma de pedido completa | Flujo crítico |
| 06-precios.yaml | Precios correctos | Flujo C3 |
| 07-offline.yaml | Modo offline | Flujo C4 |
| **08-pagos.yaml** | Cobranza y pagos | **Deuda técnica** |
| **09-concurrencia.yaml** | Race conditions | **Deuda técnica** |
| **10-descuentos.yaml** | Descuentos en pedido | **Post-mortem PM3** |

---

## Pendientes de automatizar (requieren acceso API)

Estos items están documentados en checklists pero necesitan tests de API (no E2E de UI):

- [ ] ERP-01 a ERP-42: Integraciones ERP — requiere endpoint `/orders/admin/` con auth
- [ ] KHP-01 a KHP-47: Fintech Khipu — requiere acceso a servicio NestJS
- [ ] IV-01 a IV-53: Integration Validator — requiere acceso a Lambda/Gateway
- [ ] PM6-01 a PM6-03: Performance queries MongoDB — requiere acceso a BD

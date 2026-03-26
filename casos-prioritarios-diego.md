# Revisión de Tests B2B — Casos Prioritarios
> Revisión del repo YOMCL/b2b + cruce con Linear proyecto B2B
> Fecha: 2026-03-26

---

## Lo que ya está hecho (validado en Linear)

Diego ya resolvió estas deudas técnicas:

- ✅ Coverage threshold en jest.config (YOM-DEBT)
- ✅ 38 servicios con tests (YOM-DEBT)
- ✅ Tests para hooks fetcher: useLegacy, useApi, useMicroservices (YOM-DEBT)
- ✅ Dockerfile con npm ci en vez de npm install
- ✅ .env.example documentado
- ✅ console.log reemplazado por Sentry
- ✅ Dockerfile con USER directive

---

## Lo que queda en Backlog (priorizado)

### 1. 18+ hooks SWR sin tests (High en Linear)

Los hooks fetcher base ya están testeados, pero los hooks de negocio siguen sin cobertura. Los más críticos:

#### use-cart

| # | Caso de prueba | Qué verificar |
|---|---|---|
| 1 | Agregar producto al carro | Estado actualiza, total recalcula |
| 2 | Agregar producto duplicado | Incrementa cantidad, no duplica item |
| 3 | Modificar cantidad a 0 | Producto se elimina del carro |
| 4 | Carro vacío | Estado inicial correcto, total = 0 |
| 5 | Cupón aplicado | Total con descuento correcto |
| 6 | Cupón inválido | Error, total sin cambio |
| 7 | Monto bajo el mínimo | Warning visible, no permite checkout |
| 8 | Persistencia de carro | Carro sobrevive a navegación entre páginas |

#### use-store (multi-tenant)

| # | Caso de prueba | Qué verificar |
|---|---|---|
| 9 | Store con anonymousAccess=true | Catálogo visible sin login |
| 10 | Store con anonymousAccess=false | Redirect a login |
| 11 | Store con enableCoupons=false | Sección de cupón oculta |
| 12 | Store con hidePrices=true | Precios no visibles |
| 13 | Store con disableCart=true | Carrito deshabilitado |
| 14 | Store token refresh | Token se renueva antes de expirar |
| 15 | Store token inválido | Manejo de error, no crash |

#### use-purchase-limit (339 líneas, refactor en Backlog)

| # | Caso de prueba |
|---|---|
| 16 | Producto dentro del límite → se puede agregar |
| 17 | Producto excede límite → tooltip de aviso |
| 18 | Límite cambia según packaging → cálculo correcto |

---

### 2. Cypress E2E roto post Next.js 16 (High en Linear)

Ya está en el Backlog como bug. Los problemas identificados:
- Node version mismatch en CI
- Selectores rotos post-upgrade

Además de arreglar eso, los hard waits existentes causan flakiness:

```typescript
// ❌ Hoy (falla si el API tarda más de 2 seg)
cy.get('[data-testid="add-button"]').click();
cy.wait(2000);
cy.get('[data-testid="cart-count"]').should('have.text', '1');

// ✓ Propuesto (espera al API, sin importar cuánto tarde)
cy.intercept('POST', '**/v2/cart').as('addToCart');
cy.get('[data-testid="add-button"]').click();
cy.wait('@addToCart');
cy.get('[data-testid="cart-count"]').should('have.text', '1');
```

---

### 3. Servicios sin tests (nuevos desde que se resolvió el debt)

Con los 38 servicios base ya testeados, quedan casos específicos:

#### Crear orden (solo existe fetch, no create)

| # | Caso de prueba | Qué verificar |
|---|---|---|
| 19 | Crear orden con carro válido | POST exitoso, retorna orderId |
| 20 | Crear orden con carro vacío | Error 400, no crea orden |
| 21 | Doble submit de crear orden | Solo 1 orden creada |
| 22 | Crear orden con cupón aplicado | Descuento reflejado en orden |

#### Cupones

| # | Caso de prueba |
|---|---|
| 23 | Validar cupón activo → descuento aplicado |
| 24 | Validar cupón expirado → error |
| 25 | Validar cupón ya usado → error |

#### Precios / impuestos

| # | Caso de prueba |
|---|---|
| 26 | Precio con IVA (useTaxRate=true) → total incluye impuesto |
| 27 | Precio sin IVA → total neto |
| 28 | Precio con descuento porcentual → cálculo correcto |
| 29 | Redondeo según priceRoundingDecimals |

---

## Resumen

| Área | Estado | Acción |
|---|---|---|
| Coverage threshold | ✅ Hecho | — |
| Tests de servicios (38) | ✅ Hecho | — |
| Hooks fetcher (useLegacy, useApi) | ✅ Hecho | — |
| **Hooks de negocio (18+)** | ❌ Backlog | 18 casos propuestos (use-cart, use-store, use-purchase-limit) |
| **Cypress E2E roto** | ❌ Backlog | Fix Node + selectores + reemplazar hard waits |
| **Servicios nuevos** | ❌ Pendiente | 11 casos propuestos (crear orden, cupones, precios) |
| Componentes (415/449 sin tests) | ❌ Backlog | Gradual, no urgente |

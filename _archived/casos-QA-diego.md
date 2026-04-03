# Revisión de Tests B2B — Casos Prioritarios
> Revisión del repo YOMCL/b2b (rama production)
> Fecha: 2026-03-26

---

## Estado actual

Revisé el repo y la base está bien armada:
- 37 servicios con unit tests
- CartInteraction con 730 líneas de tests (el más completo)
- CI corriendo en cada PR (TypeScript check + lint + Jest)
- Cypress con Allure reports y custom commands

### Cobertura por área

| Área | Con tests | Total | Cobertura |
|---|---|---|---|
| Servicios | 37 | 38 | ~85% |
| Componentes | ~30 | 50+ | ~60% |
| **Hooks** | **1** | **69** | **~1%** |
| Utils | 5 | 30+ | ~40% |

---

## Gap principal: hooks sin tests

Los hooks manejan toda la lógica de estado del B2B (carro, config del sitio, productos). Hoy están mockeados en tests de componentes pero nunca testeados directamente. Si alguien cambia un hook, ningún test avisa si rompió algo.

### use-cart (8 casos)

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

### use-store (7 casos)

| # | Caso de prueba | Qué verificar |
|---|---|---|
| 9 | Store con anonymousAccess=true | Catálogo visible sin login |
| 10 | Store con anonymousAccess=false | Redirect a login |
| 11 | Store con enableCoupons=false | Sección de cupón oculta |
| 12 | Store con hidePrices=true | Precios no visibles |
| 13 | Store con disableCart=true | Carrito deshabilitado |
| 14 | Store token refresh | Token se renueva antes de expirar |
| 15 | Store token inválido | Manejo de error, no crash |

Patrón para implementar (ya existe en el repo):
```typescript
import { renderHook, act } from '@testing-library/react';
import { useCart } from '@hooks/use-cart';

describe('useCart', () => {
  it('agregar producto actualiza total', () => {
    const { result } = renderHook(() => useCart(), { wrapper: CartProvider });
    act(() => { result.current.addProduct(mockProduct); });
    expect(result.current.total).toBe(1000);
  });
});
```

---

## Servicios sin tests

### Crear orden (solo existe fetch, no create)

| # | Caso de prueba | Qué verificar |
|---|---|---|
| 16 | Crear orden con carro válido | POST exitoso, retorna orderId |
| 17 | Crear orden con carro vacío | Error 400, no crea orden |
| 18 | Crear orden con monto bajo mínimo | Error o warning |
| 19 | Doble submit de crear orden | Solo 1 orden creada |
| 20 | Crear orden con cupón aplicado | Descuento reflejado en orden |

### Cupones (no existe test)

| # | Caso de prueba |
|---|---|
| 21 | Validar cupón activo → descuento aplicado |
| 22 | Validar cupón expirado → error |
| 23 | Validar cupón ya usado → error |
| 24 | Aplicar cupón + descuento por volumen → cálculo correcto |

### Precios / impuestos (no existe test)

| # | Caso de prueba |
|---|---|
| 25 | Precio con IVA (useTaxRate=true) → total incluye impuesto |
| 26 | Precio sin IVA → total neto |
| 27 | Precio con descuento porcentual → cálculo correcto |
| 28 | Precio con descuento fijo → cálculo correcto |
| 29 | Redondeo según priceRoundingDecimals |

---

## Cypress: reemplazar hard waits

Hay ~15 `cy.wait(milisegundos)` en `catalog/cart-interaction.cy.ts` que causan tests intermitentes. El fix es reemplazar por `cy.intercept` que espera la respuesta del API en vez de un tiempo fijo:

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

No requiere instalar nada. `cy.intercept` es nativo de Cypress.

---

## Quick win: coverage threshold

Hoy coverage se recolecta pero no bloquea. Código sin tests pasa en CI. Agregar en `jest.config.cjs`:

```javascript
coverageThreshold: {
  global: {
    branches: 70,
    functions: 70,
    lines: 70,
    statements: 70
  }
}
```

Si la cobertura baja de 70%, CI falla. Se puede empezar más bajo y subir gradualmente.

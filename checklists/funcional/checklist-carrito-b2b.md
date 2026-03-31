# Checklist QA — Carrito B2B (refactor activo)

> Fuente: [Tareas de carrito — Notion](https://www.notion.so/294d8139ba4e8067b628f5af1d37e6a9)
> Estado: Desarrollo activo (tareas en progress)
> Fecha creación: 2026-03-27

---

## Contexto

El carrito B2B está siendo refactorizado. Incluye: refresh automático, migración al nuevo formato, historial de carritos, y triggers al crear orden. Estas funcionalidades nuevas necesitan cobertura QA.

### Tareas identificadas en Notion

| Tarea | Estado | Tipo |
|-------|--------|------|
| Refresh del carrito por usuario (tienda pre-order) | In progress | Backend |
| Refresh de carrito a la 00:00 | Not started | - |
| Código para migrar carritos actuales a los nuevos | Not started | - |
| Job: Mover carritos de >3 meses al historial | Not started | - |
| Backend: CartHistory | Not started | - |
| Trigger: Modificar yom-api para usar nuevo carrito al crear orden | Not started | - |
| Trigger: Mover carrito al historial al crear orden | Not started | - |
| Refresh de carritos por integración | Not started | - |
| Implementar variables de sitio para probar carritos | Not started | - |
| Implementación en el front B2B | Not started | - |
| Mailing | Not started | - |

---

## 1. Carrito básico (funcionalidad actual)

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| CART-01 | Agregar producto al carrito | Producto aparece con cantidad y precio correcto | PENDIENTE |
| CART-02 | Modificar cantidad de producto en carrito | Total se recalcula | PENDIENTE |
| CART-03 | Eliminar producto del carrito | Producto desaparece, total se actualiza | PENDIENTE |
| CART-04 | Carrito vacío muestra estado vacío | Mensaje "sin productos" o similar | PENDIENTE |
| CART-05 | Carrito persiste al navegar entre páginas | Items no se pierden al ir a catálogo y volver | PENDIENTE |
| CART-06 | Carrito persiste al cerrar y abrir sesión | Mismos items al re-loguearse | PENDIENTE |

---

## 2. Refresh de carrito (nuevas funcionalidades)

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| CART-10 | Refresh a las 00:00 actualiza precios | Si un precio cambió, el carrito refleja el nuevo precio | PENDIENTE |
| CART-11 | Refresh a las 00:00 — producto descontinuado | Producto se marca como no disponible o se remueve | PENDIENTE |
| CART-12 | Refresh a las 00:00 — stock agotado | Cantidad se ajusta al stock disponible o muestra advertencia | PENDIENTE |
| CART-13 | Refresh por usuario (pre-order) | Carrito se actualiza al entrar a la tienda | PENDIENTE |
| CART-14 | Refresh por integración (cambio masivo de precios) | Todos los carritos afectados se actualizan | PENDIENTE |
| CART-15 | Refresh no pierde descuentos/cupones aplicados | Cupón sigue vigente post-refresh | PENDIENTE |

---

## 3. Migración de carrito (al formato nuevo)

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| CART-20 | Carrito existente se migra correctamente | Mismos productos, cantidades y precios post-migración | PENDIENTE |
| CART-21 | Carrito vacío no genera error en migración | Se maneja silenciosamente | PENDIENTE |
| CART-22 | Carrito con productos descontinuados se migra | Productos inválidos se marcan o remueven | PENDIENTE |

---

## 4. CartHistory (historial de carritos)

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| CART-30 | Carrito de >3 meses se mueve al historial | Job lo detecta y mueve a CartHistory | PENDIENTE |
| CART-31 | Carrito activo (<3 meses) NO se mueve | Sigue funcionando normalmente | PENDIENTE |
| CART-32 | Al crear orden, carrito se mueve al historial | Trigger post-orden ejecuta el movimiento | PENDIENTE |
| CART-33 | Historial de carritos es consultable | Usuario puede ver carritos pasados | PENDIENTE |

---

## 5. Trigger: Crear orden desde nuevo carrito

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| CART-40 | yom-api obtiene carrito nuevo al crear orden | API lee del formato nuevo correctamente | PENDIENTE |
| CART-41 | Orden creada tiene items correctos del carrito | Productos, cantidades y precios coinciden | PENDIENTE |
| CART-42 | Post-orden el carrito se vacía o mueve a historial | No quedan items residuales en carrito activo | PENDIENTE |
| CART-43 | Orden parcial (no todos los items del carrito) | Items restantes permanecen en carrito | PENDIENTE |

---

## 6. Edge cases del carrito

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| CART-50 | Producto en carrito cambia de precio entre sesiones | Al volver, precio actualizado visible con aviso | PENDIENTE |
| CART-51 | Producto en carrito se queda sin stock | Aviso al usuario, no puede checkout ese item | PENDIENTE |
| CART-52 | Dos sesiones simultáneas modifican el mismo carrito | Última escritura gana, sin corrupción de datos | PENDIENTE |
| CART-53 | Carrito con 100+ productos | Performance aceptable, no timeout | PENDIENTE |
| CART-54 | Cambio de moneda/impuestos post-agregar al carrito | Totales se recalculan correctamente | PENDIENTE |

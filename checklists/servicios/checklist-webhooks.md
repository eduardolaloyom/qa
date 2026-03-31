# Checklist QA — Webhooks (Integration Hooks)

> Fuente: [Webhooks — Tech Wiki](https://www.notion.so/222d8139ba4e805a9d1fd8c35d51d9c4)
> + [Integración de estados](https://www.notion.so/17dd8139ba4e807f8b06ddfb85343c01)
> Fecha creación: 2026-03-27

---

## Contexto

YOM usa webhooks (hooks) para comunicarse con los ERPs de clientes. Se configuran en `customer.integrationHooks` en MongoDB. Cada hook es una URL que YOM llama cuando ocurre un evento.

### Hooks disponibles

| Hook | Propósito | Criticidad |
|------|-----------|-----------|
| `createOrderHook` | Crear pedido en ERP | **Crítica** — todos los clientes lo usan |
| `createCommerceHook` | Crear comercio en ERP | Media |
| `editOrderHook` | Editar pedido en ERP | Media |
| `changeOrderStatusHook` | Cambiar estado de pedido | Alta |
| `checkStockHook` | Verificar stock en ERP | Alta |
| `shippingCostHook` | Obtener costo de despacho | Alta |
| `createPaymentHook` | Crear pago en ERP | Alta |
| `updateTrafficLightHook` | Actualizar semáforo | Baja |
| `getPendingDocumentsHook` | Obtener docs pendientes | Media |
| `nextDeliveryHook` | Fecha de próxima entrega | Alta |
| `visitDaysHook` | Días de visita del vendedor | Media |
| `nextDeliveryTextHook` | Texto de próxima entrega | Baja |
| `getVoucherHook` | Obtener voucher | Baja |

### Repositorios
- [yom-api/server/hooks/](https://github.com/YOMCL/yom-api/tree/production/server/hooks)
- [yom-hooks](https://github.com/YOMCL/yom-hooks)

---

## 1. createOrderHook (el más crítico)

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| WH-01 | Orden creada → hook se dispara | POST a la URL configurada con order + commerce + user | PENDIENTE |
| WH-02 | Cliente sin hook configurado | Orden se crea normalmente, sin llamada externa | PENDIENTE |
| WH-03 | Hook retorna error 500 | Orden queda en pending, se registra en erpIntegrations | PENDIENTE |
| WH-04 | Hook retorna error 4xx | Se registra como warning, no se reintenta | PENDIENTE |
| WH-05 | Hook timeout (ERP lento) | No bloquea la creación de la orden | PENDIENTE |

---

## 2. Hooks de stock y despacho

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| WH-10 | checkStockHook → stock disponible | Producto se puede agregar al carro | PENDIENTE |
| WH-11 | checkStockHook → sin stock | Mensaje "sin stock" visible al usuario | PENDIENTE |
| WH-12 | checkStockHook → timeout | Fallback: permite agregar (o muestra error) | PENDIENTE |
| WH-13 | shippingCostHook → retorna costo | Costo de despacho visible en checkout | PENDIENTE |
| WH-14 | shippingCostHook → error | Checkout muestra "costo no disponible" o valor default | PENDIENTE |
| WH-15 | nextDeliveryHook → retorna fecha | Fecha de entrega visible en checkout | PENDIENTE |

---

## 3. Integración de estados (order status)

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| WH-20 | ERP llama PUT con status válido (default) | Estado de la orden se actualiza | PENDIENTE |
| WH-21 | ERP llama PUT con customStatus válido | Estado custom se asigna a la orden | PENDIENTE |
| WH-22 | ERP llama PUT con status inexistente | Error 400, orden no cambia de estado | PENDIENTE |
| WH-23 | ERP llama PUT con orderId inexistente | Error 404 | PENDIENTE |
| WH-24 | Cambio de estado genera statuschangelog | Log con timestamp de cuándo cambió | PENDIENTE |
| WH-25 | ERP usa identificador externo (no YOM ID) | Búsqueda por externalId funciona | PENDIENTE |

---

## 4. Seguridad y autenticación

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| WH-30 | Hook usa autenticación interna | Solo requests con token interno aceptados | PENDIENTE |
| WH-31 | Variables de entorno del cliente configuradas | Hook puede autenticarse con el ERP | PENDIENTE |
| WH-32 | Secrets de K8s existen para el cliente | Deploy no falla por variables faltantes | PENDIENTE |

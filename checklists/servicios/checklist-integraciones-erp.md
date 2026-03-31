# Checklist QA — Integraciones ERP y Reintento de Pedidos

> Fuentes:
> - [Cronjob de reintento de pedidos](https://www.notion.so/24fd8139ba4e80438aa0e71412c0721e)
> - [Hooks de creación de pedidos](https://www.notion.so/24fd8139ba4e807594c7e4f16c375c82)
> Fecha creación: 2026-03-27

---

## Contexto

Cuando se crea un pedido, un hook envía la orden al ERP del cliente. Si falla, un cronjob cada 30 minutos reintenta los pedidos pendientes. Cada cliente tiene transformaciones específicas.

### Clientes con cronjob activo

| Cliente | Update delivery date | Custom status ID | Schedule |
|---------|---------------------|------------------|----------|
| Soprole | Si | `6528a24b0c280d992c80c70f` | */30 * * * * |
| Bidfood | No | - | */30 * * * * |
| Surtiventas | No | - | */30 * * * * |
| Codelpa | No | - | */30 * * * * |

### Endpoints del sistema

| Endpoint | Método | Propósito |
|----------|--------|-----------|
| `/orders/admin/status` | GET | Buscar órdenes pendientes (últimos 4 días) |
| `/orders/admin/{orderId}/delivery-date` | PUT | Actualizar fecha de entrega |
| `/orders/admin/{orderId}/integration` | POST | Enviar orden al ERP |

---

## 1. Hook de creación de pedido (trigger automático)

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| ERP-01 | Crear orden con status `pending` | Hook se dispara, orden se envía al ERP del cliente | PENDIENTE |
| ERP-02 | Orden cambia de `pending_approval` a `pending` | Hook se dispara igualmente | PENDIENTE |
| ERP-03 | Orden creada en cliente sin hook configurado | No hay error, orden queda en estado pending sin envío | PENDIENTE |
| ERP-04 | Hook falla (ERP no disponible) | Orden queda en pending, se registra error en `erpIntegrations` | PENDIENTE |
| ERP-05 | Hook responde con orderId distinto | Se actualiza `orderId` y `sentToClientErp=true` en BD | PENDIENTE |
| ERP-06 | Datos del comercio/vendedor/supervisor se incluyen en el payload | Body del hook tiene `order`, `commerce`, `user` completos | PENDIENTE |

---

## 2. Transformación por cliente

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| ERP-10 | Orden de Coéxito → timezone America/Bogota | Fechas en hora colombiana | PENDIENTE |
| ERP-11 | Orden de Coéxito → dirección concatenada | `concatShippingAddress=true` aplicado | PENDIENTE |
| ERP-12 | Orden de Coéxito → 2 decimales en montos | Valores con precisión de 2 decimales | PENDIENTE |
| ERP-13 | Orden de Marley Coffee → 0 decimales | Valores enteros, sin decimales | PENDIENTE |
| ERP-14 | Orden de Marley Coffee → timezone America/Santiago | Fechas en hora chilena | PENDIENTE |

---

## 3. Cronjob de reintento

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| ERP-20 | Órdenes pendientes de últimos 4 días se reenvían | Script las encuentra y reenvía | PENDIENTE |
| ERP-21 | Órdenes de hace >4 días no se reenvían | No aparecen en el filtro del script | PENDIENTE |
| ERP-22 | Soprole: fecha de entrega vencida se actualiza | PUT delivery-date actualiza la fecha antes del reenvío | PENDIENTE |
| ERP-23 | Bidfood/Surtiventas/Codelpa: fecha NO se actualiza | `updateDeliveryDate=false` respetado | PENDIENTE |
| ERP-24 | Error en una orden no detiene el resto | Script continúa con la siguiente orden | PENDIENTE |
| ERP-25 | Delay de 3 segundos entre envíos | No hay ráfaga de requests al ERP | PENDIENTE |
| ERP-26 | Log muestra estadísticas de éxito/fallo | "Status: X/Y successful orders" | PENDIENTE |
| ERP-27 | Soprole: filtro por customStatusId funciona | Solo procesa órdenes con ese status específico | PENDIENTE |

---

## 4. Logging y monitoreo

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| ERP-30 | Envío exitoso se registra en `erpIntegrations` | Registro con `isSuccess=true`, responseBody, processingTime | PENDIENTE |
| ERP-31 | Envío fallido se registra en `erpIntegrations` | Registro con `isSuccess=false`, error message | PENDIENTE |
| ERP-32 | Error 4xx del ERP no se reintenta | Se registra como warning, no se reprocesa | PENDIENTE |
| ERP-33 | Error 5xx del ERP se reintenta | Según configuración del cliente | PENDIENTE |

---

## 5. Autenticación del hook

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| ERP-40 | Hook usa `internalHookAuth()` | Solo requests internos con token válido aceptados | PENDIENTE |
| ERP-41 | Request externo al endpoint del hook | Rechazado (401/403) | PENDIENTE |
| ERP-42 | clientId/clientSecret inválidos en cronjob | Error de autenticación logueado | PENDIENTE |

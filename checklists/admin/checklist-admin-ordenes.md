# Checklist Admin — Gestión de Órdenes

**Fuente:** Funcionalidad Admin YOM — gestión de pedidos  
**Cuándo ejecutar:** Post-deploy en módulo de órdenes, onboarding cliente  
**Plataforma:** admin.youorder.me → sección Pedidos

---

## Visualización de Pedidos

| ID | Caso | Cómo validar | Estado |
|----|------|--------------|--------|
| ADM-ORD-01 | Ver lista de pedidos | Acceder a /pedidos → lista con todas las órdenes del cliente visible | PENDIENTE |
| ADM-ORD-02 | Filtrar pedidos por estado | Filtrar por PENDIENTE / CONFIRMADA / EN_PROCESO → solo pedidos con ese estado | PENDIENTE |
| ADM-ORD-03 | Filtrar pedidos por fecha | Filtrar por rango de fechas → solo pedidos en ese período | PENDIENTE |
| ADM-ORD-04 | Buscar pedido por ID | Ingresar ID de pedido en buscador → pedido específico aparece | PENDIENTE |
| ADM-ORD-05 | Ver detalle de pedido | Click en pedido → detalle con items, montos, comercio, estado ERP | PENDIENTE |
| ADM-ORD-06 | Multi-tenant isolation | Admin de cliente A no puede ver pedidos de cliente B | PENDIENTE |
| ADM-ORD-07 | Paginación de pedidos | Con 100+ pedidos, paginación funciona correctamente | PENDIENTE |

---

## Gestión de Estado de Pedidos

| ID | Caso | Cómo validar | Estado |
|----|------|--------------|--------|
| ADM-ORD-10 | Cambiar estado de pedido | Cambiar estado PENDIENTE → CONFIRMADA → verificar que se refleja en B2B del comercio | PENDIENTE |
| ADM-ORD-11 | Cambiar estado a CANCELADA | Cancelar pedido → comercio ve estado CANCELADA en su historial | PENDIENTE |
| ADM-ORD-12 | Cambio de estado auditable | Cambio de estado guarda timestamp y usuario que lo realizó | PENDIENTE |
| ADM-ORD-13 | Notificación post-cambio de estado | Si está configurado, comercio recibe notificación al cambiar estado | PENDIENTE |

---

## Integración con ERP

| ID | Caso | Cómo validar | Estado |
|----|------|--------------|--------|
| ADM-ORD-20 | Ver estado de inyección al ERP | En detalle de pedido, campo "Estado ERP" muestra si fue inyectado | PENDIENTE |
| ADM-ORD-21 | Pedido con error de inyección | Pedido que falló al enviarse al ERP — Admin puede ver el error y reintentar | PENDIENTE |
| ADM-ORD-22 | Reintentar inyección fallida | Botón "Reintentar envío al ERP" en pedido con error → fuerza reintento | PENDIENTE |
| ADM-ORD-23 | Log de erpIntegrations | Para verificar: `db.erpIntegrations.find({domain})` muestra registros de cada intento | PENDIENTE |

---

## Exportación y Reportes

| ID | Caso | Cómo validar | Estado |
|----|------|--------------|--------|
| ADM-ORD-30 | Exportar pedidos a CSV | Click en "Exportar" → archivo CSV descarga con datos correctos | PENDIENTE |
| ADM-ORD-31 | Exportar filtrado por fechas | Exportar solo pedidos del mes → CSV solo incluye ese período | PENDIENTE |
| ADM-ORD-32 | Totales en exportación correctos | Montos en CSV coinciden con lo mostrado en pantalla | PENDIENTE |

---

## Notas de Escalamiento

Si cambio de estado en Admin no se refleja en B2B → P1, escalar a backend (puede ser webhook no disparado).  
Si pedidos de otro cliente son visibles → P0, escalar inmediatamente (problema de tenant isolation).

**Post-mortem relacionado:** Ninguno registrado actualmente.

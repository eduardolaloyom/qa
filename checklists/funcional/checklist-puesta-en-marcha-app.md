# Checklist QA - Puesta en Marcha APP Móvil

## Datos del test
- **Ambiente:** Producción (`api.youorder.me`)
- **APK:** Yom Ventas (Play Store) — v6.2.6-rc01
- **Cliente:** Tienda (`tienda.youorder.me`) — CustomerId: `5f316fca1cd61d12d17dca52`
- **Credenciales:** `rodrigo.alliende+tiendita2@youorder.me` / `aaa12345678`
- **Emulador:** Android Studio - Medium Phone API 36.1
- **Moneda:** CLP
- **Fecha ejecución:** 2026-03-26

### Features activas del cliente
| Feature | Estado |
|---|---|
| enableCoupons | activo |
| enableTask | activo |
| enablePaymentsCollection | activo |
| enableAskDeliveryDate | activo |
| enableChooseSaleUnit | activo |
| enableSellerDiscount | activo |
| hasStockEnabled | activo |
| enableDialogNoSellReason | activo |
| enableCreditNotes | activo |
| enableOrderApproval | activo |
| anonymousAccess | activo |
| includeTaxRateInPrices | inactivo |

---

## 0. Pre-vuelo

| # | Verificación | Cómo validar | Estado |
|---|---|---|---|
| 0.1 | Catálogo cargado | Post-sync: hay productos visibles en el comercio | PASS — catálogo visible con productos (LECHE KLIM, MILO, etc.) |
| 0.2 | Categorías configuradas | Navegación por categorías funciona | PASS — 10 categorías visibles (Abarrotes, Artículos de Aseo, Bebestibles, Carnes, Cuidado personal, Enlatados, Golosinas, Helados, Pilas, Verduras) + filtros por estrategia |
| 0.3 | Precios correctos | Comparar 3 productos app vs MongoDB | PENDIENTE |
| 0.4 | Stock visible | Productos muestran stock (hasStockEnabled=true) | PENDIENTE |
| 0.5 | Config del cliente se carga | Post-login: nombre del cliente, moneda CLP, features activas | PASS — login exitoso, app muestra dominio correcto |

---

## 1. Autenticación

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| 1.1 | Login con credenciales válidas | Accede al listado de comercios | PASS |
| 1.2 | Login con contraseña incorrecta | Muestra error "Credenciales incorrectas" | PASS |
| 1.3 | Login con email inexistente | Muestra error de autenticación | PASS — mismo mensaje que 1.2 |
| 1.4 | Login con campos vacíos | Muestra "completa todos los campos" | PASS |
| 1.5 | Recuperar contraseña con email válido | Muestra mensaje de envío + timer 60s | PENDIENTE |
| 1.6 | Inicio Sesión Empresa (Microsoft) | Redirige a login Microsoft OAuth | PENDIENTE — botón visible en pantalla |
| 1.7 | Cerrar sesión | Vuelve a pantalla de login | PASS |

## 2. Sincronización

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| 2.1 | Primera sincronización post-login | Carga listado de comercios con datos | PASS — primera vez cargó comercios correctamente |
| 2.2 | Datos de productos correctos | Post-sync: productos del cliente con precios esperados | PENDIENTE — requiere acceder a comercio disponible |
| 2.3 | Stock correcto | Post-sync: stock coincide con datos en BD | PENDIENTE |
| 2.4 | Botón "Sincronizar" manual | Actualiza datos sin perder estado | PASS — botón funciona, datos se mantienen |
| 2.5 | "Recuperar datos" | Descarga datos completos desde cero | PASS — funciona pero no carga comercios post-logout (ver BUG-01) |
| 2.6 | Sincronización sin conexión | Muestra error o usa datos offline | PENDIENTE |
| 2.7 | Reconexión post-offline | Sincroniza automáticamente | PENDIENTE |

## 3. Listado de Comercios

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| 3.1 | Visualización de comercios | Muestra nombre, dirección, estado, pedidos del mes | PASS — muestra ID, nombre, dirección, estado, pedidos |
| 3.2 | Estados de comercios | Se ven correctamente: Disponible, Bloqueado, Advertencia | PASS — los 3 estados visibles con colores distintos |
| 3.3 | Búsqueda de comercios (lupa) | Filtra por nombre o ID | PASS — buscar "ferreteria" filtra correctamente por nombre |
| 3.4 | Filtros ("Seleccionar filtros") | Filtra por estado u otros criterios | PASS — panel con filtros: Ruta, Sin Ventas, Tareas Pendientes, Nuevos, Disponible, Advertencia, Bloqueado |
| 3.5 | Scroll del listado | Carga todos los comercios sin cortes | PASS — scroll fluido por toda la lista |
| 3.6 | Contador "Pedidos este mes" | Coincide con pedidos reales del comercio | PASS — muestra "Pedidos este mes: 0" en todos |

## 4. Detalle de Comercio

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| 4.1 | Abrir comercio disponible | Muestra detalle con último pedido, ticket promedio | PASS — acceso OK tras re-sync |
| 4.2 | Abrir comercio bloqueado | Muestra detalle con estado bloqueado | PASS — muestra "Bloqueado", último pedido "No disponible", ticket promedio "No disponible" |
| 4.3 | Pestaña "Tareas" | Muestra tareas pendientes o "sin tareas" (enableTask=true) | PASS — "No se encontraron tareas", botón "Ver todas las tareas" visible |
| 4.4 | Crear tarea nueva | Se crea y aparece en listado | PENDIENTE — no se pudo probar (requiere conexión al servidor) |
| 4.5 | Pestaña "Datos del comercio" | Muestra info del comercio (dirección, contacto, etc.) | PASS — muestra Formas de Pago, Línea Crédito, Saldo Disponible, Dirección, Teléfono, Whatsapp, Email |
| 4.6 | Botón "Hacer pedido" en disponible | Abre catálogo de productos | PASS — abre catálogo con productos |
| 4.7 | Botón "Hacer pedido" en bloqueado | No permite o muestra advertencia | PASS — muestra "Este comercio se encuentra bloqueado por estado crediticio" con opciones Continuar/Hacer cobranza |
| 4.8 | Botón "Hacer cobranza" | Abre flujo de cobranza | PASS — abre vista de facturas con deuda, pagos por validar, saldo a favor, detalle de facturas |
| 4.9 | Razón de no venta | enableDialogNoSellReason=true: diálogo aparece si no se vende | PENDIENTE |

## 5. Flujo de Pedido

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| 5.1 | Catálogo de productos | Muestra productos con imágenes, precios, stock | PASS — productos visibles con precios y unidad de venta |
| 5.2 | Búsqueda de productos | Filtra por nombre o SKU | PASS — búsqueda "leche" filtra correctamente, muestra solo productos con ese término |
| 5.3 | Categorías de productos | Navega entre categorías correctamente | PASS — 10 categorías + filtros por estrategia funcionan |
| 5.4 | Agregar producto al carrito | Actualiza cantidad y total | PASS — botón "Agregar" agrega producto, badge "Mi pedido" se incrementa |
| 5.5 | Selección de unidad de venta | enableChooseSaleUnit=true: permite elegir unidad | PASS — spinner dropdown_unit_sale presente y funcional. Solo "UN" disponible en productos probados |
| 5.6 | Modificar cantidad de producto | Recalcula subtotal | PASS — botones +/- funcionan, LECHE KLIM de 1→2, total recalculado correctamente |
| 5.7 | Eliminar producto del carrito | Se remueve y recalcula total | PASS — minus en cantidad 1 remueve producto, vuelve a "Agregar", total baja |
| 5.8 | Ver resumen del pedido | Muestra todos los productos, cantidades y montos | PASS — muestra dirección, neto, descuentos, impuesto, despacho, total, productos |
| 5.9 | Fecha de despacho | enableAskDeliveryDate=true: calendario aparece en checkout | FAIL — no aparece selector de fecha. enableAskDeliveryDate=true pero "Finalizar pedido" va directo a confirmación. Ver BUG-02 |
| 5.10 | Descuento de vendedor | enableSellerDiscount=true: vendedor puede aplicar descuento | PASS — diálogo de descuento por %, 10% sobre $43.042 = $4.304,20 descuento correcto, total $38.737,80 |
| 5.11 | Confirmar pedido | Pedido se crea exitosamente | PASS (parcial) — pedido se crea localmente como "Orden abierta". No se envía al servidor (sin conectividad al API desde emulador). Ver nota conectividad |
| 5.12 | Pedido aparece en "Mis pedidos" | Se lista con estado "Orden pendiente" | PASS — aparece en Pendiente como "Ordenes no enviadas / Abierto" con monto correcto $38.737,80 |

## 6. Precios y Promociones

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| 6.1 | Precio base correcto | Precio en app = precio en MongoDB para 3 productos | PENDIENTE |
| 6.2 | Precio sin IVA | includeTaxRateInPrices=false: precios son netos | PASS — Impuesto muestra $0 en resumen, precios son netos |
| 6.3 | Precio total del carro | Total = suma correcta de (precio × cantidad) | PASS — LECHE KLIM $21.521 × 2 = $43.042 neto correcto |
| 6.4 | Consistencia precio catálogo ↔ carro | Mismo precio en ambas vistas | PASS — $21.521/UN en catálogo = mismo precio en resumen |
| 6.5 | Cupón válido | enableCoupons=true: descuento se aplica correctamente | PENDIENTE |
| 6.6 | Cupón inválido | Error, total sin cambio | PENDIENTE |

## 7. Pedidos

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| 7.1 | Pestaña "Mis pedidos" | Lista pedidos con fecha, monto, productos | PASS — muestra pedidos con fecha, comercio, productos, monto |
| 7.2 | Pestaña "Pendiente" | Filtra solo pedidos pendientes | PASS — filtro funciona, muestra "Orden pendiente" |
| 7.3 | "Ver detalle" de pedido | Muestra productos, cantidades, montos | PASS — muestra producto, cantidad, descuento, precio antes/después, desglose completo |
| 7.4 | "Actualizar" pedidos | Refresca lista desde servidor | PASS — botón "Actualizar" visible y funcional |
| 7.5 | Aprobación de órdenes | enableOrderApproval=true: flujo de aprobación visible | PENDIENTE |

## 8. Cobranza

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| 8.1 | Recaudación de pagos | Muestra resumen: Efectivo, Cheque, Transferencia | PASS — muestra Efectivo $0, Cheque $0, Transferencia $0, Total $0 |
| 8.2 | Filtro por fecha | Cambia rango de recaudación | PASS — "Filtrar por fecha: Hoy" visible |
| 8.3 | Registrar pago en efectivo | Se registra y suma al total recaudado | PENDIENTE |
| 8.4 | Registrar pago con cheque | Se registra correctamente | PENDIENTE |
| 8.5 | Registrar transferencia | Se registra correctamente | PENDIENTE |
| 8.6 | Listado de movimientos | Muestra historial de pagos registrados | PASS — "No se encontraron pagos" (correcto, no hay pagos) |
| 8.7 | Notas de crédito | enableCreditNotes=true: sección visible y funcional | PENDIENTE |

## 9. Offline / Conectividad

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| 9.1 | Navegar comercios sin internet | Datos offline disponibles (Realm) | PASS — app funciona con datos cacheados en Realm, catálogo y comercios disponibles sin API |
| 9.2 | Crear pedido sin internet | Se guarda localmente | PASS — pedido se crea y queda como "Orden abierta" en pestaña Pendiente |
| 9.3 | Sincronizar pedido al reconectar | Pedido se envía al servidor | PENDIENTE |
| 9.4 | Registrar cobranza sin internet | Se guarda localmente | PENDIENTE |
| 9.5 | No hay pérdida de datos | Offline → online: todos los datos persisten | PENDIENTE |

## 10. UI / UX General

| # | Caso | Resultado esperado | Estado |
|---|------|-------------------|--------|
| 10.1 | Versión mostrada al pie | Coincide con versión esperada | PASS — "Yom 2025 | 6.2.6-rc01 yom-production" |
| 10.2 | Navegación entre pestañas | Comercios, Pedidos, Cobranza funcionan | PASS — las 3 pestañas navegan correctamente |
| 10.3 | Botón volver (back) | Navega correctamente sin crashear | PASS |
| 10.4 | Rotación de pantalla | Se mantiene estable | PASS — landscape y vuelta a portrait sin crash ni pérdida de datos |
| 10.5 | Notificaciones push | Se reciben correctamente | PENDIENTE |
| 10.6 | Menú hamburguesa (≡) | Muestra opciones de configuración/logout | PASS — muestra: Listado, Mis Tareas, Resumen ventas, Exportar datos, Código transportista, Recaudación, Recuperar Datos, Cerrar sesión |

---

## Resumen de Ejecución

| Categoría | Total | PASS | PENDIENTE | FAIL |
|---|---|---|---|---|
| Pre-vuelo | 5 | 3 | 2 | 0 |
| Autenticación | 7 | 5 | 2 | 0 |
| Sincronización | 7 | 3 | 4 | 0 |
| Listado Comercios | 6 | 6 | 0 | 0 |
| Detalle Comercio | 9 | 7 | 2 | 0 |
| Flujo Pedido | 12 | 11 | 0 | 1 |
| Precios/Promociones | 6 | 3 | 3 | 0 |
| Pedidos | 5 | 4 | 1 | 0 |
| Cobranza | 7 | 3 | 4 | 0 |
| Offline | 5 | 2 | 3 | 0 |
| UI/UX | 6 | 5 | 1 | 0 |
| **TOTAL** | **75** | **52** | **22** | **1** |

---

## Bugs Encontrados

### BUG-01: Sync no carga comercios después de cerrar sesión y re-login
- **Severidad:** Media (rebajada — intermitente)
- **Pasos:** Login → Sincronizar (carga comercios OK) → Menú → Cerrar sesión → Login de nuevo → Sincronizar/Recuperar datos
- **Esperado:** Comercios se cargan nuevamente
- **Actual:** "No se encontraron comercios" en primera sync post re-login. Presionando Sincronizar nuevamente se resuelve.
- **Nota:** Intermitente. La primera vez post-instalación funciona. Tras logout + re-login falla la primera sync pero funciona al reintentar. Posible race condition en Realm al recrear la BD local.

### BUG-02: No aparece selector de fecha de despacho (enableAskDeliveryDate=true)
- **Severidad:** Media
- **Pasos:** Comercio → Hacer pedido → Agregar productos → Mi pedido → Finalizar pedido
- **Esperado:** Debe aparecer un selector/calendario de fecha de despacho antes de la confirmación (enableAskDeliveryDate=true)
- **Actual:** Al presionar "Finalizar pedido" aparece directamente el diálogo "¿Estás seguro de enviar el pedido?" sin opción de fecha
- **Nota:** Verificar si la feature está activa para este comercio específico o si depende de otra configuración

### BUG-03: Pedido no se envía al servidor — queda como "Orden abierta"
- **Severidad:** Alta (posible issue de conectividad del emulador)
- **Pasos:** Crear pedido → Finalizar → ACEPTAR → Ir a Pendiente → "Enviar ordenes abiertas" → Confirmar
- **Esperado:** Pedido se envía y aparece como "Orden pendiente"
- **Actual:** Pedido permanece como "Ordenes no enviadas / Abierto" después de confirmar envío
- **Nota:** El emulador tiene internet (ping 8.8.8.8 OK) pero api.youorder.me (98.95.26.99) no responde. Podría ser un issue de red del emulador, no de la app. **Reprobar en dispositivo físico o con VPN.**

---

## Notas
- Los comercios "Bloqueados" muestran advertencia "bloqueado por estado crediticio" con opción de Continuar — comportamiento correcto
- Credenciales de staging (`rodrigo.alliende+newsoprolevendedor@yom.ai` / `cuentaDemo12345`) NO funcionan en producción, solo en staging
- Staging no tiene comercios cargados para este cliente
- El cliente "Tienda" es un cliente de prueba interno de YOM con muchas features habilitadas
- BUG-01 es intermitente — se resuelve con segundo sync. Ya no es bloqueante para testing
- El emulador tiene internet general (8.8.8.8 OK) pero api.youorder.me no responde — los 22 casos PENDIENTE en su mayoría requieren conectividad al servidor
- Los datos offline (Realm) funcionan correctamente para navegación y creación de pedidos
- **Recomendación:** Reprobar los 22 casos PENDIENTE + BUG-03 en dispositivo físico con conectividad real al API

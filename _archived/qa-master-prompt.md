# QA MASTER PROMPT — Plataforma B2B YOM
> Documento de instrucciones para Claude Code
> Propósito: Explorar los repositorios, identificar el stack, y construir la arquitectura completa de QA automatizado

---

## PASO 0 — EXPLORACIÓN DE REPOS (hacer esto PRIMERO)

Antes de generar cualquier código, debes explorar todos los repositorios disponibles y responder:

```
1. ¿Cuántos repos existen? ¿Cuáles son sus nombres y propósitos?
2. ¿Qué lenguaje y versión usa el backend? (esperado: Node.js / Express)
3. ¿Qué framework usa el frontend web B2B? (esperado: Next.js / React)
4. ¿Qué framework usa el Admin? (esperado: Next.js / React)
5. ¿Qué framework usa la APP mobile? (confirmado: React Native + Expo SDK 53 + TypeScript. Java legacy como submodule Android para Realm/SessionBridge)
6. ¿Qué base de datos usa? (esperado: MongoDB)
7. ¿Qué librerías de testing ya están instaladas?
8. ¿Existe algún archivo de CI/CD (.github/workflows, etc.)?
9. ¿Cómo están estructuradas las rutas de la API? (ver referencia abajo)
10. ¿Cómo maneja la autenticación? (Bearer token / username-password)
11. ¿Qué sistema de pagos está integrado?
12. ¿Cómo se manejan las integraciones con ERPs de clientes?
```

Genera un reporte de exploración antes de continuar.

### Referencia: APIs documentadas (integration-docs)

| Entidad | Endpoint | Propósito |
|---|---|---|
| Health | `/api/health-check` | Estado del API |
| Comercios | `/api/commerce` | Empresas B2B que compran |
| Productos | `/api/product` | Catálogo de productos |
| Vendedores | `/api/seller` | Fuerza de venta (APP) |
| Supervisores | `/api/supervisor` | Gestión de vendedores |
| Stock | `/api/stock` | Inventario por centro de distribución |
| Asignación Vendedores | `/api/seller-assignment` | Vendedor ↔ Comercio |
| Sobrescrituras | `/api/override` | Precios custom por segmento |
| Promociones | `/api/promotion` | Descuentos por producto/segmento |
| Segmentos | `/api/segment` | Categorización de comercios |
| Pagos | `/api/payment` | Transacciones financieras |
| Documentos Tributarios | `/api/tax-document` | Facturas, boletas, notas de crédito |
| Centros Distribución | `/api/distribution-center` | Almacenes y cobertura |
| Órdenes | `/api/order` | Pedidos de compra |

---

## CONTEXTO DEL PRODUCTO

**Tipo:** Plataforma SaaS B2B — digitalización del canal tradicional
**Nombre:** YOM (You Order Me)
**Dominio:** youorder.me
**Plataformas:** Web B2B + Admin + APP mobile
**Base de datos:** MongoDB
**API:** REST v2 (`api.youorder.me`)

### Herramientas

| Plataforma | URL / Acceso | Stack esperado |
|---|---|---|
| **B2B** (tienda) | `{cliente}.youorder.me` | Next.js / React |
| **Admin** | `admin.youorder.me` | Next.js / React |
| **APP** (vendedores) | App móvil | React Native + Expo SDK 53 + TypeScript. Java Android legacy como submodule (`yom-sales`) para Realm/Native Modules |
| **API** | `api.youorder.me/api/v2/` | Node.js / Express |

### Roles en el sistema

| ID | Rol | Descripción |
|---|---|---|
| COMMERCE | Comercio | Negocio que compra productos a través del B2B |
| SELLER | Vendedor | Fuerza de venta que gestiona comercios vía APP |
| SUPERVISOR | Supervisor | Gestiona y supervisa vendedores |
| ADMIN | Administrador | Gestiona la plataforma por cliente |
| CLIENT_ADMIN | Admin del cliente | Empresa que vende (configura su tienda) |

### Modelo de negocio

```
Empresa grande (cliente YOM) → Plataforma YOM → Canal tradicional (comercios, tiendas, distribuidores)
```

- Cada **cliente** de YOM tiene su propia tienda B2B (`{slug}.youorder.me`)
- Los **comercios** compran productos del cliente a través del B2B
- Los **vendedores** gestionan comercios y toman pedidos vía APP
- Los **pagos** son B2B (transferencia, crédito, factura) — no hay pago con tarjeta en plataforma
- Las **integraciones** sincronizan datos entre el ERP del cliente y YOM

### Modelo de datos principal

```
Comercios → Segmentos → Sobrescrituras (precios custom)
     ↓                        ↓
Vendedores → Asignaciones    Productos → Stock → Centros Distribución
     ↓                        ↓
Supervisores                 Promociones (descuentos por reglas)
                              ↓
                    Órdenes → Pagos → Documentos Tributarios
```

---

## ARQUITECTURA DE TESTS A CONSTRUIR

### Estructura de carpetas esperada

```
tests/
├── unit/
│   ├── services/
│   │   ├── order.service.test.ts
│   │   ├── pricing.service.test.ts
│   │   ├── promotion.service.test.ts
│   │   ├── stock.service.test.ts
│   │   └── override.service.test.ts
│   ├── models/
│   │   ├── order.model.test.ts
│   │   ├── product.model.test.ts
│   │   ├── commerce.model.test.ts
│   │   └── payment.model.test.ts
│   └── utils/
│       ├── pricing.util.test.ts
│       └── validation.util.test.ts
├── integration/
│   ├── api/
│   │   ├── auth/
│   │   ├── products/
│   │   ├── orders/
│   │   ├── payments/
│   │   ├── commerces/
│   │   ├── stock/
│   │   ├── promotions/
│   │   ├── overrides/
│   │   ├── segments/
│   │   ├── sellers/
│   │   └── tax-documents/
│   ├── database/
│   │   ├── commerce.db.test.ts
│   │   ├── order.db.test.ts
│   │   └── product.db.test.ts
│   └── integrations/
│       ├── erp-injection.test.ts
│       ├── scheduled-api.test.ts
│       └── data-sync.test.ts
├── e2e/
│   ├── b2b/
│   │   ├── auth.spec.ts
│   │   ├── catalog.spec.ts
│   │   ├── cart.spec.ts
│   │   ├── checkout.spec.ts
│   │   ├── orders.spec.ts
│   │   ├── promotions.spec.ts
│   │   └── search.spec.ts
│   ├── admin/
│   │   ├── auth.spec.ts
│   │   ├── products.spec.ts
│   │   ├── orders.spec.ts
│   │   ├── commerces.spec.ts
│   │   ├── promotions.spec.ts
│   │   ├── banners.spec.ts
│   │   └── store-config.spec.ts
│   └── app/
│       ├── auth.spec.ts
│       ├── route.spec.ts
│       ├── order-taking.spec.ts
│       ├── suggestions.spec.ts
│       └── offline.spec.ts
├── fixtures/
│   ├── commerces.fixture.ts
│   ├── products.fixture.ts
│   ├── orders.fixture.ts
│   ├── payments.fixture.ts
│   ├── sellers.fixture.ts
│   ├── promotions.fixture.ts
│   ├── overrides.fixture.ts
│   └── segments.fixture.ts
├── helpers/
│   ├── auth.helper.ts
│   ├── db.helper.ts
│   ├── api.helper.ts
│   └── erp-mock.helper.ts
└── config/
    ├── jest.config.ts (o vitest.config.ts)
    ├── playwright.config.ts
    ├── setup.ts
    └── teardown.ts
```

---

## FLUJOS CRÍTICOS — TIER 1 (PRIORIDAD MÁXIMA)

Estos flujos son los primeros en construirse. Si alguno falla en producción, el cliente no puede operar.

---

### [C1] Login de Comercio (B2B)

**Descripción:** El comercio accede a su tienda B2B para comprar productos.
**Impacto si falla:** Ningún comercio puede usar la plataforma.

| ID | Caso | Datos de entrada | Resultado esperado | Tipo |
|---|---|---|---|---|
| C1-01 | Login exitoso con email y contraseña | email válido, password correcto | Token de sesión, redirect a catálogo | Unit + E2E |
| C1-02 | Login fallido — contraseña incorrecta | email válido, password incorrecto | Error 401, mensaje claro | Unit + Integration |
| C1-03 | Login fallido — usuario no existe | email no registrado | Error genérico (no revelar existencia) | Unit + Integration |
| C1-04 | Bloqueo por intentos fallidos | 5+ intentos fallidos | Cuenta bloqueada, email de aviso | Integration |
| C1-05 | Login con comercio bloqueado (crédito) | comercio con estado BLOQUEADO | Error específico, no acceso o acceso restringido | Integration |
| C1-06 | Recuperación de contraseña | email registrado | Email enviado, link expira en X tiempo | Integration |
| C1-07 | Sesión persistente | login con "recordarme" | Sesión persiste al cerrar browser | E2E |
| C1-08 | Logout exitoso | usuario autenticado | Token invalidado, redirect a login | Unit + E2E |
| C1-09 | Token expirado | token vencido en request | Error 401, refresh o redirect a login | Integration |
| C1-10 | Login de vendedor (APP) | credenciales de vendedor | Accede a lista de comercios asignados | E2E |

---

### [C2] Flujo de Compra Completo (B2B)

**Descripción:** El comercio navega el catálogo, agrega productos al carro y crea un pedido.
**Impacto si falla:** Pérdida directa de ventas, cliente no puede operar.

| ID | Caso | Datos de entrada | Resultado esperado | Tipo |
|---|---|---|---|---|
| C2-01 | Ver catálogo con productos | comercio autenticado | Productos visibles con nombre, precio, imagen | E2E |
| C2-02 | Buscar producto por nombre | término de búsqueda | Resultados relevantes | Integration + E2E |
| C2-03 | Buscar producto por SKU | SKU exacto | Producto encontrado | Integration |
| C2-04 | Navegar por categorías | click en categoría | Productos de esa categoría | E2E |
| C2-05 | Agregar producto al carro | productId, cantidad | Carro actualiza, total correcto | Unit + E2E |
| C2-06 | Agregar producto con cantidad < mínimo | cantidad menor a MinUnit | Error: no permite agregar | Unit + Integration |
| C2-07 | Agregar producto con cantidad no múltiplo del paso | cantidad no válida por step | Error o corrección automática | Unit |
| C2-08 | Modificar cantidad en carro | nueva cantidad | Total recalcula correctamente | Unit + E2E |
| C2-09 | Eliminar producto del carro | productId | Producto removido, total actualiza | Unit + E2E |
| C2-10 | Carro vacío — crear pedido | carro sin items | Error claro, no permite crear pedido | Integration |
| C2-11 | Crear pedido exitoso | carro válido | Orden creada con estado PENDIENTE, confirmación | Integration + E2E |
| C2-12 | Doble submit de crear pedido | doble click en botón | Solo 1 orden creada | Integration |
| C2-13 | Pedido aparece en historial | orden recién creada | Visible en lista con estado correcto | E2E |
| C2-14 | Crear pedido con observaciones | texto de observación | Observación guardada en la orden | Integration |
| C2-15 | Crear pedido con fecha de despacho | fecha seleccionada | Fecha guardada en la orden | Integration |

---

### [C3] Cálculo de Precios y Descuentos

**Descripción:** Los precios se calculan correctamente según segmento, sobrescrituras y promociones.
**Impacto si falla:** Precios incorrectos — pérdida de confianza y dinero.

| ID | Caso | Datos de entrada | Resultado esperado | Tipo |
|---|---|---|---|---|
| C3-01 | Precio base sin sobrescritura | producto sin override para el segmento | Precio base del producto | Unit |
| C3-02 | Precio con sobrescritura REPLACE | override con operación REPLACE | Precio = valor del override | Unit |
| C3-03 | Precio con sobrescritura ADD | override con operación ADD | Precio = base + valor override | Unit |
| C3-04 | Precio con sobrescritura MULTIPLY | override con operación MULTIPLY | Precio = base × factor override | Unit |
| C3-05 | Prioridad de sobrescrituras | múltiples overrides para mismo producto | Aplica el de mayor prioridad (menor número) | Unit |
| C3-17 | Producto sin override en ningún segmento | producto sin override para comercio | Producto NO visible en catálogo (override base tiene enabled=false) | Unit + Integration |
| C3-18 | Override base (enabled=false) + override segmento (enabled=true) | comercio en segmento con override activo | Producto visible con precio del override de segmento | Unit |
| C3-19 | Override base con precio trampa (99999) sin override de segmento | producto solo con override base | Producto oculto. Si visible, precio $99.999 indica error de config | Integration |
| C3-20 | Comercio en múltiples segmentos con overrides conflictivos | 2+ segmentos con overrides para mismo producto | Se aplica override del segmento con menor número de prioridad | Unit |
| C3-21 | Override con enabled=false en segmento prioritario | segmento prioridad 1 con enabled=false, segmento prioridad 5 con enabled=true | Producto oculto (prioridad 1 manda) | Unit |
| C3-06 | Promoción de catálogo activa | producto con promoción vigente | Precio descontado visible | Unit + Integration |
| C3-07 | Promoción expirada | promoción fuera de fecha | Precio vuelve a normal | Unit |
| C3-08 | Descuento por volumen — escala 1 | cantidad >= umbral escala 1 | Descuento escala 1 aplicado | Unit |
| C3-09 | Descuento por volumen — escala 2 | cantidad >= umbral escala 2 | Descuento escala 2 (mayor) aplicado | Unit |
| C3-10 | Descuento por volumen — debajo del umbral | cantidad < mínimo de cualquier escala | Sin descuento de volumen | Unit |
| C3-11 | Precio bruto vs neto | configuración del sitio | Formato consistente en catálogo, carro y pedido | Integration + E2E |
| C3-12 | Precio futuro con fecha de despacho | deliveryDate en request | Precio cambia según fecha | Integration |
| C3-13 | Total del carro con múltiples descuentos | productos con distintas promos | Total = suma correcta de precios finales | Unit |
| C3-14 | Cupón de descuento válido | código de cupón activo | Descuento aplicado al total | Unit + Integration |
| C3-15 | Cupón expirado | código vencido | Error claro, precio sin descuento | Unit + Integration |
| C3-16 | Bloqueo por precio anómalo (< $50) | producto con precio < $50 | No permite agregar al carro | Unit + Integration |

---

### [C4] Inyección de Pedido al ERP

**Descripción:** El pedido creado en YOM se envía al ERP del cliente para procesamiento.
**Impacto si falla:** Pedidos se pierden, el cliente no recibe las órdenes.

| ID | Caso | Datos de entrada | Resultado esperado | Tipo |
|---|---|---|---|---|
| C4-01 | Inyección exitosa | orden creada, hook configurado | Pedido recibido por ERP, estado CONFIRMADA | Integration |
| C4-02 | Inyección con timeout | ERP no responde en tiempo SLA | Orden queda PENDIENTE, reintento programado | Integration |
| C4-03 | Inyección con error de ERP | ERP responde con error | Error logueado, notificación a ops, orden no se pierde | Integration |
| C4-04 | Inyección con datos inválidos | orden con campo requerido faltante | Validación antes de enviar, error descriptivo | Unit + Integration |
| C4-05 | Webhook de confirmación | ERP confirma recepción | Orden actualiza a estado EN_PROCESO | Integration |
| C4-06 | Actualización de estado desde ERP | ERP envía nuevo estado | Orden refleja estado actualizado en B2B y APP | Integration |
| C4-07 | Pedido con múltiples items | orden con 20+ productos | Todos los items se inyectan correctamente | Integration |
| C4-08 | Reintentos ante fallo | 3 fallos consecutivos | Reintentos con backoff, alerta después de N fallos | Integration |
| C4-09 | `externalIdRequired = true` sin externalId | Cliente con `externalIdRequired: true`, orden creada sin `commerce.contact.externalId` | Hook retorna null — orden se crea en YOM pero NO se envía al ERP. Fallo silencioso. Verificar en `db.erpIntegrations.find({domain})` que el registro existe con `isSuccess: true` | Integration |

---

### [C5] Canasta Base y Recomendaciones

**Descripción:** El sistema sugiere productos al comercio basado en su historial de compras.
**Impacto si falla:** Valor comercial principal de la plataforma desaparece.

| ID | Caso | Datos de entrada | Resultado esperado | Tipo |
|---|---|---|---|---|
| C5-01 | Canasta base con historial | comercio con 13+ meses de órdenes | Sugerencias de 5-N productos frecuentes | Integration |
| C5-02 | Cold start — comercio nuevo | comercio sin historial | Productos populares de comercios similares | Integration |
| C5-03 | Canasta respeta MINSIZE/MAXSIZE | parámetros configurados | Cantidad de sugerencias dentro del rango | Unit |
| C5-04 | Canasta con ALPHA=2 | ALPHA configurado en 2 | Sugiere el doble de productos óptimos | Unit |
| C5-05 | Sugerencia se puede agregar al carro | click en "agregar" desde sugerencia | Producto agregado correctamente al carro | E2E |
| C5-06 | Canasta Exploración | comercio con historial | Sugiere productos de comercios similares (no los que ya compra) | Integration |
| C5-07 | Canasta Foco | SAF del cliente configurado | SKUs estratégicos priorizados | Integration |
| C5-08 | Consistencia B2B-APP | mismo comercio | Mismas sugerencias en ambas plataformas | Integration |

---

### [C6] Sincronización de Datos (Scheduled API)

**Descripción:** YOM consume los endpoints del cliente para mantener datos actualizados.
**Impacto si falla:** Catálogo desactualizado, precios incorrectos, stock irreal.

| ID | Caso | Datos de entrada | Resultado esperado | Tipo |
|---|---|---|---|---|
| C6-01 | Sync de productos exitoso | endpoint /api/product del cliente | Productos actualizados en YOM | Integration |
| C6-02 | Sync de precios/overrides | endpoint /api/override | Precios por segmento actualizados | Integration |
| C6-03 | Sync de stock | endpoint /api/stock | Niveles de stock actualizados | Integration |
| C6-04 | Sync de comercios | endpoint /api/commerce | Datos de comercios actualizados | Integration |
| C6-05 | Sync con paginación | >1000 registros | Todos los registros procesados correctamente | Integration |
| C6-06 | Sync con filtro de fechas | updated_from/updated_to | Solo registros modificados se actualizan | Integration |
| C6-07 | Endpoint del cliente caído | timeout o error 500 | Log de error, reintento, no se pierden datos existentes | Integration |
| C6-08 | Datos con formato inválido | JSON malformado del cliente | Error logueado, registros válidos se procesan | Integration |
| C6-09 | Producto DISCONTINUED | estado cambia a DISCONTINUED | Producto no visible en catálogo | Integration |
| C6-10 | CronJob ejecuta en horario | ventana configurada | Job corre y completa dentro de la ventana | Integration |

---

### [V1] Vendedor Toma Pedido (APP)

**Descripción:** El vendedor visita un comercio y toma un pedido desde la APP.
**Impacto si falla:** Fuerza de venta paralizada, comercios sin atención.

| ID | Caso | Datos de entrada | Resultado esperado | Tipo |
|---|---|---|---|---|
| V1-01 | Ver lista de comercios asignados | vendedor autenticado | Solo comercios del vendedor visibles | Integration + E2E |
| V1-02 | Seleccionar comercio de la ruta | click en comercio | Datos del comercio visibles | E2E |
| V1-03 | Tomar pedido — agregar productos | productos + cantidades | Carro del comercio se llena | E2E |
| V1-04 | Confirmar pedido | carro válido | Orden creada asociada al comercio y vendedor | Integration + E2E |
| V1-05 | Pedido offline | sin conexión a internet | Pedido se encola localmente | E2E |
| V1-06 | Sync de pedidos offline | conexión restaurada | Pedidos encolados se envían, confirmación | Integration + E2E |
| V1-07 | Ver historial de pedidos del comercio | comercio seleccionado | Lista de pedidos anteriores | E2E |
| V1-08 | Re-hacer pedido anterior | pedido del historial | Productos del pedido anterior en el carro | E2E |
| V1-09 | Canasta sugerida en APP | comercio con historial | Sugerencias visibles, agregables al carro | Integration + E2E |
| V1-10 | Georreferencia del comercio | APP con permisos GPS | Ubicación correcta en mapa | E2E |

---

### [A1] Login de Admin

**Descripción:** El administrador accede al panel para gestionar la tienda del cliente.
**Impacto si falla:** Sin gestión de productos, pedidos, promociones ni comercios.

| ID | Caso | Datos de entrada | Resultado esperado | Tipo |
|---|---|---|---|---|
| A1-01 | Login admin exitoso | credenciales válidas | Acceso al dashboard | E2E |
| A1-02 | Login admin — credenciales inválidas | password incorrecto | Error 401, acceso denegado | Integration |
| A1-03 | Acceso a ruta admin sin autenticación | request directo a /admin | Redirect a login, no data expuesta | Integration |
| A1-04 | Acceso a admin con rol de comercio | token de COMMERCE | Error 403, acceso denegado | Integration |
| A1-05 | Sesión admin expira por inactividad | 30+ min sin actividad | Sesión cerrada, redirect a login | E2E |
| A1-06 | Admin gestiona productos | CRUD de productos | Productos reflejados en B2B | Integration + E2E |
| A1-07 | Admin gestiona promociones | crear/editar promoción | Promoción activa en B2B | Integration + E2E |
| A1-08 | Admin gestiona banners | crear banner con imagen y URL | Banner visible en B2B | Integration + E2E |

---

### [C7] Documentos Tributarios

**Descripción:** Facturas, boletas, notas de crédito y notas de débito generados a partir de pedidos.
**Impacto si falla:** Documentos tributarios incorrectos — problemas legales y contables para el cliente.

| ID | Caso | Datos de entrada | Resultado esperado | Tipo |
|---|---|---|---|---|
| C7-01 | Factura generada post-pedido | orden confirmada con datos fiscales | Factura con tipo FACTURA, items correctos, montos coinciden con orden | Integration |
| C7-02 | Numeración correlativa | múltiples facturas del mismo cliente | Números correlativos sin saltos (prefijo + serie + número) | Integration |
| C7-03 | Datos fiscales completos | factura emitida | RUT emisor, razón social, dirección fiscal, giro presentes y correctos | Integration |
| C7-04 | Desglose de impuestos | factura con IVA (useTaxRate=true) | taxDetails muestra tasa, monto y base imponible correctos | Integration |
| C7-05 | Factura exenta | comercio exento de impuestos | taxDetails.exempt=true, monto impuesto = 0 | Integration |
| C7-06 | Nota de crédito vinculada | NC emitida para factura existente | NC referencia documentId de factura original, montos coinciden | Integration |
| C7-07 | Nota de crédito parcial | NC por devolución de 1 item | NC con items parciales, monto menor que factura original | Integration |
| C7-08 | Boleta vs factura según comercio | comercio tipo persona vs empresa | Tipo de documento correcto según clasificación tributaria | Integration |
| C7-09 | Documento anulado | factura con status ANULADO | Documento no aparece en cobros pendientes, cancelledAt presente | Integration |
| C7-10 | Factura visible en B2B | enablePaymentDocumentsB2B=true | Botón de facturas visible en lista de órdenes, descarga funciona | E2E |
| C7-11 | Lista de facturas en menú | enableInvoicesList=true | Opción de facturas accesible desde menú de órdenes | E2E |
| C7-12 | Documentos pendientes badge | pendingDocuments=true | Indicador/badge de documentos pendientes visible en menú | E2E |

---

### [C8] Validación de Integración del Cliente (Pre-QA)

**Descripción:** Los endpoints del cliente cumplen los requisitos técnicos para que la sync de datos funcione.
**Impacto si falla:** Datos desactualizados, precios incorrectos, stock irreal — todo lo que QA detecta como "dato malo" puede venir de aquí.

| ID | Caso | Datos de entrada | Resultado esperado | Tipo |
|---|---|---|---|---|
| C8-01 | Health check del API del cliente | GET /api/health-check | Respuesta 200 OK, API accesible | Integration |
| C8-02 | Endpoints sobre HTTPS | cualquier endpoint del cliente | Solo HTTPS, no HTTP plano | Integration |
| C8-03 | Autenticación funcional | token o credenciales del cliente | Auth exitoso, token válido retornado | Integration |
| C8-04 | Paginación implementada | GET /api/product?page=1&limit=50 | Respuesta con pagination: current_page, total_pages, total_items | Integration |
| C8-05 | Filtro de fechas funcional | GET /api/product?updated_from=2026-01-01 | Solo registros actualizados después de la fecha | Integration |
| C8-06 | Formato JSON UTF-8 | cualquier endpoint | Content-Type: application/json; charset=utf-8 | Integration |
| C8-07 | Tiempo de respuesta < 100s | endpoint con datos completos | Respuesta en < 100 segundos | Integration |
| C8-08 | Datos históricos completos | GET /api/product (sin filtros) | Incluye productos activos E inactivos (histórico completo) | Integration |
| C8-09 | Whitelist de IPs configurada | request desde IP de YOM | Acceso permitido desde IPs de YOM, bloqueado desde otras | Integration |
| C8-10 | Todos los endpoints disponibles | cada entidad del contrato | Comercios, productos, stock, overrides, promociones, segmentos responden | Integration |

---

## FLUJOS TIER 2 — (implementar después de Tier 1)

| ID | Flujo | Descripción |
|---|---|---|
| C9 | Seguimiento de pedido | Comercio ve estado del pedido en B2B |
| C10 | Estado crediticio | Comercio con crédito bloqueado no puede comprar |
| V2 | Ruta del día | Vendedor ve comercios asignados en orden de visita |
| V3 | Registro de visitas | Vendedor registra visita con encuesta |
| V4 | Cobranza (APP) | Vendedor gestiona facturas y pagos pendientes |
| A2 | Gestión de comercios | Admin invita, activa, bloquea comercios |
| A3 | Configuración de tienda | Admin personaliza branding (logo, colores, favicon) |
| B1 | Notificaciones push | Mensajes masivos desde Admin a comercios |

---

## FLUJOS TIER 3 — (backlog)

| ID | Flujo | Descripción |
|---|---|---|
| C11 | Compartir pedido | Comercio comparte detalle del pedido |
| V5 | Gestión de tareas | Vendedor completa tareas asignadas |
| V6 | Exportación de datos | Vendedor exporta datos de la APP |
| A4 | Dashboards (Metabase) | Admin ve reportes y métricas |
| I1 | Migración SFTP → API | Cuando se habilite SFTP nuevamente |

---

## FIXTURES Y DATOS DE PRUEBA

### commerces.fixture
```
- commerce_active: comercio activo, crédito OK, segmento estándar
- commerce_blocked: comercio con estado crediticio BLOQUEADO
- commerce_alert: comercio con estado crediticio ALERTA
- commerce_new: comercio recién creado, sin historial de compras
- commerce_b2b_multi_segment: comercio en múltiples segmentos con overrides
```

### products.fixture
```
- product_active: producto ACTIVE con stock > 0, imagen, precio base
- product_no_stock: producto ACTIVE con stock = 0
- product_discontinued: producto DISCONTINUED (no debe aparecer en catálogo)
- product_inactive: producto INACTIVE
- product_with_min_unit: producto con MinUnit = 6 (mínimo de compra)
- product_with_step: producto con paso de incremento (comprar en múltiplos)
- product_low_price: producto con precio < $50 (debe bloquearse en carro)
- product_with_labels: producto con new=true, featured=true
- product_multi_format: producto con formatos pack/unidad/caja
```

### orders.fixture
```
- order_pending: orden PENDIENTE (creada, sin confirmar)
- order_confirmed: orden CONFIRMADA por ERP
- order_in_process: orden EN_PROCESO (en preparación)
- order_delivered: orden ENTREGADA
- order_cancelled: orden CANCELADA
- order_with_observations: orden con observaciones del comercio
- order_with_delivery_date: orden con fecha de despacho seleccionada
- order_offline: orden creada offline en APP (pendiente de sync)
```

### payments.fixture
```
- payment_pending: pago PENDING (transferencia no confirmada)
- payment_approved: pago APPROVED
- payment_rejected: pago REJECTED
- payment_by_transfer: pago por TRANSFER
- payment_by_credit: pago con crédito del comercio
```

### sellers.fixture
```
- seller_active: vendedor ACTIVE con zona asignada
- seller_inactive: vendedor INACTIVE
- seller_vacation: vendedor en VACACIONES
- seller_with_route: vendedor con ruta del día configurada
- seller_with_commerces: vendedor con 10 comercios asignados
```

### promotions.fixture
```
- promo_catalog_active: promoción de catálogo vigente (-20% en producto)
- promo_catalog_expired: promoción de catálogo expirada
- promo_volume_stepped: descuento por volumen con 3 escalas
- promo_bundle: pack de productos con descuento
- promo_gift: regalo por compra mínima
- promo_coupon_valid: cupón de descuento activo
- promo_coupon_expired: cupón de descuento vencido
- promo_coupon_used: cupón de uso único ya utilizado
```

### overrides.fixture
```
- override_replace: sobrescritura de precio REPLACE para segmento A
- override_add: sobrescritura ADD (+$500) para segmento B
- override_multiply: sobrescritura MULTIPLY (×0.9) para segmento C
- override_high_priority: override con prioridad 1 (más alta)
- override_low_priority: override con prioridad 10 (más baja)
- override_with_scales: override con escalas de descuento por volumen
- override_base_disabled: override base con enabled=false, prioridad 10000, precio 99999
- override_segment_enabled: override de segmento con enabled=true que activa producto sobre base
- override_conflict_multi_segment: 2 overrides para mismo producto en segmentos distintos con prioridades diferentes
```

### segments.fixture
```
- segment_standard: segmento estándar (prioridad 5)
- segment_premium: segmento premium (prioridad 1)
- segment_wholesale: segmento mayorista con precios especiales
- segment_base: segmento base (prioridad 10000) — todos los comercios pertenecen, overrides con enabled=false
```

### tax_documents.fixture
```
- taxdoc_factura_emitida: factura EMITIDA con items, impuestos y numeración correcta
- taxdoc_factura_exenta: factura con exempt=true, impuesto=0
- taxdoc_boleta: boleta para comercio tipo persona natural
- taxdoc_nota_credito: NC vinculada a factura original, monto parcial
- taxdoc_nota_credito_total: NC por monto total de factura
- taxdoc_anulado: documento con status ANULADO y cancelledAt
- taxdoc_borrador: documento en status BORRADOR (no emitido)
```

---

## SETUP DE CI/CD A CREAR

```yaml
# .github/workflows/qa.yml

name: QA Pipeline

on:
  pull_request:          # Unit + Integration en cada PR
  push:
    branches: [main, staging]  # + E2E en staging

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - checkout
      - setup node
      - install dependencies
      - run unit tests (paralelo)
    # FALLA el PR si no pasan

  integration-tests:
    needs: unit-tests
    runs-on: ubuntu-latest
    services:
      mongodb:
        image: mongo:6
        ports: ['27017:27017']
    steps:
      - checkout
      - setup node
      - install dependencies
      - run integration tests
    # Requiere MongoDB en contenedor

  e2e-tests:
    needs: integration-tests
    if: github.ref == 'refs/heads/staging' || github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - checkout
      - setup node
      - install dependencies
      - install playwright
      - run e2e web tests (B2B + Admin)
      - upload test artifacts (screenshots, videos)
      - notify Slack con resultado
    # Solo en push a staging/main

  e2e-mobile:
    needs: integration-tests
    if: github.ref == 'refs/heads/staging'
    runs-on: ubuntu-latest
    steps:
      - run mobile tests (según framework detectado)
      - upload artifacts
```

---

## REGLAS GENERALES PARA GENERAR LOS TESTS

1. **Cada test debe ser independiente** — no depender del orden ni del estado de otro test
2. **Usar fixtures para datos** — nunca hardcodear emails, IDs o slugs de clientes reales
3. **Limpiar estado después de cada test** — rollback de MongoDB o datos creados
4. **Nombres descriptivos** — `should_block_cart_when_product_price_below_50` no `test_cart_3`
5. **Un assert por comportamiento** — no mezclar múltiples comportamientos en un test
6. **Mockear servicios externos** — ERP del cliente, servicios de email, push notifications en tests unitarios e integración. Solo en E2E usar sandbox
7. **Separar ambientes** — `.env.test` con BD de test, nunca tocar datos de clientes reales
8. **Respetar la lógica de segmentos** — los precios dependen del segmento del comercio, siempre testear con segmento explícito
9. **Testear consistencia cross-platform** — lo que se ve en B2B debe coincidir con APP para el mismo comercio
10. **Testear integraciones con mock de ERP** — crear helper que simule respuestas del ERP del cliente (éxito, timeout, error)

---

## ENTREGABLES ESPERADOS

Al completar este trabajo, deben existir:

- [ ] Reporte de exploración del stack tecnológico (Paso 0)
- [ ] Carpeta `tests/` con estructura completa
- [ ] Tests escritos para todos los casos Tier 1 (unit + integration)
- [ ] Scripts E2E para flujos críticos en B2B (Playwright)
- [ ] Scripts E2E para flujos críticos en Admin (Playwright)
- [ ] Scripts E2E para flujos críticos en APP (según framework)
- [ ] Fixtures reutilizables para los 7 modelos principales
- [ ] Helpers: autenticación, MongoDB, API client, mock ERP
- [ ] Configuración de CI/CD (GitHub Actions)
- [ ] README en `tests/` explicando cómo correr cada suite
- [ ] Mock de ERP para testear inyección de pedidos y sync de datos

---

## REFERENCIA: ESQUEMAS DE DATOS

### Producto
```json
{
  "productId": "string (único)",
  "name": "string",
  "description": "string",
  "brand": "string",
  "category": "string",
  "price": { "amount": "number", "currency": "CLP" },
  "unit": "KG | UN | CAJA",
  "packaging": { "weight": "number", "unitsPerBox": "number" },
  "images": [{ "url": "string" }],
  "attributes": { "flavor": "string", "allergens": ["string"] },
  "restrictions": { "minUnit": "number", "step": "number", "maxUnit": "number" },
  "status": "ACTIVE | INACTIVE | DISCONTINUED",
  "labels": { "new": "boolean", "featured": "boolean" }
}
```

### Orden
```json
{
  "orderId": "string (único)",
  "commerceId": "string",
  "sellerId": "string (opcional)",
  "items": [{
    "productId": "string",
    "quantity": "number",
    "unitPrice": "number",
    "discount": "number",
    "total": "number"
  }],
  "amounts": { "subtotal": "number", "tax": "number", "shipping": "number", "total": "number" },
  "shipping": { "address": "string", "deliveryDate": "date", "notes": "string" },
  "observations": "string",
  "status": "PENDIENTE | CONFIRMADA | EN_PROCESO | ENTREGADA | CANCELADA",
  "createdAt": "date",
  "updatedAt": "date"
}
```

### Comercio
```json
{
  "commerceId": "string (único)",
  "name": "string",
  "type": "string",
  "rut": "string",
  "status": "ACTIVE | INACTIVE | BLOCKED",
  "contact": { "name": "string", "email": "string", "phone": "string" },
  "addresses": [{ "type": "BILLING | SHIPPING", "street": "string", "gps": { "lat": "number", "lng": "number" } }],
  "credit": { "limit": "number", "state": "OK | ALERT | BLOCKED", "terms": "string" },
  "segments": ["string"],
  "assignedSeller": "string",
  "distributionCenter": "string"
}
```

### Sobrescritura (Override)
```json
{
  "productId": "string",
  "segmentId": "string",
  "priority": "number (menor = más alta)",
  "pricing": {
    "unitPrice": "number",
    "operation": "REPLACE | ADD | MULTIPLY",
    "discountType": "PERCENTAGE | FIXED"
  },
  "scales": [{
    "minQuantity": "number",
    "discount": "number"
  }],
  "restrictions": { "minUnit": "number", "step": "number" },
  "validFrom": "date",
  "validTo": "date",
  "status": "ACTIVE | INACTIVE"
}
```

### Promoción
```json
{
  "promotionId": "string",
  "type": "CATALOG | STEPPED | MIXED_STEPPED | GIFT | BUNDLE",
  "scope": "PRODUCTS | SEGMENTS | CATEGORIES | BRANDS",
  "targets": ["string"],
  "discount": { "type": "PERCENTAGE | FIXED", "value": "number" },
  "conditions": { "minQuantity": "number", "maxQuantity": "number" },
  "scales": [{ "minQty": "number", "discount": "number" }],
  "validFrom": "date",
  "validTo": "date",
  "status": "ACTIVE | INACTIVE"
}
```

---

*Documento adaptado para YOM — basado en integration-docs (github.com/YOMCL) y matriz de features*
*Versión 1.0 — 2026-03-24*

# QA Checklist — Soprole
**Fecha:** 2026-03-25  
**Features activas:** 40 (35 B2B, 23 APP, 4 Admin)  
**Requieren integración:** 0  
**Casos de prueba:** 159

**Tipos de prueba:**  
⚙️ Funcional — ¿funciona? · 📊 Datos — ¿datos correctos? · 🔀 Edge case — ¿qué pasa si...? · 🔗 Integración — ¿ERP conectado? · 🎨 Visual — ¿se ve bien? · 💼 Regla de negocio — ¿lógica comercial correcta?

---

## 1. Pre-vuelo

| # | Verificación | Cómo validar | ✓ |
|---|---|---|---|
| 1 | Catálogo cargado | Admin → Productos: hay productos del cliente | ☐ |
| 2 | Categorías configuradas | B2B → Navegación: categorías visibles | ☐ |
| 3 | Precios correctos | Comparar 5 productos con fuente del cliente | ☐ |
| 4 | Branding aplicado | B2B: logo, colores, favicon del cliente | ☐ |
| 5 | Usuarios de prueba | Tener credenciales: comercio + admin + vendedor | ☐ |
| 6 | Integraciones activas | Confirmar con Analytics — 0 features requieren integración | ☐ |
| 7 | Variables de entorno | Confirmar con Tech que están configuradas | ☐ |

---

## 2. Accesos

| # | Test | Herramienta | Pasos | ✓ |
|---|---|---|---|---|
| 1 | Login B2B | B2B | Ir a soprole.youorder.me → credenciales comercio | ☐ |
| 2 | Login Admin | Admin | Ir a admin.youorder.me → credenciales admin | ☐ |
| 3 | Login APP | APP | Abrir app → credenciales vendedor | ☐ |
| 4 | Cambio de contraseña | B2B | Flujo 'olvidé mi contraseña' → email → reset | ☐ |

---

## 3. Flujos core

### 3.1 Flujo de compra B2B

```
Catálogo → Seleccionar producto → Agregar al carro → Revisar carro → Crear pedido → Confirmación
```

| # | Paso | Qué verificar | ✓ |
|---|---|---|---|
| 1 | Catálogo | Productos visibles, navegables, con precio | ☐ |
| 2 | Detalle producto | Precio, descripción, imagen, botón agregar | ☐ |
| 3 | Agregar al carro | Feedback visual, contador actualiza | ☐ |
| 4 | Carro de compras | Items, cantidades, precios, total correcto | ☐ |
| 5 | Modificar carro | Cambiar cantidad, eliminar item, total recalcula | ☐ |
| 6 | Crear pedido | Botón funciona, no permite doble click | ☐ |
| 7 | Confirmación | Resumen del pedido, número de orden | ☐ |
| 8 | Historial | Pedido aparece en lista con estado correcto | ☐ |

### 3.2 Flujo de compra APP

| # | Paso | Qué verificar | ✓ |
|---|---|---|---|
| 1 | Seleccionar comercio | Lista visible, se puede elegir | ☐ |
| 2 | Tomador de pedidos | Catálogo del comercio carga | ☐ |
| 3 | Agregar productos | Cantidad, feedback visual | ☐ |
| 4 | Confirmar pedido | Resumen correcto, confirmación | ☐ |
| 5 | Historial | Pedido aparece con estado | ☐ |

---

## 4. Features del cliente — Casos de prueba

### Venta

#### Alerta de cliente bloqueado (B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Comercio bloqueado: popup con alerta HTML personalizada | ⚙️ funcional | ☐ |
| 2 | B2B | Comercio no bloqueado: sin popup | ⚙️ funcional | ☐ |

#### Bloqueo (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Comercio bloqueado: acción de venta restringida | 💼 negocio | ☐ |
| 2 | APP | Indicador visual de bloqueo | ⚙️ funcional | ☐ |

#### Bloqueo de carro en casos de precios anómalos (APP, B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Producto con precio < $50: no se puede agregar al carro | 💼 negocio | ☐ |
| 2 | B2B | Mensaje claro de por qué está bloqueado | ⚙️ funcional | ☐ |
| 3 | APP | Mismo bloqueo funcional en APP | ⚙️ funcional | ☐ |

#### Botones de acceso configurables (deprecado) (B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Feature visible y accesible | ⚙️ funcional | ☐ |
| 2 | B2B | Funcionalidad principal opera correctamente | ⚙️ funcional | ☐ |

#### Búsqueda de productos (B2B, APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Buscar por nombre exacto: producto aparece primero | ⚙️ funcional | ☐ |
| 2 | B2B | Buscar por SKU: producto encontrado | ⚙️ funcional | ☐ |
| 3 | B2B | Buscar término parcial: resultados relevantes | ⚙️ funcional | ☐ |
| 4 | B2B | Buscar término inexistente: mensaje 'sin resultados', no error | 🔀 edge | ☐ |
| 5 | B2B | Buscar con caracteres especiales (ñ, tildes): funciona correctamente | 🔀 edge | ☐ |
| 6 | APP | Búsqueda en APP retorna mismos resultados que B2B | 📊 datos | ☐ |

#### Cambio de contraseña (APP, B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Flujo 'olvidé contraseña': email llega | ⚙️ funcional | ☐ |
| 2 | B2B | Link de reset funciona y permite cambiar | ⚙️ funcional | ☐ |
| 3 | B2B | Nueva contraseña: login exitoso | ⚙️ funcional | ☐ |
| 4 | APP | Mismo flujo funcional en APP | ⚙️ funcional | ☐ |

#### Carro de compras (B2B, APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Agregar producto: carro actualiza contador y total | ⚙️ funcional | ☐ |
| 2 | B2B | Modificar cantidad: total recalcula correctamente | ⚙️ funcional | ☐ |
| 3 | B2B | Eliminar producto del carro: se remueve y total actualiza | ⚙️ funcional | ☐ |
| 4 | B2B | Carro vacío: mensaje descriptivo, no pantalla en blanco | 🔀 edge | ☐ |
| 5 | B2B | Carro con producto sin stock: muestra aviso (si stock integrado) | 🔀 edge | ☐ |
| 6 | B2B | Carro persiste al navegar entre páginas | ⚙️ funcional | ☐ |
| 7 | B2B | Carro persiste al cerrar y reabrir sesión | 🔀 edge | ☐ |

#### Catálogo (B2B, APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Abrir catálogo: productos visibles con nombre, precio e imagen | ⚙️ funcional | ☐ |
| 2 | B2B | Navegar por categorías: cada categoría muestra productos relevantes | ⚙️ funcional | ☐ |
| 3 | B2B | Producto sin imagen: muestra placeholder, no quiebra layout | 🔀 edge | ☐ |
| 4 | B2B | Catálogo con +500 productos: scroll fluido, paginación/infinite scroll funciona | 🔀 edge | ☐ |
| 5 | APP | Catálogo filtra por portafolio del vendedor (si configurado) | 💼 negocio | ☐ |
| 6 | APP | Catálogo funciona offline (muestra última sincronización) | 🔀 edge | ☐ |
| 7 | Admin | Productos en Admin coinciden con lo que muestra B2B | 📊 datos | ☐ |

#### Cobranza y facturación (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Documentos de cobranza visibles para el comercio | ⚙️ funcional | ☐ |
| 2 | APP | Facturas con datos correctos (monto, fecha, estado) | 📊 datos | ☐ |

#### Compra mínima (B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Pedido por debajo del mínimo: no permite crear | 💼 negocio | ☐ |
| 2 | B2B | Mensaje claro con el monto mínimo | ⚙️ funcional | ☐ |

#### Contacto (B2B, APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Información de contacto del comercio visible | ⚙️ funcional | ☐ |
| 2 | B2B | Datos de contacto correctos | 📊 datos | ☐ |

#### Crear pedido (B2B, APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Flujo completo: catálogo → producto → carro → checkout → confirmación | ⚙️ funcional | ☐ |
| 2 | B2B | Pedido con 1 solo producto: se crea correctamente | ⚙️ funcional | ☐ |
| 3 | B2B | Pedido con 20+ productos: todos aparecen en resumen y confirmación | 🔀 edge | ☐ |
| 4 | B2B | Pedido con cantidad 0 o negativa: no permite crear | 🔀 edge | ☐ |
| 5 | B2B | Doble click en 'crear pedido': no genera pedido duplicado | 🔀 edge | ☐ |
| 6 | B2B | Pedido aparece en historial inmediatamente después de crear | ⚙️ funcional | ☐ |
| 7 | APP | Crear pedido desde tomador: seleccionar comercio → productos → confirmar | ⚙️ funcional | ☐ |
| 8 | APP | Crear pedido offline: se encola y envía al recuperar conexión | 🔀 edge | ☐ |

#### Cupón de descuento (Admin, B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Campo para ingresar cupón visible en checkout | ⚙️ funcional | ☐ |
| 2 | B2B | Cupón válido: descuento se aplica al total | ⚙️ funcional | ☐ |
| 3 | B2B | Cupón inválido: mensaje de error claro | 🔀 edge | ☐ |
| 4 | B2B | Cupón expirado: mensaje de error claro | 🔀 edge | ☐ |
| 5 | B2B | Cupón ya usado (si uso único): rechazado | 🔀 edge | ☐ |
| 6 | Admin | Crear cupón: fecha inicio, fin, tipo descuento, monto | ⚙️ funcional | ☐ |

#### Detalle del producto (B2B, APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Muestra: nombre, descripción, precio, imagen, especificaciones | ⚙️ funcional | ☐ |
| 2 | APP | Producto sin imagen: muestra placeholder | 🔀 edge | ☐ |
| 3 | APP | Producto sin descripción: no muestra campo vacío | 🔀 edge | ☐ |

#### Documentos manuales (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Crear documento manual: formulario funcional | ⚙️ funcional | ☐ |
| 2 | APP | Documento creado aparece en historial | ⚙️ funcional | ☐ |

#### Edición de comercios (B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Edición deshabilitada: campos no editables | ⚙️ funcional | ☐ |
| 2 | B2B | Edición de dirección: campos editables en checkout, cambio se guarda | ⚙️ funcional | ☐ |
| 3 | B2B | Tipo de recibo oculto: selector no visible en checkout | ⚙️ funcional | ☐ |

#### FAQ (B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Sección FAQ visible y accesible | ⚙️ funcional | ☐ |
| 2 | B2B | Contenido relevante al cliente (no genérico de otro) | 📊 datos | ☐ |
| 3 | B2B | Links dentro de FAQ funcionan | ⚙️ funcional | ☐ |

#### Filtros de productos (B2B, APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Filtros disponibles y funcionales | ⚙️ funcional | ☐ |
| 2 | APP | Filtro por categoría: muestra solo productos de esa categoría | ⚙️ funcional | ☐ |
| 3 | APP | Combinar filtros: resultados coherentes | 🔀 edge | ☐ |
| 4 | APP | Limpiar filtros: vuelve a mostrar todo | ⚙️ funcional | ☐ |

#### Gestión de pedidos (Admin, B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Lista de pedidos completa | ⚙️ funcional | ☐ |
| 2 | Admin | Pedidos visibles con detalle completo | ⚙️ funcional | ☐ |
| 3 | Admin | Filtrar pedidos por fecha, estado, comercio | ⚙️ funcional | ☐ |

#### Historial de facturas (APP, B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Historial de facturas visible | ⚙️ funcional | ☐ |
| 2 | APP | Mismas facturas visibles en APP | 📊 datos | ☐ |

#### Historial de pagos (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Lista de facturas y pagos del comercio | ⚙️ funcional | ☐ |
| 2 | APP | Detalle de cada documento: monto, fecha, estado | ⚙️ funcional | ☐ |
| 3 | APP | Datos coinciden con fuente del cliente (PendingDocuments) | 📊 datos | ☐ |

#### Historial de pedidos (B2B, APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Lista muestra pedidos del comercio logueado | ⚙️ funcional | ☐ |
| 2 | B2B | Detalle de pedido: items, cantidades, precios, total correcto | ⚙️ funcional | ☐ |
| 3 | B2B | Pedido recién creado aparece al tope de la lista | ⚙️ funcional | ☐ |
| 4 | APP | Historial en APP coincide con B2B para el mismo comercio | 📊 datos | ☐ |

#### Home y experiencia (APP, Admin, B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Home habilitado: página con banners/contenido al entrar | ⚙️ funcional | ☐ |
| 2 | B2B | Hora estimada de entrega oculta cuando configurado | ⚙️ funcional | ☐ |
| 3 | B2B | Footer personalizado: HTML custom renderiza correctamente | 🎨 visual | ☐ |
| 4 | B2B | Botones beta visibles y funcionales cuando habilitado | ⚙️ funcional | ☐ |
| 5 | B2B | Texto personalizado en botón confirmar carro | 🎨 visual | ☐ |
| 6 | APP | Filtro de no venta: lista filtra correctamente | ⚙️ funcional | ☐ |
| 7 | Admin | Límite de descuento visible cuando configurado | ⚙️ funcional | ☐ |

#### Impuestos para productos (B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Impuestos calculados correctamente según config | ⚙️ funcional | ☐ |
| 2 | B2B | Desglose de impuestos visible (si aplica) | ⚙️ funcional | ☐ |

#### Listas de precio (Admin, B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Comercio del segmento A ve precios del segmento A | 💼 negocio | ☐ |
| 2 | B2B | Comercio del segmento B ve precios diferentes al segmento A | 💼 negocio | ☐ |
| 3 | B2B | Precio en detalle de producto = precio en carro = precio en pedido | 📊 datos | ☐ |
| 4 | Admin | Overrides aplicados por segmento visibles en Admin | 📊 datos | ☐ |

#### Log in App (APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Login con credenciales de vendedor: accede a la app | ⚙️ funcional | ☐ |
| 2 | APP | Login con credenciales inválidas: mensaje claro | 🔀 edge | ☐ |

#### Log in B2B (B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Login con credenciales válidas: accede al catálogo | ⚙️ funcional | ☐ |
| 2 | B2B | Login con credenciales inválidas: mensaje de error claro | 🔀 edge | ☐ |
| 3 | B2B | Login con campo vacío: validación de formulario | 🔀 edge | ☐ |

#### Método de pago (B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Métodos de pago del cliente configurados y visibles | ⚙️ funcional | ☐ |

#### Módulo de pagos (B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Sección de pagos visible en menú lateral cuando habilitado | ⚙️ funcional | ☐ |
| 2 | B2B | Pagos deshabilitados: sección oculta, rutas devuelven 403 | ⚙️ funcional | ☐ |
| 3 | B2B | Nuevo módulo de pagos renderiza correctamente | ⚙️ funcional | ☐ |
| 4 | B2B | Pago requiere monto completo: pago parcial muestra error | 💼 negocio | ☐ |
| 5 | B2B | Pago externo: redirect a pasarela, callback correcto | 🔗 integración | ☐ |
| 6 | B2B | Validar pago desde admin: pago cambia a APPROVED | ⚙️ funcional | ☐ |

#### Notificaciones y alertas (APP, B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Notificaciones sobre estado de pedidos llegan | ⚙️ funcional | ☐ |
| 2 | APP | Alertas de facturas/pedidos visibles | ⚙️ funcional | ☐ |

#### Ordenar (B2B, APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Ordenar por precio ascendente: funciona | ⚙️ funcional | ☐ |
| 2 | APP | Ordenar por nombre: funciona | ⚙️ funcional | ☐ |
| 3 | APP | Cambiar criterio de orden: lista se actualiza | ⚙️ funcional | ☐ |

#### Packaging y empaque (B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Info empaque oculta cuando hidePackagingInformationB2B=true | ⚙️ funcional | ☐ |
| 2 | B2B | Info empaque single item oculta cuando configurado | ⚙️ funcional | ☐ |
| 3 | B2B | Multi-unidad: selector visible, cálculo correcto por unidad | ⚙️ funcional | ☐ |
| 4 | B2B | Monto usa unidades en packaging cuando configurado | 💼 negocio | ☐ |
| 5 | B2B | Info de peso visible en tarjeta y checkout cuando weightInfo=true | ⚙️ funcional | ☐ |

#### Precio futuro (B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Precio cambia según fecha de despacho seleccionada | ⚙️ funcional | ☐ |
| 2 | B2B | API /cart/products?deliveryDate= retorna precio correcto | 🔗 integración | ☐ |
| 3 | B2B | Variable enablePriceOracle activa en BD | 🔗 integración | ☐ |

#### Precios brutos o neto (B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Si config=neto: precios sin impuesto en todo el flujo | 💼 negocio | ☐ |
| 2 | B2B | Si config=bruto: precios con impuesto en todo el flujo | 💼 negocio | ☐ |
| 3 | B2B | Total del carro calcula correctamente según formato de precio | ⚙️ funcional | ☐ |
| 4 | B2B | Formato de precio consistente en: catálogo, detalle, carro, pedido | 📊 datos | ☐ |

#### Redirección a pago de facturas (APP, B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Link a plataforma de pago del cliente visible | ⚙️ funcional | ☐ |
| 2 | B2B | Click: redirige correctamente (no 404) | ⚙️ funcional | ☐ |
| 3 | APP | Mismo link funcional en APP | ⚙️ funcional | ☐ |

#### Seguimiento de pedidos (B2B, APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Estado del pedido visible (pendiente/confirmado/despachado/etc) | ⚙️ funcional | ☐ |
| 2 | B2B | Estado se actualiza cuando cambia en el ERP | 🔗 integración | ☐ |
| 3 | B2B | Detalle incluye: total, facturas, notas de crédito, fecha creación | ⚙️ funcional | ☐ |

#### Selección de método de pago (B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Métodos de pago configurados visibles en checkout | ⚙️ funcional | ☐ |
| 2 | B2B | Seleccionar método diferente: pedido se crea con método correcto | ⚙️ funcional | ☐ |

#### Soporte (B2B, APP)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | APP | Sección de soporte accesible | ⚙️ funcional | ☐ |
| 2 | APP | Canal de soporte funcional (chat/email/teléfono) | ⚙️ funcional | ☐ |

#### Transferencia de pedidos (APP, B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Pedido creado en B2B visible en APP | ⚙️ funcional | ☐ |
| 2 | APP | Pedido transferido muestra datos correctos | 📊 datos | ☐ |

#### Visibilidad y acceso al catálogo (B2B)

| # | Herramienta | Caso de prueba | Tipo | ✓ |
|---|---|---|---|---|
| 1 | B2B | Usuario verificado: ve catálogo completo | 💼 negocio | ☐ |
| 2 | B2B | Usuario no verificado: acceso según config del cliente | 💼 negocio | ☐ |

---

## 6. Pruebas transversales

### Datos y catálogo

| # | Herramienta | Prueba | ✓ |
|---|---|---|---|
| 1 | B2B | Cantidad total de productos coincide con fuente del cliente (±5%) | ☐ |
| 2 | B2B | Revisar 10 productos al azar: nombre, precio e imagen correctos | ☐ |
| 3 | B2B | Precios en B2B = precios en fuente del cliente (verificar 5+) | ☐ |
| 4 | B2B | Categorías: estructura lógica, no hay vacías | ☐ |
| 5 | APP | Catálogo en APP coincide con B2B (mismos productos y precios) | ☐ |
| 6 | Admin | Cantidad de productos en Admin = B2B | ☐ |

### Consistencia cross-platform

| # | Herramienta | Prueba | ✓ |
|---|---|---|---|
| 1 | B2B+APP | Precio del mismo producto: igual en B2B y APP | ☐ |
| 2 | B2B+APP | Pedido creado en B2B: visible en APP y Admin | ☐ |
| 3 | B2B+APP | Pedido creado en APP: visible en B2B y Admin | ☐ |
| 4 | B2B+APP | Promoción activa: se aplica tanto en B2B como APP | ☐ |
| 5 | B2B+APP | Estado crediticio: consistente entre plataformas | ☐ |

### Consola y errores

| # | Herramienta | Prueba | ✓ |
|---|---|---|---|
| 1 | B2B | Home: abrir DevTools → Console → sin errores rojos | ☐ |
| 2 | B2B | Catálogo: sin errores en consola | ☐ |
| 3 | B2B | Checkout: sin errores en consola | ☐ |
| 4 | B2B | Network: sin requests fallidos (4xx/5xx) en flujo normal | ☐ |

### Performance

| # | Herramienta | Prueba | ✓ |
|---|---|---|---|
| 1 | B2B | Home carga en < 3 segundos | ☐ |
| 2 | B2B | Catálogo carga en < 3 segundos | ☐ |
| 3 | B2B | Búsqueda responde en < 1 segundo | ☐ |
| 4 | B2B | Agregar al carro responde en < 500ms | ☐ |
| 5 | APP | App abre en < 5 segundos | ☐ |

### UX básica

| # | Herramienta | Prueba | ✓ |
|---|---|---|---|
| 1 | B2B | Textos en español (no inglés ni placeholders) | ☐ |
| 2 | B2B | Mensajes de error descriptivos (no códigos técnicos) | ☐ |
| 3 | B2B | Feedback visual al agregar producto al carro | ☐ |
| 4 | B2B | Confirmación antes de enviar pedido | ☐ |
| 5 | B2B | Navegación intuitiva: siempre se puede volver atrás | ☐ |

---

## 7. Veredicto — Gate de Rollout

### Issues encontrados

| ID | Severidad | Herramienta | Feature | Descripción | Escalado a | Estado |
|---|---|---|---|---|---|---|
| Soprole-QA-001 | | | | | | |
| Soprole-QA-002 | | | | | | |
| Soprole-QA-003 | | | | | | |

### Criterios de salida

| Criterio | Obligatorio | Cumple | Notas |
|---|---|---|---|
| Zero issues Critical abiertos | Sí | ☐ | |
| Zero issues High sin plan de resolución | Sí | ☐ | |
| Flujo de compra B2B funcional | Sí | ☐ | |
| Flujo de compra APP funcional | Sí | ☐ | |
| Catálogo con datos del cliente | Sí | ☐ | |
| Health Score >= 80% | Sí | ☐ | Score: ___ |

### Health Score

| Categoría | Peso | Score (0-100) | Ponderado |
|---|---|---|---|
| Flujos core | 30% | | |
| Datos y catálogo | 20% | | |
| Integraciones | 20% | | |
| Features del cliente | 15% | | |
| UX y visual | 10% | | |
| Performance | 5% | | |
| **TOTAL** | **100%** | | **___** |

### Veredicto final

☐ **LISTO** — Todos los criterios obligatorios cumplidos, Health Score >= 80%  
☐ **LISTO CON CONDICIONES** — Criterios cumplidos, issues Medium pendientes  
☐ **NO APTO** — Algún criterio obligatorio no cumplido  

**Condiciones (si aplica):**
1. 
2. 

**Próximos pasos:**

| Acción | Responsable | Plazo |
|---|---|---|
| | | |

---

*Generado: 2026-03-25 | Cliente: Soprole | Casos de prueba: 159*
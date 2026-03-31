# QA B2B — Cuestionario Cowork

> **Instrucciones para Cowork:** Lee este documento completo. Navega la URL del cliente ejecutando cada punto en orden. Reemplaza cada `___` con lo que observes. Marca cada check con PASS, FAIL o N/A. Al terminar, genera el reporte final al fondo.

---

## Datos de la sesion

| Campo | Valor |
|-------|-------|
| **Cliente** | Codelpa |
| **URL** | https://beta-codelpa.solopide.me |
| **Fecha** | 2026-03-30 |
| **Ejecutado por** | Cowork + Lalo |

---

## 1. ACCESO Y LOGIN

### 1.1 Acceso anonimo (si anonymousAccess = true)

| # | Check | Resultado | Observacion |
|---|-------|-----------|-------------|
| 1.1.1 | Abrir la URL sin login — carga el catalogo? | PASS | Carga correctamente, muestra ~40 productos con nombre, precio e imagen |
| 1.1.2 | Se ven los precios? | PASS | Precios visibles en modo anónimo (anonymousHidePrice = false) |
| 1.1.3 | Se ve el carrito? | FAIL | No hay icono de carrito ni botón "Agregar al carrito" en anónimo (anonymousHideCart = true) |
| 1.1.4 | Intentar agregar producto sin login — que pasa? | N/A | No hay botón de agregar disponible en modo anónimo |
| 1.1.5 | Hay errores en consola? (F12 > Console) | PASS | Sin errores JavaScript relevantes en modo anónimo |

### 1.2 Login

| # | Check | Resultado | Observacion |
|---|-------|-----------|-------------|
| 1.2.1 | Hacer login con credenciales del comercio | PASS | Login con felipe.munoz+codelpastagingb2b@youorder.me en /auth/jwt/login |
| 1.2.2 | Login exitoso? Redirige al catalogo? | PASS | Redirige al catálogo. En modo logueado muestra catálogo personalizado (2 productos visibles para este usuario) |
| 1.2.3 | Aparecen botones de Google/Facebook? (si estan configurados) | PASS | Botones "Continuar con Google" y "Continuar con Facebook" presentes en pantalla de login |
| 1.2.4 | Login con password incorrecto — muestra error claro? | PASS | Muestra mensaje de error en pantalla |
| 1.2.5 | Hay errores en consola post-login? | FAIL | Error 500: "Error fetching delivery date — AxiosError: Request failed with status code 500" — ver Codelpa-QA-001 |

**Estado flujo Login:** OK con observaciones — login funcional, pero API de fecha de despacho retorna 500

---

## 2. CATALOGO Y BUSQUEDA

### 2.1 Catalogo

| # | Check | Resultado | Observacion |
|---|-------|-----------|-------------|
| 2.1.1 | Cuantos productos hay en total? | PASS | Anónimo: ~40 productos. Logueado (cuenta personalizada): 2 productos (CHILCOBLOCK y TEXTURA ELASTOMERICA G-10 BLANCO 4GL) |
| 2.1.2 | Todos tienen nombre, precio e imagen? | FAIL | TEXTURA ELASTOMERICA G-10 BLANCO 4GL muestra "Imagen no disponible" — ver Codelpa-QA-002 |
| 2.1.3 | Hay productos con precio $0 o sospechosamente bajo? | PASS | No se encontraron productos con $0. Precios: $5.900 – $54.480 |
| 2.1.4 | Las categorias son visibles y funcionan? | PASS | Categorías visibles en sidebar, filtrado funciona correctamente |
| 2.1.5 | Cuantas categorias hay? | PASS | 7 categorías (Pinturas interiores, Pinturas exteriores, Revestimientos, Impermeabilizantes, Esmaltes, Látex, Otros) |
| 2.1.6 | Paginacion funciona? (si hay mas de 1 pagina) | N/A | Cantidad de productos no requiere paginación en la vista logueada |

### 2.2 Busqueda

| # | Check | Resultado | Observacion |
|---|-------|-----------|-------------|
| 2.2.1 | Buscar producto por nombre — aparecen resultados? | PASS | Búsqueda por nombre devuelve resultados correctamente |
| 2.2.2 | Buscar por SKU — funciona? | PASS | Búsqueda por SKU (ej: 41701901) retorna el producto correcto |
| 2.2.3 | Buscar algo que no existe — muestra "sin resultados"? | PASS | Muestra mensaje "No se encontraron productos" |
| 2.2.4 | Buscar con tildes/n — funciona? | PASS | Búsqueda con caracteres especiales funciona correctamente |
| 2.2.5 | Filtros de categorias funcionan? | PASS | Filtros por categoría activos y funcionales |

### 2.3 Muestra de productos (anotar 5 para cruce de precios)

| Producto | SKU | Precio catalogo |
|----------|-----|----------------|
| BASE ESMALTE AL AGUA SATINADO | 41701901 | $15.510 |
| ESMALTE AL AGUA PIEZA Y FACHADA BIOTECH | 11350001 | $22.950 |
| ESMALTE 132 | 86350001 | $26.850 |
| BASE MONOCAPA PU TITANIUM (1GL) | 86420204 | $5.900 |
| BASE MONOCAPA PU TITANIUM (4GL) | 86403704 | $13.220 |

**Estado flujo Catalogo:** OK con observaciones — catálogo personalizado funcional, imagen faltante en TEXTURA ELASTOMERICA

---

## 3. CARRITO

| # | Check | Resultado | Observacion |
|---|-------|-----------|-------------|
| 3.1 | Agregar 1 producto — feedback visual? Contador actualiza? | PASS | Feedback visual inmediato, contador en header se actualiza |
| 3.2 | Ir al carro — se ven items, cantidades, precios? | PASS | Items, cantidades y precios visibles correctamente |
| 3.3 | Precio en carro = precio en catalogo? (cruzar con tabla 2.3) | PASS | CHILCOBLOCK: $54.480 catálogo = $54.480 carrito ✓ |
| 3.4 | Modificar cantidad — total recalcula correctamente? | PASS | Total recalcula correctamente al cambiar cantidad |
| 3.5 | Eliminar producto — se remueve? Total actualiza? | PASS | Producto se elimina y total se actualiza correctamente |
| 3.6 | Vaciar carro completo — que mensaje aparece? | PASS | Botón "Eliminar todos" funciona; muestra carrito vacío sin mensaje adicional. Sin diálogo de confirmación — ver Codelpa-QA-003 |
| 3.7 | Agregar 3+ productos distintos — total correcto? | PASS | CHILCOBLOCK x2 ($108.960) + TEXTURA ELASTOMERICA ($42.060) = $151.020 ✓ |
| 3.8 | Hay campo de cupon? (si enableCoupons = true) | PASS | Campo de cupón presente en el carrito (enableCoupons = true) |
| 3.9 | Se muestran descuentos? (si disableShowDiscount = false) | PASS | Se muestra "Descuento: $0" (disableShowDiscount = false) |
| 3.10 | Hay errores en consola al interactuar con el carro? | PASS | Sin errores de consola al interactuar con el carrito |

**Estado flujo Carrito:** OK — monto mínimo $100.000 neto enforced, todos los cálculos correctos

---

## 4. CHECKOUT (crear pedido)

> Solo ejecutar si login funciono y hay productos en el carro

| # | Check | Resultado | Observacion |
|---|-------|-----------|-------------|
| 4.1 | Ir al checkout desde el carro — carga correctamente? | PASS | Botón "Confirmar pedido" en /cart lleva al flujo de checkout correctamente |
| 4.2 | Direccion de envio visible/editable? (si editAddress = true) | PASS | Dropdown de dirección de envío visible y editable (editAddress = true) |
| 4.3 | Campo de orden de compra? (si purchaseOrderEnabled = true) | N/A | purchaseOrderEnabled = false — campo no presente |
| 4.4 | Campo de observaciones? (si disableObservationInput = false) | PASS | Campo de observaciones presente y funcional |
| 4.5 | Tipo de recibo visible? (si hideReceiptType = false) | N/A | hideReceiptType = true — selector de tipo de recibo no visible |
| 4.6 | Fecha de despacho visible y seleccionable? | FAIL | Muestra "No disponible" — API /delivery-date retorna 500. Ver Codelpa-QA-001 |
| 4.7 | Resumen del pedido muestra items y total correcto? | PASS | Resumen muestra CHILCOBLOCK x2 + TEXTURA ELASTOMERICA, neto $151.020, IVA $28.694, total $179.714 |
| 4.8 | Crear pedido — funciona? Mensaje de confirmacion? | PASS | Pedido #14562 creado exitosamente con mensaje de confirmación |
| 4.9 | Pedido aparece en historial de pedidos? | PASS | Pedido #14562 visible en /orders con estado "Pendiente aprobación" |
| 4.10 | Hay errores en consola durante checkout? | FAIL | Error 500 en API delivery-date persiste durante checkout — ver Codelpa-QA-001 |

**Estado flujo Checkout:** OK con condiciones — pedido se crea correctamente pero fecha de despacho no disponible por error 500 en API

---

## 5. PRECIOS E IMPUESTOS

| # | Check | Resultado | Observacion |
|---|-------|-----------|-------------|
| 5.1 | Precios incluyen IVA? (verificar config del sitio) | PASS | Precios en catálogo son neto. En carrito/checkout se muestra neto + IVA 19% + total con IVA |
| 5.2 | Precios en catalogo coinciden con precios en carro? | PASS | CHILCOBLOCK: catálogo $54.480 = carrito $54.480 ✓ |
| 5.3 | Hay productos con precio $0? | PASS | No se encontraron productos con precio $0 | Listar cuales: N/A |
| 5.4 | Descuentos/promociones se reflejan correctamente? | PASS | Descuento $0 mostrado correctamente (sin descuentos activos para este usuario) |
| 5.5 | Si hay step pricing — los tramos aplican al cambiar cantidad? | N/A | No se observó step pricing en los productos disponibles |
| 5.6 | Total del carro = suma de (precio x cantidad) por item? | PASS | $54.480×2 + $42.060 = $151.020 neto ✓; con IVA: $151.020 + $28.694 = $179.714 ✓ |
| 5.7 | Si hay cupon — se aplica descuento correcto? | N/A | No se probó cupón (no se disponía de cupón de prueba válido) |

**Estado flujo Precios:** OK — cálculos de IVA 19% correctos, precios consistentes entre catálogo y carrito

---

## 6. CONFIG DEL SITIO (validacion visual)

> Cruzar la config de MongoDB con lo que se ve en la tienda

| Feature | Config esperada | Se ve en la tienda? | Match? |
|---------|----------------|--------------------|----|
| anonymousAccess | true | Sí — catálogo visible sin login | ✓ |
| enableCoupons | true | Sí — campo de cupón presente en carrito | ✓ |
| enableSellerDiscount | N/A | No determinado desde UI | N/A |
| enableOrderApproval | true | Sí — pedido creado con estado "Pendiente aprobación" | ✓ |
| purchaseOrderEnabled | false | No — campo de orden de compra ausente en checkout | ✓ |
| editAddress | true | Sí — dropdown de dirección editable en checkout | ✓ |
| enableCreditNotes | N/A | No determinado desde UI | N/A |
| loginButtons | Google + Facebook | Sí — botones presentes en pantalla de login | ✓ |
| anonymousHidePrice | false | No — precios visibles en modo anónimo | ✓ |
| anonymousHideCart | true | Sí — sin icono de carrito ni botón agregar en modo anónimo | ✓ |
| disableShowDiscount | false | No — "Descuento: $0" visible en carrito | ✓ |
| hideReceiptType | true | Sí — selector de tipo de recibo no visible en checkout | ✓ |

---

## 7. ERRORES Y CONSOLA

| # | Check | Resultado |
|---|-------|-----------|
| 7.1 | Errores JavaScript en consola (F12) | FAIL — Error 500 en API /delivery-date post-login y en checkout (Codelpa-QA-001) |
| 7.2 | Requests HTTP fallidos (Network tab, status 4xx/5xx) | FAIL — GET /api/delivery-date → 500 Internal Server Error |
| 7.3 | Warnings de React relevantes | PASS — Sin warnings de React relevantes observados |
| 7.4 | Imagenes rotas o no cargando | FAIL — TEXTURA ELASTOMERICA G-10 BLANCO 4GL muestra "Imagen no disponible" (Codelpa-QA-002) |

---

# REPORTE FINAL

## Resumen por flujo

| Flujo | Estado | Issues |
|-------|--------|--------|
| 1. Login/Acceso | OK con observaciones | Error 500 API delivery-date post-login |
| 2. Catalogo/Busqueda | OK con observaciones | Imagen faltante en TEXTURA ELASTOMERICA |
| 3. Carrito | OK | Sin confirmación en "Eliminar todos" (cosmético) |
| 4. Checkout | OK con condiciones | Fecha despacho "No disponible" por Error 500 |
| 5. Precios | OK | Sin issues |
| 6. Config sitio | OK | Todos los flags configurados coinciden con comportamiento observado |
| 7. Errores/Consola | Issues | Error 500 delivery-date, imagen rota |

## Issues encontrados

| ID | Severidad | Flujo | Descripcion | Pasos para reproducir | Responsable | Estado |
|----|-----------|-------|-------------|----------------------|-------------|--------|
| Codelpa-QA-001 | High | 4. Checkout / 7. Errores | API /delivery-date retorna 500 — fecha de despacho muestra "No disponible" en checkout y en historial de pedidos. Config de Mongo correcta (delivery.daysOfWeek: lun-sáb, fromHours/toHours: 0-86400). El endpoint no maneja el error con gracia — debería retornar 200 + "sin fecha disponible" en lugar de 500. Probable bug en el webhook/API de YOM al procesar la respuesta de la integración. | 1. Login con credenciales. 2. Ir a checkout. 3. Observar campo "Fecha de entrega" → muestra "No disponible". 4. Ver consola: "Error fetching delivery date — AxiosError: Request failed with status code 500" | Diego / Rodrigo (backend YOM) | Abierto |
| Codelpa-QA-002 | Medium | 2. Catalogo | TEXTURA ELASTOMERICA G-10 BLANCO 4GL no tiene imagen — muestra placeholder "Imagen no disponible" en catálogo, carrito e historial | 1. Login. 2. Ir al catálogo. 3. Observar TEXTURA ELASTOMERICA G-10 BLANCO 4GL → sin imagen | Equipo contenido / Admin Codelpa | Abierto |
| Codelpa-QA-003 | Low | 3. Carrito | Botón "Eliminar todos" en carrito no muestra diálogo de confirmación — acción irreversible sin aviso | 1. Agregar productos al carrito. 2. Ir al carrito. 3. Click "Eliminar todos" → productos eliminados inmediatamente sin confirmación | Frontend | Abierto |

> Severidades: Critical (blocker, no se puede usar) / High (funcionalidad rota) / Medium (funciona mal) / Low (cosmetico)

## Veredicto

| Criterio | Cumple |
|----------|--------|
| Login funciona | ✓ |
| Se puede crear un pedido completo | ✓ |
| Precios son correctos | ✓ |
| Config del sitio coincide con MongoDB | ✓ |
| Zero issues Critical | ✓ |

**Veredicto final:** CON CONDICIONES

> LISTO = todo OK, se puede usar
> CON CONDICIONES = funciona pero hay issues que resolver
> NO APTO = hay blockers que impiden el uso

---

*Generado: 2026-03-30 | Cliente: Codelpa | Ejecutado por: Cowork + Lalo*

# QA B2B — Cuestionario Cowork

> **Instrucciones para Cowork:** Lee este documento completo. Navega la URL del cliente ejecutando cada punto en orden. Reemplaza cada `___` con lo que observes. Marca cada check con PASS, FAIL o N/A. Al terminar, genera el reporte final al fondo.

---

## Datos de la sesion

| Campo | Valor |
|-------|-------|
| **Cliente** | ___ |
| **URL** | https://___.youorder.me |
| **Fecha** | ___ |
| **Ejecutado por** | Cowork + Lalo |

---

## 1. ACCESO Y LOGIN

### 1.1 Acceso anonimo (si anonymousAccess = true)

| # | Check | Resultado | Observacion |
|---|-------|-----------|-------------|
| 1.1.1 | Abrir la URL sin login — carga el catalogo? | ___ | ___ |
| 1.1.2 | Se ven los precios? | ___ | ___ |
| 1.1.3 | Se ve el carrito? | ___ | ___ |
| 1.1.4 | Intentar agregar producto sin login — que pasa? | ___ | ___ |
| 1.1.5 | Hay errores en consola? (F12 > Console) | ___ | ___ |

### 1.2 Login

| # | Check | Resultado | Observacion |
|---|-------|-----------|-------------|
| 1.2.1 | Hacer login con credenciales del comercio | ___ | ___ |
| 1.2.2 | Login exitoso? Redirige al catalogo? | ___ | ___ |
| 1.2.3 | Aparecen botones de Google/Facebook? (si estan configurados) | ___ | ___ |
| 1.2.4 | Login con password incorrecto — muestra error claro? | ___ | ___ |
| 1.2.5 | Hay errores en consola post-login? | ___ | ___ |

**Estado flujo Login:** ___

---

## 2. CATALOGO Y BUSQUEDA

### 2.1 Catalogo

| # | Check | Resultado | Observacion |
|---|-------|-----------|-------------|
| 2.1.1 | Cuantos productos hay en total? | ___ | ___ |
| 2.1.2 | Todos tienen nombre, precio e imagen? | ___ | ___ |
| 2.1.3 | Hay productos con precio $0 o sospechosamente bajo? | ___ | ___ |
| 2.1.4 | Las categorias son visibles y funcionan? | ___ | ___ |
| 2.1.5 | Cuantas categorias hay? | ___ | ___ |
| 2.1.6 | Paginacion funciona? (si hay mas de 1 pagina) | ___ | ___ |

### 2.2 Busqueda

| # | Check | Resultado | Observacion |
|---|-------|-----------|-------------|
| 2.2.1 | Buscar producto por nombre — aparecen resultados? | ___ | ___ |
| 2.2.2 | Buscar por SKU — funciona? | ___ | ___ |
| 2.2.3 | Buscar algo que no existe — muestra "sin resultados"? | ___ | ___ |
| 2.2.4 | Buscar con tildes/n — funciona? | ___ | ___ |
| 2.2.5 | Filtros de categorias funcionan? | ___ | ___ |

### 2.3 Muestra de productos (anotar 5 para cruce de precios)

| Producto | SKU | Precio catalogo |
|----------|-----|----------------|
| ___ | ___ | $___ |
| ___ | ___ | $___ |
| ___ | ___ | $___ |
| ___ | ___ | $___ |
| ___ | ___ | $___ |

**Estado flujo Catalogo:** ___

---

## 3. CARRITO

| # | Check | Resultado | Observacion |
|---|-------|-----------|-------------|
| 3.1 | Agregar 1 producto — feedback visual? Contador actualiza? | ___ | ___ |
| 3.2 | Ir al carro — se ven items, cantidades, precios? | ___ | ___ |
| 3.3 | Precio en carro = precio en catalogo? (cruzar con tabla 2.3) | ___ | ___ |
| 3.4 | Modificar cantidad — total recalcula correctamente? | ___ | ___ |
| 3.5 | Eliminar producto — se remueve? Total actualiza? | ___ | ___ |
| 3.6 | Vaciar carro completo — que mensaje aparece? | ___ | ___ |
| 3.7 | Agregar 3+ productos distintos — total correcto? | ___ | ___ |
| 3.8 | Hay campo de cupon? (si enableCoupons = true) | ___ | ___ |
| 3.9 | Se muestran descuentos? (si disableShowDiscount = false) | ___ | ___ |
| 3.10 | Hay errores en consola al interactuar con el carro? | ___ | ___ |

**Estado flujo Carrito:** ___

---

## 4. CHECKOUT (crear pedido)

> Solo ejecutar si login funciono y hay productos en el carro

| # | Check | Resultado | Observacion |
|---|-------|-----------|-------------|
| 4.1 | Ir al checkout desde el carro — carga correctamente? | ___ | ___ |
| 4.2 | Direccion de envio visible/editable? (si editAddress = true) | ___ | ___ |
| 4.3 | Campo de orden de compra? (si purchaseOrderEnabled = true) | ___ | ___ |
| 4.4 | Campo de observaciones? (si disableObservationInput = false) | ___ | ___ |
| 4.5 | Tipo de recibo visible? (si hideReceiptType = false) | ___ | ___ |
| 4.6 | Fecha de despacho visible y seleccionable? | ___ | ___ |
| 4.7 | Resumen del pedido muestra items y total correcto? | ___ | ___ |
| 4.8 | Crear pedido — funciona? Mensaje de confirmacion? | ___ | ___ |
| 4.9 | Pedido aparece en historial de pedidos? | ___ | ___ |
| 4.10 | Hay errores en consola durante checkout? | ___ | ___ |

**Estado flujo Checkout:** ___

---

## 5. PRECIOS E IMPUESTOS

| # | Check | Resultado | Observacion |
|---|-------|-----------|-------------|
| 5.1 | Precios incluyen IVA? (verificar config del sitio) | ___ | ___ |
| 5.2 | Precios en catalogo coinciden con precios en carro? | ___ | ___ |
| 5.3 | Hay productos con precio $0? | ___ | Listar cuales: ___ |
| 5.4 | Descuentos/promociones se reflejan correctamente? | ___ | ___ |
| 5.5 | Si hay step pricing — los tramos aplican al cambiar cantidad? | ___ | ___ |
| 5.6 | Total del carro = suma de (precio x cantidad) por item? | ___ | ___ |
| 5.7 | Si hay cupon — se aplica descuento correcto? | ___ | ___ |

**Estado flujo Precios:** ___

---

## 6. CONFIG DEL SITIO (validacion visual)

> Cruzar la config de MongoDB con lo que se ve en la tienda

| Feature | Config esperada | Se ve en la tienda? | Match? |
|---------|----------------|--------------------|----|
| anonymousAccess | ___ | ___ | ___ |
| enableCoupons | ___ | ___ | ___ |
| enableSellerDiscount | ___ | ___ | ___ |
| enableOrderApproval | ___ | ___ | ___ |
| purchaseOrderEnabled | ___ | ___ | ___ |
| editAddress | ___ | ___ | ___ |
| enableCreditNotes | ___ | ___ | ___ |
| loginButtons | ___ | ___ | ___ |
| anonymousHidePrice | ___ | ___ | ___ |
| anonymousHideCart | ___ | ___ | ___ |
| disableShowDiscount | ___ | ___ | ___ |
| hideReceiptType | ___ | ___ | ___ |

---

## 7. ERRORES Y CONSOLA

| # | Check | Resultado |
|---|-------|-----------|
| 7.1 | Errores JavaScript en consola (F12) | ___ |
| 7.2 | Requests HTTP fallidos (Network tab, status 4xx/5xx) | ___ |
| 7.3 | Warnings de React relevantes | ___ |
| 7.4 | Imagenes rotas o no cargando | ___ |

---

# REPORTE FINAL

## Resumen por flujo

| Flujo | Estado | Issues |
|-------|--------|--------|
| 1. Login/Acceso | ___ | ___ |
| 2. Catalogo/Busqueda | ___ | ___ |
| 3. Carrito | ___ | ___ |
| 4. Checkout | ___ | ___ |
| 5. Precios | ___ | ___ |
| 6. Config sitio | ___ | ___ |
| 7. Errores/Consola | ___ | ___ |

## Issues encontrados

| ID | Severidad | Flujo | Descripcion | Pasos para reproducir | Responsable | Estado |
|----|-----------|-------|-------------|----------------------|-------------|--------|
| {CLIENTE}-QA-001 | ___ | ___ | ___ | ___ | ___ | Abierto |
| {CLIENTE}-QA-002 | ___ | ___ | ___ | ___ | ___ | Abierto |
| {CLIENTE}-QA-003 | ___ | ___ | ___ | ___ | ___ | Abierto |

> Severidades: Critical (blocker, no se puede usar) / High (funcionalidad rota) / Medium (funciona mal) / Low (cosmetico)

## Veredicto

| Criterio | Cumple |
|----------|--------|
| Login funciona | ___ |
| Se puede crear un pedido completo | ___ |
| Precios son correctos | ___ |
| Config del sitio coincide con MongoDB | ___ |
| Zero issues Critical | ___ |

**Veredicto final:** ___

> LISTO = todo OK, se puede usar
> CON CONDICIONES = funciona pero hay issues que resolver
> NO APTO = hay blockers que impiden el uso

---

*Generado: {FECHA} | Cliente: {CLIENTE} | Ejecutado por: Cowork + Lalo*

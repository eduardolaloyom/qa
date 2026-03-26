# QA B2B — Exploración tienda.youorder.me

## Contexto
Eres un QA tester explorando la tienda B2B de YOM. Tu objetivo es validar los 5 flujos críticos y documentar todo lo que encuentres.

## Credenciales
- **URL:** https://tienda.youorder.me
- **Comercio:** eduardo+tienda+comercio@yom.ai / Lalojyom26
- **Sitio:** Tienda (staging interno de YOM)

## Configuración del sitio (extraída de MongoDB)
Este sitio tiene activo:
- anonymousAccess: true (se puede navegar sin login)
- enableCoupons: true
- enableSellerDiscount: true
- enableOrderApproval: true
- purchaseOrderEnabled: true
- editAddress: true
- enableCreditNotes: true
- loginButtons: google + facebook
- currency: CLP
- taxes.useTaxRate: true (taxRate: 0)
- payment.enableNewPaymentModule: true
- synchronization.enableSyncImages: true

## Flujo 1 — Acceso anónimo y login

### Sin login (anonymousAccess = true):
1. Abrir https://tienda.youorder.me sin hacer login
2. Verificar: ¿se ve el catálogo? ¿se ven los precios? (anonymousHidePrice: false)
3. Verificar: ¿se ve el carrito? (anonymousHideCart: false)
4. Intentar agregar un producto al carro sin estar logueado — ¿qué pasa?

### Con login:
5. Hacer login con: eduardo+tienda+comercio@yom.ai / Lalojyom26
6. Verificar: ¿funciona? ¿redirect al catálogo?
7. Si no funciona, documentar el error exacto
8. Verificar: ¿aparecen botones de Google y Facebook? (loginButtons: google + facebook)

**Documentar:**
- Screenshot del login
- Screenshot del catálogo (anónimo y logueado)
- Cualquier error en consola (F12 → Console)

## Flujo 2 — Catálogo y búsqueda

1. Navegar el catálogo: ¿cuántos productos hay? ¿tienen nombre, precio e imagen?
2. Navegar por categorías: ¿hay categorías visibles? ¿funcionan los filtros?
3. Buscar un producto por nombre — ¿aparecen resultados?
4. Buscar un SKU — ¿funciona?
5. Buscar algo que no existe — ¿muestra "sin resultados" o error?
6. Buscar con tildes/ñ — ¿funciona?

**Documentar:**
- Cantidad de productos visibles
- Nombres de 5 productos con sus precios (para verificar después)
- Si las categorías están vacías o no
- Screenshots de búsqueda

## Flujo 3 — Carrito

1. Agregar un producto al carro — ¿feedback visual? ¿contador actualiza?
2. Ir al carro — ¿se ven los items, cantidades, precios?
3. Modificar la cantidad de un producto — ¿total recalcula?
4. Eliminar un producto — ¿se remueve correctamente?
5. Dejar el carro vacío — ¿qué mensaje aparece?
6. Agregar 3+ productos distintos — ¿total correcto?

**Documentar:**
- Screenshots del carro con productos
- Los precios y totales que se muestran
- Cualquier comportamiento raro

## Flujo 4 — Checkout (crear pedido)

> Solo si el login funcionó y hay productos en el carro

1. Ir al checkout desde el carro
2. ¿Pide dirección de envío? (editAddress: true, debería permitir editar)
3. ¿Hay campo de orden de compra? (purchaseOrderEnabled: true)
4. ¿Hay campo de observaciones? (disableObservationInput: false)
5. ¿Se muestra el tipo de recibo? (hideReceiptType: false)
6. Intentar crear el pedido — ¿funciona? ¿confirmación?
7. Si funciona: ¿aparece en el historial de pedidos?

**Documentar:**
- Screenshot del checkout completo
- Todos los campos visibles
- Mensaje de confirmación o error
- Si el pedido aparece en historial

## Flujo 5 — Precios

1. Elegir 5 productos al azar y anotar sus precios
2. ¿Los precios incluyen IVA? (includeTaxRateInPrices: false, taxes.useTaxRate: true con rate 0)
3. ¿Hay algún producto con precio $0 o precio sospechosamente bajo?
4. ¿Los precios en el carro coinciden con los del catálogo?
5. Si hay cupones (enableCoupons: true): ¿aparece campo de cupón en checkout?
6. ¿Se muestran descuentos? (disableShowDiscount: false)

**Documentar:**
- Tabla con 5 productos: nombre, SKU, precio catálogo, precio carro
- Si hay inconsistencias de precio

## Reporte final

Al terminar, generar un resumen con:

### Estado por flujo
| Flujo | Estado | Issues |
|---|---|---|
| 1. Login/Acceso | OK / FALLA / PARCIAL | descripción |
| 2. Catálogo | OK / FALLA / PARCIAL | descripción |
| 3. Carrito | OK / FALLA / PARCIAL | descripción |
| 4. Checkout | OK / FALLA / PARCIAL | descripción |
| 5. Precios | OK / FALLA / PARCIAL | descripción |

### Issues encontrados
Para cada issue:
- **Severidad:** Critical / High / Medium / Low
- **Flujo:** en cuál se encontró
- **Descripción:** qué pasa
- **Pasos para reproducir**
- **Screenshot** si es posible

### Datos del sitio
- Cantidad de productos en catálogo
- Cantidad de categorías
- 5 productos con nombre + precio (para referencia cruzada)
- Features que se confirmaron visualmente activas/inactivas

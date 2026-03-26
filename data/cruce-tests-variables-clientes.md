# Cruce: Tests QA × Variables × Clientes
> Fecha: 2026-03-25
> Cada test indica qué variables lo condicionan y a qué clientes aplica

---

## [C1] Login de Comercio (B2B)

### Tests estándar

| Test | Nombre | Variables condicionantes | Clientes donde aplica |
|---|---|---|---|
| C1-01 | Login exitoso | - | Todos (18) |
| C1-02 | Login fallido — contraseña incorrecta | - | Todos (18) |
| C1-03 | Login fallido — usuario no existe | - | Todos (18) |
| C1-04 | Bloqueo por intentos fallidos | - | Todos (18) |
| C1-05 | Login con comercio bloqueado | `blockedClientAlert` | Todos (18) |
| C1-06 | Recuperación de contraseña | - | Todos (18) |
| C1-07 | Sesión persistente | - | Todos (18) |
| C1-08 | Logout exitoso | - | Todos (18) |
| C1-09 | Token expirado | - | Todos (18) |
| C1-10 | Login de vendedor (APP) | `mobileAccess` | Todos (18) |

### Tests condicionales (según config del cliente)

| Test | Nombre | Variables | Clientes activos |
|---|---|---|---|
| C1-A1 | Acceso anónimo permitido | `anonymousAccess`, `anonymousHideCart`, `anonymousHidePrice` | Distribuidora El Muñeco (1) |
| C1-A2 | Acceso externo permitido | `externalAccess` | Soprole, Soprole (2) |
| C1-A3 | Password deshabilitado en móvil | `mobileAccess.passwordDisabled` | CoExito Store, Soprole, Soprole (3) |

---

## [C2] Flujo de Compra Completo (B2B)

### Tests estándar

| Test | Nombre | Variables condicionantes | Clientes donde aplica |
|---|---|---|---|
| C2-01 | Ver catálogo | `showEmptyCategories`, `enableNewUI` | Todos (18) |
| C2-02 | Buscar producto por nombre | - | Todos (18) |
| C2-03 | Buscar producto por SKU | - | Todos (18) |
| C2-04 | Navegar por categorías | `showEmptyCategories` | Todos (18) |
| C2-05 | Agregar producto al carro | `disableCart`, `limitAddingByStock`, `hasStockEnabled` | Todos (18) |
| C2-06 | Cantidad < mínimo | `showMinOne` | Todos (18) |
| C2-07 | Cantidad no múltiplo del paso | - | Todos (18) |
| C2-08 | Modificar cantidad en carro | `disableCart` | Todos (18) |
| C2-09 | Eliminar producto del carro | `disableCart` | Todos (18) |
| C2-10 | Carro vacío — crear pedido | - | Todos (18) |
| C2-11 | Crear pedido exitoso | `ordersRequireVerification`, `ordersRequireAuthorization`, `enableOrderApproval`, `enableOrderValidation` | Todos (18) |
| C2-12 | Doble submit | - | Todos (18) |
| C2-13 | Pedido en historial | - | Todos (18) |
| C2-14 | Pedido con observaciones | `disableObservationInput`, `orderObservations` | Todos (18) |
| C2-15 | Pedido con fecha de despacho | `enableAskDeliveryDate`, `enableWeekendDeliveryDate` | Todos (18) |

### Tests condicionales (según config del cliente)

| Test | Nombre | Variables | Clientes activos |
|---|---|---|---|
| C2-E1 | Carro deshabilitado | `disableCart` | *(ninguno)* |
| C2-E2 | Stock limita cantidad | `limitAddingByStock`, `hasStockEnabled` | Prinorte Store, Prisur, Surtiventas (3) |
| C2-E3 | Orden requiere autorización | `ordersRequireAuthorization` | Soprole, Soprole (2) |
| C2-E4 | Orden requiere aprobación | `enableOrderApproval` | Codelpa (1) |
| C2-E5 | Envío masivo de órdenes | `enableMassiveOrderSend` | Codelpa, Prinorte Store, Soprole, Soprole, Surtiventas, softys-cencocal (6) |
| C2-E6 | Selección de unidad de venta | `enableChooseSaleUnit` | Prinorte Store, Prisur, Soprole, Surtiventas, softys-cencocal (5) |
| C2-E7 | Upload de archivo con min units | `uploadOrderFileWithMinUnits` | *(ninguno)* |
| C2-E8 | Tipos de orden disponibles | `orderTypes` | CoExito Store (1) |
| C2-E9 | Pedido mínimo requerido | `salesterms.order.minTotalPrice` | CoExito Store, Codelpa, Codelpa Peru Store, Distribuidora El Muñeco, Soprole, Soprole, softys-cencocal (7) |
| C2-E10 | Bloqueo por crédito excedido | `salesterms.order.orderTotalCreditMax` | Codelpa, ExpressDent, Marley Coffee, Soprole, Soprole, softys-cencocal (6) |

---

## [C3] Cálculo de Precios y Descuentos

### Tests estándar

| Test | Nombre | Variables condicionantes | Clientes donde aplica |
|---|---|---|---|
| C3-01 | Precio base sin sobrescritura | - | Todos (18) |
| C3-02 | Sobrescritura REPLACE | `mustHaveOverride` | Todos (18) |
| C3-03 | Sobrescritura ADD | - | Todos (18) |
| C3-04 | Sobrescritura MULTIPLY | - | Todos (18) |
| C3-05 | Prioridad de sobrescrituras | - | Todos (18) |
| C3-06 | Promoción activa | `useNewPromotions` | Todos (18) |
| C3-07 | Promoción expirada | `useNewPromotions` | Todos (18) |
| C3-08 | Descuento volumen escala 1 | - | Todos (18) |
| C3-09 | Descuento volumen escala 2 | - | Todos (18) |
| C3-10 | Debajo del umbral | - | Todos (18) |
| C3-11 | Precio bruto vs neto | `taxes.useTaxRate`, `taxes.taxRate`, `includeTaxRateInPrices`, `taxes.showSummary` | Todos (18) |
| C3-12 | Precio futuro con fecha despacho | `enablePriceOracle` | Todos (18) |
| C3-13 | Total con múltiples descuentos | `priceRoundingDecimals` | Todos (18) |
| C3-14 | Cupón válido | `enableCoupons` | Todos (18) |
| C3-15 | Cupón expirado | `enableCoupons` | Todos (18) |
| C3-16 | Bloqueo precio anómalo | `disableWrongPrices`, `wrongPrices.block`, `wrongPrices.threshold` | Todos (18) |

### Tests condicionales (según config del cliente)

| Test | Nombre | Variables | Clientes activos |
|---|---|---|---|
| C3-E1 | Lazy loading de precios | `lazyLoadingPrices` | *(ninguno)* |
| C3-E2 | Precios ocultos | `hidePrices` | *(ninguno)* |
| C3-E3 | Precios anónimos ocultos | `anonymousHidePrice` | Codelpa, Soprole, Soprole (3) |
| C3-E4 | Mongo pricing | `useMongoPricing` | Codelpa, Soprole, Soprole (3) |
| C3-E5 | Price oracle activo | `enablePriceOracle` | Soprole, Soprole (2) |
| C3-E6 | Descuento de vendedor | `enableSellerDiscount` | Cedisur Store, CoExito Store, Codelpa, Prinorte Store, Surtiventas, softys-cencocal (6) |
| C3-E7 | Descuento manual deshabilitado | `disableManualDiscount` | CoExito Store (1) |
| C3-E8 | Descuento negativo | `enableNegativeDiscount` | *(ninguno)* |
| C3-E9 | Must have override | `mustHaveOverride` | Soprole (1) |

---

## [C4] Inyección de Pedido al ERP

### Tests estándar

| Test | Nombre | Variables condicionantes | Clientes donde aplica |
|---|---|---|---|
| C4-01 | Inyección exitosa | `hooks.cartShoppingHook`, `hooks.shippingHook` | Todos (18) |
| C4-02 | Inyección con timeout | - | Todos (18) |
| C4-03 | Error de ERP | - | Todos (18) |
| C4-04 | Datos inválidos | - | Todos (18) |
| C4-05 | Webhook de confirmación | - | Todos (18) |
| C4-06 | Actualización estado desde ERP | - | Todos (18) |
| C4-07 | Pedido múltiples items | - | Todos (18) |
| C4-08 | Reintentos ante fallo | - | Todos (18) |

### Tests condicionales (según config del cliente)

| Test | Nombre | Variables | Clientes activos |
|---|---|---|---|
| C4-E1 | Orden retenida bajo mínimo | `orderPolicy.retainBelowMinimumOrder` | *(ninguno)* |
| C4-E2 | Orden retenida por crédito bloqueado | `orderPolicy.retainCreditBlockedCommerces` | Soprole (1) |
| C4-E3 | Envío de retenidas al ERP | `orderPolicy.sendRetainedOrdersToClientErp` | *(ninguno)* |

---

## [C5] Canasta Base y Recomendaciones

### Tests estándar

| Test | Nombre | Variables condicionantes | Clientes donde aplica |
|---|---|---|---|
| C5-01 | Canasta con historial | - | Todos (18) |
| C5-02 | Cold start | - | Todos (18) |
| C5-03 | Respeta MINSIZE/MAXSIZE | - | Todos (18) |
| C5-04 | ALPHA=2 | - | Todos (18) |
| C5-05 | Agregar desde sugerencia | `disableCart` | Todos (18) |
| C5-06 | Canasta Exploración | - | Todos (18) |
| C5-07 | Canasta Foco | - | Todos (18) |
| C5-08 | Consistencia B2B-APP | - | Todos (18) |

### Tests condicionales (según config del cliente)

| Test | Nombre | Variables | Clientes activos |
|---|---|---|---|
| C5-E1 | Sugerencias ocultas | `suggestions.hide` | *(ninguno)* |
| C5-E2 | Sugerencias ordenadas por categoría | `suggestions.enableSortingByCategories` | *(ninguno)* |
| C5-E3 | Sugerencias separadas | `hasSeparatedSuggestions` | *(ninguno)* |
| C5-E4 | Sugerencias por categorías en lista | `productList.enableSuggestionByCategories` | *(ninguno)* |

---

## [C6] Sincronización de Datos

### Tests estándar

| Test | Nombre | Variables condicionantes | Clientes donde aplica |
|---|---|---|---|
| C6-01 | Sync productos | - | Todos (18) |
| C6-02 | Sync precios/overrides | - | Todos (18) |
| C6-03 | Sync stock | `hasStockEnabled` | Todos (18) |
| C6-04 | Sync comercios | - | Todos (18) |
| C6-05 | Sync paginación | - | Todos (18) |
| C6-06 | Sync filtro fechas | - | Todos (18) |
| C6-07 | Endpoint caído | - | Todos (18) |
| C6-08 | Datos formato inválido | - | Todos (18) |
| C6-09 | Producto DISCONTINUED | - | Todos (18) |
| C6-10 | CronJob en horario | - | Todos (18) |

### Tests condicionales (según config del cliente)

| Test | Nombre | Variables | Clientes activos |
|---|---|---|---|
| C6-E1 | Background sync habilitado | `synchronization.enableBackgroundSync` | *(ninguno)* |
| C6-E2 | Background send orders | `synchronization.enableBackgroundSendOrders` | *(ninguno)* |
| C6-E3 | Sync de imágenes | `synchronization.enableSyncImages` | Codelpa, softys-cencocal (2) |

---

## [V1] Vendedor Toma Pedido (APP)

### Tests estándar

| Test | Nombre | Variables condicionantes | Clientes donde aplica |
|---|---|---|---|
| V1-01 | Lista de comercios asignados | - | Todos (18) |
| V1-02 | Seleccionar comercio | - | Todos (18) |
| V1-03 | Agregar productos | `enableChooseSaleUnit`, `limitAddingByStock` | Todos (18) |
| V1-04 | Confirmar pedido | `enableDialogNoSellReason` | Todos (18) |
| V1-05 | Pedido offline | - | Todos (18) |
| V1-06 | Sync pedidos offline | - | Todos (18) |
| V1-07 | Historial pedidos del comercio | - | Todos (18) |
| V1-08 | Re-hacer pedido anterior | - | Todos (18) |
| V1-09 | Canasta sugerida en APP | - | Todos (18) |
| V1-10 | Georreferencia | `useMobileGps` | Todos (18) |

### Tests condicionales (según config del cliente)

| Test | Nombre | Variables | Clientes activos |
|---|---|---|---|
| V1-E1 | Descuento de vendedor | `enableSellerDiscount` | Cedisur Store, CoExito Store, Codelpa, Prinorte Store, Surtiventas, softys-cencocal (6) |
| V1-E2 | Diálogo no venta | `enableDialogNoSellReason` | *(ninguno)* |
| V1-E3 | Gestor de tareas | `enableTask` | Cedisur Store, CoExito Store, Codelpa, Soprole, softys-cencocal, softys-dimak (6) |
| V1-E4 | Stock visible en tarjeta (single DC) | `hasSingleDistributionCenter`, `hasStockEnabled` | Bastien Store, Cedisur Store, CoExito Store, Codelpa Peru Store, Distribuidora El Muñeco, ExpressDent, Las Américas, Marley Coffee, Prinorte Store, Prisa Store, Prisur, Prisur Store, Soprole, Surtiventas, softys-cencocal, softys-dimak (16) |
| V1-E5 | Stock multicentro (all DCs) | `hasAllDistributionCenters`, `hasStockEnabled` | Codelpa (1) |
| V1-E6 | Voucher printer | `hasVoucherPrinterEnabled` | softys-cencocal (1) |
| V1-E7 | Segmentos por vendedor | `enableSegmentsBySeller` | *(ninguno)* |
| V1-E8 | Deshabilitar productos por vendedor | `enableDisableProductsBySeller` | *(ninguno)* |

---

## Resumen: Tests por Cliente

| Cliente | Dominio | Tests estándar | Tests condicionales | Total |
|---|---|---|---|---|
| Bastien Store | bastien.youorder.me | 77 | 1 | 78 |
| Cedisur Store | cedisur.youorder.me | 77 | 4 | 81 |
| CoExito Store | coexito.youorder.me | 77 | 8 | 85 |
| Codelpa | codelpa.youorder.me | 77 | 11 | 88 |
| Codelpa Peru Store | codelpa-peru.youorder.me | 77 | 2 | 79 |
| Distribuidora El Muñeco | elmuneco.youorder.me | 77 | 3 | 80 |
| ExpressDent | expressdent.youorder.me | 77 | 2 | 79 |
| Las Américas | americas.youorder.me | 77 | 1 | 78 |
| Marley Coffee | marleycoffee.youorder.me | 77 | 2 | 79 |
| Prinorte Store | prinorte.youorder.me | 77 | 6 | 83 |
| Prisa Store | prisa.youorder.me | 77 | 1 | 78 |
| Prisur | prisur.youorder.me | 77 | 3 | 80 |
| Prisur Store (STG) | prisur.solopide.me | 77 | 1 | 78 |
| Soprole | soprole.youorder.me | 77 | 9 | 86 |
| Soprole | new-soprole.youorder.me | 77 | 14 | 91 |
| Surtiventas | surtiventas.youorder.me | 77 | 6 | 83 |
| softys-cencocal | softys-cencocal.youorder.me | 77 | 10 | 87 |
| softys-dimak | softys-dimak.youorder.me | 77 | 2 | 79 |

---

## Nuevos Flujos — Cobertura de Variables Faltantes

> Tests generados para cubrir las 56 variables que no tenían test asociado.
> Se organizan en 6 nuevos flujos (P1-P6).

---

### [P1] Pagos y Cobranza

**Descripción:** Módulo de pagos, cobranza, notas de crédito y documentos financieros.

| ID | Caso | Variables | Datos de entrada | Resultado esperado | Tipo | Clientes |
|---|---|---|---|---|---|---|
| P1-01 | Módulo de pagos habilitado — acceso y navegación | `enablePayments` | Cliente con enablePayments=true | Sección de pagos visible en menú lateral, carga info de pagos | Integration + E2E | Soprole, Soprole, softys-cencocal (3) |
| P1-02 | Pagos deshabilitados — sección oculta | `disablePayments` | Cliente con disablePayments=true | Sección de pagos no visible, rutas de pago devuelven 403 | E2E | Las Américas (1) |
| P1-03 | Nuevo módulo de pagos | `payment.enableNewPaymentModule` | Cliente con payment.enableNewPaymentModule=true | Interfaz nueva de pagos renderiza correctamente | Integration + E2E | CoExito Store, Codelpa Peru Store, Soprole, softys-cencocal (4) |
| P1-04 | Pago requiere monto completo | `payment.requiresFullPayment` | Pago parcial en cliente con requiresFullPayment=true | Error: debe pagar el monto total | Integration | Soprole (1) |
| P1-05 | Pago externo | `payment.externalPayment` | Cliente con payment.externalPayment configurado | Redirect a pasarela externa, callback correcto | Integration | ExpressDent, Marley Coffee (2) |
| P1-06 | Cobranza habilitada en APP | `enablePaymentsCollection` | Vendedor accede a módulo de cobranza | Lista de facturas pendientes, puede registrar cobro | Integration + E2E | Soprole, softys-cencocal (2) |
| P1-07 | Documentos de pago B2B | `enablePaymentDocumentsB2B` | Comercio con enablePaymentDocumentsB2B=true | Botón de facturas visible en lista de órdenes | E2E | Soprole, Soprole (2) |
| P1-08 | Notas de crédito | `enableCreditNotes` | Admin genera nota de crédito | NC creada, vinculada a factura, visible para comercio | Integration + E2E | softys-cencocal (1) |
| P1-09 | Mensaje de estado crediticio | `enableCreditStateMessage` | Comercio con crédito cercano al límite | Mensaje de alerta visible con estado de crédito | E2E | softys-cencocal (1) |
| P1-10 | Validar pago desde admin | `validatePaymentFromAdmin` | Admin valida un pago pendiente | Pago cambia a APPROVED, comercio recibe confirmación | Integration | *(ninguno activo)* |
| P1-11 | Lista de facturas en menú | `enableInvoicesList` | Comercio con enableInvoicesList=true | Opción de facturas visible en menú de órdenes | E2E | Soprole, Soprole (2) |
| P1-12 | Documentos pendientes en menú usuario | `pendingDocuments` | Comercio con pendingDocuments=true | Badge/indicador de documentos pendientes visible | E2E | Codelpa (1) |

---

### [P2] Gestión de Comercios

**Descripción:** Creación, edición y configuración de comercios.

| ID | Caso | Variables | Datos de entrada | Resultado esperado | Tipo | Clientes |
|---|---|---|---|---|---|---|
| P2-01 | Crear comercio habilitado | `commerce.enableCreateCommerce` | Cliente con enableCreateCommerce=true | Botón crear comercio visible, flujo completo funciona | Integration + E2E | Prinorte Store, Prisur, Soprole, Surtiventas (4) |
| P2-02 | Edición de comercio deshabilitada | `disableCommerceEdit` | Cliente con disableCommerceEdit=true | Campos de edición del comercio no editables | E2E | Codelpa, Soprole, Soprole (3) |
| P2-03 | Edición de dirección habilitada | `editAddress` | Comercio edita dirección en checkout | Campos de dirección editables, cambio se guarda | E2E | Bastien Store, Cedisur Store, CoExito Store, Codelpa Peru Store, Distribuidora El Muñeco, ExpressDent, Las Américas, Marley Coffee, Prinorte Store, Prisa Store, Prisur, Prisur Store, Surtiventas, softys-cencocal, softys-dimak (15) |
| P2-04 | Alerta de cliente bloqueado | `blockedClientAlert.enableBlockedClientAlert` | Comercio bloqueado accede al sitio | Popup con alerta HTML personalizada | E2E | Soprole, Soprole (2) |
| P2-05 | Tipo de recibo oculto | `hideReceiptType` | Checkout en cliente con hideReceiptType=true | Selector de tipo de recibo no visible | E2E | Codelpa, Soprole, Soprole (3) |

---

### [P3] Packaging y Unidades

**Descripción:** Información de empaque, multi-unidad y formatos de producto.

| ID | Caso | Variables | Datos de entrada | Resultado esperado | Tipo | Clientes |
|---|---|---|---|---|---|---|
| P3-01 | Info empaque oculta en B2B | `packagingInformation.hidePackagingInformationB2B` | Producto con info de empaque en cliente con hide=true | Info de empaque no visible en tarjeta/detalle | E2E | Bastien Store, Cedisur Store, CoExito Store, Codelpa Peru Store, Distribuidora El Muñeco, ExpressDent, Las Américas, Marley Coffee, Prinorte Store, Prisa Store, Prisur, Prisur Store, Soprole, Soprole, Surtiventas (15) |
| P3-02 | Info empaque single item oculta | `packagingInformation.hideSingleItemPackagingInformationB2B` | Producto individual con empaque | Info de empaque oculta para items individuales | E2E | Bastien Store, Cedisur Store, CoExito Store, Codelpa, Codelpa Peru Store, Distribuidora El Muñeco, ExpressDent, Las Américas, Marley Coffee, Prinorte Store, Prisa Store, Prisur, Prisur Store, Surtiventas (14) |
| P3-03 | Ignorar unidad en info empaque | `packagingInformation.ignoreUnitOnPackInformationB2B` | Producto con unidad definida | Unidad no se muestra en info de empaque | Unit | *(ninguno activo)* |
| P3-04 | Multi-unidad habilitada | `hasMultiUnitEnabled` | Producto con múltiples unidades de venta | Selector de unidad visible, cálculo correcto por unidad | Integration + E2E | Prinorte Store, Prisur, Soprole, Surtiventas (4) |
| P3-05 | Monto usa unidades en packaging | `packaging.amountUsesUnits` | Producto con packaging configurado | Monto se calcula en base a unidades, no packs | Unit | Prinorte Store, Prisur, Soprole, Surtiventas (4) |
| P3-06 | Info de peso visible | `weightInfo` | Producto con peso en cliente con weightInfo=true | Precio por peso visible en tarjeta y checkout | E2E | *(ninguno activo)* |

---

### [P4] Políticas de Orden y Crédito

**Descripción:** Retención de órdenes, deuda vencida, bloqueos por crédito.

| ID | Caso | Variables | Datos de entrada | Resultado esperado | Tipo | Clientes |
|---|---|---|---|---|---|---|
| P4-01 | Bloqueo por deuda vencida | `orderPolicy.overdueDebtConfiguration.blockSettings.enabled`, `orderPolicy.overdueDebtConfiguration.blockSettings.thresholdDays` | Comercio con deuda > thresholdDays | Orden bloqueada, mensaje de deuda vencida | Integration | Soprole (1) |
| P4-02 | Retención por deuda vencida | `orderPolicy.overdueDebtConfiguration.retentionSettings.enabled`, `orderPolicy.overdueDebtConfiguration.retentionSettings.thresholdDays` | Comercio con deuda entre umbral retención y bloqueo | Orden retenida, no bloqueada | Integration | Soprole (1) |
| P4-03 | Status crédito excedido configurable | `orderPolicy.creditExceededStatus` | Orden excede crédito con status custom | Orden toma el status configurado en creditExceededStatus | Integration | Soprole (1) |
| P4-04 | Orden de compra (purchase order) | `purchaseOrderEnabled` | Checkout con purchaseOrderEnabled=true | Campo de OC visible, se guarda en la orden | Integration + E2E | CoExito Store, Codelpa (2) |
| P4-05 | Última orden en detalle de compra | `shoppingDetail.lastOrder` | Comercio con historial accede a detalle | Última orden visible como referencia rápida | E2E | Codelpa, Soprole (2) |

---

### [P5] Hooks y Semáforos

**Descripción:** Hooks de integración y semáforo de tráfico.

| ID | Caso | Variables | Datos de entrada | Resultado esperado | Tipo | Clientes |
|---|---|---|---|---|---|---|
| P5-01 | Hook de stock activo | `hooks.stockHook` | Producto consultado en cliente con stockHook=true | Stock se consulta vía hook externo, respuesta integrada | Integration | Codelpa (1) |
| P5-02 | Hook de documentos pendientes | `hooks.getPendingDocumentsHook` | Comercio consulta documentos pendientes | Documentos obtenidos vía hook externo | Integration | *(ninguno activo)* |
| P5-03 | Hook de semáforo (traffic light) | `hooks.updateTrafficLightHook` | Evento dispara actualización de semáforo | Semáforo actualizado correctamente vía hook | Integration | softys-cencocal (1) |
| P5-04 | Código de transporte | `hasTransportCode` | Orden con código de transporte requerido | Campo de transporte visible, se envía al ERP | Integration | softys-cencocal (1) |

---

### [P6] UI y Experiencia de Usuario

**Descripción:** Configuraciones visuales y de experiencia que afectan la funcionalidad.

| ID | Caso | Variables | Datos de entrada | Resultado esperado | Tipo | Clientes |
|---|---|---|---|---|---|---|
| P6-01 | Home habilitado | `enableHome` | Cliente con enableHome=true | Página de home con banners/contenido se muestra al entrar | E2E | Soprole (1) |
| P6-02 | Hora estimada de entrega oculta | `disableShowEstimatedDeliveryHour` | Orden con hora estimada en cliente con flag=true | Hora no visible en detalle de orden ni factura | E2E | Soprole, Soprole (2) |
| P6-03 | Footer personalizado | `footerCustomContent.useFooterCustomContent` | Cliente con footer custom habilitado | HTML personalizado renderiza en footer | E2E | Soprole, Soprole (2) |
| P6-04 | Botones beta habilitados | `enableBetaButtons` | Cliente con enableBetaButtons=true | Funcionalidades beta visibles y funcionales | E2E | Soprole, Soprole (2) |
| P6-05 | Texto personalizado en confirmar carro | `confirmCartText` | Cliente con confirmCartText configurado | Botón muestra texto custom en vez de default | E2E | Soprole, Soprole (2) |
| P6-06 | Filtro de no venta | `hasNoSaleFilter` | Vendedor filtra comercios sin venta | Lista se filtra correctamente mostrando solo sin venta | E2E | CoExito Store, Prinorte Store, Prisur, Surtiventas, softys-cencocal (5) |
| P6-07 | Límite de descuento visible en admin | `adminConfiguration.showDiscountLimitAdmin` | Admin con showDiscountLimitAdmin=true | Límite de descuento visible al configurar productos | E2E | *(ninguno activo)* |

---

## Resumen Final Actualizado

| Cliente | Dominio | Tests estándar | Tests cond. originales | Tests cond. nuevos (P1-P6) | Total |
|---|---|---|---|---|---|
| Bastien Store | bastien.youorder.me | 77 | 1 | 3 | 81 |
| Cedisur Store | cedisur.youorder.me | 77 | 4 | 3 | 84 |
| CoExito Store | coexito.youorder.me | 77 | 8 | 6 | 91 |
| Codelpa | codelpa.youorder.me | 77 | 11 | 7 | 95 |
| Codelpa Peru Store | codelpa-peru.youorder.me | 77 | 2 | 4 | 83 |
| Distribuidora El Muñeco | elmuneco.youorder.me | 77 | 3 | 3 | 83 |
| ExpressDent | expressdent.youorder.me | 77 | 2 | 4 | 83 |
| Las Américas | americas.youorder.me | 77 | 1 | 4 | 82 |
| Marley Coffee | marleycoffee.youorder.me | 77 | 2 | 4 | 83 |
| Prinorte Store | prinorte.youorder.me | 77 | 6 | 7 | 90 |
| Prisa Store | prisa.youorder.me | 77 | 1 | 3 | 81 |
| Prisur | prisur.youorder.me | 77 | 3 | 7 | 87 |
| Prisur Store (STG) | prisur.solopide.me | 77 | 1 | 3 | 81 |
| Soprole | soprole.youorder.me | 77 | 9 | 22 | 108 |
| Soprole | new-soprole.youorder.me | 77 | 14 | 22 | 113 |
| Surtiventas | surtiventas.youorder.me | 77 | 6 | 7 | 90 |
| softys-cencocal | softys-cencocal.youorder.me | 77 | 10 | 9 | 96 |
| softys-dimak | softys-dimak.youorder.me | 77 | 2 | 1 | 80 |

**Total tests nuevos (P1-P6): 39**

---

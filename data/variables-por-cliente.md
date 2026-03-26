# Variables por Cliente YOM — Extracción Completa con Definiciones
> Fuentes: sites (yom-stores), salesterms (yom-production), customers (yom-production)
> Fecha: 2026-03-25
> Clientes: 18 (producción + staging)

---

## Bastien Store

| Dato | Valor |
|---|---|
| Dominio | bastien.youorder.me |
| Moneda | clp |
| CustomerId | `691e198aa7ec350b1520c51f` |
| Customer legacy | ✓ Bastien |
| Salesterms | ✓ |

### Sites (yom-stores)

| Variable | Valor | Definición |
|---|---|---|
| anonymousAccess | ✗ | Permite acceso anónimo al sitio sin autenticación. Si es false requiere login. |
| anonymousHideCart | ✗ | Oculta el carrito para usuarios anónimos. |
| anonymousHidePrice | ✗ | Oculta los precios para usuarios anónimos. |
| blockedClientAlert.enableBlockedClientAlert | ✗ | Habilita popup de alerta cuando un cliente está bloqueado. |
| businessUnits | [] | Variable en desuso. Permitía catálogos divididos por unidad de negocio. |
| commerce.enableCreateCommerce | ✗ | Habilita el botón y flujo de creación de comercio. |
| disableCart | ✗ | Deshabilita completamente el carrito de compras. |
| disableCommerceEdit | ✗ | Deshabilita edición de comercio. |
| disableObservationInput | ✗ | Deshabilita campo de observaciones en el pedido. |
| disablePayments | ✗ | Deshabilita pagos. |
| disableShowEstimatedDeliveryHour | ✗ | Oculta hora estimada de entrega. |
| discountTypes.discountTypesList | [] | Variable en desuso. Tags para descuento de vendedor. |
| discountTypes.enableOrderDiscountType | ✗ | Variable en desuso. |
| discountTypes.enableProductDiscountType | ✗ | Variable en desuso. |
| editAddress | ✓ | Permite editar dirección de envío. Default true. |
| enableAskDeliveryDate | ✗ | Habilita pregunta de fecha de entrega. |
| enableBetaButtons | ✗ | Habilita botones beta. |
| enableChooseSaleUnit | ✗ | Habilita selección de unidad de venta (B2B nuevo + app). |
| enableCoupons | ✓ | Habilita cupones de descuento. |
| enableCreditNotes | ✗ | Habilita notas de crédito. |
| enableDialogNoSellReason | ✗ | Habilita diálogo de razón de no venta. |
| enableDistributionCentersSelector | ✗ | Habilita selector de centros de distribución. |
| enableInvoicesList | ✗ | Habilita lista de facturas en menú de órdenes. |
| enableNewUI | ✗ | Habilita nueva interfaz. Siempre debería estar activa, la vieja está descontinuada. |
| enableOrderApproval | ✗ | Habilita aprobación de órdenes por vendedores. |
| enableOrderValidation | ✗ | Habilita validación de órdenes. |
| enablePaymentDocumentsB2B | ✗ | Habilita documentos de pago B2B. Botón de facturas en order-list. |
| enablePayments | ✗ | Habilita módulo de pagos. |
| enablePaymentsCollection | ✗ | Habilita módulo de cobranza. disablePayments la desactiva. |
| enablePriceOracle | ✗ | Habilita precios futuros (oracle). Obtiene fecha de entrega antes de cargar precios. |
| enableSellerDiscount | ✗ | Permite que el vendedor haga descuentos. |
| enableTask | ✗ | Habilita gestor de tareas. |
| externalAccess | ✗ | Permite acceso externo. |
| filterGroupedSuggestionsBy | [] | Define campo para filtrar sugerencias agrupadas (ej: packaging.amountPerPackage). |
| footerCustomContent.useFooterCustomContent | ✗ | Habilita contenido personalizado en footer. |
| hasAllDistributionCenters | ✗ | Si stock es multicentro, asigna todos los centros a todos los comercios. |
| hasMultiUnitEnabled | ✗ | Habilita múltiples unidades. |
| hasMultipleBusinessUnit | ✗ | En desuso. |
| hasNoSaleFilter | ✗ | Habilita filtro de no venta. |
| hasSingleDistributionCenter | ✓ | Con stock, indica si comercios tienen un solo centro de distribución. Si true, stock se ve directo en tarjeta. Si false, botón 'ver stock' muestra todos los centros. |
| hasStockEnabled | ✗ | Indica si hay o no stock. |
| hasTransferPaymentType | ✗ | Habilita tipo de pago por transferencia. |
| hasTransportCode | ✗ | Variable de nicho para softys-cencocal. |
| hasVoucherPrinterEnabled | ✗ | Habilita impresora de voucher. |
| hidePrices | ✗ | Oculta todos los precios del sitio. |
| hideReceiptType | ✗ | Oculta tipo de recibo en checkout. |
| hooks.cartShoppingHook | ✗ | Hook de carrito de compras. |
| hooks.getPendingDocumentsHook | ✗ | Hook de documentos pendientes. |
| hooks.shippingHook | ✗ | Hook de envío. Usado en checkout. |
| hooks.stockHook | ✗ | Hook de stock. |
| hooks.updateTrafficLightHook | ✗ | Hook de semáforo. |
| inMaintenance | ✗ | Indica si el sitio está en mantenimiento. |
| includeTaxRateInPrices | ✗ | Incluye tasa de impuesto en los precios. |
| lazyLoadingPrices | ✗ | Habilita carga perezosa de precios (async). |
| limitAddingByStock | ✗ | Limita agregar productos según stock disponible. |
| orderObservations | [] | Configuración de observaciones de orden. |
| ordersRequireAuthorization | ✗ | Órdenes requieren autorización. |
| ordersRequireVerification | ✗ | Órdenes requieren verificación de cuenta. |
| packagingInformation.hidePackagingInformationB2B | ✓ | Oculta info de empaque B2B. Default true. |
| packagingInformation.hideSingleItemPackagingInformationB2B | ✓ | Oculta info de empaque para items individuales B2B. Default true. |
| packagingInformation.ignoreUnitOnPackInformationB2B | ✗ | Ignora unidad en info de empaque B2B. Default false. |
| payment.balances | [] | Configuración de balances de pago. |
| payment.enableNewPaymentModule | ✗ | Habilita nuevo módulo de pagos. |
| payment.requiresFullPayment | ✗ | Requiere pago completo. |
| paymentsWithoutAccount | ✗ | Pagos sin cuenta. |
| pendingDocuments | ✗ | Habilita documentos pendientes en menú de usuario. Default false. |
| pointsEnabled | ✗ | Habilita sistema de puntos. |
| priceRoundingDecimals | 0 | Decimales para redondeo de precios. Default 0. |
| productVariability | none | No encontrado en el código. |
| purchaseOrderEnabled | ✗ | Habilita órdenes de compra. |
| shareOrderNewDesign | ✗ | No encontrado en el código. |
| shoppingDetail.lastOrder | ✗ | Muestra última orden en detalle de compra. |
| showEmptyCategories | ✗ | Muestra categorías vacías. Default false. |
| showMinOne | ✗ | Muestra mínimo uno. Info de medición en catálogo. |
| synchronization.backgroundSyncList | [] | Lista de sync en background. |
| synchronization.enableBackgroundSendOrders | ✗ | Habilita envío de órdenes en background. |
| synchronization.enableBackgroundSync | ✗ | Habilita sincronización en background. |
| synchronization.enableSyncImages | ✗ | Habilita sincronización de imágenes. |
| taxes.showSummary | ✗ | Muestra resumen de impuestos en checkout. |
| taxes.taxRate | 0 | Tasa de impuesto. |
| taxes.useTaxRate | ✗ | Usa tasa de impuestos en cálculos de precios. |
| uploadOrderFileWithMinUnits | ✗ | Permite subir archivo de orden con unidades mínimas. |
| useMobileGps | ✗ | Usa GPS del móvil. |
| useMongoPricing | ✗ | Usa pricing de MongoDB. |
| useNewPromotions | ✗ | Usa nuevo sistema de promociones. |
| validatePaymentFromAdmin | ✗ | Valida pago desde admin. |
| weightInfo | ✗ | Muestra info de peso de productos. Precio por peso en tarjetas. |

### Salesterms (yom-production)

| Variable | Valor |
|---|---|
| delivery.daysOfWeek | [] |
| order.disableOrder | ✗ |
| order.orderTotalCreditMax | ✗ |
| order.orderTotalCreditMaxMustBlockOrder | ✗ |
| payment.paymentTypes | [] |
| saleConfig.noSellReasons | [] |

### Customer (yom-production)

| Variable | Valor |
|---|---|
| contactMailingList | [] |
| creditReturnStates | [] |
| currency | clp |
| domain | bastien.youorder.me |
| eventOptions.newOrderEvent | ✗ |
| mailingList | [] |
| name | Bastien |
| registerMailingList | [] |

---

## Cedisur Store

| Dato | Valor |
|---|---|
| Dominio | cedisur.youorder.me |
| Moneda | clp |
| CustomerId | `68ed01fa788577aacd689daa` |
| Customer legacy | ✓ Cedisur |
| Salesterms | ✓ |

### Sites (yom-stores)

| Variable | Valor | Definición |
|---|---|---|
| anonymousAccess | ✗ | Permite acceso anónimo al sitio sin autenticación. Si es false requiere login. |
| anonymousHideCart | ✗ | Oculta el carrito para usuarios anónimos. |
| anonymousHidePrice | ✗ | Oculta los precios para usuarios anónimos. |
| blockedClientAlert.enableBlockedClientAlert | ✗ | Habilita popup de alerta cuando un cliente está bloqueado. |
| businessUnits | [] | Variable en desuso. Permitía catálogos divididos por unidad de negocio. |
| commerce.enableCreateCommerce | ✗ | Habilita el botón y flujo de creación de comercio. |
| disableCart | ✗ | Deshabilita completamente el carrito de compras. |
| disableCommerceEdit | ✗ | Deshabilita edición de comercio. |
| disableObservationInput | ✗ | Deshabilita campo de observaciones en el pedido. |
| disablePayments | ✗ | Deshabilita pagos. |
| disableShowEstimatedDeliveryHour | ✗ | Oculta hora estimada de entrega. |
| discountTypes.discountTypesList | [] | Variable en desuso. Tags para descuento de vendedor. |
| discountTypes.enableOrderDiscountType | ✗ | Variable en desuso. |
| discountTypes.enableProductDiscountType | ✗ | Variable en desuso. |
| editAddress | ✓ | Permite editar dirección de envío. Default true. |
| enableAskDeliveryDate | ✗ | Habilita pregunta de fecha de entrega. |
| enableBetaButtons | ✗ | Habilita botones beta. |
| enableChooseSaleUnit | ✗ | Habilita selección de unidad de venta (B2B nuevo + app). |
| enableCoupons | ✓ | Habilita cupones de descuento. |
| enableCreditNotes | ✗ | Habilita notas de crédito. |
| enableDialogNoSellReason | ✗ | Habilita diálogo de razón de no venta. |
| enableDistributionCentersSelector | ✗ | Habilita selector de centros de distribución. |
| enableInvoicesList | ✗ | Habilita lista de facturas en menú de órdenes. |
| enableNewUI | ✗ | Habilita nueva interfaz. Siempre debería estar activa, la vieja está descontinuada. |
| enableOrderApproval | ✗ | Habilita aprobación de órdenes por vendedores. |
| enableOrderValidation | ✗ | Habilita validación de órdenes. |
| enablePaymentDocumentsB2B | ✗ | Habilita documentos de pago B2B. Botón de facturas en order-list. |
| enablePayments | ✗ | Habilita módulo de pagos. |
| enablePaymentsCollection | ✗ | Habilita módulo de cobranza. disablePayments la desactiva. |
| enablePriceOracle | ✗ | Habilita precios futuros (oracle). Obtiene fecha de entrega antes de cargar precios. |
| enableSellerDiscount | ✓ | Permite que el vendedor haga descuentos. |
| enableTask | ✓ | Habilita gestor de tareas. |
| externalAccess | ✗ | Permite acceso externo. |
| filterGroupedSuggestionsBy | [] | Define campo para filtrar sugerencias agrupadas (ej: packaging.amountPerPackage). |
| footerCustomContent.useFooterCustomContent | ✗ | Habilita contenido personalizado en footer. |
| hasAllDistributionCenters | ✗ | Si stock es multicentro, asigna todos los centros a todos los comercios. |
| hasMultiUnitEnabled | ✗ | Habilita múltiples unidades. |
| hasMultipleBusinessUnit | ✗ | En desuso. |
| hasNoSaleFilter | ✗ | Habilita filtro de no venta. |
| hasSingleDistributionCenter | ✓ | Con stock, indica si comercios tienen un solo centro de distribución. Si true, stock se ve directo en tarjeta. Si false, botón 'ver stock' muestra todos los centros. |
| hasStockEnabled | ✗ | Indica si hay o no stock. |
| hasTransferPaymentType | ✗ | Habilita tipo de pago por transferencia. |
| hasTransportCode | ✗ | Variable de nicho para softys-cencocal. |
| hasVoucherPrinterEnabled | ✗ | Habilita impresora de voucher. |
| hidePrices | ✗ | Oculta todos los precios del sitio. |
| hideReceiptType | ✗ | Oculta tipo de recibo en checkout. |
| hooks.cartShoppingHook | ✗ | Hook de carrito de compras. |
| hooks.getPendingDocumentsHook | ✗ | Hook de documentos pendientes. |
| hooks.shippingHook | ✗ | Hook de envío. Usado en checkout. |
| hooks.stockHook | ✗ | Hook de stock. |
| hooks.updateTrafficLightHook | ✗ | Hook de semáforo. |
| inMaintenance | ✗ | Indica si el sitio está en mantenimiento. |
| includeTaxRateInPrices | ✗ | Incluye tasa de impuesto en los precios. |
| lazyLoadingPrices | ✗ | Habilita carga perezosa de precios (async). |
| limitAddingByStock | ✗ | Limita agregar productos según stock disponible. |
| orderObservations | [] | Configuración de observaciones de orden. |
| ordersRequireAuthorization | ✗ | Órdenes requieren autorización. |
| ordersRequireVerification | ✗ | Órdenes requieren verificación de cuenta. |
| packagingInformation.hidePackagingInformationB2B | ✓ | Oculta info de empaque B2B. Default true. |
| packagingInformation.hideSingleItemPackagingInformationB2B | ✓ | Oculta info de empaque para items individuales B2B. Default true. |
| packagingInformation.ignoreUnitOnPackInformationB2B | ✗ | Ignora unidad en info de empaque B2B. Default false. |
| payment.balances | [] | Configuración de balances de pago. |
| payment.enableNewPaymentModule | ✗ | Habilita nuevo módulo de pagos. |
| payment.requiresFullPayment | ✗ | Requiere pago completo. |
| paymentsWithoutAccount | ✗ | Pagos sin cuenta. |
| pendingDocuments | ✗ | Habilita documentos pendientes en menú de usuario. Default false. |
| pointsEnabled | ✗ | Habilita sistema de puntos. |
| priceRoundingDecimals | 0 | Decimales para redondeo de precios. Default 0. |
| productVariability | none | No encontrado en el código. |
| purchaseOrderEnabled | ✗ | Habilita órdenes de compra. |
| shareOrderNewDesign | ✗ | No encontrado en el código. |
| shoppingDetail.lastOrder | ✗ | Muestra última orden en detalle de compra. |
| showEmptyCategories | ✗ | Muestra categorías vacías. Default false. |
| showMinOne | ✗ | Muestra mínimo uno. Info de medición en catálogo. |
| synchronization.backgroundSyncList | [] | Lista de sync en background. |
| synchronization.enableBackgroundSendOrders | ✗ | Habilita envío de órdenes en background. |
| synchronization.enableBackgroundSync | ✗ | Habilita sincronización en background. |
| synchronization.enableSyncImages | ✗ | Habilita sincronización de imágenes. |
| taxes.showSummary | ✗ | Muestra resumen de impuestos en checkout. |
| taxes.taxRate | 0 | Tasa de impuesto. |
| taxes.useTaxRate | ✗ | Usa tasa de impuestos en cálculos de precios. |
| uploadOrderFileWithMinUnits | ✗ | Permite subir archivo de orden con unidades mínimas. |
| useMobileGps | ✗ | Usa GPS del móvil. |
| useMongoPricing | ✗ | Usa pricing de MongoDB. |
| useNewPromotions | ✓ | Usa nuevo sistema de promociones. |
| validatePaymentFromAdmin | ✗ | Valida pago desde admin. |
| weightInfo | ✗ | Muestra info de peso de productos. Precio por peso en tarjetas. |

### Salesterms (yom-production)

| Variable | Valor |
|---|---|
| delivery.daysOfWeek | [] |
| order.disableOrder | ✗ |
| order.orderTotalCreditMax | ✗ |
| order.orderTotalCreditMaxMustBlockOrder | ✗ |
| payment.paymentTypes | [] |
| saleConfig.noSellReasons | [] |

### Customer (yom-production)

| Variable | Valor |
|---|---|
| contactMailingList | [] |
| creditReturnStates | [] |
| currency | clp |
| domain | cedisur.youorder.me |
| eventOptions.newOrderEvent | ✗ |
| mailingList | [] |
| name | Cedisur |
| registerMailingList | [] |

---

## CoExito Store

| Dato | Valor |
|---|---|
| Dominio | coexito.youorder.me |
| Moneda | clp |
| CustomerId | `67d9d45b0c75f0e6c45cdfad` |
| Customer legacy | ✓ CoExito |
| Salesterms | ✓ |

### Sites (yom-stores)

| Variable | Valor | Definición |
|---|---|---|
| adminConfiguration.showDiscountLimitAdmin | ✗ | Muestra límite de descuento en admin. |
| anonymousAccess | ✗ | Permite acceso anónimo al sitio sin autenticación. Si es false requiere login. |
| anonymousHideCart | ✗ | Oculta el carrito para usuarios anónimos. |
| anonymousHidePrice | ✗ | Oculta los precios para usuarios anónimos. |
| blockedClientAlert.enableBlockedClientAlert | ✗ | Habilita popup de alerta cuando un cliente está bloqueado. |
| businessUnits | [] | Variable en desuso. Permitía catálogos divididos por unidad de negocio. |
| commerce.enableCreateCommerce | ✗ | Habilita el botón y flujo de creación de comercio. |
| disableCart | ✗ | Deshabilita completamente el carrito de compras. |
| disableCommerceEdit | ✗ | Deshabilita edición de comercio. |
| disableManualDiscount | ✓ | Deshabilita descuento manual. |
| disableObservationInput | ✗ | Deshabilita campo de observaciones en el pedido. |
| disablePayments | ✗ | Deshabilita pagos. |
| disableShowEstimatedDeliveryHour | ✗ | Oculta hora estimada de entrega. |
| discountTypes.discountTypesList | [] | Variable en desuso. Tags para descuento de vendedor. |
| discountTypes.enableOrderDiscountType | ✗ | Variable en desuso. |
| discountTypes.enableProductDiscountType | ✗ | Variable en desuso. |
| editAddress | ✓ | Permite editar dirección de envío. Default true. |
| enableAskDeliveryDate | ✗ | Habilita pregunta de fecha de entrega. |
| enableBetaButtons | ✗ | Habilita botones beta. |
| enableChooseSaleUnit | ✗ | Habilita selección de unidad de venta (B2B nuevo + app). |
| enableCoupons | ✓ | Habilita cupones de descuento. |
| enableCreditNotes | ✗ | Habilita notas de crédito. |
| enableDialogNoSellReason | ✗ | Habilita diálogo de razón de no venta. |
| enableDistributionCentersSelector | ✗ | Habilita selector de centros de distribución. |
| enableInvoicesList | ✗ | Habilita lista de facturas en menú de órdenes. |
| enableNewUI | ✗ | Habilita nueva interfaz. Siempre debería estar activa, la vieja está descontinuada. |
| enableOrderApproval | ✗ | Habilita aprobación de órdenes por vendedores. |
| enableOrderValidation | ✗ | Habilita validación de órdenes. |
| enablePaymentDocumentsB2B | ✗ | Habilita documentos de pago B2B. Botón de facturas en order-list. |
| enablePayments | ✗ | Habilita módulo de pagos. |
| enablePaymentsCollection | ✗ | Habilita módulo de cobranza. disablePayments la desactiva. |
| enablePriceOracle | ✗ | Habilita precios futuros (oracle). Obtiene fecha de entrega antes de cargar precios. |
| enableSellerDiscount | ✓ | Permite que el vendedor haga descuentos. |
| enableTask | ✓ | Habilita gestor de tareas. |
| externalAccess | ✗ | Permite acceso externo. |
| filterGroupedSuggestionsBy | [] | Define campo para filtrar sugerencias agrupadas (ej: packaging.amountPerPackage). |
| footerCustomContent.useFooterCustomContent | ✗ | Habilita contenido personalizado en footer. |
| hasAllDistributionCenters | ✗ | Si stock es multicentro, asigna todos los centros a todos los comercios. |
| hasMultiUnitEnabled | ✗ | Habilita múltiples unidades. |
| hasMultipleBusinessUnit | ✗ | En desuso. |
| hasNoSaleFilter | ✓ | Habilita filtro de no venta. |
| hasSingleDistributionCenter | ✓ | Con stock, indica si comercios tienen un solo centro de distribución. Si true, stock se ve directo en tarjeta. Si false, botón 'ver stock' muestra todos los centros. |
| hasStockEnabled | ✗ | Indica si hay o no stock. |
| hasTransferPaymentType | ✗ | Habilita tipo de pago por transferencia. |
| hasTransportCode | ✗ | Variable de nicho para softys-cencocal. |
| hasVoucherPrinterEnabled | ✗ | Habilita impresora de voucher. |
| hidePrices | ✗ | Oculta todos los precios del sitio. |
| hideReceiptType | ✗ | Oculta tipo de recibo en checkout. |
| hooks.cartShoppingHook | ✗ | Hook de carrito de compras. |
| hooks.getPendingDocumentsHook | ✗ | Hook de documentos pendientes. |
| hooks.shippingHook | ✗ | Hook de envío. Usado en checkout. |
| hooks.stockHook | ✗ | Hook de stock. |
| hooks.updateTrafficLightHook | ✗ | Hook de semáforo. |
| inMaintenance | ✗ | Indica si el sitio está en mantenimiento. |
| includeTaxRateInPrices | ✓ | Incluye tasa de impuesto en los precios. |
| lazyLoadingPrices | ✗ | Habilita carga perezosa de precios (async). |
| limitAddingByStock | ✗ | Limita agregar productos según stock disponible. |
| mobileAccess.passwordDisabled | ✓ | Deshabilita contraseña en acceso móvil. |
| orderObservations | [{"disabled":false,"maxCharacters":240,"observationKey":"purchaseObservation","observationTitle":"Observaciones Factura"... | Configuración de observaciones de orden. |
| orderTypes | [{"displayName":"VENTA NORMAL","key":"VEN_NOR_"},{"displayName":"VENTA ENTREGA TERCEROS","key":"VEN_ENT_3ROS_"},{"displa... | Tipos de orden disponibles. |
| ordersRequireAuthorization | ✗ | Órdenes requieren autorización. |
| ordersRequireVerification | ✗ | Órdenes requieren verificación de cuenta. |
| packagingInformation.hidePackagingInformationB2B | ✓ | Oculta info de empaque B2B. Default true. |
| packagingInformation.hideSingleItemPackagingInformationB2B | ✓ | Oculta info de empaque para items individuales B2B. Default true. |
| packagingInformation.ignoreUnitOnPackInformationB2B | ✗ | Ignora unidad en info de empaque B2B. Default false. |
| payment.balances | [{"additionalBalanceFields":[{"displayName":"Saldo","key":"balance","type":"textField"},{"displayName":"Observaciones","... | Configuración de balances de pago. |
| payment.enableNewPaymentModule | ✓ | Habilita nuevo módulo de pagos. |
| payment.requiresFullPayment | ✗ | Requiere pago completo. |
| paymentsWithoutAccount | ✗ | Pagos sin cuenta. |
| pendingDocuments | ✗ | Habilita documentos pendientes en menú de usuario. Default false. |
| pointsEnabled | ✗ | Habilita sistema de puntos. |
| priceRoundingDecimals | 0 | Decimales para redondeo de precios. Default 0. |
| purchaseOrderEnabled | ✓ | Habilita órdenes de compra. |
| shareOrderNewDesign | ✗ | No encontrado en el código. |
| shoppingDetail.lastOrder | ✗ | Muestra última orden en detalle de compra. |
| showEmptyCategories | ✗ | Muestra categorías vacías. Default false. |
| showMinOne | ✗ | Muestra mínimo uno. Info de medición en catálogo. |
| synchronization.backgroundSyncList | [] | Lista de sync en background. |
| synchronization.enableBackgroundSendOrders | ✗ | Habilita envío de órdenes en background. |
| synchronization.enableBackgroundSync | ✗ | Habilita sincronización en background. |
| synchronization.enableSyncImages | ✗ | Habilita sincronización de imágenes. |
| taxes.showSummary | ✗ | Muestra resumen de impuestos en checkout. |
| taxes.taxRate | 0 | Tasa de impuesto. |
| taxes.useTaxRate | ✓ | Usa tasa de impuestos en cálculos de precios. |
| uploadOrderFileWithMinUnits | ✗ | Permite subir archivo de orden con unidades mínimas. |
| useMobileGps | ✗ | Usa GPS del móvil. |
| useMongoPricing | ✗ | Usa pricing de MongoDB. |
| useNewPromotions | ✓ | Usa nuevo sistema de promociones. |
| validatePaymentFromAdmin | ✗ | Valida pago desde admin. |
| weightInfo | ✗ | Muestra info de peso de productos. Precio por peso en tarjetas. |

### Salesterms (yom-production)

| Variable | Valor |
|---|---|
| delivery.daysOfWeek | [] |
| order.disableOrder | ✗ |
| order.maxProducts | 50 |
| order.minTotalPrice | 300000 |
| order.orderTotalCreditMax | ✗ |
| order.orderTotalCreditMaxMustBlockOrder | ✗ |
| payment.paymentTypes | [{"key":"cash","text":"Efectivo"},{"key":"card","text":"Tarjeta"},{"key":"transfer","text":"Transferencia"},{"key":"chec... |
| saleConfig.noSellReasons | [] |

### Customer (yom-production)

| Variable | Valor |
|---|---|
| contactMailingList | [] |
| currency | clp |
| domain | coexito.youorder.me |
| eventOptions.newOrderEvent | ✗ |
| integrationHooks.createOrderHook | https://api.youorder.me/hooks/coexito/create-order |
| integrationHooks.createPaymentHook | https://api.youorder.me/hooks/coexito/create-payments |
| mailingList | [] |
| name | CoExito |
| refreshTokenDuration | 24h |
| registerMailingList | [] |

---

## Codelpa

| Dato | Valor |
|---|---|
| Dominio | codelpa.youorder.me |
| Moneda | clp |
| CustomerId | `5d1e363d20721a0f7e0b3cf2` |
| Customer legacy | ✓ codelpa |
| Salesterms | ✓ |

### Sites (yom-stores)

| Variable | Valor | Definición |
|---|---|---|
| anonymousAccess | ✗ | Permite acceso anónimo al sitio sin autenticación. Si es false requiere login. |
| anonymousHideCart | ✓ | Oculta el carrito para usuarios anónimos. |
| anonymousHidePrice | ✓ | Oculta los precios para usuarios anónimos. |
| contact.about | Grupo Codelpa Colores del Pacífico, es la empresa de pinturas y revestimientos más grande del país, agrupando marcas de pinturas como Ceresita, Sipa, Soquina, Chilcorrofín, Pinmor y Titanium 2K de Sipa. | Información sobre la empresa (máx 250 chars). Mostrado en footer. |
| contact.branchesContactInformation | [{"address":"Camino Lo Echevers 801, Quilicura","phone":"+562227262800","email":"info@codelpa.cl"}] | Info de contacto de sucursales. Usado en checkout y profile. |
| contact.email | info@codelpa.cl | Email de contacto. Mostrado en footer. |
| disableCart | ✗ | Deshabilita completamente el carrito de compras. |
| disableCommerceEdit | ✓ | Deshabilita edición de comercio. |
| disableShowEstimatedDeliveryHour | ✗ | Oculta hora estimada de entrega. |
| editAddress | ✗ | Permite editar dirección de envío. Default true. |
| enableAskDeliveryDate | ✗ | Habilita pregunta de fecha de entrega. |
| enableCoupons | ✓ | Habilita cupones de descuento. |
| enableCreditStateMessage | ✗ | Habilita mensaje de estado de crédito. |
| enableDialogNoSellReason | ✗ | Habilita diálogo de razón de no venta. |
| enableInvoicesList | ✗ | Habilita lista de facturas en menú de órdenes. |
| enableMassiveOrderSend | ✓ | Permite enviar órdenes pendientes de forma masiva. |
| enableOrderApproval | ✓ | Habilita aprobación de órdenes por vendedores. |
| enableOrderValidation | ✓ | Habilita validación de órdenes. |
| enableSellerDiscount | ✓ | Permite que el vendedor haga descuentos. |
| enableTask | ✓ | Habilita gestor de tareas. |
| externalAccess | ✗ | Permite acceso externo. |
| hasAllDistributionCenters | ✓ | Si stock es multicentro, asigna todos los centros a todos los comercios. |
| hasSingleDistributionCenter | ✗ | Con stock, indica si comercios tienen un solo centro de distribución. Si true, stock se ve directo en tarjeta. Si false, botón 'ver stock' muestra todos los centros. |
| hasStockEnabled | ✓ | Indica si hay o no stock. |
| hidePrices | ✗ | Oculta todos los precios del sitio. |
| hideReceiptType | ✓ | Oculta tipo de recibo en checkout. |
| hooks.cartShoppingHook | ✗ | Hook de carrito de compras. |
| hooks.getPendingDocumentsHook | ✗ | Hook de documentos pendientes. |
| hooks.shippingHook | ✓ | Hook de envío. Usado en checkout. |
| hooks.stockHook | ✓ | Hook de stock. |
| hooks.updateTrafficLightHook | ✗ | Hook de semáforo. |
| inMaintenance | ✗ | Indica si el sitio está en mantenimiento. |
| includeTaxRateInPrices | ✗ | Incluye tasa de impuesto en los precios. |
| lazyLoadingPrices | ✗ | Habilita carga perezosa de precios (async). |
| ordersRequireAuthorization | ✗ | Órdenes requieren autorización. |
| ordersRequireVerification | ✗ | Órdenes requieren verificación de cuenta. |
| packagingInformation.hidePackagingInformationB2B | ✗ | Oculta info de empaque B2B. Default true. |
| packagingInformation.hideSingleItemPackagingInformationB2B | ✓ | Oculta info de empaque para items individuales B2B. Default true. |
| packagingInformation.ignoreUnitOnPackInformationB2B | ✗ | Ignora unidad en info de empaque B2B. Default false. |
| payment.enableNewPaymentModule | ✗ | Habilita nuevo módulo de pagos. |
| pendingDocuments | ✓ | Habilita documentos pendientes en menú de usuario. Default false. |
| pointsEnabled | ✗ | Habilita sistema de puntos. |
| productVariability | none | No encontrado en el código. |
| purchaseOrderEnabled | ✓ | Habilita órdenes de compra. |
| shoppingDetail.lastOrder | ✓ | Muestra última orden en detalle de compra. |
| showEmptyCategories | ✗ | Muestra categorías vacías. Default false. |
| showMinOne | ✗ | Muestra mínimo uno. Info de medición en catálogo. |
| synchronization.enableSyncImages | ✓ | Habilita sincronización de imágenes. |
| taxes.showSummary | ✓ | Muestra resumen de impuestos en checkout. |
| taxes.taxRate | 0 | Tasa de impuesto. |
| taxes.useTaxRate | ✗ | Usa tasa de impuestos en cálculos de precios. |
| useMobileGps | ✓ | Usa GPS del móvil. |
| useMongoPricing | ✓ | Usa pricing de MongoDB. |
| weightInfo | ✗ | Muestra info de peso de productos. Precio por peso en tarjetas. |

### Salesterms (yom-production)

| Variable | Valor |
|---|---|
| coverage.text |  |
| delivery.daysOfWeek | ["monday","tuesday","wednesday","thursday","friday","saturday"] |
| delivery.fromHours | 0 |
| delivery.text |  |
| delivery.toHours | 86400 |
| order.discountPercentageMax | 0.3 |
| order.minTotalPrice | 200000 |
| order.orderTotalCreditMax | ✓ |
| order.orderTotalCreditMaxText | Pedido supera el saldo disponible, esta orden entrará como cotización y será vista en el área de Credito y Cobranza de Codelpa |
| order.text | - |
| payment.paymentTypes | [{"key":"checkToDate","text":"Cheque a fecha"},{"key":"check","text":"Cheque"}] |

### Customer (yom-production)

| Variable | Valor |
|---|---|
| currency | clp |
| domain | codelpa.youorder.me |
| eventOptions.newOrderEvent | ✗ |
| integrationHooks.createOrderHook | https://api.youorder.me/hooks/codelpa/create-order |
| integrationHooks.createPaymentHook | https://api.youorder.me/hooks/codelpa/create-payment |
| integrationHooks.shippingCostHook | https://api.youorder.me/hooks/codelpa/shipping-cost |
| integrationHooks.updateStockHook | yom-hooks.codelpa.getStock |
| integrationHooks.webpushMessageHook | https://message-sender-570360699009.southamerica-west1.run.app/api/v1/webhooks/receive/yom |
| mailingList | [] |
| name | codelpa |
| registerMailingList | ["jfloresm@codelpa.clx"] |

---

## Codelpa Peru Store

| Dato | Valor |
|---|---|
| Dominio | codelpa-peru.youorder.me |
| Moneda | clp |
| CustomerId | `69678b86c07044566413053a` |
| Customer legacy | ✓ Codelpa Peru |
| Salesterms | ✓ |

### Sites (yom-stores)

| Variable | Valor | Definición |
|---|---|---|
| anonymousAccess | ✗ | Permite acceso anónimo al sitio sin autenticación. Si es false requiere login. |
| anonymousHideCart | ✗ | Oculta el carrito para usuarios anónimos. |
| anonymousHidePrice | ✗ | Oculta los precios para usuarios anónimos. |
| blockedClientAlert.enableBlockedClientAlert | ✗ | Habilita popup de alerta cuando un cliente está bloqueado. |
| businessUnits | [] | Variable en desuso. Permitía catálogos divididos por unidad de negocio. |
| commerce.enableCreateCommerce | ✗ | Habilita el botón y flujo de creación de comercio. |
| disableCart | ✗ | Deshabilita completamente el carrito de compras. |
| disableCommerceEdit | ✗ | Deshabilita edición de comercio. |
| disableObservationInput | ✗ | Deshabilita campo de observaciones en el pedido. |
| disablePayments | ✗ | Deshabilita pagos. |
| disableShowEstimatedDeliveryHour | ✗ | Oculta hora estimada de entrega. |
| discountTypes.discountTypesList | [] | Variable en desuso. Tags para descuento de vendedor. |
| discountTypes.enableOrderDiscountType | ✗ | Variable en desuso. |
| discountTypes.enableProductDiscountType | ✗ | Variable en desuso. |
| editAddress | ✓ | Permite editar dirección de envío. Default true. |
| enableAskDeliveryDate | ✗ | Habilita pregunta de fecha de entrega. |
| enableBetaButtons | ✗ | Habilita botones beta. |
| enableChooseSaleUnit | ✗ | Habilita selección de unidad de venta (B2B nuevo + app). |
| enableCoupons | ✓ | Habilita cupones de descuento. |
| enableCreditNotes | ✗ | Habilita notas de crédito. |
| enableDialogNoSellReason | ✗ | Habilita diálogo de razón de no venta. |
| enableDistributionCentersSelector | ✗ | Habilita selector de centros de distribución. |
| enableInvoicesList | ✗ | Habilita lista de facturas en menú de órdenes. |
| enableNewUI | ✗ | Habilita nueva interfaz. Siempre debería estar activa, la vieja está descontinuada. |
| enableOrderApproval | ✗ | Habilita aprobación de órdenes por vendedores. |
| enableOrderValidation | ✗ | Habilita validación de órdenes. |
| enablePaymentDocumentsB2B | ✗ | Habilita documentos de pago B2B. Botón de facturas en order-list. |
| enablePayments | ✗ | Habilita módulo de pagos. |
| enablePaymentsCollection | ✗ | Habilita módulo de cobranza. disablePayments la desactiva. |
| enablePriceOracle | ✗ | Habilita precios futuros (oracle). Obtiene fecha de entrega antes de cargar precios. |
| enableSellerDiscount | ✗ | Permite que el vendedor haga descuentos. |
| enableTask | ✗ | Habilita gestor de tareas. |
| externalAccess | ✗ | Permite acceso externo. |
| filterGroupedSuggestionsBy | [] | Define campo para filtrar sugerencias agrupadas (ej: packaging.amountPerPackage). |
| footerCustomContent.useFooterCustomContent | ✗ | Habilita contenido personalizado en footer. |
| hasAllDistributionCenters | ✗ | Si stock es multicentro, asigna todos los centros a todos los comercios. |
| hasMultiUnitEnabled | ✗ | Habilita múltiples unidades. |
| hasMultipleBusinessUnit | ✗ | En desuso. |
| hasNoSaleFilter | ✗ | Habilita filtro de no venta. |
| hasSingleDistributionCenter | ✓ | Con stock, indica si comercios tienen un solo centro de distribución. Si true, stock se ve directo en tarjeta. Si false, botón 'ver stock' muestra todos los centros. |
| hasStockEnabled | ✗ | Indica si hay o no stock. |
| hasTransferPaymentType | ✗ | Habilita tipo de pago por transferencia. |
| hasTransportCode | ✗ | Variable de nicho para softys-cencocal. |
| hasVoucherPrinterEnabled | ✗ | Habilita impresora de voucher. |
| hidePrices | ✗ | Oculta todos los precios del sitio. |
| hideReceiptType | ✗ | Oculta tipo de recibo en checkout. |
| hooks.cartShoppingHook | ✗ | Hook de carrito de compras. |
| hooks.getPendingDocumentsHook | ✗ | Hook de documentos pendientes. |
| hooks.shippingHook | ✗ | Hook de envío. Usado en checkout. |
| hooks.stockHook | ✗ | Hook de stock. |
| hooks.updateTrafficLightHook | ✗ | Hook de semáforo. |
| inMaintenance | ✗ | Indica si el sitio está en mantenimiento. |
| includeTaxRateInPrices | ✗ | Incluye tasa de impuesto en los precios. |
| lazyLoadingPrices | ✗ | Habilita carga perezosa de precios (async). |
| limitAddingByStock | ✗ | Limita agregar productos según stock disponible. |
| mustHaveOverride | ✗ | Requiere override de precio. |
| orderObservations | [] | Configuración de observaciones de orden. |
| ordersRequireAuthorization | ✗ | Órdenes requieren autorización. |
| ordersRequireVerification | ✗ | Órdenes requieren verificación de cuenta. |
| packagingInformation.hidePackagingInformationB2B | ✓ | Oculta info de empaque B2B. Default true. |
| packagingInformation.hideSingleItemPackagingInformationB2B | ✓ | Oculta info de empaque para items individuales B2B. Default true. |
| packagingInformation.ignoreUnitOnPackInformationB2B | ✗ | Ignora unidad en info de empaque B2B. Default false. |
| payment.balances | [] | Configuración de balances de pago. |
| payment.enableNewPaymentModule | ✓ | Habilita nuevo módulo de pagos. |
| payment.requiresFullPayment | ✗ | Requiere pago completo. |
| paymentsWithoutAccount | ✗ | Pagos sin cuenta. |
| pendingDocuments | ✗ | Habilita documentos pendientes en menú de usuario. Default false. |
| pointsEnabled | ✗ | Habilita sistema de puntos. |
| priceRoundingDecimals | 2 | Decimales para redondeo de precios. Default 0. |
| productVariability | none | No encontrado en el código. |
| purchaseOrderEnabled | ✗ | Habilita órdenes de compra. |
| shareOrderNewDesign | ✗ | No encontrado en el código. |
| shoppingDetail.lastOrder | ✗ | Muestra última orden en detalle de compra. |
| showEmptyCategories | ✗ | Muestra categorías vacías. Default false. |
| showMinOne | ✗ | Muestra mínimo uno. Info de medición en catálogo. |
| synchronization.backgroundSyncList | [] | Lista de sync en background. |
| synchronization.enableBackgroundSendOrders | ✗ | Habilita envío de órdenes en background. |
| synchronization.enableBackgroundSync | ✗ | Habilita sincronización en background. |
| synchronization.enableSyncImages | ✗ | Habilita sincronización de imágenes. |
| taxes.showSummary | ✗ | Muestra resumen de impuestos en checkout. |
| taxes.taxRate | 0 | Tasa de impuesto. |
| taxes.useTaxRate | ✗ | Usa tasa de impuestos en cálculos de precios. |
| uploadOrderFileWithMinUnits | ✗ | Permite subir archivo de orden con unidades mínimas. |
| useMobileGps | ✗ | Usa GPS del móvil. |
| useMongoPricing | ✗ | Usa pricing de MongoDB. |
| useNewPromotions | ✗ | Usa nuevo sistema de promociones. |
| validatePaymentFromAdmin | ✗ | Valida pago desde admin. |
| weightInfo | ✗ | Muestra info de peso de productos. Precio por peso en tarjetas. |

### Salesterms (yom-production)

| Variable | Valor |
|---|---|
| delivery.daysOfWeek | [] |
| order.disableOrder | ✗ |
| order.minTotalPrice | 1500 |
| order.orderTotalCreditMax | ✗ |
| order.orderTotalCreditMaxMustBlockOrder | ✗ |
| payment.paymentTypes | [{"key":"checkToDate","text":"Cheque a fecha"},{"key":"letters","text":"Letras"},{"key":"cash","text":"Efectivo"},{"key"... |
| saleConfig.noSellReasons | [] |

### Customer (yom-production)

| Variable | Valor |
|---|---|
| contactMailingList | [] |
| creditReturnStates | [] |
| currency | clp |
| domain | codelpa-peru.youorder.me |
| eventOptions.newOrderEvent | ✗ |
| mailingList | [] |
| name | Codelpa Peru |
| registerMailingList | [] |

---

## Distribuidora El Muñeco

| Dato | Valor |
|---|---|
| Dominio | elmuneco.youorder.me |
| Moneda | clp |
| CustomerId | `6852ca9cbc6123cc3fbe021f` |
| Customer legacy | ✓ El Muñeco |
| Salesterms | ✓ |

### Sites (yom-stores)

| Variable | Valor | Definición |
|---|---|---|
| anonymousAccess | ✓ | Permite acceso anónimo al sitio sin autenticación. Si es false requiere login. |
| anonymousHideCart | ✓ | Oculta el carrito para usuarios anónimos. |
| anonymousHidePrice | ✗ | Oculta los precios para usuarios anónimos. |
| blockedClientAlert.enableBlockedClientAlert | ✗ | Habilita popup de alerta cuando un cliente está bloqueado. |
| businessUnits | [] | Variable en desuso. Permitía catálogos divididos por unidad de negocio. |
| commerce.enableCreateCommerce | ✗ | Habilita el botón y flujo de creación de comercio. |
| contact.about | Distribuidora de helados, confites, congelados y bebidas. Tenemos todo para tu almacén a los precios más convenientes. | Información sobre la empresa (máx 250 chars). Mostrado en footer. |
| contact.branchesContactInformation | [{"address":"Lucila Godoy #374, Quilicura, Santiago","phone":"+56965995359","email":"elmuneco@tie.cl"}] | Info de contacto de sucursales. Usado en checkout y profile. |
| contact.email | elmuneco@tie.cl | Email de contacto. Mostrado en footer. |
| disableCart | ✗ | Deshabilita completamente el carrito de compras. |
| disableCommerceEdit | ✗ | Deshabilita edición de comercio. |
| disableObservationInput | ✗ | Deshabilita campo de observaciones en el pedido. |
| disablePayments | ✗ | Deshabilita pagos. |
| disableShowEstimatedDeliveryHour | ✗ | Oculta hora estimada de entrega. |
| discountTypes.discountTypesList | [] | Variable en desuso. Tags para descuento de vendedor. |
| discountTypes.enableOrderDiscountType | ✗ | Variable en desuso. |
| discountTypes.enableProductDiscountType | ✗ | Variable en desuso. |
| editAddress | ✓ | Permite editar dirección de envío. Default true. |
| enableAskDeliveryDate | ✗ | Habilita pregunta de fecha de entrega. |
| enableBetaButtons | ✗ | Habilita botones beta. |
| enableChooseSaleUnit | ✗ | Habilita selección de unidad de venta (B2B nuevo + app). |
| enableCoupons | ✓ | Habilita cupones de descuento. |
| enableCreditNotes | ✗ | Habilita notas de crédito. |
| enableDialogNoSellReason | ✗ | Habilita diálogo de razón de no venta. |
| enableDistributionCentersSelector | ✗ | Habilita selector de centros de distribución. |
| enableInvoicesList | ✗ | Habilita lista de facturas en menú de órdenes. |
| enableNewUI | ✗ | Habilita nueva interfaz. Siempre debería estar activa, la vieja está descontinuada. |
| enableOrderApproval | ✗ | Habilita aprobación de órdenes por vendedores. |
| enableOrderValidation | ✗ | Habilita validación de órdenes. |
| enablePaymentDocumentsB2B | ✗ | Habilita documentos de pago B2B. Botón de facturas en order-list. |
| enablePayments | ✗ | Habilita módulo de pagos. |
| enablePaymentsCollection | ✗ | Habilita módulo de cobranza. disablePayments la desactiva. |
| enablePriceOracle | ✗ | Habilita precios futuros (oracle). Obtiene fecha de entrega antes de cargar precios. |
| enableSellerDiscount | ✗ | Permite que el vendedor haga descuentos. |
| enableTask | ✗ | Habilita gestor de tareas. |
| externalAccess | ✗ | Permite acceso externo. |
| filterGroupedSuggestionsBy | [] | Define campo para filtrar sugerencias agrupadas (ej: packaging.amountPerPackage). |
| footerCustomContent.useFooterCustomContent | ✗ | Habilita contenido personalizado en footer. |
| hasAllDistributionCenters | ✗ | Si stock es multicentro, asigna todos los centros a todos los comercios. |
| hasMultiUnitEnabled | ✗ | Habilita múltiples unidades. |
| hasMultipleBusinessUnit | ✗ | En desuso. |
| hasNoSaleFilter | ✗ | Habilita filtro de no venta. |
| hasSingleDistributionCenter | ✓ | Con stock, indica si comercios tienen un solo centro de distribución. Si true, stock se ve directo en tarjeta. Si false, botón 'ver stock' muestra todos los centros. |
| hasStockEnabled | ✓ | Indica si hay o no stock. |
| hasTransferPaymentType | ✗ | Habilita tipo de pago por transferencia. |
| hasTransportCode | ✗ | Variable de nicho para softys-cencocal. |
| hasVoucherPrinterEnabled | ✗ | Habilita impresora de voucher. |
| hidePrices | ✗ | Oculta todos los precios del sitio. |
| hideReceiptType | ✗ | Oculta tipo de recibo en checkout. |
| hooks.cartShoppingHook | ✗ | Hook de carrito de compras. |
| hooks.getPendingDocumentsHook | ✗ | Hook de documentos pendientes. |
| hooks.shippingHook | ✗ | Hook de envío. Usado en checkout. |
| hooks.stockHook | ✗ | Hook de stock. |
| hooks.updateTrafficLightHook | ✗ | Hook de semáforo. |
| inMaintenance | ✗ | Indica si el sitio está en mantenimiento. |
| includeTaxRateInPrices | ✓ | Incluye tasa de impuesto en los precios. |
| lazyLoadingPrices | ✗ | Habilita carga perezosa de precios (async). |
| limitAddingByStock | ✗ | Limita agregar productos según stock disponible. |
| ordersRequireAuthorization | ✗ | Órdenes requieren autorización. |
| ordersRequireVerification | ✗ | Órdenes requieren verificación de cuenta. |
| packagingInformation.hidePackagingInformationB2B | ✓ | Oculta info de empaque B2B. Default true. |
| packagingInformation.hideSingleItemPackagingInformationB2B | ✓ | Oculta info de empaque para items individuales B2B. Default true. |
| packagingInformation.ignoreUnitOnPackInformationB2B | ✗ | Ignora unidad en info de empaque B2B. Default false. |
| payment.balances | [] | Configuración de balances de pago. |
| payment.enableNewPaymentModule | ✗ | Habilita nuevo módulo de pagos. |
| payment.requiresFullPayment | ✗ | Requiere pago completo. |
| paymentsWithoutAccount | ✗ | Pagos sin cuenta. |
| pendingDocuments | ✗ | Habilita documentos pendientes en menú de usuario. Default false. |
| pointsEnabled | ✗ | Habilita sistema de puntos. |
| priceRoundingDecimals | 0 | Decimales para redondeo de precios. Default 0. |
| productVariability | none | No encontrado en el código. |
| purchaseOrderEnabled | ✗ | Habilita órdenes de compra. |
| shareOrderNewDesign | ✗ | No encontrado en el código. |
| shoppingDetail.lastOrder | ✗ | Muestra última orden en detalle de compra. |
| showEmptyCategories | ✗ | Muestra categorías vacías. Default false. |
| showMinOne | ✗ | Muestra mínimo uno. Info de medición en catálogo. |
| synchronization.backgroundSyncList | [] | Lista de sync en background. |
| synchronization.enableBackgroundSendOrders | ✗ | Habilita envío de órdenes en background. |
| synchronization.enableBackgroundSync | ✗ | Habilita sincronización en background. |
| synchronization.enableSyncImages | ✗ | Habilita sincronización de imágenes. |
| taxes.showSummary | ✗ | Muestra resumen de impuestos en checkout. |
| taxes.taxRate | 0 | Tasa de impuesto. |
| taxes.useTaxRate | ✓ | Usa tasa de impuestos en cálculos de precios. |
| uploadOrderFileWithMinUnits | ✗ | Permite subir archivo de orden con unidades mínimas. |
| useMobileGps | ✗ | Usa GPS del móvil. |
| useMongoPricing | ✗ | Usa pricing de MongoDB. |
| validatePaymentFromAdmin | ✗ | Valida pago desde admin. |
| weightInfo | ✗ | Muestra info de peso de productos. Precio por peso en tarjetas. |

### Salesterms (yom-production)

| Variable | Valor |
|---|---|
| coverage.text | Envíos a Quilicura, Renca, Cerro Navia, Lo Prado, Pudahuel, Independencia, Conchali, Huechuraba, Recoleta, Lampa y Colina |
| delivery.daysOfWeek | ["monday","tuesday","wednesday","thursday","friday"] |
| delivery.fromHours | 32400 |
| delivery.text | Despachamos de 24 a 48 horas hábiles |
| delivery.toHours | 66600 |
| order.disableOrder | ✗ |
| order.maxProducts | 20 |
| order.minTotalPrice | 15000 |
| order.orderTotalCreditMax | ✗ |
| order.orderTotalCreditMaxMustBlockOrder | ✗ |
| order.text | Despacho gratis sobre $20.000 |
| payment.paymentTypes | [] |
| saleConfig.noSellReasons | [] |

### Customer (yom-production)

| Variable | Valor |
|---|---|
| contactMailingList | [] |
| currency | clp |
| domain | elmuneco.youorder.me |
| eventOptions.newOrderEvent | ✗ |
| integrationHooks.createOrderHook | https://api.youorder.me/hooks/elmuneco/create-order |
| mailingList | [] |
| name | El Muñeco |
| registerMailingList | [] |

---

## ExpressDent

| Dato | Valor |
|---|---|
| Dominio | expressdent.youorder.me |
| Moneda | clp |
| CustomerId | `67c9bf57d4ace772b8e3b11e` |
| Customer legacy | ✓ ExpressDent |
| Salesterms | ✓ |

### Sites (yom-stores)

| Variable | Valor | Definición |
|---|---|---|
| anonymousAccess | ✗ | Permite acceso anónimo al sitio sin autenticación. Si es false requiere login. |
| anonymousHideCart | ✓ | Oculta el carrito para usuarios anónimos. |
| anonymousHidePrice | ✗ | Oculta los precios para usuarios anónimos. |
| blockedClientAlert.enableBlockedClientAlert | ✗ | Habilita popup de alerta cuando un cliente está bloqueado. |
| businessUnits | [] | Variable en desuso. Permitía catálogos divididos por unidad de negocio. |
| commerce.enableCreateCommerce | ✗ | Habilita el botón y flujo de creación de comercio. |
| contact.about | Una solución integral para el dentista | Información sobre la empresa (máx 250 chars). Mostrado en footer. |
| contact.branchesContactInformation | [{"address":"Av. Presidente Errázuriz 4125, Las Condes, Santiago, Chile","phone":"Fijo: +562 4367 1570  -  Whatsapp: +56... | Info de contacto de sucursales. Usado en checkout y profile. |
| contact.email | contacto@expressdent.cl | Email de contacto. Mostrado en footer. |
| disableCart | ✗ | Deshabilita completamente el carrito de compras. |
| disableCommerceEdit | ✗ | Deshabilita edición de comercio. |
| disableObservationInput | ✗ | Deshabilita campo de observaciones en el pedido. |
| disablePayments | ✗ | Deshabilita pagos. |
| disableShowEstimatedDeliveryHour | ✗ | Oculta hora estimada de entrega. |
| discountTypes.discountTypesList | [] | Variable en desuso. Tags para descuento de vendedor. |
| discountTypes.enableOrderDiscountType | ✗ | Variable en desuso. |
| discountTypes.enableProductDiscountType | ✗ | Variable en desuso. |
| editAddress | ✓ | Permite editar dirección de envío. Default true. |
| enableAskDeliveryDate | ✗ | Habilita pregunta de fecha de entrega. |
| enableBetaButtons | ✗ | Habilita botones beta. |
| enableChooseSaleUnit | ✗ | Habilita selección de unidad de venta (B2B nuevo + app). |
| enableCoupons | ✓ | Habilita cupones de descuento. |
| enableCreditNotes | ✗ | Habilita notas de crédito. |
| enableDialogNoSellReason | ✗ | Habilita diálogo de razón de no venta. |
| enableDistributionCentersSelector | ✗ | Habilita selector de centros de distribución. |
| enableInvoicesList | ✗ | Habilita lista de facturas en menú de órdenes. |
| enableNewUI | ✗ | Habilita nueva interfaz. Siempre debería estar activa, la vieja está descontinuada. |
| enableOrderApproval | ✗ | Habilita aprobación de órdenes por vendedores. |
| enableOrderValidation | ✗ | Habilita validación de órdenes. |
| enablePaymentDocumentsB2B | ✗ | Habilita documentos de pago B2B. Botón de facturas en order-list. |
| enablePayments | ✗ | Habilita módulo de pagos. |
| enablePaymentsCollection | ✗ | Habilita módulo de cobranza. disablePayments la desactiva. |
| enablePriceOracle | ✗ | Habilita precios futuros (oracle). Obtiene fecha de entrega antes de cargar precios. |
| enableSellerDiscount | ✗ | Permite que el vendedor haga descuentos. |
| enableTask | ✗ | Habilita gestor de tareas. |
| externalAccess | ✗ | Permite acceso externo. |
| filterGroupedSuggestionsBy | [] | Define campo para filtrar sugerencias agrupadas (ej: packaging.amountPerPackage). |
| footerCustomContent.useFooterCustomContent | ✗ | Habilita contenido personalizado en footer. |
| hasAllDistributionCenters | ✗ | Si stock es multicentro, asigna todos los centros a todos los comercios. |
| hasMultiUnitEnabled | ✗ | Habilita múltiples unidades. |
| hasMultipleBusinessUnit | ✗ | En desuso. |
| hasNoSaleFilter | ✗ | Habilita filtro de no venta. |
| hasSingleDistributionCenter | ✓ | Con stock, indica si comercios tienen un solo centro de distribución. Si true, stock se ve directo en tarjeta. Si false, botón 'ver stock' muestra todos los centros. |
| hasStockEnabled | ✗ | Indica si hay o no stock. |
| hasTransferPaymentType | ✗ | Habilita tipo de pago por transferencia. |
| hasTransportCode | ✗ | Variable de nicho para softys-cencocal. |
| hasVoucherPrinterEnabled | ✗ | Habilita impresora de voucher. |
| hidePrices | ✗ | Oculta todos los precios del sitio. |
| hideReceiptType | ✗ | Oculta tipo de recibo en checkout. |
| hooks.cartShoppingHook | ✗ | Hook de carrito de compras. |
| hooks.getPendingDocumentsHook | ✗ | Hook de documentos pendientes. |
| hooks.shippingHook | ✗ | Hook de envío. Usado en checkout. |
| hooks.stockHook | ✗ | Hook de stock. |
| hooks.updateTrafficLightHook | ✗ | Hook de semáforo. |
| inMaintenance | ✗ | Indica si el sitio está en mantenimiento. |
| includeTaxRateInPrices | ✓ | Incluye tasa de impuesto en los precios. |
| lazyLoadingPrices | ✗ | Habilita carga perezosa de precios (async). |
| limitAddingByStock | ✗ | Limita agregar productos según stock disponible. |
| ordersRequireAuthorization | ✗ | Órdenes requieren autorización. |
| ordersRequireVerification | ✗ | Órdenes requieren verificación de cuenta. |
| packagingInformation.hidePackagingInformationB2B | ✓ | Oculta info de empaque B2B. Default true. |
| packagingInformation.hideSingleItemPackagingInformationB2B | ✓ | Oculta info de empaque para items individuales B2B. Default true. |
| packagingInformation.ignoreUnitOnPackInformationB2B | ✗ | Ignora unidad en info de empaque B2B. Default false. |
| payment.balances | [] | Configuración de balances de pago. |
| payment.enableNewPaymentModule | ✗ | Habilita nuevo módulo de pagos. |
| payment.externalPayment | khipu | Habilita pago externo. |
| payment.requiresFullPayment | ✗ | Requiere pago completo. |
| paymentsWithoutAccount | ✗ | Pagos sin cuenta. |
| pendingDocuments | ✗ | Habilita documentos pendientes en menú de usuario. Default false. |
| pointsEnabled | ✗ | Habilita sistema de puntos. |
| priceRoundingDecimals | 0 | Decimales para redondeo de precios. Default 0. |
| productVariability | full | No encontrado en el código. |
| purchaseOrderEnabled | ✗ | Habilita órdenes de compra. |
| shareOrderNewDesign | ✗ | No encontrado en el código. |
| shoppingDetail.lastOrder | ✗ | Muestra última orden en detalle de compra. |
| showEmptyCategories | ✗ | Muestra categorías vacías. Default false. |
| showMinOne | ✗ | Muestra mínimo uno. Info de medición en catálogo. |
| synchronization.backgroundSyncList | [] | Lista de sync en background. |
| synchronization.enableBackgroundSendOrders | ✗ | Habilita envío de órdenes en background. |
| synchronization.enableBackgroundSync | ✗ | Habilita sincronización en background. |
| synchronization.enableSyncImages | ✗ | Habilita sincronización de imágenes. |
| taxes.showSummary | ✓ | Muestra resumen de impuestos en checkout. |
| taxes.taxRate | 0 | Tasa de impuesto. |
| taxes.useTaxRate | ✓ | Usa tasa de impuestos en cálculos de precios. |
| uploadOrderFileWithMinUnits | ✗ | Permite subir archivo de orden con unidades mínimas. |
| useMobileGps | ✗ | Usa GPS del móvil. |
| useMongoPricing | ✗ | Usa pricing de MongoDB. |
| useNewPromotions | ✓ | Usa nuevo sistema de promociones. |
| validatePaymentFromAdmin | ✗ | Valida pago desde admin. |
| weightInfo | ✗ | Muestra info de peso de productos. Precio por peso en tarjetas. |

### Salesterms (yom-production)

| Variable | Valor |
|---|---|
| coverage.text | Envíos a todo Chile |
| delivery.daysOfWeek | ["monday","tuesday","wednesday","thursday","friday"] |
| delivery.fromHours | 32400 |
| delivery.text | Región Metropolitana desde 48-72 hrs; Regiones desde 72 hrs |
| delivery.toHours | 66600 |
| order.disableOrder | ✗ |
| order.orderTotalCreditMax | ✓ |
| order.orderTotalCreditMaxMustBlockOrder | ✗ |
| order.orderTotalCreditMaxText | Pedido supera el saldo disponible, por favor disminuya su orden o libere crédito |
| order.text | Región Metropolitana: despacho $7.000 + iva y sobre $70.000 gratis - - - - - - - - - - - - Otras Regiones: despacho $11.000 + iva y sobre $100.000 gratis - - - - - - - - - - - - Regiones Extremas (Arica, Tarapacá, Antofagasta, Atacama, Aysén, Magallanes):     despacho con envío por pagar y sobre $200.000 gratis |
| payment.paymentTypes | [] |
| saleConfig.noSellReasons | [] |

### Customer (yom-production)

| Variable | Valor |
|---|---|
| contactMailingList | ["contacto@expressdent.cl"] |
| currency | clp |
| domain | expressdent.youorder.me |
| eventOptions.newOrderEvent | ✗ |
| integrationHooks.createOrderHook | https://api.solopide.me/hooks/expressdent/create-order |
| mailingList | [] |
| name | ExpressDent |
| registerMailingList | ["contacto@expressdent.cl"] |

---

## Las Américas

| Dato | Valor |
|---|---|
| Dominio | americas.youorder.me |
| Moneda | clp |
| CustomerId | `69173273a1ab64ebab565653` |
| Customer legacy | ✓ Americas |
| Salesterms | ✓ |

### Sites (yom-stores)

| Variable | Valor | Definición |
|---|---|---|
| anonymousAccess | ✗ | Permite acceso anónimo al sitio sin autenticación. Si es false requiere login. |
| anonymousHideCart | ✗ | Oculta el carrito para usuarios anónimos. |
| anonymousHidePrice | ✗ | Oculta los precios para usuarios anónimos. |
| blockedClientAlert.enableBlockedClientAlert | ✗ | Habilita popup de alerta cuando un cliente está bloqueado. |
| businessUnits | [] | Variable en desuso. Permitía catálogos divididos por unidad de negocio. |
| commerce.enableCreateCommerce | ✗ | Habilita el botón y flujo de creación de comercio. |
| disableCart | ✗ | Deshabilita completamente el carrito de compras. |
| disableCommerceEdit | ✗ | Deshabilita edición de comercio. |
| disableObservationInput | ✗ | Deshabilita campo de observaciones en el pedido. |
| disablePayments | ✓ | Deshabilita pagos. |
| disableShowEstimatedDeliveryHour | ✗ | Oculta hora estimada de entrega. |
| discountTypes.discountTypesList | [] | Variable en desuso. Tags para descuento de vendedor. |
| discountTypes.enableOrderDiscountType | ✗ | Variable en desuso. |
| discountTypes.enableProductDiscountType | ✗ | Variable en desuso. |
| editAddress | ✓ | Permite editar dirección de envío. Default true. |
| enableAskDeliveryDate | ✗ | Habilita pregunta de fecha de entrega. |
| enableBetaButtons | ✗ | Habilita botones beta. |
| enableChooseSaleUnit | ✗ | Habilita selección de unidad de venta (B2B nuevo + app). |
| enableCoupons | ✓ | Habilita cupones de descuento. |
| enableCreditNotes | ✗ | Habilita notas de crédito. |
| enableDialogNoSellReason | ✗ | Habilita diálogo de razón de no venta. |
| enableDistributionCentersSelector | ✗ | Habilita selector de centros de distribución. |
| enableInvoicesList | ✗ | Habilita lista de facturas en menú de órdenes. |
| enableNewUI | ✗ | Habilita nueva interfaz. Siempre debería estar activa, la vieja está descontinuada. |
| enableOrderApproval | ✗ | Habilita aprobación de órdenes por vendedores. |
| enableOrderValidation | ✗ | Habilita validación de órdenes. |
| enablePaymentDocumentsB2B | ✗ | Habilita documentos de pago B2B. Botón de facturas en order-list. |
| enablePayments | ✗ | Habilita módulo de pagos. |
| enablePaymentsCollection | ✗ | Habilita módulo de cobranza. disablePayments la desactiva. |
| enablePriceOracle | ✗ | Habilita precios futuros (oracle). Obtiene fecha de entrega antes de cargar precios. |
| enableSellerDiscount | ✗ | Permite que el vendedor haga descuentos. |
| enableTask | ✗ | Habilita gestor de tareas. |
| externalAccess | ✗ | Permite acceso externo. |
| filterGroupedSuggestionsBy | [] | Define campo para filtrar sugerencias agrupadas (ej: packaging.amountPerPackage). |
| footerCustomContent.useFooterCustomContent | ✗ | Habilita contenido personalizado en footer. |
| hasAllDistributionCenters | ✗ | Si stock es multicentro, asigna todos los centros a todos los comercios. |
| hasMultiUnitEnabled | ✗ | Habilita múltiples unidades. |
| hasMultipleBusinessUnit | ✗ | En desuso. |
| hasNoSaleFilter | ✗ | Habilita filtro de no venta. |
| hasSingleDistributionCenter | ✓ | Con stock, indica si comercios tienen un solo centro de distribución. Si true, stock se ve directo en tarjeta. Si false, botón 'ver stock' muestra todos los centros. |
| hasStockEnabled | ✗ | Indica si hay o no stock. |
| hasTransferPaymentType | ✗ | Habilita tipo de pago por transferencia. |
| hasTransportCode | ✗ | Variable de nicho para softys-cencocal. |
| hasVoucherPrinterEnabled | ✗ | Habilita impresora de voucher. |
| hidePrices | ✗ | Oculta todos los precios del sitio. |
| hideReceiptType | ✗ | Oculta tipo de recibo en checkout. |
| hooks.cartShoppingHook | ✗ | Hook de carrito de compras. |
| hooks.getPendingDocumentsHook | ✗ | Hook de documentos pendientes. |
| hooks.shippingHook | ✗ | Hook de envío. Usado en checkout. |
| hooks.stockHook | ✗ | Hook de stock. |
| hooks.updateTrafficLightHook | ✗ | Hook de semáforo. |
| inMaintenance | ✗ | Indica si el sitio está en mantenimiento. |
| includeTaxRateInPrices | ✗ | Incluye tasa de impuesto en los precios. |
| lazyLoadingPrices | ✗ | Habilita carga perezosa de precios (async). |
| limitAddingByStock | ✗ | Limita agregar productos según stock disponible. |
| orderObservations | [] | Configuración de observaciones de orden. |
| ordersRequireAuthorization | ✗ | Órdenes requieren autorización. |
| ordersRequireVerification | ✗ | Órdenes requieren verificación de cuenta. |
| packagingInformation.hidePackagingInformationB2B | ✓ | Oculta info de empaque B2B. Default true. |
| packagingInformation.hideSingleItemPackagingInformationB2B | ✓ | Oculta info de empaque para items individuales B2B. Default true. |
| packagingInformation.ignoreUnitOnPackInformationB2B | ✗ | Ignora unidad en info de empaque B2B. Default false. |
| payment.balances | [] | Configuración de balances de pago. |
| payment.enableNewPaymentModule | ✗ | Habilita nuevo módulo de pagos. |
| payment.requiresFullPayment | ✗ | Requiere pago completo. |
| paymentsWithoutAccount | ✗ | Pagos sin cuenta. |
| pendingDocuments | ✗ | Habilita documentos pendientes en menú de usuario. Default false. |
| pointsEnabled | ✗ | Habilita sistema de puntos. |
| priceRoundingDecimals | 0 | Decimales para redondeo de precios. Default 0. |
| productVariability | none | No encontrado en el código. |
| purchaseOrderEnabled | ✗ | Habilita órdenes de compra. |
| shareOrderNewDesign | ✗ | No encontrado en el código. |
| shoppingDetail.lastOrder | ✗ | Muestra última orden en detalle de compra. |
| showEmptyCategories | ✗ | Muestra categorías vacías. Default false. |
| showMinOne | ✗ | Muestra mínimo uno. Info de medición en catálogo. |
| synchronization.backgroundSyncList | [] | Lista de sync en background. |
| synchronization.enableBackgroundSendOrders | ✗ | Habilita envío de órdenes en background. |
| synchronization.enableBackgroundSync | ✗ | Habilita sincronización en background. |
| synchronization.enableSyncImages | ✗ | Habilita sincronización de imágenes. |
| taxes.showSummary | ✗ | Muestra resumen de impuestos en checkout. |
| taxes.taxRate | 0 | Tasa de impuesto. |
| taxes.useTaxRate | ✗ | Usa tasa de impuestos en cálculos de precios. |
| uploadOrderFileWithMinUnits | ✗ | Permite subir archivo de orden con unidades mínimas. |
| useMobileGps | ✗ | Usa GPS del móvil. |
| useMongoPricing | ✗ | Usa pricing de MongoDB. |
| useNewPromotions | ✗ | Usa nuevo sistema de promociones. |
| validatePaymentFromAdmin | ✗ | Valida pago desde admin. |
| weightInfo | ✗ | Muestra info de peso de productos. Precio por peso en tarjetas. |

### Salesterms (yom-production)

| Variable | Valor |
|---|---|
| delivery.daysOfWeek | [] |
| order.disableOrder | ✗ |
| order.orderTotalCreditMax | ✗ |
| order.orderTotalCreditMaxMustBlockOrder | ✗ |
| payment.paymentTypes | [] |
| saleConfig.noSellReasons | [] |

### Customer (yom-production)

| Variable | Valor |
|---|---|
| contactMailingList | [] |
| creditReturnStates | [] |
| currency | cop |
| domain | americas.youorder.me |
| eventOptions.newOrderEvent | ✗ |
| integrationHooks.createOrderHook | https://api.youorder.me/hooks/globalwines/create-order |
| mailingList | [] |
| name | Americas |
| registerMailingList | [] |

---

## Marley Coffee

| Dato | Valor |
|---|---|
| Dominio | marleycoffee.youorder.me |
| Moneda | clp |
| CustomerId | `681f80e3d6f3750b04604dd2` |
| Customer legacy | ✓ Marley Coffee |
| Salesterms | ✓ |

### Sites (yom-stores)

| Variable | Valor | Definición |
|---|---|---|
| anonymousAccess | ✗ | Permite acceso anónimo al sitio sin autenticación. Si es false requiere login. |
| anonymousHideCart | ✗ | Oculta el carrito para usuarios anónimos. |
| anonymousHidePrice | ✗ | Oculta los precios para usuarios anónimos. |
| blockedClientAlert.enableBlockedClientAlert | ✗ | Habilita popup de alerta cuando un cliente está bloqueado. |
| businessUnits | [] | Variable en desuso. Permitía catálogos divididos por unidad de negocio. |
| commerce.enableCreateCommerce | ✗ | Habilita el botón y flujo de creación de comercio. |
| contact.about | La principal marca cafetera orgánica del mundo, siempre respetando el legado de Bob Marley, manifestándolo en cada taza. | Información sobre la empresa (máx 250 chars). Mostrado en footer. |
| contact.branchesContactInformation | [{"phone":"+56998946436","email":"servicioalcliente@marleycoffee.cl"}] | Info de contacto de sucursales. Usado en checkout y profile. |
| contact.email | servicioalcliente@marleycoffee.cl | Email de contacto. Mostrado en footer. |
| disableCart | ✗ | Deshabilita completamente el carrito de compras. |
| disableCommerceEdit | ✗ | Deshabilita edición de comercio. |
| disableObservationInput | ✗ | Deshabilita campo de observaciones en el pedido. |
| disablePayments | ✗ | Deshabilita pagos. |
| disableShowEstimatedDeliveryHour | ✗ | Oculta hora estimada de entrega. |
| discountTypes.discountTypesList | [] | Variable en desuso. Tags para descuento de vendedor. |
| discountTypes.enableOrderDiscountType | ✗ | Variable en desuso. |
| discountTypes.enableProductDiscountType | ✗ | Variable en desuso. |
| editAddress | ✓ | Permite editar dirección de envío. Default true. |
| enableAskDeliveryDate | ✗ | Habilita pregunta de fecha de entrega. |
| enableBetaButtons | ✗ | Habilita botones beta. |
| enableChooseSaleUnit | ✗ | Habilita selección de unidad de venta (B2B nuevo + app). |
| enableCoupons | ✓ | Habilita cupones de descuento. |
| enableCreditNotes | ✗ | Habilita notas de crédito. |
| enableDialogNoSellReason | ✗ | Habilita diálogo de razón de no venta. |
| enableDistributionCentersSelector | ✗ | Habilita selector de centros de distribución. |
| enableInvoicesList | ✗ | Habilita lista de facturas en menú de órdenes. |
| enableNewUI | ✗ | Habilita nueva interfaz. Siempre debería estar activa, la vieja está descontinuada. |
| enableOrderApproval | ✗ | Habilita aprobación de órdenes por vendedores. |
| enableOrderValidation | ✗ | Habilita validación de órdenes. |
| enablePaymentDocumentsB2B | ✗ | Habilita documentos de pago B2B. Botón de facturas en order-list. |
| enablePayments | ✗ | Habilita módulo de pagos. |
| enablePaymentsCollection | ✗ | Habilita módulo de cobranza. disablePayments la desactiva. |
| enablePriceOracle | ✗ | Habilita precios futuros (oracle). Obtiene fecha de entrega antes de cargar precios. |
| enableSellerDiscount | ✗ | Permite que el vendedor haga descuentos. |
| enableTask | ✗ | Habilita gestor de tareas. |
| externalAccess | ✗ | Permite acceso externo. |
| filterGroupedSuggestionsBy | [] | Define campo para filtrar sugerencias agrupadas (ej: packaging.amountPerPackage). |
| footerCustomContent.useFooterCustomContent | ✗ | Habilita contenido personalizado en footer. |
| hasAllDistributionCenters | ✗ | Si stock es multicentro, asigna todos los centros a todos los comercios. |
| hasMultiUnitEnabled | ✗ | Habilita múltiples unidades. |
| hasMultipleBusinessUnit | ✗ | En desuso. |
| hasNoSaleFilter | ✗ | Habilita filtro de no venta. |
| hasSingleDistributionCenter | ✓ | Con stock, indica si comercios tienen un solo centro de distribución. Si true, stock se ve directo en tarjeta. Si false, botón 'ver stock' muestra todos los centros. |
| hasStockEnabled | ✗ | Indica si hay o no stock. |
| hasTransferPaymentType | ✗ | Habilita tipo de pago por transferencia. |
| hasTransportCode | ✗ | Variable de nicho para softys-cencocal. |
| hasVoucherPrinterEnabled | ✗ | Habilita impresora de voucher. |
| hidePrices | ✗ | Oculta todos los precios del sitio. |
| hideReceiptType | ✗ | Oculta tipo de recibo en checkout. |
| hooks.cartShoppingHook | ✗ | Hook de carrito de compras. |
| hooks.getPendingDocumentsHook | ✗ | Hook de documentos pendientes. |
| hooks.shippingHook | ✗ | Hook de envío. Usado en checkout. |
| hooks.stockHook | ✗ | Hook de stock. |
| hooks.updateTrafficLightHook | ✗ | Hook de semáforo. |
| inMaintenance | ✗ | Indica si el sitio está en mantenimiento. |
| includeTaxRateInPrices | ✗ | Incluye tasa de impuesto en los precios. |
| lazyLoadingPrices | ✗ | Habilita carga perezosa de precios (async). |
| limitAddingByStock | ✗ | Limita agregar productos según stock disponible. |
| ordersRequireAuthorization | ✗ | Órdenes requieren autorización. |
| ordersRequireVerification | ✗ | Órdenes requieren verificación de cuenta. |
| packagingInformation.hidePackagingInformationB2B | ✓ | Oculta info de empaque B2B. Default true. |
| packagingInformation.hideSingleItemPackagingInformationB2B | ✓ | Oculta info de empaque para items individuales B2B. Default true. |
| packagingInformation.ignoreUnitOnPackInformationB2B | ✗ | Ignora unidad en info de empaque B2B. Default false. |
| payment.balances | [] | Configuración de balances de pago. |
| payment.enableNewPaymentModule | ✗ | Habilita nuevo módulo de pagos. |
| payment.externalPayment | khipu | Habilita pago externo. |
| payment.requiresFullPayment | ✗ | Requiere pago completo. |
| paymentsWithoutAccount | ✗ | Pagos sin cuenta. |
| pendingDocuments | ✗ | Habilita documentos pendientes en menú de usuario. Default false. |
| pointsEnabled | ✗ | Habilita sistema de puntos. |
| priceRoundingDecimals | 0 | Decimales para redondeo de precios. Default 0. |
| productVariability | none | No encontrado en el código. |
| purchaseOrderEnabled | ✗ | Habilita órdenes de compra. |
| shareOrderNewDesign | ✗ | No encontrado en el código. |
| shoppingDetail.lastOrder | ✗ | Muestra última orden en detalle de compra. |
| showEmptyCategories | ✗ | Muestra categorías vacías. Default false. |
| showMinOne | ✗ | Muestra mínimo uno. Info de medición en catálogo. |
| synchronization.backgroundSyncList | [] | Lista de sync en background. |
| synchronization.enableBackgroundSendOrders | ✗ | Habilita envío de órdenes en background. |
| synchronization.enableBackgroundSync | ✗ | Habilita sincronización en background. |
| synchronization.enableSyncImages | ✗ | Habilita sincronización de imágenes. |
| taxes.showSummary | ✗ | Muestra resumen de impuestos en checkout. |
| taxes.taxRate | 0 | Tasa de impuesto. |
| taxes.useTaxRate | ✗ | Usa tasa de impuestos en cálculos de precios. |
| uploadOrderFileWithMinUnits | ✗ | Permite subir archivo de orden con unidades mínimas. |
| useMobileGps | ✗ | Usa GPS del móvil. |
| useMongoPricing | ✗ | Usa pricing de MongoDB. |
| validatePaymentFromAdmin | ✗ | Valida pago desde admin. |
| weightInfo | ✗ | Muestra info de peso de productos. Precio por peso en tarjetas. |

### Salesterms (yom-production)

| Variable | Valor |
|---|---|
| coverage.text | Todo Chile con excepción de las regiones de Aysén del General Carlos Ibáñez del Campo y de Magallanes y de la Antártica Chilena, junto con Isla de Pascua (contactar a distribuidor de la zona) |
| delivery.daysOfWeek | ["monday","tuesday","wednesday","thursday","friday"] |
| delivery.fromHours | 32400 |
| delivery.text | Tiempos de entrega varían según ubicación, consulte los términos y condiciones |
| delivery.toHours | 66600 |
| order.disableOrder | ✗ |
| order.orderTotalCreditMax | ✓ |
| order.orderTotalCreditMaxMustBlockOrder | ✓ |
| order.text | Costos de despacho varían según ubicación, consulte los términos y condiciones o revise su carrito de compras para más información |
| payment.paymentTypes | [{"key":"cash","text":"Efectivo"},{"key":"check","text":"Cheque"},{"key":"transfer","text":"Transferencia"}] |
| saleConfig.noSellReasons | [] |

### Customer (yom-production)

| Variable | Valor |
|---|---|
| contactMailingList | [] |
| currency | clp |
| domain | marleycoffee.youorder.me |
| eventOptions.newOrderEvent | ✗ |
| integrationHooks.createOrderHook | https://api.youorder.me/hooks/marleycoffee/create-order |
| mailingList | [] |
| name | Marley Coffee |
| registerMailingList | [] |

---

## Prinorte Store

| Dato | Valor |
|---|---|
| Dominio | prinorte.youorder.me |
| Moneda | clp |
| CustomerId | `699f0b74fb3f3677f2b34abe` |
| Customer legacy | ✓ Prinorte |
| Salesterms | ✓ |

### Sites (yom-stores)

| Variable | Valor | Definición |
|---|---|---|
| anonymousAccess | ✗ | Permite acceso anónimo al sitio sin autenticación. Si es false requiere login. |
| anonymousHideCart | ✓ | Oculta el carrito para usuarios anónimos. |
| anonymousHidePrice | ✗ | Oculta los precios para usuarios anónimos. |
| blockedClientAlert.enableBlockedClientAlert | ✗ | Habilita popup de alerta cuando un cliente está bloqueado. |
| businessUnits | [] | Variable en desuso. Permitía catálogos divididos por unidad de negocio. |
| commerce.enableCreateCommerce | ✓ | Habilita el botón y flujo de creación de comercio. |
| contact.about | Surtiventas opera con el claro propósito de satisfacer las necesidades básicas del comerciante chileno, con un servicio personalizado de venta que se extiende a lo largo y ancho del país. | Información sobre la empresa (máx 250 chars). Mostrado en footer. |
| contact.branchesContactInformation | [{"phone":"+562 2820 6400","email":"srvcliente1@surtiventas.cl"}] | Info de contacto de sucursales. Usado en checkout y profile. |
| contact.email | srvcliente1@surtiventas.cl | Email de contacto. Mostrado en footer. |
| disableCart | ✗ | Deshabilita completamente el carrito de compras. |
| disableCommerceEdit | ✗ | Deshabilita edición de comercio. |
| disableObservationInput | ✗ | Deshabilita campo de observaciones en el pedido. |
| disablePayments | ✗ | Deshabilita pagos. |
| disableShowEstimatedDeliveryHour | ✗ | Oculta hora estimada de entrega. |
| discountTypes.discountTypesList | [] | Variable en desuso. Tags para descuento de vendedor. |
| discountTypes.enableOrderDiscountType | ✗ | Variable en desuso. |
| discountTypes.enableProductDiscountType | ✗ | Variable en desuso. |
| editAddress | ✓ | Permite editar dirección de envío. Default true. |
| enableAskDeliveryDate | ✗ | Habilita pregunta de fecha de entrega. |
| enableBetaButtons | ✗ | Habilita botones beta. |
| enableChooseSaleUnit | ✓ | Habilita selección de unidad de venta (B2B nuevo + app). |
| enableCoupons | ✓ | Habilita cupones de descuento. |
| enableCreditNotes | ✗ | Habilita notas de crédito. |
| enableDialogNoSellReason | ✗ | Habilita diálogo de razón de no venta. |
| enableDistributionCentersSelector | ✗ | Habilita selector de centros de distribución. |
| enableInvoicesList | ✗ | Habilita lista de facturas en menú de órdenes. |
| enableMassiveOrderSend | ✓ | Permite enviar órdenes pendientes de forma masiva. |
| enableNewUI | ✗ | Habilita nueva interfaz. Siempre debería estar activa, la vieja está descontinuada. |
| enableOrderApproval | ✗ | Habilita aprobación de órdenes por vendedores. |
| enableOrderValidation | ✗ | Habilita validación de órdenes. |
| enablePaymentDocumentsB2B | ✗ | Habilita documentos de pago B2B. Botón de facturas en order-list. |
| enablePayments | ✗ | Habilita módulo de pagos. |
| enablePaymentsCollection | ✗ | Habilita módulo de cobranza. disablePayments la desactiva. |
| enablePriceOracle | ✗ | Habilita precios futuros (oracle). Obtiene fecha de entrega antes de cargar precios. |
| enableSellerDiscount | ✓ | Permite que el vendedor haga descuentos. |
| enableTask | ✗ | Habilita gestor de tareas. |
| externalAccess | ✗ | Permite acceso externo. |
| filterGroupedSuggestionsBy | [] | Define campo para filtrar sugerencias agrupadas (ej: packaging.amountPerPackage). |
| footerCustomContent.useFooterCustomContent | ✗ | Habilita contenido personalizado en footer. |
| hasAllDistributionCenters | ✗ | Si stock es multicentro, asigna todos los centros a todos los comercios. |
| hasMultiUnitEnabled | ✓ | Habilita múltiples unidades. |
| hasMultipleBusinessUnit | ✗ | En desuso. |
| hasNoSaleFilter | ✓ | Habilita filtro de no venta. |
| hasSingleDistributionCenter | ✓ | Con stock, indica si comercios tienen un solo centro de distribución. Si true, stock se ve directo en tarjeta. Si false, botón 'ver stock' muestra todos los centros. |
| hasStockEnabled | ✓ | Indica si hay o no stock. |
| hasTransferPaymentType | ✗ | Habilita tipo de pago por transferencia. |
| hasTransportCode | ✗ | Variable de nicho para softys-cencocal. |
| hasVoucherPrinterEnabled | ✗ | Habilita impresora de voucher. |
| hidePrices | ✗ | Oculta todos los precios del sitio. |
| hideReceiptType | ✗ | Oculta tipo de recibo en checkout. |
| hooks.cartShoppingHook | ✗ | Hook de carrito de compras. |
| hooks.getPendingDocumentsHook | ✗ | Hook de documentos pendientes. |
| hooks.shippingHook | ✗ | Hook de envío. Usado en checkout. |
| hooks.stockHook | ✗ | Hook de stock. |
| hooks.updateTrafficLightHook | ✗ | Hook de semáforo. |
| inMaintenance | ✗ | Indica si el sitio está en mantenimiento. |
| includeTaxRateInPrices | ✓ | Incluye tasa de impuesto en los precios. |
| lazyLoadingPrices | ✗ | Habilita carga perezosa de precios (async). |
| limitAddingByStock | ✓ | Limita agregar productos según stock disponible. |
| ordersRequireAuthorization | ✗ | Órdenes requieren autorización. |
| ordersRequireVerification | ✗ | Órdenes requieren verificación de cuenta. |
| packaging.amountUsesUnits | ✓ | El monto usa unidades en packaging. |
| packagingInformation.hidePackagingInformationB2B | ✓ | Oculta info de empaque B2B. Default true. |
| packagingInformation.hideSingleItemPackagingInformationB2B | ✓ | Oculta info de empaque para items individuales B2B. Default true. |
| packagingInformation.ignoreUnitOnPackInformationB2B | ✗ | Ignora unidad en info de empaque B2B. Default false. |
| payment.balances | [] | Configuración de balances de pago. |
| payment.enableNewPaymentModule | ✗ | Habilita nuevo módulo de pagos. |
| payment.requiresFullPayment | ✗ | Requiere pago completo. |
| paymentsWithoutAccount | ✗ | Pagos sin cuenta. |
| pendingDocuments | ✗ | Habilita documentos pendientes en menú de usuario. Default false. |
| pointsEnabled | ✗ | Habilita sistema de puntos. |
| priceRoundingDecimals | 0 | Decimales para redondeo de precios. Default 0. |
| productDetailViewConfiguration.tabsOrder | ["steps","description"] | No encontrado en el código. |
| productVariability | none | No encontrado en el código. |
| purchaseOrderEnabled | ✗ | Habilita órdenes de compra. |
| shareOrderNewDesign | ✗ | No encontrado en el código. |
| shoppingDetail.lastOrder | ✗ | Muestra última orden en detalle de compra. |
| showEmptyCategories | ✗ | Muestra categorías vacías. Default false. |
| showMinOne | ✗ | Muestra mínimo uno. Info de medición en catálogo. |
| synchronization.backgroundSyncList | [] | Lista de sync en background. |
| synchronization.enableBackgroundSendOrders | ✗ | Habilita envío de órdenes en background. |
| synchronization.enableBackgroundSync | ✗ | Habilita sincronización en background. |
| synchronization.enableSyncImages | ✗ | Habilita sincronización de imágenes. |
| taxes.showSummary | ✓ | Muestra resumen de impuestos en checkout. |
| taxes.taxRate | 0 | Tasa de impuesto. |
| taxes.useTaxRate | ✓ | Usa tasa de impuestos en cálculos de precios. |
| uploadOrderFileWithMinUnits | ✗ | Permite subir archivo de orden con unidades mínimas. |
| useMobileGps | ✗ | Usa GPS del móvil. |
| useMongoPricing | ✗ | Usa pricing de MongoDB. |
| useNewPromotions | ✓ | Usa nuevo sistema de promociones. |
| validatePaymentFromAdmin | ✗ | Valida pago desde admin. |
| weightInfo | ✗ | Muestra info de peso de productos. Precio por peso en tarjetas. |

### Salesterms (yom-production)

| Variable | Valor |
|---|---|
| delivery.daysOfWeek | [] |
| order.disableOrder | ✗ |
| order.orderTotalCreditMax | ✗ |
| order.orderTotalCreditMaxMustBlockOrder | ✗ |
| payment.paymentTypes | [] |
| saleConfig.noSellReasons | [] |

### Customer (yom-production)

| Variable | Valor |
|---|---|
| contactMailingList | [] |
| creditReturnStates | [] |
| currency | clp |
| domain | prinorte.youorder.me |
| eventOptions.newOrderEvent | ✗ |
| mailingList | [] |
| name | Prinorte |
| registerMailingList | [] |

---

## Prisa Store

| Dato | Valor |
|---|---|
| Dominio | prisa.youorder.me |
| Moneda | clp |
| CustomerId | `68e585470f043b43bcbcad3b` |
| Customer legacy | ✓ Prisa |
| Salesterms | ✓ |

### Sites (yom-stores)

| Variable | Valor | Definición |
|---|---|---|
| anonymousAccess | ✗ | Permite acceso anónimo al sitio sin autenticación. Si es false requiere login. |
| anonymousHideCart | ✗ | Oculta el carrito para usuarios anónimos. |
| anonymousHidePrice | ✗ | Oculta los precios para usuarios anónimos. |
| blockedClientAlert.enableBlockedClientAlert | ✗ | Habilita popup de alerta cuando un cliente está bloqueado. |
| businessUnits | [] | Variable en desuso. Permitía catálogos divididos por unidad de negocio. |
| commerce.enableCreateCommerce | ✗ | Habilita el botón y flujo de creación de comercio. |
| disableCart | ✗ | Deshabilita completamente el carrito de compras. |
| disableCommerceEdit | ✗ | Deshabilita edición de comercio. |
| disableObservationInput | ✗ | Deshabilita campo de observaciones en el pedido. |
| disablePayments | ✗ | Deshabilita pagos. |
| disableShowEstimatedDeliveryHour | ✗ | Oculta hora estimada de entrega. |
| discountTypes.discountTypesList | [] | Variable en desuso. Tags para descuento de vendedor. |
| discountTypes.enableOrderDiscountType | ✗ | Variable en desuso. |
| discountTypes.enableProductDiscountType | ✗ | Variable en desuso. |
| editAddress | ✓ | Permite editar dirección de envío. Default true. |
| enableAskDeliveryDate | ✗ | Habilita pregunta de fecha de entrega. |
| enableBetaButtons | ✗ | Habilita botones beta. |
| enableChooseSaleUnit | ✗ | Habilita selección de unidad de venta (B2B nuevo + app). |
| enableCoupons | ✓ | Habilita cupones de descuento. |
| enableCreditNotes | ✗ | Habilita notas de crédito. |
| enableDialogNoSellReason | ✗ | Habilita diálogo de razón de no venta. |
| enableDistributionCentersSelector | ✗ | Habilita selector de centros de distribución. |
| enableInvoicesList | ✗ | Habilita lista de facturas en menú de órdenes. |
| enableNewUI | ✗ | Habilita nueva interfaz. Siempre debería estar activa, la vieja está descontinuada. |
| enableOrderApproval | ✗ | Habilita aprobación de órdenes por vendedores. |
| enableOrderValidation | ✗ | Habilita validación de órdenes. |
| enablePaymentDocumentsB2B | ✗ | Habilita documentos de pago B2B. Botón de facturas en order-list. |
| enablePayments | ✗ | Habilita módulo de pagos. |
| enablePaymentsCollection | ✗ | Habilita módulo de cobranza. disablePayments la desactiva. |
| enablePriceOracle | ✗ | Habilita precios futuros (oracle). Obtiene fecha de entrega antes de cargar precios. |
| enableSellerDiscount | ✗ | Permite que el vendedor haga descuentos. |
| enableTask | ✗ | Habilita gestor de tareas. |
| externalAccess | ✗ | Permite acceso externo. |
| filterGroupedSuggestionsBy | [] | Define campo para filtrar sugerencias agrupadas (ej: packaging.amountPerPackage). |
| footerCustomContent.useFooterCustomContent | ✗ | Habilita contenido personalizado en footer. |
| hasAllDistributionCenters | ✗ | Si stock es multicentro, asigna todos los centros a todos los comercios. |
| hasMultiUnitEnabled | ✗ | Habilita múltiples unidades. |
| hasMultipleBusinessUnit | ✗ | En desuso. |
| hasNoSaleFilter | ✗ | Habilita filtro de no venta. |
| hasSingleDistributionCenter | ✓ | Con stock, indica si comercios tienen un solo centro de distribución. Si true, stock se ve directo en tarjeta. Si false, botón 'ver stock' muestra todos los centros. |
| hasStockEnabled | ✗ | Indica si hay o no stock. |
| hasTransferPaymentType | ✗ | Habilita tipo de pago por transferencia. |
| hasTransportCode | ✗ | Variable de nicho para softys-cencocal. |
| hasVoucherPrinterEnabled | ✗ | Habilita impresora de voucher. |
| hidePrices | ✗ | Oculta todos los precios del sitio. |
| hideReceiptType | ✗ | Oculta tipo de recibo en checkout. |
| hooks.cartShoppingHook | ✗ | Hook de carrito de compras. |
| hooks.getPendingDocumentsHook | ✗ | Hook de documentos pendientes. |
| hooks.shippingHook | ✗ | Hook de envío. Usado en checkout. |
| hooks.stockHook | ✗ | Hook de stock. |
| hooks.updateTrafficLightHook | ✗ | Hook de semáforo. |
| inMaintenance | ✗ | Indica si el sitio está en mantenimiento. |
| includeTaxRateInPrices | ✗ | Incluye tasa de impuesto en los precios. |
| lazyLoadingPrices | ✗ | Habilita carga perezosa de precios (async). |
| limitAddingByStock | ✗ | Limita agregar productos según stock disponible. |
| orderObservations | [] | Configuración de observaciones de orden. |
| ordersRequireAuthorization | ✗ | Órdenes requieren autorización. |
| ordersRequireVerification | ✗ | Órdenes requieren verificación de cuenta. |
| packagingInformation.hidePackagingInformationB2B | ✓ | Oculta info de empaque B2B. Default true. |
| packagingInformation.hideSingleItemPackagingInformationB2B | ✓ | Oculta info de empaque para items individuales B2B. Default true. |
| packagingInformation.ignoreUnitOnPackInformationB2B | ✗ | Ignora unidad en info de empaque B2B. Default false. |
| payment.balances | [] | Configuración de balances de pago. |
| payment.enableNewPaymentModule | ✗ | Habilita nuevo módulo de pagos. |
| payment.requiresFullPayment | ✗ | Requiere pago completo. |
| paymentsWithoutAccount | ✗ | Pagos sin cuenta. |
| pendingDocuments | ✗ | Habilita documentos pendientes en menú de usuario. Default false. |
| pointsEnabled | ✗ | Habilita sistema de puntos. |
| priceRoundingDecimals | 0 | Decimales para redondeo de precios. Default 0. |
| productVariability | none | No encontrado en el código. |
| purchaseOrderEnabled | ✗ | Habilita órdenes de compra. |
| shareOrderNewDesign | ✗ | No encontrado en el código. |
| shoppingDetail.lastOrder | ✗ | Muestra última orden en detalle de compra. |
| showEmptyCategories | ✗ | Muestra categorías vacías. Default false. |
| showMinOne | ✗ | Muestra mínimo uno. Info de medición en catálogo. |
| synchronization.backgroundSyncList | [] | Lista de sync en background. |
| synchronization.enableBackgroundSendOrders | ✗ | Habilita envío de órdenes en background. |
| synchronization.enableBackgroundSync | ✗ | Habilita sincronización en background. |
| synchronization.enableSyncImages | ✗ | Habilita sincronización de imágenes. |
| taxes.showSummary | ✗ | Muestra resumen de impuestos en checkout. |
| taxes.taxRate | 0 | Tasa de impuesto. |
| taxes.useTaxRate | ✗ | Usa tasa de impuestos en cálculos de precios. |
| uploadOrderFileWithMinUnits | ✗ | Permite subir archivo de orden con unidades mínimas. |
| useMobileGps | ✗ | Usa GPS del móvil. |
| useMongoPricing | ✗ | Usa pricing de MongoDB. |
| useNewPromotions | ✗ | Usa nuevo sistema de promociones. |
| validatePaymentFromAdmin | ✗ | Valida pago desde admin. |
| weightInfo | ✗ | Muestra info de peso de productos. Precio por peso en tarjetas. |

### Salesterms (yom-production)

| Variable | Valor |
|---|---|
| delivery.daysOfWeek | [] |
| order.disableOrder | ✗ |
| order.orderTotalCreditMax | ✗ |
| order.orderTotalCreditMaxMustBlockOrder | ✗ |
| payment.paymentTypes | [] |
| saleConfig.noSellReasons | [] |

### Customer (yom-production)

| Variable | Valor |
|---|---|
| contactMailingList | [] |
| creditReturnStates | [] |
| currency | clp |
| domain | prisa.youorder.me |
| eventOptions.newOrderEvent | ✗ |
| mailingList | [] |
| name | Prisa |
| registerMailingList | [] |

---

## Prisur

| Dato | Valor |
|---|---|
| Dominio | prisur.youorder.me |
| Moneda | clp |
| CustomerId | `695516b1388ea9df4a6b91f4` |
| Customer legacy | ✓ Prisur |
| Salesterms | ✓ |

### Sites (yom-stores)

| Variable | Valor | Definición |
|---|---|---|
| anonymousAccess | ✗ | Permite acceso anónimo al sitio sin autenticación. Si es false requiere login. |
| anonymousHideCart | ✗ | Oculta el carrito para usuarios anónimos. |
| anonymousHidePrice | ✗ | Oculta los precios para usuarios anónimos. |
| blockedClientAlert.enableBlockedClientAlert | ✗ | Habilita popup de alerta cuando un cliente está bloqueado. |
| businessUnits | [] | Variable en desuso. Permitía catálogos divididos por unidad de negocio. |
| commerce.enableCreateCommerce | ✓ | Habilita el botón y flujo de creación de comercio. |
| disableCart | ✗ | Deshabilita completamente el carrito de compras. |
| disableCommerceEdit | ✗ | Deshabilita edición de comercio. |
| disableObservationInput | ✗ | Deshabilita campo de observaciones en el pedido. |
| disablePayments | ✗ | Deshabilita pagos. |
| disableShowEstimatedDeliveryHour | ✗ | Oculta hora estimada de entrega. |
| discountTypes.discountTypesList | [] | Variable en desuso. Tags para descuento de vendedor. |
| discountTypes.enableOrderDiscountType | ✗ | Variable en desuso. |
| discountTypes.enableProductDiscountType | ✗ | Variable en desuso. |
| editAddress | ✓ | Permite editar dirección de envío. Default true. |
| enableAskDeliveryDate | ✗ | Habilita pregunta de fecha de entrega. |
| enableBetaButtons | ✗ | Habilita botones beta. |
| enableChooseSaleUnit | ✓ | Habilita selección de unidad de venta (B2B nuevo + app). |
| enableCoupons | ✓ | Habilita cupones de descuento. |
| enableCreditNotes | ✗ | Habilita notas de crédito. |
| enableDialogNoSellReason | ✗ | Habilita diálogo de razón de no venta. |
| enableDistributionCentersSelector | ✗ | Habilita selector de centros de distribución. |
| enableInvoicesList | ✗ | Habilita lista de facturas en menú de órdenes. |
| enableNewUI | ✗ | Habilita nueva interfaz. Siempre debería estar activa, la vieja está descontinuada. |
| enableOrderApproval | ✗ | Habilita aprobación de órdenes por vendedores. |
| enableOrderValidation | ✗ | Habilita validación de órdenes. |
| enablePaymentDocumentsB2B | ✗ | Habilita documentos de pago B2B. Botón de facturas en order-list. |
| enablePayments | ✗ | Habilita módulo de pagos. |
| enablePaymentsCollection | ✗ | Habilita módulo de cobranza. disablePayments la desactiva. |
| enablePriceOracle | ✗ | Habilita precios futuros (oracle). Obtiene fecha de entrega antes de cargar precios. |
| enableSellerDiscount | ✗ | Permite que el vendedor haga descuentos. |
| enableTask | ✗ | Habilita gestor de tareas. |
| externalAccess | ✗ | Permite acceso externo. |
| filterGroupedSuggestionsBy | [] | Define campo para filtrar sugerencias agrupadas (ej: packaging.amountPerPackage). |
| footerCustomContent.useFooterCustomContent | ✗ | Habilita contenido personalizado en footer. |
| hasAllDistributionCenters | ✗ | Si stock es multicentro, asigna todos los centros a todos los comercios. |
| hasMultiUnitEnabled | ✓ | Habilita múltiples unidades. |
| hasMultipleBusinessUnit | ✗ | En desuso. |
| hasNoSaleFilter | ✓ | Habilita filtro de no venta. |
| hasSingleDistributionCenter | ✓ | Con stock, indica si comercios tienen un solo centro de distribución. Si true, stock se ve directo en tarjeta. Si false, botón 'ver stock' muestra todos los centros. |
| hasStockEnabled | ✓ | Indica si hay o no stock. |
| hasTransferPaymentType | ✗ | Habilita tipo de pago por transferencia. |
| hasTransportCode | ✗ | Variable de nicho para softys-cencocal. |
| hasVoucherPrinterEnabled | ✗ | Habilita impresora de voucher. |
| hidePrices | ✗ | Oculta todos los precios del sitio. |
| hideReceiptType | ✗ | Oculta tipo de recibo en checkout. |
| hooks.cartShoppingHook | ✗ | Hook de carrito de compras. |
| hooks.getPendingDocumentsHook | ✗ | Hook de documentos pendientes. |
| hooks.shippingHook | ✗ | Hook de envío. Usado en checkout. |
| hooks.stockHook | ✗ | Hook de stock. |
| hooks.updateTrafficLightHook | ✗ | Hook de semáforo. |
| inMaintenance | ✗ | Indica si el sitio está en mantenimiento. |
| includeTaxRateInPrices | ✗ | Incluye tasa de impuesto en los precios. |
| lazyLoadingPrices | ✗ | Habilita carga perezosa de precios (async). |
| limitAddingByStock | ✓ | Limita agregar productos según stock disponible. |
| orderObservations | [] | Configuración de observaciones de orden. |
| ordersRequireAuthorization | ✗ | Órdenes requieren autorización. |
| ordersRequireVerification | ✗ | Órdenes requieren verificación de cuenta. |
| packaging.amountUsesUnits | ✓ | El monto usa unidades en packaging. |
| packagingInformation.hidePackagingInformationB2B | ✓ | Oculta info de empaque B2B. Default true. |
| packagingInformation.hideSingleItemPackagingInformationB2B | ✓ | Oculta info de empaque para items individuales B2B. Default true. |
| packagingInformation.ignoreUnitOnPackInformationB2B | ✗ | Ignora unidad en info de empaque B2B. Default false. |
| payment.balances | [] | Configuración de balances de pago. |
| payment.enableNewPaymentModule | ✗ | Habilita nuevo módulo de pagos. |
| payment.requiresFullPayment | ✗ | Requiere pago completo. |
| paymentsWithoutAccount | ✗ | Pagos sin cuenta. |
| pendingDocuments | ✗ | Habilita documentos pendientes en menú de usuario. Default false. |
| pointsEnabled | ✗ | Habilita sistema de puntos. |
| priceRoundingDecimals | 0 | Decimales para redondeo de precios. Default 0. |
| productVariability | none | No encontrado en el código. |
| purchaseOrderEnabled | ✗ | Habilita órdenes de compra. |
| shareOrderNewDesign | ✗ | No encontrado en el código. |
| shoppingDetail.lastOrder | ✗ | Muestra última orden en detalle de compra. |
| showEmptyCategories | ✗ | Muestra categorías vacías. Default false. |
| showMinOne | ✗ | Muestra mínimo uno. Info de medición en catálogo. |
| synchronization.backgroundSyncList | [] | Lista de sync en background. |
| synchronization.enableBackgroundSendOrders | ✗ | Habilita envío de órdenes en background. |
| synchronization.enableBackgroundSync | ✗ | Habilita sincronización en background. |
| synchronization.enableSyncImages | ✗ | Habilita sincronización de imágenes. |
| taxes.showSummary | ✗ | Muestra resumen de impuestos en checkout. |
| taxes.taxRate | 0 | Tasa de impuesto. |
| taxes.useTaxRate | ✓ | Usa tasa de impuestos en cálculos de precios. |
| uploadOrderFileWithMinUnits | ✗ | Permite subir archivo de orden con unidades mínimas. |
| useMobileGps | ✗ | Usa GPS del móvil. |
| useMongoPricing | ✗ | Usa pricing de MongoDB. |
| useNewPromotions | ✓ | Usa nuevo sistema de promociones. |
| validatePaymentFromAdmin | ✗ | Valida pago desde admin. |
| weightInfo | ✗ | Muestra info de peso de productos. Precio por peso en tarjetas. |

### Salesterms (yom-production)

| Variable | Valor |
|---|---|
| delivery.daysOfWeek | [] |
| order.disableOrder | ✗ |
| order.orderTotalCreditMax | ✗ |
| order.orderTotalCreditMaxMustBlockOrder | ✗ |
| payment.paymentTypes | [] |
| saleConfig.noSellReasons | [] |

### Customer (yom-production)

| Variable | Valor |
|---|---|
| contactMailingList | [] |
| creditReturnStates | [] |
| currency | clp |
| domain | prisur.youorder.me |
| eventOptions.newOrderEvent | ✗ |
| integrationHooks.createCommerceHook | yom-hooks.prisur.createCommerce |
| integrationHooks.createOrderHook | https://api.youorder.me/hooks/prisur/create-order |
| mailingList | [] |
| name | Prisur |
| registerMailingList | [] |

---

## Prisur Store (STAGING)

| Dato | Valor |
|---|---|
| Dominio | prisur.solopide.me |
| Moneda | clp |
| CustomerId | `69162df4a1ab64ebab26e689` |
| Customer legacy | ✓ Prisur |
| Salesterms | ✓ |

### Sites (yom-stores)

| Variable | Valor | Definición |
|---|---|---|
| anonymousAccess | ✗ | Permite acceso anónimo al sitio sin autenticación. Si es false requiere login. |
| anonymousHideCart | ✗ | Oculta el carrito para usuarios anónimos. |
| anonymousHidePrice | ✗ | Oculta los precios para usuarios anónimos. |
| blockedClientAlert.enableBlockedClientAlert | ✗ | Habilita popup de alerta cuando un cliente está bloqueado. |
| businessUnits | [] | Variable en desuso. Permitía catálogos divididos por unidad de negocio. |
| commerce.enableCreateCommerce | ✗ | Habilita el botón y flujo de creación de comercio. |
| disableCart | ✗ | Deshabilita completamente el carrito de compras. |
| disableCommerceEdit | ✗ | Deshabilita edición de comercio. |
| disableObservationInput | ✗ | Deshabilita campo de observaciones en el pedido. |
| disablePayments | ✗ | Deshabilita pagos. |
| disableShowEstimatedDeliveryHour | ✗ | Oculta hora estimada de entrega. |
| discountTypes.discountTypesList | [] | Variable en desuso. Tags para descuento de vendedor. |
| discountTypes.enableOrderDiscountType | ✗ | Variable en desuso. |
| discountTypes.enableProductDiscountType | ✗ | Variable en desuso. |
| editAddress | ✓ | Permite editar dirección de envío. Default true. |
| enableAskDeliveryDate | ✗ | Habilita pregunta de fecha de entrega. |
| enableBetaButtons | ✗ | Habilita botones beta. |
| enableChooseSaleUnit | ✗ | Habilita selección de unidad de venta (B2B nuevo + app). |
| enableCoupons | ✓ | Habilita cupones de descuento. |
| enableCreditNotes | ✗ | Habilita notas de crédito. |
| enableDialogNoSellReason | ✗ | Habilita diálogo de razón de no venta. |
| enableDistributionCentersSelector | ✗ | Habilita selector de centros de distribución. |
| enableInvoicesList | ✗ | Habilita lista de facturas en menú de órdenes. |
| enableNewUI | ✗ | Habilita nueva interfaz. Siempre debería estar activa, la vieja está descontinuada. |
| enableOrderApproval | ✗ | Habilita aprobación de órdenes por vendedores. |
| enableOrderValidation | ✗ | Habilita validación de órdenes. |
| enablePaymentDocumentsB2B | ✗ | Habilita documentos de pago B2B. Botón de facturas en order-list. |
| enablePayments | ✗ | Habilita módulo de pagos. |
| enablePaymentsCollection | ✗ | Habilita módulo de cobranza. disablePayments la desactiva. |
| enablePriceOracle | ✗ | Habilita precios futuros (oracle). Obtiene fecha de entrega antes de cargar precios. |
| enableSellerDiscount | ✗ | Permite que el vendedor haga descuentos. |
| enableTask | ✗ | Habilita gestor de tareas. |
| externalAccess | ✗ | Permite acceso externo. |
| filterGroupedSuggestionsBy | [] | Define campo para filtrar sugerencias agrupadas (ej: packaging.amountPerPackage). |
| footerCustomContent.useFooterCustomContent | ✗ | Habilita contenido personalizado en footer. |
| hasAllDistributionCenters | ✗ | Si stock es multicentro, asigna todos los centros a todos los comercios. |
| hasMultiUnitEnabled | ✗ | Habilita múltiples unidades. |
| hasMultipleBusinessUnit | ✗ | En desuso. |
| hasNoSaleFilter | ✗ | Habilita filtro de no venta. |
| hasSingleDistributionCenter | ✓ | Con stock, indica si comercios tienen un solo centro de distribución. Si true, stock se ve directo en tarjeta. Si false, botón 'ver stock' muestra todos los centros. |
| hasStockEnabled | ✗ | Indica si hay o no stock. |
| hasTransferPaymentType | ✗ | Habilita tipo de pago por transferencia. |
| hasTransportCode | ✗ | Variable de nicho para softys-cencocal. |
| hasVoucherPrinterEnabled | ✗ | Habilita impresora de voucher. |
| hidePrices | ✗ | Oculta todos los precios del sitio. |
| hideReceiptType | ✗ | Oculta tipo de recibo en checkout. |
| hooks.cartShoppingHook | ✗ | Hook de carrito de compras. |
| hooks.getPendingDocumentsHook | ✗ | Hook de documentos pendientes. |
| hooks.shippingHook | ✗ | Hook de envío. Usado en checkout. |
| hooks.stockHook | ✗ | Hook de stock. |
| hooks.updateTrafficLightHook | ✗ | Hook de semáforo. |
| inMaintenance | ✗ | Indica si el sitio está en mantenimiento. |
| includeTaxRateInPrices | ✗ | Incluye tasa de impuesto en los precios. |
| lazyLoadingPrices | ✗ | Habilita carga perezosa de precios (async). |
| limitAddingByStock | ✗ | Limita agregar productos según stock disponible. |
| orderObservations | [] | Configuración de observaciones de orden. |
| ordersRequireAuthorization | ✗ | Órdenes requieren autorización. |
| ordersRequireVerification | ✗ | Órdenes requieren verificación de cuenta. |
| packagingInformation.hidePackagingInformationB2B | ✓ | Oculta info de empaque B2B. Default true. |
| packagingInformation.hideSingleItemPackagingInformationB2B | ✓ | Oculta info de empaque para items individuales B2B. Default true. |
| packagingInformation.ignoreUnitOnPackInformationB2B | ✗ | Ignora unidad en info de empaque B2B. Default false. |
| payment.balances | [] | Configuración de balances de pago. |
| payment.enableNewPaymentModule | ✗ | Habilita nuevo módulo de pagos. |
| payment.requiresFullPayment | ✗ | Requiere pago completo. |
| paymentsWithoutAccount | ✗ | Pagos sin cuenta. |
| pendingDocuments | ✗ | Habilita documentos pendientes en menú de usuario. Default false. |
| pointsEnabled | ✗ | Habilita sistema de puntos. |
| priceRoundingDecimals | 0 | Decimales para redondeo de precios. Default 0. |
| productVariability | none | No encontrado en el código. |
| purchaseOrderEnabled | ✗ | Habilita órdenes de compra. |
| shareOrderNewDesign | ✗ | No encontrado en el código. |
| shoppingDetail.lastOrder | ✗ | Muestra última orden en detalle de compra. |
| showEmptyCategories | ✗ | Muestra categorías vacías. Default false. |
| showMinOne | ✗ | Muestra mínimo uno. Info de medición en catálogo. |
| synchronization.backgroundSyncList | [] | Lista de sync en background. |
| synchronization.enableBackgroundSendOrders | ✗ | Habilita envío de órdenes en background. |
| synchronization.enableBackgroundSync | ✗ | Habilita sincronización en background. |
| synchronization.enableSyncImages | ✗ | Habilita sincronización de imágenes. |
| taxes.showSummary | ✗ | Muestra resumen de impuestos en checkout. |
| taxes.taxRate | 0 | Tasa de impuesto. |
| taxes.useTaxRate | ✗ | Usa tasa de impuestos en cálculos de precios. |
| uploadOrderFileWithMinUnits | ✗ | Permite subir archivo de orden con unidades mínimas. |
| useMobileGps | ✗ | Usa GPS del móvil. |
| useMongoPricing | ✗ | Usa pricing de MongoDB. |
| useNewPromotions | ✗ | Usa nuevo sistema de promociones. |
| validatePaymentFromAdmin | ✗ | Valida pago desde admin. |
| weightInfo | ✗ | Muestra info de peso de productos. Precio por peso en tarjetas. |

### Salesterms (yom-production)

| Variable | Valor |
|---|---|
| delivery.daysOfWeek | [] |
| order.disableOrder | ✗ |
| order.orderTotalCreditMax | ✗ |
| order.orderTotalCreditMaxMustBlockOrder | ✗ |
| payment.paymentTypes | [] |
| saleConfig.noSellReasons | [] |

### Customer (yom-production)

| Variable | Valor |
|---|---|
| contactMailingList | [] |
| creditReturnStates | [] |
| currency | clp |
| domain | prisur.solopide.me |
| eventOptions.newOrderEvent | ✗ |
| mailingList | [] |
| name | Prisur |
| registerMailingList | [] |

---

## Soprole

| Dato | Valor |
|---|---|
| Dominio | soprole.youorder.me |
| Moneda | clp |
| CustomerId | `5eb98089b67c4010185e7c1f` |
| Customer legacy | ✓ soprole |
| Salesterms | ✓ |

### Sites (yom-stores)

| Variable | Valor | Definición |
|---|---|---|
| anonymousAccess | ✗ | Permite acceso anónimo al sitio sin autenticación. Si es false requiere login. |
| anonymousHideCart | ✓ | Oculta el carrito para usuarios anónimos. |
| anonymousHidePrice | ✓ | Oculta los precios para usuarios anónimos. |
| blockedClientAlert.blockedClientAlertHtmlContent | <div class="text-center">
  <h4>Tu comercio se encuentra bloqueado para compras. Favor contactarse con nuestro Servicio al Cliente (600 600 6600) y revisaremos su caso.</h4>
  <div class="modal-buttons">
    <button type="button" class="btn-back" ng-click="redirectTo('/contact')"><b>Contacto</b></button>
  </div>
</div> | Contenido HTML personalizado para popup de cliente bloqueado. |
| blockedClientAlert.enableBlockedClientAlert | ✓ | Habilita popup de alerta cuando un cliente está bloqueado. |
| confirmCartText | Pasar a confirmación del pedido | Texto personalizado para botón confirmar carrito. Default 'Confirmar dirección'. |
| contact.about | Comprometidos desde 1949 con la alimentación saludable de las familias chilenas, entregando productos sanos y ricos. | Información sobre la empresa (máx 250 chars). Mostrado en footer. |
| contact.phone | 600 600 6600 | Teléfono de contacto. Usado en checkout y profile para mensajes de error. |
| disableCart | ✗ | Deshabilita completamente el carrito de compras. |
| disableCommerceEdit | ✓ | Deshabilita edición de comercio. |
| disableObservationInput | ✓ | Deshabilita campo de observaciones en el pedido. |
| disableShowEstimatedDeliveryHour | ✓ | Oculta hora estimada de entrega. |
| disableWrongPrices | ✓ | Deshabilita validación de precios incorrectos. |
| editAddress | ✗ | Permite editar dirección de envío. Default true. |
| enableAskDeliveryDate | ✗ | Habilita pregunta de fecha de entrega. |
| enableBetaButtons | ✓ | Habilita botones beta. |
| enableCoupons | ✓ | Habilita cupones de descuento. |
| enableCreditStateMessage | ✗ | Habilita mensaje de estado de crédito. |
| enableDialogNoSellReason | ✗ | Habilita diálogo de razón de no venta. |
| enableInvoicesList | ✓ | Habilita lista de facturas en menú de órdenes. |
| enableMassiveOrderSend | ✓ | Permite enviar órdenes pendientes de forma masiva. |
| enableOrderApproval | ✗ | Habilita aprobación de órdenes por vendedores. |
| enableOrderValidation | ✗ | Habilita validación de órdenes. |
| enablePaymentDocumentsB2B | ✓ | Habilita documentos de pago B2B. Botón de facturas en order-list. |
| enablePayments | ✓ | Habilita módulo de pagos. |
| enablePriceOracle | ✓ | Habilita precios futuros (oracle). Obtiene fecha de entrega antes de cargar precios. |
| enableSellerDiscount | ✗ | Permite que el vendedor haga descuentos. |
| externalAccess | ✓ | Permite acceso externo. |
| footerCustomContent.footerCustomHtmlContent | <p class="footer-links">
  <a href="/">Inicio</a>
  &middot;
  <a href="/catalog">Catálogo</a>
  &middot;
  <a href="/contact">Contacto</a>
  &middot;
  <a href="/faq">Preguntas frecuentes</a>
</p> | Contenido HTML personalizado para footer. |
| footerCustomContent.useFooterCustomContent | ✓ | Habilita contenido personalizado en footer. |
| hidePrices | ✗ | Oculta todos los precios del sitio. |
| hideReceiptType | ✓ | Oculta tipo de recibo en checkout. |
| hooks.cartShoppingHook | ✗ | Hook de carrito de compras. |
| hooks.getPendingDocumentsHook | ✗ | Hook de documentos pendientes. |
| hooks.shippingHook | ✗ | Hook de envío. Usado en checkout. |
| hooks.stockHook | ✗ | Hook de stock. |
| hooks.updateTrafficLightHook | ✗ | Hook de semáforo. |
| inMaintenance | ✗ | Indica si el sitio está en mantenimiento. |
| includeTaxRateInPrices | ✓ | Incluye tasa de impuesto en los precios. |
| lazyLoadingPrices | ✗ | Habilita carga perezosa de precios (async). |
| mobileAccess.passwordDisabled | ✓ | Deshabilita contraseña en acceso móvil. |
| ordersRequireAuthorization | ✓ | Órdenes requieren autorización. |
| ordersRequireVerification | ✗ | Órdenes requieren verificación de cuenta. |
| packagingInformation.hidePackagingInformationB2B | ✓ | Oculta info de empaque B2B. Default true. |
| packagingInformation.hideSingleItemPackagingInformationB2B | ✗ | Oculta info de empaque para items individuales B2B. Default true. |
| packagingInformation.ignoreUnitOnPackInformationB2B | ✗ | Ignora unidad en info de empaque B2B. Default false. |
| pendingDocuments | ✗ | Habilita documentos pendientes en menú de usuario. Default false. |
| pointsEnabled | ✗ | Habilita sistema de puntos. |
| purchaseOrderEnabled | ✗ | Habilita órdenes de compra. |
| showEmptyCategories | ✗ | Muestra categorías vacías. Default false. |
| showMinOne | ✓ | Muestra mínimo uno. Info de medición en catálogo. |
| taxes.showSummary | ✓ | Muestra resumen de impuestos en checkout. |
| taxes.taxRate | 0 | Tasa de impuesto. |
| taxes.useTaxRate | ✓ | Usa tasa de impuestos en cálculos de precios. |
| useMobileGps | ✗ | Usa GPS del móvil. |
| useMongoPricing | ✓ | Usa pricing de MongoDB. |
| weightInfo | ✗ | Muestra info de peso de productos. Precio por peso en tarjetas. |
| wrongPrices.block | ✓ | Bloquea productos con precios incorrectos. |
| wrongPrices.threshold | 50 | Umbral para considerar precios incorrectos. Default 50. |

### Salesterms (yom-production)

| Variable | Valor |
|---|---|
| coverage.text |  |
| delivery.daysOfWeek | ["monday","tuesday","wednesday","thursday","friday","saturday"] |
| delivery.fromHours | 28800 |
| delivery.text |  |
| delivery.toHours | 63000 |
| order.minTotalPrice | 48000 |
| order.orderTotalCreditMax | ✓ |
| order.orderTotalCreditMaxMustBlockOrder | ✓ |
| order.orderTotalCreditMaxText | Pedido supera el saldo disponible, por favor disminuya su orden o libere crédito |
| order.text | - |

### Customer (yom-production)

| Variable | Valor |
|---|---|
| contactMailingList | ["paulo.letelier.ext@soprole.cl","carolaine.fuentes.ext@soprole.cl","catherine.silva@soprole.cl","sergio.benavides@sopro... |
| currency | clp |
| domain | soprole.youorder.me |
| eventOptions.newOrderEvent | ✗ |
| integrationHooks.createOrderHook | https://api.youorder.me/hooks/soprole/create-order |
| integrationHooks.nextDeliveryHook | https://api.youorder.me/hooks/soprole/delivery-info |
| integrationHooks.nextDeliveryTextHook | https://api.youorder.me/hooks/soprole/delivery-text-info |
| integrationHooks.paymentDocumentHook | yom-hooks.soprole.getPaymentDocument |
| integrationHooks.shippingCostHook | https://api.youorder.me/hooks/soprole/shipping-cost |
| integrationHooks.visitDaysHook | https://api.youorder.me/hooks/soprole/visit-days |
| mailingList | ["catherine.silva@soprole.cl","francisca.munoz@soprole.cl"] |
| name | soprole |

---

## Soprole

| Dato | Valor |
|---|---|
| Dominio | new-soprole.youorder.me |
| Moneda | clp |
| CustomerId | `69af2a54e573383f6154b0c5` |
| Customer legacy | ✓ New Soprole |
| Salesterms | ✓ |

### Sites (yom-stores)

| Variable | Valor | Definición |
|---|---|---|
| anonymousAccess | ✗ | Permite acceso anónimo al sitio sin autenticación. Si es false requiere login. |
| anonymousHideCart | ✓ | Oculta el carrito para usuarios anónimos. |
| anonymousHidePrice | ✓ | Oculta los precios para usuarios anónimos. |
| blockedClientAlert.blockedClientAlertHtmlContent | <div class="text-center">
  <h4>Tu comercio se encuentra bloqueado para compras. Favor contactarse con nuestro Servicio al Cliente (600 600 6600) y revisaremos su caso.</h4>
  <div class="modal-buttons">
    <button type="button" class="btn-back" ng-click="redirectTo('/contact')"><b>Contacto</b></button>
  </div>
</div> | Contenido HTML personalizado para popup de cliente bloqueado. |
| blockedClientAlert.enableBlockedClientAlert | ✓ | Habilita popup de alerta cuando un cliente está bloqueado. |
| commerce.enableCreateCommerce | ✓ | Habilita el botón y flujo de creación de comercio. |
| confirmCartText | Pasar a confirmación del pedido | Texto personalizado para botón confirmar carrito. Default 'Confirmar dirección'. |
| contact.about | Comprometidos desde 1949 con la alimentación saludable de las familias chilenas, entregando productos sanos y ricos. | Información sobre la empresa (máx 250 chars). Mostrado en footer. |
| contact.branchesContactInformation | [{"phone":"600 600 6600"}] | Info de contacto de sucursales. Usado en checkout y profile. |
| contact.phone | 600 600 6600 | Teléfono de contacto. Usado en checkout y profile para mensajes de error. |
| disableCart | ✗ | Deshabilita completamente el carrito de compras. |
| disableCommerceEdit | ✓ | Deshabilita edición de comercio. |
| disableObservationInput | ✓ | Deshabilita campo de observaciones en el pedido. |
| disableShowEstimatedDeliveryHour | ✓ | Oculta hora estimada de entrega. |
| disableWrongPrices | ✓ | Deshabilita validación de precios incorrectos. |
| editAddress | ✗ | Permite editar dirección de envío. Default true. |
| enableAskDeliveryDate | ✗ | Habilita pregunta de fecha de entrega. |
| enableBetaButtons | ✓ | Habilita botones beta. |
| enableChooseSaleUnit | ✓ | Habilita selección de unidad de venta (B2B nuevo + app). |
| enableCoupons | ✓ | Habilita cupones de descuento. |
| enableCreditStateMessage | ✗ | Habilita mensaje de estado de crédito. |
| enableDialogNoSellReason | ✗ | Habilita diálogo de razón de no venta. |
| enableHome | ✓ | Habilita home. |
| enableInvoicesList | ✓ | Habilita lista de facturas en menú de órdenes. |
| enableMassiveOrderSend | ✓ | Permite enviar órdenes pendientes de forma masiva. |
| enableOrderApproval | ✗ | Habilita aprobación de órdenes por vendedores. |
| enableOrderAproval | ✗ | Duplicado con typo de enableOrderApproval. |
| enableOrderValidation | ✗ | Habilita validación de órdenes. |
| enablePaymentDocumentsB2B | ✓ | Habilita documentos de pago B2B. Botón de facturas en order-list. |
| enablePayments | ✓ | Habilita módulo de pagos. |
| enablePaymentsCollection | ✓ | Habilita módulo de cobranza. disablePayments la desactiva. |
| enablePriceOracle | ✓ | Habilita precios futuros (oracle). Obtiene fecha de entrega antes de cargar precios. |
| enableSellerDiscount | ✗ | Permite que el vendedor haga descuentos. |
| enableTask | ✓ | Habilita gestor de tareas. |
| externalAccess | ✓ | Permite acceso externo. |
| footerCustomContent.footerCustomHtmlContent | <p class="footer-links">
  <a href="/">Inicio</a>
  &middot;
  <a href="/catalog">Catálogo</a>
  &middot;
  <a href="/contact">Contacto</a>
  &middot;
  <a href="/faq">Preguntas frecuentes</a>
</p> | Contenido HTML personalizado para footer. |
| footerCustomContent.useFooterCustomContent | ✓ | Habilita contenido personalizado en footer. |
| hasMultiUnitEnabled | ✓ | Habilita múltiples unidades. |
| hasSingleDistributionCenter | ✓ | Con stock, indica si comercios tienen un solo centro de distribución. Si true, stock se ve directo en tarjeta. Si false, botón 'ver stock' muestra todos los centros. |
| hasStockEnabled | ✓ | Indica si hay o no stock. |
| hidePrices | ✗ | Oculta todos los precios del sitio. |
| hideReceiptType | ✓ | Oculta tipo de recibo en checkout. |
| hooks.cartShoppingHook | ✗ | Hook de carrito de compras. |
| hooks.getPendingDocumentsHook | ✗ | Hook de documentos pendientes. |
| hooks.shippingHook | ✗ | Hook de envío. Usado en checkout. |
| hooks.stockHook | ✗ | Hook de stock. |
| hooks.updateTrafficLightHook | ✗ | Hook de semáforo. |
| inMaintenance | ✗ | Indica si el sitio está en mantenimiento. |
| includeTaxRateInPrices | ✓ | Incluye tasa de impuesto en los precios. |
| lazyLoadingPrices | ✗ | Habilita carga perezosa de precios (async). |
| mobileAccess.passwordDisabled | ✓ | Deshabilita contraseña en acceso móvil. |
| mustHaveOverride | ✓ | Requiere override de precio. |
| orderPolicy.creditExceededStatus | block | Estado cuando se excede crédito. |
| orderPolicy.overdueDebtConfiguration.blockSettings.enabled | ✓ | Habilita bloqueo por deuda vencida. |
| orderPolicy.overdueDebtConfiguration.blockSettings.thresholdDays | 30 | Días umbral para bloqueo por deuda. |
| orderPolicy.overdueDebtConfiguration.retentionSettings.enabled | ✓ | Habilita retención por deuda vencida. |
| orderPolicy.overdueDebtConfiguration.retentionSettings.thresholdDays | 10 | Días umbral para retención por deuda. |
| orderPolicy.retainBelowMinimumOrder | ✗ | Retiene órdenes bajo el mínimo. |
| orderPolicy.retainCreditBlockedCommerces | ✓ | Retiene órdenes de comercios con crédito bloqueado. |
| orderPolicy.sendRetainedOrdersToClientErp | ✗ | Envía órdenes retenidas al ERP del cliente. |
| ordersRequireAuthorization | ✓ | Órdenes requieren autorización. |
| ordersRequireVerification | ✗ | Órdenes requieren verificación de cuenta. |
| packaging.amountUsesUnits | ✓ | El monto usa unidades en packaging. |
| packagingInformation.hidePackagingInformationB2B | ✓ | Oculta info de empaque B2B. Default true. |
| packagingInformation.hideSingleItemPackagingInformationB2B | ✗ | Oculta info de empaque para items individuales B2B. Default true. |
| packagingInformation.ignoreUnitOnPackInformationB2B | ✗ | Ignora unidad en info de empaque B2B. Default false. |
| payment.balances | [{"additionalBalanceFields":[{"key":"balance","displayName":"Saldo","type":"textField","dropdownOptions":[]},{"key":"obs... | Configuración de balances de pago. |
| payment.enableNewPaymentModule | ✓ | Habilita nuevo módulo de pagos. |
| payment.requiresFullPayment | ✓ | Requiere pago completo. |
| pendingDocuments | ✗ | Habilita documentos pendientes en menú de usuario. Default false. |
| pointsEnabled | ✗ | Habilita sistema de puntos. |
| priceRoundingDecimals | 0 | Decimales para redondeo de precios. Default 0. |
| productDetailViewConfiguration.tabsOrder | ["steps","description"] | No encontrado en el código. |
| productVariability | low | No encontrado en el código. |
| purchaseOrderEnabled | ✗ | Habilita órdenes de compra. |
| shoppingDetail.lastOrder | ✓ | Muestra última orden en detalle de compra. |
| showEmptyCategories | ✗ | Muestra categorías vacías. Default false. |
| showMinOne | ✓ | Muestra mínimo uno. Info de medición en catálogo. |
| taxes.showSummary | ✓ | Muestra resumen de impuestos en checkout. |
| taxes.taxRate | 0 | Tasa de impuesto. |
| taxes.useTaxRate | ✓ | Usa tasa de impuestos en cálculos de precios. |
| useMobileGps | ✗ | Usa GPS del móvil. |
| useMongoPricing | ✓ | Usa pricing de MongoDB. |
| useNewPromotions | ✓ | Usa nuevo sistema de promociones. |
| weightInfo | ✗ | Muestra info de peso de productos. Precio por peso en tarjetas. |
| wrongPrices.block | ✓ | Bloquea productos con precios incorrectos. |
| wrongPrices.threshold | 50 | Umbral para considerar precios incorrectos. Default 50. |

### Salesterms (yom-production)

| Variable | Valor |
|---|---|
| delivery.daysOfWeek | [] |
| order.minTotalPrice | 48000 |
| order.orderTotalCreditMax | ✓ |
| order.orderTotalCreditMaxMustBlockOrder | ✓ |
| order.orderTotalCreditMaxText | Pedido supera el saldo disponible, por favor disminuya su orden o libere crédito |
| order.text | - |
| payment.paymentTypes | [] |
| saleConfig.noSellReasons | [] |

### Customer (yom-production)

| Variable | Valor |
|---|---|
| contactMailingList | ["paulo.letelier.ext@soprole.cl","carolaine.fuentes.ext@soprole.cl","catherine.silva@soprole.cl","sergio.benavides@sopro... |
| creditReturnStates | [] |
| currency | clp |
| domain | new-soprole.youorder.me |
| eventOptions.newOrderEvent | ✗ |
| integrationHooks.createOrderHook | https://api.youorder.me/hooks/soprole/create-order |
| integrationHooks.nextDeliveryHook | https://api.youorder.me/hooks/soprole/delivery-info |
| integrationHooks.nextDeliveryTextHook | https://api.youorder.me/hooks/soprole/delivery-text-info |
| integrationHooks.paymentDocumentHook | yom-hooks.soprole.getPaymentDocument |
| integrationHooks.shippingCostHook | https://api.youorder.me/hooks/soprole/shipping-cost |
| integrationHooks.visitDaysHook | https://api.youorder.me/hooks/soprole/visit-days |
| mailingList | ["catherine.silva@soprole.cl","francisca.munoz@soprole.cl"] |
| name | New Soprole |
| registerMailingList | [] |

---

## Surtiventas

| Dato | Valor |
|---|---|
| Dominio | surtiventas.youorder.me |
| Moneda | clp |
| CustomerId | `684f6133b2a96b4402ae28d6` |
| Customer legacy | ✓ Surtiventas |
| Salesterms | ✓ |

### Sites (yom-stores)

| Variable | Valor | Definición |
|---|---|---|
| anonymousAccess | ✗ | Permite acceso anónimo al sitio sin autenticación. Si es false requiere login. |
| anonymousHideCart | ✓ | Oculta el carrito para usuarios anónimos. |
| anonymousHidePrice | ✗ | Oculta los precios para usuarios anónimos. |
| blockedClientAlert.enableBlockedClientAlert | ✗ | Habilita popup de alerta cuando un cliente está bloqueado. |
| businessUnits | [] | Variable en desuso. Permitía catálogos divididos por unidad de negocio. |
| commerce.enableCreateCommerce | ✓ | Habilita el botón y flujo de creación de comercio. |
| contact.about | Surtiventas opera con el claro propósito de satisfacer las necesidades básicas del comerciante chileno, con un servicio personalizado de venta que se extiende a lo largo y ancho del país. | Información sobre la empresa (máx 250 chars). Mostrado en footer. |
| contact.branchesContactInformation | [{"phone":"+562 2820 6400","email":"srvcliente1@surtiventas.cl"}] | Info de contacto de sucursales. Usado en checkout y profile. |
| contact.email | srvcliente1@surtiventas.cl | Email de contacto. Mostrado en footer. |
| disableCart | ✗ | Deshabilita completamente el carrito de compras. |
| disableCommerceEdit | ✗ | Deshabilita edición de comercio. |
| disableObservationInput | ✗ | Deshabilita campo de observaciones en el pedido. |
| disablePayments | ✗ | Deshabilita pagos. |
| disableShowEstimatedDeliveryHour | ✗ | Oculta hora estimada de entrega. |
| discountTypes.discountTypesList | [] | Variable en desuso. Tags para descuento de vendedor. |
| discountTypes.enableOrderDiscountType | ✗ | Variable en desuso. |
| discountTypes.enableProductDiscountType | ✗ | Variable en desuso. |
| editAddress | ✓ | Permite editar dirección de envío. Default true. |
| enableAskDeliveryDate | ✗ | Habilita pregunta de fecha de entrega. |
| enableBetaButtons | ✗ | Habilita botones beta. |
| enableChooseSaleUnit | ✓ | Habilita selección de unidad de venta (B2B nuevo + app). |
| enableCoupons | ✓ | Habilita cupones de descuento. |
| enableCreditNotes | ✗ | Habilita notas de crédito. |
| enableDialogNoSellReason | ✗ | Habilita diálogo de razón de no venta. |
| enableDistributionCentersSelector | ✗ | Habilita selector de centros de distribución. |
| enableInvoicesList | ✗ | Habilita lista de facturas en menú de órdenes. |
| enableMassiveOrderSend | ✓ | Permite enviar órdenes pendientes de forma masiva. |
| enableNewUI | ✗ | Habilita nueva interfaz. Siempre debería estar activa, la vieja está descontinuada. |
| enableOrderApproval | ✗ | Habilita aprobación de órdenes por vendedores. |
| enableOrderValidation | ✗ | Habilita validación de órdenes. |
| enablePaymentDocumentsB2B | ✗ | Habilita documentos de pago B2B. Botón de facturas en order-list. |
| enablePayments | ✗ | Habilita módulo de pagos. |
| enablePaymentsCollection | ✗ | Habilita módulo de cobranza. disablePayments la desactiva. |
| enablePriceOracle | ✗ | Habilita precios futuros (oracle). Obtiene fecha de entrega antes de cargar precios. |
| enableSellerDiscount | ✓ | Permite que el vendedor haga descuentos. |
| enableTask | ✗ | Habilita gestor de tareas. |
| externalAccess | ✗ | Permite acceso externo. |
| filterGroupedSuggestionsBy | [] | Define campo para filtrar sugerencias agrupadas (ej: packaging.amountPerPackage). |
| footerCustomContent.useFooterCustomContent | ✗ | Habilita contenido personalizado en footer. |
| hasAllDistributionCenters | ✗ | Si stock es multicentro, asigna todos los centros a todos los comercios. |
| hasMultiUnitEnabled | ✓ | Habilita múltiples unidades. |
| hasMultipleBusinessUnit | ✗ | En desuso. |
| hasNoSaleFilter | ✓ | Habilita filtro de no venta. |
| hasSingleDistributionCenter | ✓ | Con stock, indica si comercios tienen un solo centro de distribución. Si true, stock se ve directo en tarjeta. Si false, botón 'ver stock' muestra todos los centros. |
| hasStockEnabled | ✓ | Indica si hay o no stock. |
| hasTransferPaymentType | ✗ | Habilita tipo de pago por transferencia. |
| hasTransportCode | ✗ | Variable de nicho para softys-cencocal. |
| hasVoucherPrinterEnabled | ✗ | Habilita impresora de voucher. |
| hidePrices | ✗ | Oculta todos los precios del sitio. |
| hideReceiptType | ✗ | Oculta tipo de recibo en checkout. |
| hooks.cartShoppingHook | ✗ | Hook de carrito de compras. |
| hooks.getPendingDocumentsHook | ✗ | Hook de documentos pendientes. |
| hooks.shippingHook | ✗ | Hook de envío. Usado en checkout. |
| hooks.stockHook | ✗ | Hook de stock. |
| hooks.updateTrafficLightHook | ✗ | Hook de semáforo. |
| inMaintenance | ✗ | Indica si el sitio está en mantenimiento. |
| includeTaxRateInPrices | ✓ | Incluye tasa de impuesto en los precios. |
| lazyLoadingPrices | ✗ | Habilita carga perezosa de precios (async). |
| limitAddingByStock | ✓ | Limita agregar productos según stock disponible. |
| ordersRequireAuthorization | ✗ | Órdenes requieren autorización. |
| ordersRequireVerification | ✗ | Órdenes requieren verificación de cuenta. |
| packaging.amountUsesUnits | ✓ | El monto usa unidades en packaging. |
| packagingInformation.hidePackagingInformationB2B | ✓ | Oculta info de empaque B2B. Default true. |
| packagingInformation.hideSingleItemPackagingInformationB2B | ✓ | Oculta info de empaque para items individuales B2B. Default true. |
| packagingInformation.ignoreUnitOnPackInformationB2B | ✗ | Ignora unidad en info de empaque B2B. Default false. |
| payment.balances | [] | Configuración de balances de pago. |
| payment.enableNewPaymentModule | ✗ | Habilita nuevo módulo de pagos. |
| payment.requiresFullPayment | ✗ | Requiere pago completo. |
| paymentsWithoutAccount | ✗ | Pagos sin cuenta. |
| pendingDocuments | ✗ | Habilita documentos pendientes en menú de usuario. Default false. |
| pointsEnabled | ✗ | Habilita sistema de puntos. |
| priceRoundingDecimals | 0 | Decimales para redondeo de precios. Default 0. |
| productDetailViewConfiguration.tabsOrder | ["steps","description"] | No encontrado en el código. |
| productVariability | none | No encontrado en el código. |
| purchaseOrderEnabled | ✗ | Habilita órdenes de compra. |
| shareOrderNewDesign | ✗ | No encontrado en el código. |
| shoppingDetail.lastOrder | ✗ | Muestra última orden en detalle de compra. |
| showEmptyCategories | ✗ | Muestra categorías vacías. Default false. |
| showMinOne | ✗ | Muestra mínimo uno. Info de medición en catálogo. |
| synchronization.backgroundSyncList | [] | Lista de sync en background. |
| synchronization.enableBackgroundSendOrders | ✗ | Habilita envío de órdenes en background. |
| synchronization.enableBackgroundSync | ✗ | Habilita sincronización en background. |
| synchronization.enableSyncImages | ✗ | Habilita sincronización de imágenes. |
| taxes.showSummary | ✓ | Muestra resumen de impuestos en checkout. |
| taxes.taxRate | 0 | Tasa de impuesto. |
| taxes.useTaxRate | ✓ | Usa tasa de impuestos en cálculos de precios. |
| uploadOrderFileWithMinUnits | ✗ | Permite subir archivo de orden con unidades mínimas. |
| useMobileGps | ✗ | Usa GPS del móvil. |
| useMongoPricing | ✗ | Usa pricing de MongoDB. |
| useNewPromotions | ✓ | Usa nuevo sistema de promociones. |
| validatePaymentFromAdmin | ✗ | Valida pago desde admin. |
| weightInfo | ✗ | Muestra info de peso de productos. Precio por peso en tarjetas. |

### Salesterms (yom-production)

| Variable | Valor |
|---|---|
| delivery.daysOfWeek | ["monday","tuesday","wednesday","thursday","friday"] |
| delivery.fromHours | 32400 |
| delivery.text | Despachamos desde 24 horas hábiles |
| delivery.toHours | 64800 |
| order.disableOrder | ✗ |
| order.minOrderPrice | 41650 |
| order.orderTotalCreditMax | ✗ |
| order.orderTotalCreditMaxMustBlockOrder | ✗ |
| payment.paymentTypes | [] |
| saleConfig.noSellReasons | [] |

### Customer (yom-production)

| Variable | Valor |
|---|---|
| contactMailingList | [] |
| currency | clp |
| domain | surtiventas.youorder.me |
| eventOptions.newOrderEvent | ✗ |
| integrationHooks.createCommerceHook | yom-hooks.surtiventas.createCommerce |
| integrationHooks.createOrderHook | https://api.youorder.me/hooks/surtiventas/create-order |
| mailingList | [] |
| name | Surtiventas |
| registerMailingList | [] |

---

## softys-cencocal

| Dato | Valor |
|---|---|
| Dominio | softys-cencocal.youorder.me |
| Moneda | clp |
| CustomerId | `6137b1863a82143b23e7b58a` |
| Customer legacy | ✓ softys-cencocal |
| Salesterms | ✓ |

### Sites (yom-stores)

| Variable | Valor | Definición |
|---|---|---|
| anonymousAccess | ✗ | Permite acceso anónimo al sitio sin autenticación. Si es false requiere login. |
| anonymousHideCart | ✗ | Oculta el carrito para usuarios anónimos. |
| anonymousHidePrice | ✗ | Oculta los precios para usuarios anónimos. |
| disableCart | ✗ | Deshabilita completamente el carrito de compras. |
| disableCommerceEdit | ✗ | Deshabilita edición de comercio. |
| disableShowEstimatedDeliveryHour | ✗ | Oculta hora estimada de entrega. |
| editAddress | ✓ | Permite editar dirección de envío. Default true. |
| enableAskDeliveryDate | ✗ | Habilita pregunta de fecha de entrega. |
| enableChooseSaleUnit | ✓ | Habilita selección de unidad de venta (B2B nuevo + app). |
| enableCoupons | ✓ | Habilita cupones de descuento. |
| enableCreditNotes | ✓ | Habilita notas de crédito. |
| enableCreditStateMessage | ✓ | Habilita mensaje de estado de crédito. |
| enableDialogNoSellReason | ✗ | Habilita diálogo de razón de no venta. |
| enableInvoicesList | ✗ | Habilita lista de facturas en menú de órdenes. |
| enableMassiveOrderSend | ✓ | Permite enviar órdenes pendientes de forma masiva. |
| enableOrderApproval | ✗ | Habilita aprobación de órdenes por vendedores. |
| enableOrderValidation | ✗ | Habilita validación de órdenes. |
| enablePayments | ✓ | Habilita módulo de pagos. |
| enablePaymentsCollection | ✓ | Habilita módulo de cobranza. disablePayments la desactiva. |
| enableSellerDiscount | ✓ | Permite que el vendedor haga descuentos. |
| enableTask | ✓ | Habilita gestor de tareas. |
| externalAccess | ✗ | Permite acceso externo. |
| hasNoSaleFilter | ✓ | Habilita filtro de no venta. |
| hasSingleDistributionCenter | ✓ | Con stock, indica si comercios tienen un solo centro de distribución. Si true, stock se ve directo en tarjeta. Si false, botón 'ver stock' muestra todos los centros. |
| hasStockEnabled | ✓ | Indica si hay o no stock. |
| hasTransferPaymentType | ✗ | Habilita tipo de pago por transferencia. |
| hasTransportCode | ✓ | Variable de nicho para softys-cencocal. |
| hasVoucherPrinterEnabled | ✓ | Habilita impresora de voucher. |
| hidePrices | ✗ | Oculta todos los precios del sitio. |
| hideReceiptType | ✗ | Oculta tipo de recibo en checkout. |
| hooks.cartShoppingHook | ✗ | Hook de carrito de compras. |
| hooks.getPendingDocumentsHook | ✗ | Hook de documentos pendientes. |
| hooks.shippingHook | ✓ | Hook de envío. Usado en checkout. |
| hooks.stockHook | ✗ | Hook de stock. |
| hooks.updateTrafficLightHook | ✓ | Hook de semáforo. |
| inMaintenance | ✗ | Indica si el sitio está en mantenimiento. |
| includeTaxRateInPrices | ✗ | Incluye tasa de impuesto en los precios. |
| lazyLoadingPrices | ✗ | Habilita carga perezosa de precios (async). |
| ordersRequireAuthorization | ✗ | Órdenes requieren autorización. |
| ordersRequireVerification | ✗ | Órdenes requieren verificación de cuenta. |
| payment.enableNewPaymentModule | ✓ | Habilita nuevo módulo de pagos. |
| paymentsWithoutAccount | ✗ | Pagos sin cuenta. |
| pendingDocuments | ✗ | Habilita documentos pendientes en menú de usuario. Default false. |
| pointsEnabled | ✗ | Habilita sistema de puntos. |
| productList.enableSuggestionByCategories | ✗ | Habilita sugerencias por categorías. |
| purchaseOrderEnabled | ✗ | Habilita órdenes de compra. |
| showEmptyCategories | ✗ | Muestra categorías vacías. Default false. |
| showMinOne | ✗ | Muestra mínimo uno. Info de medición en catálogo. |
| synchronization.enableSyncImages | ✓ | Habilita sincronización de imágenes. |
| taxes.showSummary | ✗ | Muestra resumen de impuestos en checkout. |
| taxes.taxRate | 0 | Tasa de impuesto. |
| taxes.useTaxRate | ✓ | Usa tasa de impuestos en cálculos de precios. |
| uploadOrderFileWithMinUnits | ✗ | Permite subir archivo de orden con unidades mínimas. |
| useMobileGps | ✓ | Usa GPS del móvil. |
| validatePaymentFromAdmin | ✗ | Valida pago desde admin. |
| weightInfo | ✗ | Muestra info de peso de productos. Precio por peso en tarjetas. |

### Salesterms (yom-production)

| Variable | Valor |
|---|---|
| coverage.text |  |
| delivery.daysOfWeek | ["monday","tuesday","wednesday","thursday","friday","saturday"] |
| delivery.fromHours | 28800 |
| delivery.text |  |
| delivery.toHours | 63000 |
| order.minTotalPrice | 12000 |
| order.orderTotalCreditMax | ✓ |
| order.orderTotalCreditMaxMustBlockOrder | ✓ |
| order.orderTotalCreditMaxPaymentConfig.credit | ["CONTADO","CREDITO CTA.CTE.","CREDITO 7 DIAS","CREDITO 15 DIAS","CREDITO 21 DIAS","CREDITO 30 DIAS","CONT.ENT.DOC.AL DI... |
| order.orderTotalCreditMaxPaymentConfig.defaultPayment | credit |
| order.orderTotalCreditMaxPaymentConfig.other | ["EFECTIVO PAGO TRANSPORTE","TRANSF.ELEC. AL DIA"] |
| order.orderTotalCreditMaxText | Orden excede límite de Crédito,¿Está seguro que desea enviarla? |
| order.text | - |
| payment.paymentTypes | [{"key":"cash","text":"Efectivo"},{"key":"check","text":"Cheque"},{"key":"checkToDate","text":"Cheque a fecha"}] |
| saleConfig.noSellReasons | ["Negocio cerrado","Inventario suficiente","Sin dinero","No se encuentra decisor de compra","Negocio terminado","Se debe... |

### Customer (yom-production)

| Variable | Valor |
|---|---|
| contactMailingList | [] |
| currency | clp |
| domain | softys-cencocal.youorder.me |
| eventOptions.newOrderEvent | ✗ |
| integrationHooks.createOrderHook | https://msapi.youorder.me/api/v3/b2b-auth/hooks/softys-cencocal/create-order |
| integrationHooks.createPaymentHook | https://msapi.youorder.me/api/v3/b2b-auth/hooks/softys-cencocal/create-payment |
| integrationHooks.getPendingDocumentsHook | https://msapi.youorder.me/api/v3/b2b-auth/hooks/softys-cencocal/get-pending-documents |
| integrationHooks.getVoucherHook | https://msapi.youorder.me/api/v3/b2b-auth/hooks/softys-cencocal/get-voucher |
| integrationHooks.shippingCostHook | https://msapi.youorder.me/api/v3/b2b-auth/hooks/softys-cencocal/get-shipping-cost |
| integrationHooks.updateTrafficLightHook | https://msapi.youorder.me/api/v3/b2b-auth/hooks/softys-cencocal/get-credits |
| integrationOptions.createOrderRetries | 3 |
| mailingList | [] |
| name | softys-cencocal |
| registerMailingList | [] |

---

## softys-dimak

| Dato | Valor |
|---|---|
| Dominio | softys-dimak.youorder.me |
| Moneda | clp |
| CustomerId | `6266d1871cc94f5fd299bd29` |
| Customer legacy | ✓ softys-dimak |
| Salesterms | ✓ |

### Sites (yom-stores)

| Variable | Valor | Definición |
|---|---|---|
| anonymousAccess | ✗ | Permite acceso anónimo al sitio sin autenticación. Si es false requiere login. |
| anonymousHideCart | ✗ | Oculta el carrito para usuarios anónimos. |
| anonymousHidePrice | ✗ | Oculta los precios para usuarios anónimos. |
| disableCart | ✗ | Deshabilita completamente el carrito de compras. |
| disableCommerceEdit | ✗ | Deshabilita edición de comercio. |
| disableShowEstimatedDeliveryHour | ✗ | Oculta hora estimada de entrega. |
| editAddress | ✓ | Permite editar dirección de envío. Default true. |
| enableAskDeliveryDate | ✗ | Habilita pregunta de fecha de entrega. |
| enableChooseSaleUnit | ✗ | Habilita selección de unidad de venta (B2B nuevo + app). |
| enableCoupons | ✓ | Habilita cupones de descuento. |
| enableCreditNotes | ✗ | Habilita notas de crédito. |
| enableCreditStateMessage | ✗ | Habilita mensaje de estado de crédito. |
| enableDialogNoSellReason | ✗ | Habilita diálogo de razón de no venta. |
| enableInvoicesList | ✗ | Habilita lista de facturas en menú de órdenes. |
| enableOrderApproval | ✗ | Habilita aprobación de órdenes por vendedores. |
| enableOrderValidation | ✗ | Habilita validación de órdenes. |
| enablePaymentDocumentsB2B | ✗ | Habilita documentos de pago B2B. Botón de facturas en order-list. |
| enablePayments | ✗ | Habilita módulo de pagos. |
| enableSellerDiscount | ✗ | Permite que el vendedor haga descuentos. |
| enableTask | ✓ | Habilita gestor de tareas. |
| externalAccess | ✗ | Permite acceso externo. |
| filterGroupedSuggestionsBy | [] | Define campo para filtrar sugerencias agrupadas (ej: packaging.amountPerPackage). |
| hasAllDistributionCenters | ✗ | Si stock es multicentro, asigna todos los centros a todos los comercios. |
| hasSingleDistributionCenter | ✓ | Con stock, indica si comercios tienen un solo centro de distribución. Si true, stock se ve directo en tarjeta. Si false, botón 'ver stock' muestra todos los centros. |
| hasStockEnabled | ✗ | Indica si hay o no stock. |
| hasTransferPaymentType | ✗ | Habilita tipo de pago por transferencia. |
| hasTransportCode | ✗ | Variable de nicho para softys-cencocal. |
| hasVoucherPrinterEnabled | ✗ | Habilita impresora de voucher. |
| hidePrices | ✗ | Oculta todos los precios del sitio. |
| hideReceiptType | ✗ | Oculta tipo de recibo en checkout. |
| hooks.cartShoppingHook | ✗ | Hook de carrito de compras. |
| hooks.getPendingDocumentsHook | ✗ | Hook de documentos pendientes. |
| hooks.shippingHook | ✗ | Hook de envío. Usado en checkout. |
| hooks.stockHook | ✗ | Hook de stock. |
| hooks.updateTrafficLightHook | ✗ | Hook de semáforo. |
| inMaintenance | ✗ | Indica si el sitio está en mantenimiento. |
| includeTaxRateInPrices | ✗ | Incluye tasa de impuesto en los precios. |
| lazyLoadingPrices | ✗ | Habilita carga perezosa de precios (async). |
| ordersRequireAuthorization | ✗ | Órdenes requieren autorización. |
| ordersRequireVerification | ✗ | Órdenes requieren verificación de cuenta. |
| paymentsWithoutAccount | ✗ | Pagos sin cuenta. |
| pendingDocuments | ✗ | Habilita documentos pendientes en menú de usuario. Default false. |
| pointsEnabled | ✗ | Habilita sistema de puntos. |
| purchaseOrderEnabled | ✗ | Habilita órdenes de compra. |
| showEmptyCategories | ✗ | Muestra categorías vacías. Default false. |
| showMinOne | ✗ | Muestra mínimo uno. Info de medición en catálogo. |
| taxes.showSummary | ✗ | Muestra resumen de impuestos en checkout. |
| taxes.taxRate | 0 | Tasa de impuesto. |
| taxes.useTaxRate | ✗ | Usa tasa de impuestos en cálculos de precios. |
| uploadOrderFileWithMinUnits | ✗ | Permite subir archivo de orden con unidades mínimas. |
| useMobileGps | ✗ | Usa GPS del móvil. |
| validatePaymentFromAdmin | ✗ | Valida pago desde admin. |
| weightInfo | ✗ | Muestra info de peso de productos. Precio por peso en tarjetas. |

### Salesterms (yom-production)

| Variable | Valor |
|---|---|
| delivery.daysOfWeek | [] |
| order.disableOrder | ✗ |
| order.orderTotalCreditMax | ✗ |
| order.orderTotalCreditMaxMustBlockOrder | ✗ |
| payment.paymentTypes | [] |
| saleConfig.noSellReasons | [] |

### Customer (yom-production)

| Variable | Valor |
|---|---|
| contactMailingList | [] |
| currency | clp |
| domain | softys-dimak.youorder.me |
| eventOptions.newOrderEvent | ✗ |
| mailingList | [] |
| name | softys-dimak |
| registerMailingList | [] |

---


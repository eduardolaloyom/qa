#!/usr/bin/env python3
"""
Genera tests/app/flows/{cliente}/04-features.yaml basándose en
los valores reales de qa-matrix-staging.json (o qa-matrix.json para prod).

Uso:
    python3 tools/gen-maestro-features.py caren
    python3 tools/gen-maestro-features.py caren --env production
    python3 tools/gen-maestro-features.py caren --dry-run

Para cada variable de MongoDB:
- Si tiene manifestación visual en la APP → assertVisible / assertNotVisible (sin optional:true)
- Si es solo backend / difícil de observar → comentario explicativo en el YAML generado
"""

import sys
import json
import argparse
from pathlib import Path

# ── Feature flags con manifestación visual en la APP ─────────────────────────
# Cada entrada: flag → spec
#   off_check / off_text : assertion cuando flag es FALSE
#   on_check  / on_text  : assertion cuando flag es TRUE (None = sin assertion)
#   context              : dónde se hace la assertion (login|lista|menu|catalogo|carrito)
#   description          : texto descriptivo para el comentario YAML

FEATURE_MAP = {

    # ── PANTALLA DE LOGIN ─────────────────────────────────────────────────────
    "loginButtons.facebook": {
        "context": "login",
        "description": "Botón login con Facebook",
        "off_check": "assertNotVisible",
        "off_text": r".*[Ff]acebook.*|.*FB.*",
        "on_check": "assertVisible",
        "on_text": r".*[Ff]acebook.*",
    },
    "loginButtons.google": {
        "context": "login",
        "description": "Botón login con Google",
        "off_check": "assertNotVisible",
        "off_text": r".*[Gg]oogle.*",
        "on_check": "assertVisible",
        "on_text": r".*[Gg]oogle.*",
    },

    # ── LISTA DE COMERCIOS ────────────────────────────────────────────────────
    "commerce.enableCreateCommerce": {
        "context": "lista",
        "description": "Botón 'Crear Comercio'",
        "off_check": "assertNotVisible",
        "off_text": r".*[Cc]rear [Cc]omercio.*|.*[Nn]uevo [Cc]omercio.*|.*[Aa]gregar [Cc]omercio.*",
        "on_check": "assertVisible",
        "on_text": r".*[Cc]rear [Cc]omercio.*|Crear comercio",
    },
    "hasNoSaleFilter": {
        "context": "lista",
        "description": "Filtro 'Sin venta' en lista de comercios",
        "off_check": None,
        "off_text": None,
        "on_check": "assertVisible",
        "on_text": r".*[Ss]in [Vv]enta.*|.*[Nn]o [Vv]enta.*",
    },
    "inMaintenance": {
        "context": "lista",
        "description": "Banner de mantenimiento en la app",
        "off_check": "assertNotVisible",
        "off_text": r".*[Mm]antenimiento.*|.*[Mm]aintenance.*",
        "on_check": "assertVisible",
        "on_text": r".*[Mm]antenimiento.*|.*[Mm]aintenance.*",
    },

    # ── MENÚ / DRAWER ─────────────────────────────────────────────────────────
    "enablePayments": {
        "context": "menu",
        "description": "Módulo Pagos en menú lateral",
        "off_check": "assertNotVisible",
        "off_text": r"^Pagos$|^PAGOS$",
        "on_check": "assertVisible",
        "on_text": r"^Pagos$|^PAGOS$",
    },
    "enablePaymentsCollection": {
        "context": "menu",
        "description": "Módulo Cobros en menú lateral",
        "off_check": "assertNotVisible",
        "off_text": r"^Cobros$|^COBROS$",
        "on_check": "assertVisible",
        "on_text": r"^Cobros$|^COBROS$",
    },
    "enableTask": {
        "context": "menu",
        "description": "Módulo Tareas en menú lateral",
        "off_check": "assertNotVisible",
        "off_text": r"^Tareas$|^TAREAS$",
        "on_check": "assertVisible",
        "on_text": r"^Tareas$|^TAREAS$",
    },
    "enableCreditNotes": {
        "context": "menu",
        "description": "Módulo Notas de crédito en menú lateral",
        "off_check": None,
        "off_text": None,
        "on_check": "assertVisible",
        "on_text": r".*[Nn]ota.*[Cc]r[eé]dito.*|.*[Cc]redit.*[Nn]ote.*",
    },
    "enableInvoicesList": {
        "context": "menu",
        "description": "Módulo Facturas en menú lateral",
        "off_check": None,
        "off_text": None,
        "on_check": "assertVisible",
        "on_text": r"^Facturas$|^FACTURAS$",
    },
    "pendingDocuments": {
        "context": "menu",
        "description": "Módulo Documentos pendientes en menú lateral",
        "off_check": None,
        "off_text": None,
        "on_check": "assertVisible",
        "on_text": r".*[Dd]ocumentos.*[Pp]endientes.*|.*[Pp]ending.*[Dd]oc.*",
    },
    "pointsEnabled": {
        "context": "menu",
        "description": "Módulo Puntos en menú lateral",
        "off_check": "assertNotVisible",
        "off_text": r"^Puntos$|^PUNTOS$",
        "on_check": "assertVisible",
        "on_text": r"^Puntos$|^PUNTOS$",
    },
    "enableHome": {
        "context": "menu",
        "description": "Sección Inicio en menú lateral",
        "off_check": None,
        "off_text": None,
        "on_check": "assertVisible",
        "on_text": r"^Inicio$|^INICIO$|^Home$",
    },
    "enableFinancePortal": {
        "context": "menu",
        "description": "Portal financiero en menú lateral",
        "off_check": None,
        "off_text": None,
        "on_check": "assertVisible",
        "on_text": r".*[Pp]ortal.*[Ff]inanciero.*|.*[Ff]inance.*[Pp]ortal.*",
    },
    "enableActivation": {
        "context": "menu",
        "description": "Módulo Activación en menú lateral",
        "off_check": None,
        "off_text": None,
        "on_check": "assertVisible",
        "on_text": r".*[Aa]ctivaci[oó]n.*|.*[Aa]ctivation.*",
    },
    "enableMassiveOrderSend": {
        "context": "menu",
        "description": "Envío masivo de pedidos en menú",
        "off_check": None,
        "off_text": None,
        "on_check": "assertVisible",
        "on_text": r".*[Ee]nv[ií]o [Mm]asivo.*|.*[Mm]assive.*",
    },
    "enableDialogNoSellReason": {
        "context": "menu",
        "description": "Opción 'Razón de no venta'",
        "off_check": None,
        "off_text": None,
        "on_check": "assertVisible",
        "on_text": r".*[Rr]az[oó]n.*[Nn]o.*[Vv]enta.*|.*[Nn]o [Ss]ell.*",
    },
    "enableSegmentsBySeller": {
        "context": "menu",
        "description": "Segmentos por vendedor en menú",
        "off_check": None,
        "off_text": None,
        "on_check": "assertVisible",
        "on_text": r".*[Ss]egmentos?.*",
    },
    "enableCreditStateMessage": {
        "context": "menu",
        "description": "Mensaje de estado de crédito",
        "off_check": None,
        "off_text": None,
        "on_check": "assertVisible",
        "on_text": r".*[Cc]r[eé]dito.*|.*[Cc]redit.*[Ss]tate.*",
    },

    # ── CATÁLOGO DE PRODUCTOS ─────────────────────────────────────────────────
    "hasMultiUnitEnabled": {
        "context": "catalogo",
        "description": "Selector DIS/UND (multi-unidad)",
        "off_check": "assertNotVisible",
        "off_text": r".*DIS.*|.*[Dd]isplay.*",
        "on_check": "assertVisible",
        "on_text": r"DIS|UND",
    },
    "useNewPromotions": {
        "context": "catalogo",
        "description": "Badge de promociones (PROMO / % descuento)",
        "off_check": "assertNotVisible",
        "off_text": r".*PROMO.*|.*%.*[Dd]escuento.*",
        "on_check": None,
        "on_text": None,
    },
    "hidePrices": {
        "context": "catalogo",
        "description": "Precios ocultos en catálogo",
        "off_check": None,
        "off_text": None,
        "on_check": "assertNotVisible",
        "on_text": r"\$\s*[0-9]+|[0-9]+\s*CLP",
    },
    "hasStockEnabled": {
        "context": "catalogo",
        "description": "Indicador de stock en productos",
        "off_check": None,
        "off_text": None,
        "on_check": "assertVisible",
        "on_text": r".*[Ss]tock.*|.*[Dd]isponible.*\s*[0-9]",
    },
    "weightInfo": {
        "context": "catalogo",
        "description": "Información de peso (Kg) en productos",
        "off_check": None,
        "off_text": None,
        "on_check": "assertVisible",
        "on_text": r".*[Kk]g.*|.*[Pp]eso.*",
    },
    "disableCart": {
        "context": "catalogo",
        "description": "Carrito deshabilitado (sin botón Agregar)",
        "off_check": None,
        "off_text": None,
        "on_check": "assertNotVisible",
        "on_text": r".*[Aa]gregar.*",
    },
    "disableShowOffer": {
        "context": "catalogo",
        "description": "Badge de oferta oculto en catálogo",
        "off_check": None,
        "off_text": None,
        "on_check": "assertNotVisible",
        "on_text": r".*[Oo]ferta.*|.*OFERTA.*",
    },
    "disableShowDiscount": {
        "context": "catalogo",
        "description": "Descuentos ocultos en catálogo",
        "off_check": None,
        "off_text": None,
        "on_check": "assertNotVisible",
        "on_text": r".*[Dd]escuento.*\d+%|.*\d+%.*[Dd]escuento.*",
    },
    "enableChooseSaleUnit": {
        "context": "catalogo",
        "description": "Selector de unidad de venta",
        "off_check": None,
        "off_text": None,
        "on_check": "assertVisible",
        "on_text": r".*[Uu]nidad.*[Vv]enta.*|.*[Ss]ale [Uu]nit.*",
    },
    "enableDistributionCentersSelector": {
        "context": "catalogo",
        "description": "Selector de centros de distribución",
        "off_check": "assertNotVisible",
        "off_text": r".*[Ss]eleccionar.*[Cc][Dd].*|.*[Cc]entro.*[Dd]istribuci[oó]n.*",
        "on_check": "assertVisible",
        "on_text": r".*[Cc]entro.*[Dd]istribuci[oó]n.*|.*[Ss]elect.*CD.*",
    },
    "enableDisableProductsBySeller": {
        "context": "catalogo",
        "description": "Vendedor puede habilitar/deshabilitar productos",
        "off_check": None,
        "off_text": None,
        "on_check": "assertVisible",
        "on_text": r".*[Hh]abilitar.*[Pp]roducto.*|.*[Dd]eshabilitar.*[Pp]roducto.*",
    },
    "disableWrongPrices": {
        "context": "catalogo",
        "description": "Alerta de precios incorrectos deshabilitada",
        "off_check": None,
        "off_text": None,
        "on_check": "assertNotVisible",
        "on_text": r".*[Pp]recio.*[Ii]ncorrecto.*|.*[Ww]rong.*[Pp]rice.*",
    },

    # ── CARRITO / CHECKOUT ────────────────────────────────────────────────────
    "enableSellerDiscount": {
        "context": "carrito",
        "description": "Opción 'Descuento Vendedor'",
        "off_check": "assertNotVisible",
        "off_text": r".*[Dd]escuento [Vv]endedor.*|.*[Aa]plicar [Dd]escuento.*",
        "on_check": "assertVisible",
        "on_text": r".*[Dd]escuento [Vv]endedor.*",
    },
    "enableCoupons": {
        "context": "carrito",
        "description": "Sección de cupones en carrito",
        "off_check": "assertNotVisible",
        "off_text": r".*[Cc]up[oó]n.*|.*[Cc]oupon.*",
        "on_check": "assertVisible",
        "on_text": r".*[Cc]up[oó]n.*|.*[Cc]oupon.*",
    },
    "purchaseOrderEnabled": {
        "context": "carrito",
        "description": "Campo Orden de compra / Nº pedido",
        "off_check": "assertNotVisible",
        "off_text": r".*[Oo]rden.*[Cc]ompra.*|.*OC\b.*|.*N[°º].*[Pp]edido.*",
        "on_check": "assertVisible",
        "on_text": r".*[Oo]rden.*[Cc]ompra.*|.*OC\b.*|.*N[°º].*[Pp]edido.*",
    },
    "enableAskDeliveryDate": {
        "context": "carrito",
        "description": "Selector de fecha de entrega",
        "off_check": "assertNotVisible",
        "off_text": r".*[Ff]echa.*[Ee]ntrega.*|.*[Ff]echa.*[Pp]edido.*",
        "on_check": "assertVisible",
        "on_text": r".*[Ff]echa.*[Ee]ntrega.*|.*[Ff]echa.*[Pp]edido.*",
    },
    "disableObservationInput": {
        "context": "carrito",
        "description": "Campo de observación/nota en checkout",
        "off_check": None,
        "off_text": None,
        "on_check": "assertNotVisible",
        "on_text": r".*[Oo]bservaci[oó]n.*|.*[Nn]ota.*[Pp]edido.*",
    },
    "hideReceiptType": {
        "context": "carrito",
        "description": "Selector tipo de documento (boleta/factura)",
        "off_check": None,
        "off_text": None,
        "on_check": "assertNotVisible",
        "on_text": r".*[Bb]oleta.*|.*[Ff]actura.*|.*[Rr]eceipt.*",
    },
    "taxes.showSummary": {
        "context": "carrito",
        "description": "Resumen de impuestos/IVA en carrito",
        "off_check": "assertNotVisible",
        "off_text": r".*[Ii]mpuesto.*|.*IVA.*",
        "on_check": "assertVisible",
        "on_text": r".*[Ii]mpuesto.*|.*IVA.*",
    },
    "hasTransferPaymentType": {
        "context": "carrito",
        "description": "Opción Transferencia en métodos de pago",
        "off_check": None,
        "off_text": None,
        "on_check": "assertVisible",
        "on_text": r".*[Tt]ransferencia.*|.*[Tt]ransfer.*",
    },
    "enableOrderApproval": {
        "context": "carrito",
        "description": "Flujo de aprobación de pedido",
        "off_check": None,
        "off_text": None,
        "on_check": "assertVisible",
        "on_text": r".*[Aa]probaci[oó]n.*|.*[Aa]pproval.*",
    },
    "enableOrderValidation": {
        "context": "carrito",
        "description": "Validación de pedido antes de enviar",
        "off_check": None,
        "off_text": None,
        "on_check": "assertVisible",
        "on_text": r".*[Vv]alidar.*[Pp]edido.*|.*[Vv]alidaci[oó]n.*",
    },
    "enableNegativeDiscount": {
        "context": "carrito",
        "description": "Descuento negativo (recargo) en carrito",
        "off_check": None,
        "off_text": None,
        "on_check": "assertVisible",
        "on_text": r".*[Rr]ecargo.*|.*[Dd]escuento.*[Nn]egativo.*",
    },
    "disableManualDiscount": {
        "context": "carrito",
        "description": "Descuento manual deshabilitado",
        "off_check": None,
        "off_text": None,
        "on_check": "assertNotVisible",
        "on_text": r".*[Dd]escuento.*[Mm]anual.*",
    },
    "ordersRequireVerification": {
        "context": "carrito",
        "description": "Pedido requiere verificación",
        "off_check": None,
        "off_text": None,
        "on_check": "assertVisible",
        "on_text": r".*[Vv]erificaci[oó]n.*",
    },
    "ordersRequireAuthorization": {
        "context": "carrito",
        "description": "Pedido requiere autorización",
        "off_check": None,
        "off_text": None,
        "on_check": "assertVisible",
        "on_text": r".*[Aa]utorizaci[oó]n.*",
    },
}

# ── Variables sin manifestación UI directa en APP ────────────────────────────
# Se incluyen como comentarios en el YAML generado para trazabilidad
BACKEND_ONLY = {
    "externalAccess": "Acceso externo (login alternativo, sin UI assertion directa)",
    "anonymousAccess": "Acceso anónimo sin login",
    "anonymousHidePrice": "Ocultar precios a usuarios anónimos",
    "anonymousHideCart": "Ocultar carrito a usuarios anónimos",
    "lazyLoadingPrices": "Precios lazy-loaded (backend, sin UI assertion)",
    "useMongoPricing": "Precios desde MongoDB vs ERP",
    "priceRoundingDecimals": "Redondeo de decimales en precios",
    "includeTaxRateInPrices": "Impuesto incluido en precio mostrado",
    "mustHaveOverride": "Requiere override de precio para vender",
    "autoSync": "Sincronización automática al abrir app",
    "disableSyncDate": "Ocultar fecha de última sincronización",
    "hooks.shippingHook": "Hook de cálculo de envío (backend)",
    "hooks.stockHook": "Hook de stock en tiempo real (backend)",
    "hooks.cartShoppingHook": "Hook de carrito (backend)",
    "hooks.getPendingDocumentsHook": "Hook de documentos pendientes (backend)",
    "hooks.updateTrafficLightHook": "Hook de semáforo de crédito (backend)",
    "synchronization.enableBackgroundSync": "Sync en background (sin UI directa)",
    "synchronization.enableBackgroundSendOrders": "Envío de pedidos en background",
    "synchronization.enableSyncImages": "Sincronización de imágenes",
    "synchronization.backgroundSyncList": "Colecciones para sync background",
    "synchronization.pendingDocumentsLookbackDays": "Días hacia atrás para documentos pendientes",
    "filterGroupedSuggestionsBy": "Agrupación de sugerencias (config backend)",
    "businessUnits": "Unidades de negocio configuradas",
    "orderObservations": "Observaciones predefinidas de pedido",
    "orderPolicy.creditExceededStatus": "Comportamiento al exceder crédito",
    "orderPolicy.retainBlockedCommerces": "Retener pedidos de comercios bloqueados",
    "orderPolicy.retainCreditBlockedCommerces": "Retener pedidos bloqueados por crédito",
    "orderPolicy.retainBelowMinimumOrder": "Retener pedidos bajo mínimo",
    "orderPolicy.sendRetainedOrdersToClientErp": "Enviar retenidos al ERP del cliente",
    "orderPolicy.overdueDebtConfiguration.blockSetting.enabled": "Bloqueo por deuda vencida",
    "orderPolicy.overdueDebtConfiguration.blockSettings.enabled": "Bloqueo por deuda vencida (alias)",
    "orderPolicy.overdueDebtConfiguration.blockSetting.thresholdDays": "Días umbral bloqueo deuda",
    "orderPolicy.overdueDebtConfiguration.blockSettings.thresholdDays": "Días umbral bloqueo deuda (alias)",
    "orderPolicy.overdueDebtConfiguration.retentionSetting.enabled": "Retención por deuda vencida",
    "orderPolicy.overdueDebtConfiguration.retentionSettings.enabled": "Retención por deuda vencida (alias)",
    "orderPolicy.overdueDebtConfiguration.retentionSetting.thresholdDays": "Días umbral retención deuda",
    "orderPolicy.overdueDebtConfiguration.retentionSettings.thresholdDays": "Días umbral retención (alias)",
    "orderPolicy.newPricePromotionsOverall": "Nuevas promociones de precio global",
    "payment.enableNewPaymentModule": "Nuevo módulo de pagos (flag migración)",
    "payment.requiresFullPayment": "Requiere pago completo antes de confirmar",
    "payment.consolidatePayments": "Consolidar pagos en uno solo",
    "payment.externalPayment": "Pago externo (redirige a URL)",
    "payment.walletEnabled": "Wallet habilitada",
    "payment.balances": "Balances de pago configurados",
    "enableNewPaymentModule": "Alias de payment.enableNewPaymentModule",
    "paymentsWithoutAccount": "Pagos sin cuenta bancaria",
    "validatePaymentFromAdmin": "Validación de pago desde admin",
    "packagingInformation.hidePackagingInformationB2B": "Info de empaque (B2B web, no APP)",
    "packagingInformation.hideSingleItemPackagingInformationB2B": "Info empaque item simple (B2B web)",
    "packagingInformation.ignoreUnitOnPackInformationB2B": "Ignorar unidad en info empaque (B2B web)",
    "packaging.amountUsesUnits": "Cantidad de empaque usa unidades",
    "discountTypes.enableOrderDiscountType": "Tipo de descuento a nivel de pedido",
    "discountTypes.enableProductDiscountType": "Tipo de descuento a nivel de producto",
    "discountTypes.discountTypesList": "Lista de tipos de descuento configurados",
    "adminConfiguration.showDiscountLimitAdmin": "Mostrar límite de descuento en admin",
    "productVariability": "Variabilidad de productos (none/simple/complex)",
    "productDetailViewConfiguration.tabsOrder": "Orden de tabs en detalle de producto",
    "productFormats.enableGenericFormats": "Formatos genéricos de producto",
    "productList.enableSuggestionByCategories": "Sugerencias por categoría",
    "suggestions.enableSortingByCategories": "Ordenamiento de sugerencias por categoría",
    "suggestions.hide": "Ocultar sección de sugerencias",
    "hasSeparatedSuggestions": "Sugerencias separadas del catálogo",
    "hasTransportCode": "Código de transporte en productos",
    "hasVoucherPrinterEnabled": "Impresora de vouchers habilitada",
    "hasAllDistributionCenters": "Acceso a todos los centros de distribución",
    "hasSingleDistributionCenter": "Solo un centro de distribución (sin selector)",
    "activateMultipleDistributionCenter": "Múltiples centros de distribución activos",
    "hasMultipleBusinessUnit": "Múltiples unidades de negocio",
    "limitAddingByStock": "Limitar cantidad a agregar según stock disponible",
    "useMobileGps": "Usar GPS del móvil para ubicación",
    "locationTrackerMtsDistance": "Distancia mínima para registrar ubicación GPS",
    "enablePriceOracle": "Precio oracle en tiempo real",
    "disableShowEstimatedDeliveryHour": "Ocultar hora estimada de entrega",
    "shareOrderNewDesign": "Nuevo diseño para compartir pedido",
    "shoppingDetail.lastOrder": "Ver detalle del último pedido",
    "enableBetaButtons": "Botones beta/experimentales visibles",
    "enableNewUI": "Nueva interfaz de usuario habilitada",
    "mobileAccess.passwordDisabled": "Login sin contraseña en móvil",
    "disableCommerceEdit": "Deshabilitar edición de datos del comercio",
    "editAddress": "Editar dirección del comercio desde app",
    "blockedClientAlert.enableBlockedClientAlert": "Alerta visual en comercios bloqueados",
    "blockedClientAlert.blockedClientAlertHtmlContent": "HTML de la alerta de bloqueo",
    "contact.about": "Texto 'Acerca de' en contacto",
    "contact.address": "Dirección de la empresa",
    "contact.phone": "Teléfono de contacto",
    "contact.email": "Email de contacto",
    "contact.branchesContactInformation": "Info de contacto por sucursal",
    "footerCustomContent.useFooterCustomContent": "Footer personalizado habilitado",
    "footerCustomContent.footerCustomHtmlContent": "HTML del footer personalizado",
    "logo3": "Logo alternativo de la app",
    "confirmCartText": "Texto de confirmación en carrito",
    "orderTypes": "Tipos de pedido disponibles",
    "enableOrderAproval": "Alias de enableOrderApproval (typo en DB)",
    "uploadOrderFileWithMinUnits": "Subir archivo de pedido con unidades mínimas",
    "disablePayments": "Alias inverso de enablePayments",
    "retainBlockedCommerces": "Retener pedidos de comercios bloqueados (alias)",
    "flagFeatures.reactNativeOrderTaker": "App React Native habilitada",
    "flagFeatures.reactNativeOrderTakerForAll": "App React Native para todos los vendedores",
    "flagFeatures.reactNativeOrderTakerSellers": "Lista de vendedores con React Native",
    "flagFeatures.enableCreditNoteApplication": "Aplicación de notas de crédito habilitada",
    "taxes.taxRate": "Tasa de impuesto configurada (numérico)",
    "taxes.useTaxRate": "Usar tasa de impuesto personalizada",
    "wrongPrices.block": "Bloquear pedido si hay precios incorrectos",
    "wrongPrices.threshold": "Umbral de diferencia para precio incorrecto",
    "enablePaymentDocumentsB2B": "Módulo documentos de pago (solo B2B web, no APP)",
    "showEmptyCategories": "Categorías vacías visibles en catálogo",
    "showMinOne": "Mostrar mínimo una unidad por producto",
    "enableWeekendDeliveryDate": "Permite fecha de entrega en fin de semana",
    "enablePriceOracle": "Oracle de precios en tiempo real",
}


def load_matrix(env):
    root = Path(__file__).parent.parent
    matrix_file = root / "data" / ("qa-matrix.json" if env == "production" else "qa-matrix-staging.json")
    if not matrix_file.exists():
        print(f"❌ Archivo no encontrado: {matrix_file}", file=sys.stderr)
        sys.exit(1)
    with open(matrix_file) as f:
        data = json.load(f)
    return data.get("clients", {})


def find_client(clients, slug, env):
    suffix = "-staging" if env == "staging" else ""
    for key in [slug + suffix, slug]:
        if key in clients:
            return key, clients[key]
    for key, val in clients.items():
        if key.startswith(slug):
            return key, val
    return None, None


def get_var(variables, flag):
    val = variables.get(flag)
    if val is None:
        return None
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return bool(val)
    if isinstance(val, str):
        return val.lower() not in ("false", "0", "")
    return bool(val)


def gen_block(check, text, description):
    return "\n".join([
        f"# {description}",
        f"- {check}:",
        f'    text: "{text}"',
    ])


def generate_yaml(client_key, client_data):
    variables = client_data.get("variables", {})
    name = client_data.get("name", client_key)
    domain = client_data.get("domain", "")

    by_ctx = {}
    for flag, spec in FEATURE_MAP.items():
        val = get_var(variables, flag)
        if val is None:
            continue
        ctx = spec["context"]
        if not val:
            check, text = spec.get("off_check"), spec.get("off_text")
            label = f"{spec['description']} — INVISIBLE ({flag}: false)"
        else:
            check, text = spec.get("on_check"), spec.get("on_text")
            label = f"{spec['description']} — VISIBLE ({flag}: true)"
        if check and text:
            by_ctx.setdefault(ctx, []).append(gen_block(check, text, label))

    backend_present = {f: d for f, d in BACKEND_ONLY.items() if f in variables}
    known = set(FEATURE_MAP.keys()) | set(BACKEND_ONLY.keys())
    unknown = [f for f in variables if f not in known]

    lines = [
        "appId: ${APP_PACKAGE}",
        f'name: "Verificación features ON/OFF — {name}"',
        "# GENERADO AUTOMÁTICAMENTE por tools/gen-maestro-features.py",
        f"# Fuente: {domain} (variables MongoDB reales)",
        "# Regenerar: python3 tools/gen-maestro-features.py <cliente>",
        "---",
        "",
    ]

    has_login = "login" in by_ctx
    has_lista = "lista" in by_ctx
    has_menu = "menu" in by_ctx
    has_catalogo = "catalogo" in by_ctx
    has_carrito = "carrito" in by_ctx

    # 1. Login
    if has_login:
        lines += [
            "# ── Pantalla de login ─────────────────────────────────────────────",
            "- launchApp:",
            "    clearState: true",
            "- waitForAnimationToEnd",
            "",
        ]
        for block in by_ctx["login"]:
            lines += [block, ""]

    # 2. Lista de comercios
    lines += [
        "# ── Startup → lista de comercios ─────────────────────────────────────",
        "- runFlow: helpers-startup.yaml",
        "",
    ]
    if has_lista:
        lines += ["# ── Lista de comercios ───────────────────────────────────────────"]
        for block in by_ctx["lista"]:
            lines += [block, ""]

    # 3. Menú lateral
    if has_menu:
        lines += [
            "# ── Menú lateral (drawer) ─────────────────────────────────────────",
            "- tapOn:",
            '    text: ".*[Mm]en[úu].*|.*[Hh]amburger.*"',
            "    optional: true",
            "- waitForAnimationToEnd",
            "",
        ]
        for block in by_ctx["menu"]:
            lines += [block, ""]
        lines += [
            "- back",
            "- waitForAnimationToEnd",
            "",
        ]

    # 4. Catálogo
    if has_catalogo or has_carrito:
        lines += [
            "# ── Entrar a comercio disponible ─────────────────────────────────",
            "- runFlow: helpers-filtro-disponible.yaml",
            "- tapOn:",
            r"    text: '.*\d{7,}.*'",
            "    index: 0",
            "    optional: true",
            "- extendedWaitUntil:",
            "    visible:",
            '      text: "Continuar|.*[Hh]acer [Pp]edido.*|.*[Cc]at[aá]logo.*"',
            "    timeout: 15000",
            "- tapOn:",
            '    text: "Continuar"',
            "    optional: true",
            "- waitForAnimationToEnd",
            "- tapOn:",
            '    text: ".*[Hh]acer [Pp]edido.*|.*[Cc]at[aá]logo.*|.*[Pp]roductos.*"',
            "    optional: true",
            "- extendedWaitUntil:",
            "    visible:",
            '      text: ".*[Aa]gregar.*|.*[Cc]at[aá]logo.*|.*[Pp]roducto.*"',
            "    timeout: 20000",
            "",
        ]
        if has_catalogo:
            lines += ["# ── Catálogo: checks de features ─────────────────────────────────"]
            for block in by_ctx["catalogo"]:
                lines += [block, ""]

    # 5. Carrito
    if has_carrito:
        lines += [
            "# ── Agregar producto y ver carrito ───────────────────────────────",
            "- tapOn:",
            '    text: ".*[Aa]gregar.*"',
            "    index: 0",
            "    optional: true",
            "- waitForAnimationToEnd",
            "",
            "# ── Carrito: checks de features ──────────────────────────────────",
        ]
        for block in by_ctx["carrito"]:
            lines += [block, ""]

    lines += [
        "# ── Volver a lista ───────────────────────────────────────────────────",
        "- runFlow: helpers-volver-lista.yaml",
    ]

    # Variables backend (comentarios informativos)
    if backend_present or unknown:
        lines += [
            "",
            "# ════════════════════════════════════════════════════════════════════",
            "# Variables MongoDB sin assertion UI en APP (verificar manualmente)",
            "# ════════════════════════════════════════════════════════════════════",
        ]
        for flag, desc in sorted(backend_present.items()):
            val_repr = variables.get(flag)
            lines.append(f"# [{flag}={val_repr!r}] {desc}")
        for flag in sorted(unknown):
            val_repr = variables.get(flag)
            lines.append(f"# [{flag}={val_repr!r}] (sin mapeo — revisar)")

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Genera 04-features.yaml desde qa-matrix")
    parser.add_argument("cliente", help="Slug del cliente (ej: caren, prinorte)")
    parser.add_argument("--env", choices=["staging", "production"], default="staging")
    parser.add_argument("--dry-run", action="store_true", help="Mostrar YAML sin escribir archivo")
    args = parser.parse_args()

    clients = load_matrix(args.env)
    client_key, client_data = find_client(clients, args.cliente, args.env)

    if not client_data:
        print(f"❌ Cliente '{args.cliente}' no encontrado en matrix ({args.env})", file=sys.stderr)
        print(f"   Clientes: {', '.join(sorted(clients.keys()))}", file=sys.stderr)
        sys.exit(1)

    variables = client_data.get("variables", {})
    print(f"✅ Cliente: {client_key} — {client_data.get('name', '')}")
    print(f"   Dominio: {client_data.get('domain', '')}")
    print(f"   Variables MongoDB: {len(variables)}")

    yaml_content = generate_yaml(client_key, client_data)

    if args.dry_run:
        print("\n" + "─" * 60)
        print(yaml_content)
        return

    root = Path(__file__).parent.parent
    out_path = root / "tests" / "app" / "flows" / args.cliente / "04-features.yaml"
    if not out_path.parent.exists():
        print(f"❌ Directorio no existe: {out_path.parent}", file=sys.stderr)
        sys.exit(1)

    out_path.write_text(yaml_content)
    print(f"✅ Generado: {out_path.relative_to(root)}")

    # Resumen de cobertura
    with_assert, without_assert = [], []
    for flag, spec in FEATURE_MAP.items():
        val = get_var(variables, flag)
        if val is None:
            continue
        check = spec.get("off_check") if not val else spec.get("on_check")
        (with_assert if check else without_assert).append(flag)

    backend_present = [f for f in BACKEND_ONLY if f in variables]
    known = set(FEATURE_MAP.keys()) | set(BACKEND_ONLY.keys())
    unknown = [f for f in variables if f not in known]

    print(f"\n   Cobertura:")
    print(f"   ✓ {len(with_assert)} assertions generadas")
    print(f"   – {len(without_assert)} flags sin assertion UI (ON sin texto conocido)")
    print(f"   📋 {len(backend_present)} variables backend (comentarios en YAML)")
    if unknown:
        print(f"   ⚠  {len(unknown)} variables sin mapeo: {', '.join(unknown)}")


if __name__ == "__main__":
    main()

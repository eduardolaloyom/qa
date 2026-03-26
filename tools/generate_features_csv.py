"""
generate_features_csv.py

Generates features-clientes-2026.csv by cross-referencing:
  1. Site-variable Excel files (13 clients) from /Users/lalojimenez/Downloads/Reglas Sites/
  2. Feature Notion CSV with feature metadata
  3. A FEATURE_TO_VARIABLES mapping that links features to site variables

Logic:
  - If a feature has an empty variable list → it's a "base feature", active for ALL clients.
  - Otherwise, a feature is active for a client if ANY mapped variable is truthy
    (or falsy for inverted variables like disableXxx).

NOTE: PeM 2026 clients without Excel files (Prinorte, Caren, El Muñeco, Pil Andina)
are included ONLY in base features (those with an empty variable list) since we don't
have their site-variable data yet. Once their sites are configured, their Excel exports
should be added to regenerate with full variable-based detection.
"""

import csv
import os
from pathlib import Path
from typing import Any, Dict, List, Set

# Try openpyxl first, fall back to xlrd if needed
try:
    import openpyxl
except ImportError:
    raise ImportError("openpyxl is required: pip install openpyxl")


# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────

EXCEL_DIR = Path("/Users/lalojimenez/Downloads/Reglas Sites/")
FEATURE_NOTION_CSV = Path("/Users/lalojimenez/Downloads/Reglas Clientes - Feature Notion.csv")
OUTPUT_CSV = Path("/Users/lalojimenez/Desktop/YOM/qa/features-clientes-2026.csv")

# Client name mapping: Excel filename key → display name
FILENAME_TO_CLIENT = {
    "americas": "GlobalWines",
    "bastien": "Bastién",
    "cedisur": "Cedisur",
    "codelpa-peru": "Codelpa Perú",
    "codelpa": "Codelpa",
    "coexito": "Coéxito",
    "expressdent.youorder.me": "ExpressDent",
    "marleycoffee": "Marley Coffee",
    "prisur": "Prisa",
    "softys-cencocal": "Softys-Cencocal",
    "softys-dimak": "Softys-Dimak",
    "soprole": "Soprole",
    "surtiventas": "Surtiventas",
}

# PeM 2026 clients without Excel files — only added to base features
PEM_2026_EXTRA_CLIENTS = ["Prinorte", "Caren", "El Muñeco", "Pil Andina"]

# Variables that use inverted logic: feature is active when value is FALSE
INVERTED_VARIABLES = {
    "disableObservationInput",
    "disableManualDiscount",
    "disablePayments",
    "disableWrongPrices",
    "disableCart",
    "disableCommerceEdit",
    "disableShowEstimatedDeliveryHour",
}

# Variables that are "truthy" if they exist and are non-empty (not just boolean True)
TRUTHY_STRING_VARIABLES = {
    "analyticsTrackingId",
    "favicon",
    "contact.about",
    "contact.email",
    "contact.phone",
    "icon",
    "icons",
    "weightInfo",
    "businessUnits",
    "signupForm.fields",
    "confirmCartText",
    "orderTypes",
    "filterGroupedSuggestionsBy",
}

FEATURE_TO_VARIABLES: Dict[str, List[str]] = {
    "Acciones automáticas": [],
    "Agregar fecha despacho": ["enableAskDeliveryDate"],
    "Agregar observaciones": ["disableObservationInput"],  # INVERTED
    "Anuncio": [],
    "Banners": [],
    "Bloqueo": ["blockedClientAlert.enableBlockedClientAlert"],
    "Bloqueo de carro en casos de precios anómalos": ["wrongPrices.block", "disableWrongPrices"],
    "Botones de acceso configurables (deprecado)": ["enableBetaButtons"],
    "Búsqueda de comercios": [],
    "Búsqueda de productos": [],
    "Cambio de contraseña": ["mobileAccess.passwordDisabled"],
    "Cambios de formato": ["enableChooseSaleUnit", "hasMultiUnitEnabled"],
    "Canasta base": ["filterGroupedSuggestionsBy", "productList.enableSuggestionByCategories"],
    "Canasta Estratégica: Exploración": ["productList.enableSuggestionByCategories"],
    "Canasta Estratégica: Foco": [],
    "Canasta Estratégica: General": [],
    "Canasta Estratégica: Innovación": [],
    "Carro de compras": [],
    "Catálogo": [],
    "Clientes": [],
    "Cobranza y facturación": ["enablePaymentsCollection", "enablePayments", "enablePaymentDocumentsB2B", "pendingDocuments"],
    "Combos": [],
    "Compartir el pedido": [],
    "Compartir la sugerencia": [],
    "Compra mínima": ["showMinOne"],
    "Configuraciones": [],
    "Contacto": ["contact.about", "contact.email", "contact.phone"],
    "Creación de cuentas": ["commerce.enableCreateCommerce"],
    "Creación de roles para administradores": [],
    "Crear pedido": [],
    "Cupón de descuento": ["enableCoupons"],
    "Dashboards": [],
    "Descuentos manuales": ["enableSellerDiscount", "disableManualDiscount"],
    "Descuentos por volumen": ["useNewPromotions"],
    "Detalle del producto": [],
    "Documentos manuales": ["pendingDocuments", "enablePaymentDocumentsB2B"],
    "Edición de store": [],
    "Escalones obligados": [],
    "Estado crediticio": ["enableCreditStateMessage", "hooks.updateTrafficLightHook"],
    "Estado de retención": [],
    "Estados de orden según ERP": ["enableOrderValidation", "hooks.shippingHook"],
    "Exportación de datos": [],
    "FAQ": ["footerCustomContent.useFooterCustomContent"],
    "Favicon": ["favicon"],
    "Filtros de comercios": ["hasNoSaleFilter"],
    "Filtros de productos": [],
    "Funcionamiento offline": ["synchronization.enableBackgroundSync", "synchronization.enableBackgroundSendOrders"],
    "Georreferencia": ["useMobileGps"],
    "Gestión comercial": [],
    "Gestión de administradores": [],
    "Gestión de pedidos": ["enableMassiveOrderSend", "enableOrderApproval", "ordersRequireAuthorization"],
    "Gestión de tareas": ["enableTask"],
    "Historial de facturas": ["enableInvoicesList", "enablePaymentDocumentsB2B"],
    "Historial de pagos": ["enablePayments", "enablePaymentsCollection"],
    "Historial de pedidos": [],
    "Icons": ["icon", "icons"],
    "Impresión": ["hasVoucherPrinterEnabled"],
    "Impuestos para productos": ["includeTaxRateInPrices", "taxes.useTaxRate"],
    "Ingreso productos (deprecada)": [],
    "Integración con Google Analytics": ["analyticsTrackingId"],
    "Inyección de recomendaciones": ["filterGroupedSuggestionsBy"],
    "Inyectar pedido": ["hooks.shippingHook"],
    "Jobs de integración": [],
    "Justificaciones": ["enableDialogNoSellReason"],
    "Labels en productos": [],
    "Limitación productos": ["limitAddingByStock"],
    "Límite de descuento": ["enableSellerDiscount", "adminConfiguration.showDiscountLimitAdmin"],
    "List view (admin)": [],
    "Lista categorías": ["showEmptyCategories"],
    "Lista de comercios": ["commerce.enableCreateCommerce", "disableCommerceEdit"],
    "Lista de cotizaciones (deprecada)": ["purchaseOrderEnabled"],
    "Listas de precio": ["useMongoPricing", "mustHaveOverride"],
    "Log in App": ["mobileAccess.passwordDisabled"],
    "Log in B2B": ["anonymousAccess", "externalAccess", "loginButtons.facebook", "loginButtons.google", "hasLoginImage"],
    "Máximos de compra (items)": ["limitAddingByStock"],
    "Método de pago": ["enablePayments", "disablePayments", "payment.enableNewPaymentModule"],
    "Minibanners": [],
    "Mínimos de compra (productos)": ["showMinOne"],
    "Notificaciones push": [],
    "Notificaciones push app": [],
    "Notificaciones y alertas": ["blockedClientAlert.enableBlockedClientAlert"],
    "Ordenar": [],
    "Packs de productos": [],
    "Pedido Sugerido": ["filterGroupedSuggestionsBy", "productList.enableSuggestionByCategories"],
    "Precio despacho": ["hooks.shippingHook", "disableShowEstimatedDeliveryHour"],
    "Precio futuro": ["enablePriceOracle"],
    "Precio unitario": ["weightInfo"],
    "Precios brutos o neto": ["includeTaxRateInPrices", "taxes.useTaxRate"],
    "Priorización de visitas y acción": [],
    "Promociones de catálogo": ["useNewPromotions"],
    "Promociones personalizadas": ["useNewPromotions"],
    "Prompt Analytics": [],
    "Re-hacer un pedido anterior": ["shoppingDetail.lastOrder"],
    "Recaudación diaria": ["enablePaymentsCollection"],
    "Redirección a pago de facturas": ["enablePayments", "payment.externalPayment", "enablePaymentDocumentsB2B"],
    "Regalos": [],
    "Registro de visita": [],
    "Registro por # cliente": ["signupForm.fields"],
    "Registros de visitas": ["enableTask"],
    "Resumen de venta": [],
    "Ruta del día": [],
    "Seguimiento de pedidos": ["enableOrderValidation"],
    "Selección de método de pago": ["enablePayments", "disablePayments", "hideReceiptType", "payment.enableNewPaymentModule"],
    "Separación de marcas": ["businessUnits", "hasMultipleBusinessUnit"],
    "Sincronización de sistemas": ["synchronization.enableBackgroundSync", "synchronization.enableBackgroundSendOrders", "synchronization.enableSyncImages"],
    "Soporte": [],
    "Ticket promedio": [],
    "Tomador de pedidos": [],
    "Transferencia de pedidos": ["enableMassiveOrderSend"],
    "Visibilidad y acceso al catálogo": ["anonymousAccess", "anonymousHideCart", "anonymousHidePrice", "externalAccess"],
    "Vista de catálogo post-registro": ["anonymousAccess"],
    "Visualización de datos comercio": ["enableCreditStateMessage"],
    "Visualización de stock": ["hasStockEnabled", "hooks.stockHook"],
}


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def extract_key_from_filename(filename: str) -> str:
    """Extract the client key from an Excel filename like 'Reglas_americas.xlsx'."""
    return filename.replace("Reglas_", "").replace(".xlsx", "")


def is_variable_active(var_name: str, value: Any) -> bool:
    """
    Determine if a variable's value means the associated feature is active.

    - Inverted variables (disableXxx): active when value is False/falsy
    - Truthy-string variables: active when value exists and is non-empty
    - All others: active when value is True (boolean) or truthy
    """
    if var_name in INVERTED_VARIABLES:
        # Active when the value is explicitly False or falsy
        if isinstance(value, bool):
            return not value
        if isinstance(value, (int, float)):
            return value == 0
        if isinstance(value, str):
            return value.lower() in ("false", "0", "", "no")
        return not value

    if var_name in TRUTHY_STRING_VARIABLES:
        # Active when value exists and is non-empty
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            stripped = value.strip()
            # Empty string or empty array representation
            if stripped in ("", "[]", "{}", "null", "None"):
                return False
            # Could be a string "false"
            if stripped.lower() == "false":
                return False
            return True
        if isinstance(value, (int, float)):
            return value != 0
        return bool(value)

    # Standard boolean/truthy check
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lower = value.strip().lower()
        if lower in ("true", "1", "yes"):
            return True
        if lower in ("false", "0", "no", "", "null", "none"):
            return False
        # Non-empty string that's not a known false → truthy
        return True
    if isinstance(value, (int, float)):
        return value != 0
    if value is None:
        return False
    return bool(value)


def load_excel_variables(filepath: Path) -> Dict[str, Any]:
    """Load the Variables sheet from an Excel file into a key→value dict.

    Handles two formats:
      - Standard: columns [key, value] (2 columns)
      - Extended: columns [spreadsheetId, domain, spreadsheetIdCol, key, value] (5 columns)
    """
    wb = openpyxl.load_workbook(str(filepath), read_only=True, data_only=True)
    ws = wb["Variables"]
    variables = {}
    header = None
    key_col = None
    val_col = None

    for row in ws.iter_rows(values_only=True):
        if header is None:
            header = row
            # Detect column layout
            header_strs = [str(h).strip() if h else "" for h in header]
            if "key" in header_strs and "value" in header_strs:
                key_col = header_strs.index("key")
                val_col = header_strs.index("value")
            else:
                # Fallback: assume first two columns
                key_col = 0
                val_col = 1
            continue

        if row is None or len(row) <= max(key_col, val_col):
            continue

        key = row[key_col]
        value = row[val_col]
        if key is None:
            continue
        key = str(key).strip()
        if key:
            variables[key] = value

    wb.close()
    return variables


def load_feature_metadata(csv_path: Path) -> Dict[str, Dict[str, str]]:
    """Load feature metadata from the Notion CSV, indexed by Feature name."""
    metadata = {}
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            feature = row.get("Feature", "").strip()
            if feature:
                metadata[feature] = row
    return metadata


def is_feature_active_for_client(feature: str, client_vars: Dict[str, Any]) -> bool:
    """
    Determine if a feature is active for a client based on their variables.

    - Empty variable list → always active (base feature)
    - Otherwise → active if ANY mapped variable is active
    """
    variables = FEATURE_TO_VARIABLES.get(feature, None)
    if variables is None:
        # Feature not in mapping — treat as base feature
        return True
    if len(variables) == 0:
        # Base feature — active for all
        return True

    for var_name in variables:
        if var_name in client_vars:
            if is_variable_active(var_name, client_vars[var_name]):
                return True
    return False


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    # 1. Load all Excel files → client variables
    print("Loading Excel files...")
    client_variables: Dict[str, Dict[str, Any]] = {}  # display_name → variables

    excel_files = sorted(EXCEL_DIR.glob("Reglas_*.xlsx"))
    print(f"  Found {len(excel_files)} Excel files")

    for filepath in excel_files:
        key = extract_key_from_filename(filepath.name)
        display_name = FILENAME_TO_CLIENT.get(key)
        if display_name is None:
            print(f"  WARNING: No display name mapping for key '{key}' (file: {filepath.name})")
            continue
        variables = load_excel_variables(filepath)
        client_variables[display_name] = variables
        print(f"  Loaded {display_name}: {len(variables)} variables")

    # 2. Load feature metadata from Notion CSV
    print("\nLoading Feature Notion CSV...")
    feature_metadata = load_feature_metadata(FEATURE_NOTION_CSV)
    print(f"  Loaded {len(feature_metadata)} features")

    # 3. All clients: Excel-based + PeM 2026 extras
    all_excel_clients = sorted(client_variables.keys())
    all_clients = sorted(set(all_excel_clients + PEM_2026_EXTRA_CLIENTS))
    print(f"\nTotal clients: {len(all_clients)} ({len(all_excel_clients)} from Excel + {len(PEM_2026_EXTRA_CLIENTS)} PeM 2026 extras)")

    # 4. For each feature, determine which clients have it active
    print("\nProcessing features...")
    output_rows = []

    # Use FEATURE_TO_VARIABLES keys as the canonical feature list,
    # but also include any features from the CSV that aren't in the mapping
    all_features_in_mapping = set(FEATURE_TO_VARIABLES.keys())
    all_features_in_csv = set(feature_metadata.keys())

    # Process features in the order they appear in the CSV
    features_ordered = []
    with open(FEATURE_NOTION_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            feat = row.get("Feature", "").strip()
            if feat:
                features_ordered.append(feat)

    features_not_in_mapping = all_features_in_csv - all_features_in_mapping
    if features_not_in_mapping:
        print(f"  NOTE: {len(features_not_in_mapping)} features in CSV but not in FEATURE_TO_VARIABLES (treated as base features):")
        for f in sorted(features_not_in_mapping):
            print(f"    - {f}")

    for feature in features_ordered:
        variables_list = FEATURE_TO_VARIABLES.get(feature, [])
        is_base = len(variables_list) == 0

        active_clients = []

        for client_name in sorted(all_clients):
            if client_name in PEM_2026_EXTRA_CLIENTS:
                # PeM 2026 extras only get base features
                if is_base:
                    active_clients.append(client_name)
            else:
                # Excel-based client: check variables
                client_vars = client_variables.get(client_name, {})
                if is_feature_active_for_client(feature, client_vars):
                    active_clients.append(client_name)

        # Get metadata from Notion CSV
        meta = feature_metadata.get(feature, {})

        # Determine Cliente column value
        if is_base and len(active_clients) == len(all_clients):
            cliente_str = "Todos"
        else:
            cliente_str = ", ".join(active_clients)

        output_rows.append({
            "Feature": feature,
            "Objetivo": meta.get("Objetivo", ""),
            "Producto": meta.get("Producto", ""),
            "Herramientas": meta.get("Herramientas", ""),
            "Cliente": cliente_str,
            "Req. Integración": meta.get("Req. Integración", ""),
        })

    # 5. Write output CSV
    print(f"\nWriting output CSV to {OUTPUT_CSV}...")
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["Feature", "Objetivo", "Producto", "Herramientas", "Cliente", "Req. Integración"]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"  Done! Wrote {len(output_rows)} features.")

    # 6. Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total features:  {len(output_rows)}")
    print(f"Total clients:   {len(all_clients)}")
    print(f"  Excel clients: {', '.join(all_excel_clients)}")
    print(f"  PeM 2026 new:  {', '.join(PEM_2026_EXTRA_CLIENTS)}")

    # Count base vs variable features
    base_count = sum(1 for f in features_ordered if len(FEATURE_TO_VARIABLES.get(f, [])) == 0)
    var_count = len(features_ordered) - base_count
    print(f"\nBase features (all clients): {base_count}")
    print(f"Variable-dependent features: {var_count}")

    # Sample of 5 non-base features with their clients
    print("\nSample of 5 features with client assignments:")
    print("-" * 70)
    sample_count = 0
    for row in output_rows:
        if row["Cliente"] != "Todos" and row["Cliente"]:
            print(f"  {row['Feature']}")
            print(f"    Clients: {row['Cliente']}")
            print()
            sample_count += 1
            if sample_count >= 5:
                break


if __name__ == "__main__":
    main()

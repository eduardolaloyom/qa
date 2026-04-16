"""
mongo-extractor.py

Connects to MongoDB (yom-stores + yom-production), extracts site variables,
salesterms, and customers for all real clients, and generates qa-matrix.json
as the single source of truth for the QA system.

Usage:
    python data/mongo-extractor.py
    python data/mongo-extractor.py --cliente Soprole
    python data/mongo-extractor.py --env staging
    python data/mongo-extractor.py --env production
    python data/mongo-extractor.py --output custom-output.json

Requires: pymongo[srv]
    pip install pymongo[srv]
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from pymongo import MongoClient
except ImportError:
    print("pymongo is required: pip install pymongo[srv]")
    sys.exit(1)


# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────

def _load_env():
    """Load .env file from qa/ root."""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())

_load_env()

def _get_uris(env: str):
    """Return (legacy, micro, integrations) URIs for the given env."""
    if env == "staging":
        legacy = os.environ.get("MONGO_LEGACY_STAGING_URI", "")
        micro  = os.environ.get("MONGO_MICRO_STAGING_URI", "")
        integr = os.environ.get("MONGO_INTEGRATIONS_STAGING_URI", "")
    else:  # production (default)
        legacy = os.environ.get("MONGO_LEGACY_URI", "")
        micro  = os.environ.get("MONGO_MICRO_URI", "")
        integr = os.environ.get("MONGO_INTEGRATIONS_URI", "")
    return legacy, micro, integr

# URIs are resolved after args are parsed (see bottom of file)
# These are set as module-level vars for backwards compatibility
LEGACY_URI = ""
MICRO_URI = ""
INTEGRATIONS_URI = ""

# Real production clients (domain → display name)
# Only production (.youorder.me) domains need to be listed explicitly —
# staging (.solopide.me) domains are auto-discovered from the sites collection.
REAL_CLIENTS = {
    "bastien.youorder.me": "Bastien",
    "cedisur.youorder.me": "Cedisur",
    "coexito.youorder.me": "CoExito",
    "codelpa.youorder.me": "Codelpa",
    "codelpa-peru.youorder.me": "Codelpa Peru",
    "elmuneco.youorder.me": "El Muneco",
    "expressdent.youorder.me": "ExpressDent",
    "americas.youorder.me": "Las Americas",
    "marleycoffee.youorder.me": "Marley Coffee",
    "prinorte.youorder.me": "Prinorte",
    "prisa.youorder.me": "Prisa",
    "prisur.youorder.me": "Prisur",
    "soprole.youorder.me": "Soprole",
    "new-soprole.youorder.me": "Soprole (new)",
    "surtiventas.youorder.me": "Surtiventas",
    "softys-cencocal.youorder.me": "Softys-Cencocal",
    "softys-dimak.youorder.me": "Softys-Dimak",
}

# Staging domains to exclude from auto-discovery (dev/test/personal environments)
STAGING_EXCLUDE_DOMAINS = {
    "almacen2.solopide.me",
    "carlos.solopide.me",
    "customerprueba.solopide.me",
    "danieltest.solopide.me",
    "dbsync.solopide.me",
    "despacho.solopide.me",
    "dominiofalso.solopide.me",
    "duracell-salma.solopide.me",
    "equipotest.solopide.me",
    "erik-agro.solopide.me",
    "erik-codelpa.solopide.me",
    "fakedomain.solopide.me",
    "grupo1.solopide.me",
    "grupo2.solopide.me",
    "i2btest.solopide.me",
    "nicolas.solopide.me",
    "panchita.solopide.me",
    "puntodeventa.solopide.me",
    "santiago.solopide.me",
    "testdomain5.solopide.me",
    "tienda.solopide.me",
    "tropi2.solopide.me",
    "vicente.solopide.me",
    "weavee.solopide.me",
}

# Fields to exclude from extraction (metadata, branding, visual)
EXCLUDE_FIELDS = {
    "_id", "__v", "createdAt", "updatedAt",
    "analyticsTrackingId", "hjid", "favicon", "icon", "iconImage", "icons",
    "logo", "emailLogo", "invertedLogo", "loginImage", "loginImageMosaic",
    "hasLoginImage", "navBarColor", "primaryColor", "secondaryColor",
    "maintenanceImage", "maintenanceText",
    "aliases", "subDomains", "mainDomain", "emailName",
    "customButtons", "signupForm",
    "additionalHomeConfigs",
}

# Variables with inverted logic (feature active when value is False)
INVERTED_VARIABLES = {
    "disableObservationInput",
    "disableManualDiscount",
    "disablePayments",
    "disableWrongPrices",
    "disableCart",
    "disableCommerceEdit",
    "disableShowEstimatedDeliveryHour",
}

# ─────────────────────────────────────────────
# Test-to-variable mapping
# ─────────────────────────────────────────────

# Standard tests (apply to all clients)
STANDARD_TESTS = [
    "C1-01", "C1-02", "C1-03", "C1-04", "C1-05", "C1-06", "C1-07", "C1-08", "C1-09", "C1-10",
    "C2-01", "C2-02", "C2-03", "C2-04", "C2-05", "C2-06", "C2-07", "C2-08", "C2-09", "C2-10",
    "C2-11", "C2-12", "C2-13", "C2-14", "C2-15",
    "C3-01", "C3-02", "C3-03", "C3-04", "C3-05", "C3-06", "C3-07", "C3-08", "C3-09", "C3-10",
    "C3-11", "C3-12", "C3-13", "C3-14", "C3-15", "C3-16",
    "C4-01", "C4-02", "C4-03", "C4-04", "C4-05", "C4-06", "C4-07", "C4-08",
    "C5-01", "C5-02", "C5-03", "C5-04", "C5-05", "C5-06", "C5-07", "C5-08",
    "C6-01", "C6-02", "C6-03", "C6-04", "C6-05", "C6-06", "C6-07", "C6-08", "C6-09", "C6-10",
    "V1-01", "V1-02", "V1-03", "V1-04", "V1-05", "V1-06", "V1-07", "V1-08", "V1-09", "V1-10",
]

# Conditional tests: test_id → (condition_function_on_variables, variable_names)
# condition_function receives the flat variables dict and returns True if the test applies
CONDITIONAL_TESTS = {
    # C1 - Login
    "C1-A1": (lambda v: v.get("anonymousAccess") is True, ["anonymousAccess", "anonymousHideCart", "anonymousHidePrice"]),
    "C1-A2": (lambda v: v.get("externalAccess") is True, ["externalAccess"]),
    "C1-A3": (lambda v: v.get("mobileAccess.passwordDisabled") is True, ["mobileAccess.passwordDisabled"]),
    # C2 - Compra
    "C2-E1": (lambda v: v.get("disableCart") is True, ["disableCart"]),
    "C2-E2": (lambda v: v.get("limitAddingByStock") is True, ["limitAddingByStock", "hasStockEnabled"]),
    "C2-E3": (lambda v: v.get("ordersRequireAuthorization") is True, ["ordersRequireAuthorization"]),
    "C2-E4": (lambda v: v.get("enableOrderApproval") is True, ["enableOrderApproval"]),
    "C2-E5": (lambda v: v.get("enableMassiveOrderSend") is True, ["enableMassiveOrderSend"]),
    "C2-E6": (lambda v: v.get("enableChooseSaleUnit") is True, ["enableChooseSaleUnit"]),
    "C2-E7": (lambda v: v.get("uploadOrderFileWithMinUnits") is True, ["uploadOrderFileWithMinUnits"]),
    "C2-E8": (lambda v: isinstance(v.get("orderTypes"), list) and len(v.get("orderTypes", [])) > 0, ["orderTypes"]),
    "C2-E9": (lambda v: v.get("st.order.minTotalPrice", 0) > 0, ["st.order.minTotalPrice"]),
    "C2-E10": (lambda v: v.get("st.order.orderTotalCreditMax") is True, ["st.order.orderTotalCreditMax"]),
    # C3 - Precios
    "C3-E1": (lambda v: v.get("lazyLoadingPrices") is True, ["lazyLoadingPrices"]),
    "C3-E2": (lambda v: v.get("hidePrices") is True, ["hidePrices"]),
    "C3-E3": (lambda v: v.get("anonymousHidePrice") is True, ["anonymousHidePrice"]),
    "C3-E4": (lambda v: v.get("useMongoPricing") is True, ["useMongoPricing"]),
    "C3-E5": (lambda v: v.get("enablePriceOracle") is True, ["enablePriceOracle"]),
    "C3-E6": (lambda v: v.get("enableSellerDiscount") is True, ["enableSellerDiscount"]),
    "C3-E7": (lambda v: v.get("disableManualDiscount") is True, ["disableManualDiscount"]),
    "C3-E8": (lambda v: v.get("enableNegativeDiscount") is True, ["enableNegativeDiscount"]),
    "C3-E9": (lambda v: v.get("mustHaveOverride") is True, ["mustHaveOverride"]),
    # C4 - ERP
    "C4-E1": (lambda v: v.get("orderPolicy.retainBelowMinimumOrder") is True, ["orderPolicy.retainBelowMinimumOrder"]),
    "C4-E2": (lambda v: v.get("orderPolicy.retainCreditBlockedCommerces") is True, ["orderPolicy.retainCreditBlockedCommerces"]),
    "C4-E3": (lambda v: v.get("orderPolicy.sendRetainedOrdersToClientErp") is True, ["orderPolicy.sendRetainedOrdersToClientErp"]),
    # C5 - Canasta
    "C5-E1": (lambda v: v.get("suggestions.hide") is True, ["suggestions.hide"]),
    "C5-E2": (lambda v: v.get("suggestions.enableSortingByCategories") is True, ["suggestions.enableSortingByCategories"]),
    "C5-E3": (lambda v: v.get("hasSeparatedSuggestions") is True, ["hasSeparatedSuggestions"]),
    "C5-E4": (lambda v: v.get("productList.enableSuggestionByCategories") is True, ["productList.enableSuggestionByCategories"]),
    # C6 - Sync
    "C6-E1": (lambda v: v.get("synchronization.enableBackgroundSync") is True, ["synchronization.enableBackgroundSync"]),
    "C6-E2": (lambda v: v.get("synchronization.enableBackgroundSendOrders") is True, ["synchronization.enableBackgroundSendOrders"]),
    "C6-E3": (lambda v: v.get("synchronization.enableSyncImages") is True, ["synchronization.enableSyncImages"]),
    # V1 - Vendedor
    "V1-E1": (lambda v: v.get("enableSellerDiscount") is True, ["enableSellerDiscount"]),
    "V1-E2": (lambda v: v.get("enableDialogNoSellReason") is True, ["enableDialogNoSellReason"]),
    "V1-E3": (lambda v: v.get("enableTask") is True, ["enableTask"]),
    "V1-E4": (lambda v: v.get("hasSingleDistributionCenter") is True, ["hasSingleDistributionCenter", "hasStockEnabled"]),
    "V1-E5": (lambda v: v.get("hasAllDistributionCenters") is True, ["hasAllDistributionCenters", "hasStockEnabled"]),
    "V1-E6": (lambda v: v.get("hasVoucherPrinterEnabled") is True, ["hasVoucherPrinterEnabled"]),
    "V1-E7": (lambda v: v.get("enableSegmentsBySeller") is True, ["enableSegmentsBySeller"]),
    "V1-E8": (lambda v: v.get("enableDisableProductsBySeller") is True, ["enableDisableProductsBySeller"]),
    # P1 - Pagos y Cobranza
    "P1-01": (lambda v: v.get("enablePayments") is True, ["enablePayments"]),
    "P1-02": (lambda v: v.get("disablePayments") is True, ["disablePayments"]),
    "P1-03": (lambda v: v.get("payment.enableNewPaymentModule") is True, ["payment.enableNewPaymentModule"]),
    "P1-04": (lambda v: v.get("payment.requiresFullPayment") is True, ["payment.requiresFullPayment"]),
    "P1-05": (lambda v: v.get("payment.externalPayment") not in (None, False, ""), ["payment.externalPayment"]),
    "P1-06": (lambda v: v.get("enablePaymentsCollection") is True, ["enablePaymentsCollection"]),
    "P1-07": (lambda v: v.get("enablePaymentDocumentsB2B") is True, ["enablePaymentDocumentsB2B"]),
    "P1-08": (lambda v: v.get("enableCreditNotes") is True, ["enableCreditNotes"]),
    "P1-09": (lambda v: v.get("enableCreditStateMessage") is True, ["enableCreditStateMessage"]),
    "P1-10": (lambda v: v.get("validatePaymentFromAdmin") is True, ["validatePaymentFromAdmin"]),
    "P1-11": (lambda v: v.get("enableInvoicesList") is True, ["enableInvoicesList"]),
    "P1-12": (lambda v: v.get("pendingDocuments") is True, ["pendingDocuments"]),
    # P2 - Gestion de Comercios
    "P2-01": (lambda v: v.get("commerce.enableCreateCommerce") is True, ["commerce.enableCreateCommerce"]),
    "P2-02": (lambda v: v.get("disableCommerceEdit") is True, ["disableCommerceEdit"]),
    "P2-03": (lambda v: v.get("editAddress") is True, ["editAddress"]),
    "P2-04": (lambda v: v.get("blockedClientAlert.enableBlockedClientAlert") is True, ["blockedClientAlert.enableBlockedClientAlert"]),
    "P2-05": (lambda v: v.get("hideReceiptType") is True, ["hideReceiptType"]),
    # P3 - Packaging y Unidades
    "P3-01": (lambda v: v.get("packagingInformation.hidePackagingInformationB2B") is True, ["packagingInformation.hidePackagingInformationB2B"]),
    "P3-02": (lambda v: v.get("packagingInformation.hideSingleItemPackagingInformationB2B") is True, ["packagingInformation.hideSingleItemPackagingInformationB2B"]),
    "P3-03": (lambda v: v.get("packagingInformation.ignoreUnitOnPackInformationB2B") is True, ["packagingInformation.ignoreUnitOnPackInformationB2B"]),
    "P3-04": (lambda v: v.get("hasMultiUnitEnabled") is True, ["hasMultiUnitEnabled"]),
    "P3-05": (lambda v: v.get("packaging.amountUsesUnits") is True, ["packaging.amountUsesUnits"]),
    "P3-06": (lambda v: v.get("weightInfo") is True, ["weightInfo"]),
    # P4 - Politicas de Orden
    "P4-01": (lambda v: v.get("orderPolicy.overdueDebtConfiguration.blockSettings.enabled") is True, ["orderPolicy.overdueDebtConfiguration.blockSettings.enabled"]),
    "P4-02": (lambda v: v.get("orderPolicy.overdueDebtConfiguration.retentionSettings.enabled") is True, ["orderPolicy.overdueDebtConfiguration.retentionSettings.enabled"]),
    "P4-03": (lambda v: v.get("orderPolicy.creditExceededStatus") not in (None, False, ""), ["orderPolicy.creditExceededStatus"]),
    "P4-04": (lambda v: v.get("purchaseOrderEnabled") is True, ["purchaseOrderEnabled"]),
    "P4-05": (lambda v: v.get("shoppingDetail.lastOrder") is True, ["shoppingDetail.lastOrder"]),
    # P5 - Hooks
    "P5-01": (lambda v: v.get("hooks.stockHook") is True, ["hooks.stockHook"]),
    "P5-02": (lambda v: v.get("hooks.getPendingDocumentsHook") is True, ["hooks.getPendingDocumentsHook"]),
    "P5-03": (lambda v: v.get("hooks.updateTrafficLightHook") is True, ["hooks.updateTrafficLightHook"]),
    "P5-04": (lambda v: v.get("hasTransportCode") is True, ["hasTransportCode"]),
    # P6 - UI y Experiencia
    "P6-01": (lambda v: v.get("enableHome") is True, ["enableHome"]),
    "P6-02": (lambda v: v.get("disableShowEstimatedDeliveryHour") is True, ["disableShowEstimatedDeliveryHour"]),
    "P6-03": (lambda v: v.get("footerCustomContent.useFooterCustomContent") is True, ["footerCustomContent.useFooterCustomContent"]),
    "P6-04": (lambda v: v.get("enableBetaButtons") is True, ["enableBetaButtons"]),
    "P6-05": (lambda v: isinstance(v.get("confirmCartText"), str) and len(v.get("confirmCartText", "")) > 0, ["confirmCartText"]),
    "P6-06": (lambda v: v.get("hasNoSaleFilter") is True, ["hasNoSaleFilter"]),
    "P6-07": (lambda v: v.get("adminConfiguration.showDiscountLimitAdmin") is True, ["adminConfiguration.showDiscountLimitAdmin"]),
}


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def flatten(obj: dict, prefix: str = "") -> dict:
    """Flatten a nested dict into dot-notation keys."""
    result = {}
    for k, v in obj.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict) and not any(isinstance(val, dict) for val in v.values() if isinstance(val, dict)):
            # One level of nesting — flatten
            result.update(flatten(v, key))
        elif isinstance(v, dict):
            result.update(flatten(v, key))
        else:
            result[key] = v
    return result


def serialize(obj: Any) -> Any:
    """Make MongoDB objects JSON-serializable."""
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    if hasattr(obj, "__str__") and type(obj).__name__ == "ObjectId":
        return str(obj)
    if isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [serialize(i) for i in obj]
    return obj


def get_active_tests(variables: dict) -> Dict[str, List[str]]:
    """Determine which tests apply to a client based on their variables."""
    conditional = []
    for test_id, (condition_fn, _var_names) in CONDITIONAL_TESTS.items():
        try:
            if condition_fn(variables):
                conditional.append(test_id)
        except Exception:
            pass
    return {
        "standard": STANDARD_TESTS.copy(),
        "conditional": sorted(conditional),
    }


# ─────────────────────────────────────────────
# Collection extraction (products, commerces, orders, etc.)
# ─────────────────────────────────────────────

def extract_promotions_data(promotions_db: Any, marketing_db: Any, domain: str, cid_obj: Any) -> dict:
    """Extract coupons and promotions for QA validation.

    Returns dict with:
    - coupons: active coupons with codes that can be tested
    - promotions: active promotions for price validation
    - banners: active banners for UI validation
    """
    result = {}

    try:
        # ── COUPONS (from yom-promotions) ──
        coupons = []
        for coupon in promotions_db.coupons.find({"customerId": cid_obj, "active": True}).limit(10):
            coupons.append(serialize({
                "code": coupon.get("code", ""),
                "discount": coupon.get("discount", {}),
                "minOrderAmount": coupon.get("minOrderAmount"),
                "expiresAt": coupon.get("expiresAt"),
            }))
        result["coupons"] = coupons

        # ── PROMOTIONS (from yom-promotions) ──
        promotions = []
        for promo in promotions_db.promotions.find({"customerId": cid_obj, "status": "active"}).limit(10):
            promotions.append(serialize({
                "name": promo.get("name", ""),
                "type": promo.get("type", ""),
                "priority": promo.get("priority"),
                "triggerRules": promo.get("triggerRules", []),
                "discountRules": promo.get("discountRules", []),
            }))
        result["promotions"] = promotions

        # ── BANNERS (from b2b-marketing) ──
        banners = []
        for banner in marketing_db.banners.find({"domain": domain, "active": True}).limit(5):
            banners.append(serialize({
                "title": banner.get("title", ""),
                "position": banner.get("position", ""),
                "startDate": banner.get("startDate"),
                "endDate": banner.get("endDate"),
            }))
        result["banners"] = banners

    except Exception as e:
        print(f"Warning: Promotions extraction failed: {e}", file=sys.stderr)
        result = {"coupons": [], "promotions": [], "banners": []}

    return result


def extract_collections(db: Any, domain: str, cid_obj: Any) -> dict:
    """Extract stats and details from additional MongoDB collections.

    Uses domain (str) for most collections, customerId (ObjectId) for others.
    """
    result = {}

    try:
        # ── PRODUCTS ──
        prod_total = db.products.count_documents({"domain": domain})
        prod_active = db.products.count_documents({"domain": domain, "active": True})
        prod_hidden = db.products.count_documents({"domain": domain, "b2bHidden": True})

        # Stock statuses
        stock_stats = {}
        for doc in db.products.aggregate([
            {"$match": {"domain": domain}},
            {"$group": {"_id": "$stockStatus", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]):
            stock_stats[doc["_id"] or "null"] = doc["count"]

        result["products"] = {
            "total": prod_total,
            "active": prod_active,
            "hidden_b2b": prod_hidden,
            "stock_statuses": stock_stats,
        }

        # ── COMMERCES ──
        comm_total = db.commerces.count_documents({"domain": domain})
        comm_active = db.commerces.count_documents({"domain": domain, "active": True})
        comm_auth = db.commerces.count_documents({"domain": domain, "authorized": True})
        comm_credit = db.commerces.count_documents({"domain": domain, "credit": {"$exists": True, "$ne": None}})

        result["commerces"] = {
            "total": comm_total,
            "active": comm_active,
            "authorized": comm_auth,
            "with_credit": comm_credit,
        }

        # ── PROMOTIONS ──
        promo_total = db.promotions.count_documents({"customerId": cid_obj})
        promo_active = db.promotions.count_documents({"customerId": cid_obj, "status": "active"})

        promo_types = {}
        for doc in db.promotions.aggregate([
            {"$match": {"customerId": cid_obj}},
            {"$group": {"_id": "$type", "count": {"$sum": 1}}},
        ]):
            promo_types[doc["_id"]] = doc["count"]

        # Full promo items (usually small list)
        promo_items = []
        for p in db.promotions.find({"customerId": cid_obj}).limit(100):
            promo_items.append(serialize({
                "name": p.get("name", ""),
                "type": p.get("type", ""),
                "status": p.get("status", ""),
                "priority": p.get("priority"),
                "showDiscountRate": p.get("showDiscountRate"),
                "showTag": p.get("showTag"),
                "triggerRules": p.get("triggerRules", []),
                "discountRules": p.get("discountRules", []),
                "productTags": p.get("productTags", []),
            }))

        result["promotions"] = {
            "total": promo_total,
            "active": promo_active,
            "by_type": promo_types,
            "items": promo_items,
        }

        # ── OVERRIDES ──
        over_total = db.overrides.count_documents({"customerId": cid_obj})
        over_enabled = db.overrides.count_documents({"customerId": cid_obj, "enabled": True})

        result["overrides"] = {
            "total": over_total,
            "enabled": over_enabled,
        }

        # ── ORDERS ──
        order_total = db.orders.count_documents({"domain": domain})

        order_status = {}
        for doc in db.orders.aggregate([
            {"$match": {"domain": domain}},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]):
            order_status[doc["_id"] or "unknown"] = doc["count"]

        result["orders"] = {
            "total": order_total,
            "by_status": order_status,
        }

        # ── CATEGORIES ──
        cat_total = db.categories.count_documents({"domain": domain})
        cat_items = []
        for c in db.categories.find({"domain": domain}).sort("name", 1):
            cat_items.append(serialize({
                "name": c.get("name", ""),
                "tags": c.get("tags", []),
                "active": c.get("active", True),
                "has_parent": c.get("parent") is not None,
            }))

        result["categories"] = {
            "total": cat_total,
            "items": cat_items,
        }

        # ── SEGMENTS ──
        seg_total = db.segments.count_documents({"domain": domain})
        seg_items = []
        for s in db.segments.find({"domain": domain}).sort("name", 1).limit(100):
            seg_items.append(serialize({
                "name": s.get("name", ""),
                "code": s.get("code", ""),
            }))

        result["segments"] = {
            "total": seg_total,
            "items": seg_items,
        }

        # ── COUPONS ──
        coup_total = db.coupons.count_documents({"customerId": cid_obj})
        coup_items = []
        for c in db.coupons.find({"customerId": cid_obj}).limit(100):
            coup_items.append(serialize({
                "code": c.get("code", ""),
                "discount": c.get("discount", {}),
            }))

        result["coupons"] = {
            "total": coup_total,
            "items": coup_items,
        }

        # ── SIMPLE COUNTS ──
        result["sellers"] = {"total": db.sellers.count_documents({"domain": domain})}
        result["banners"] = {"total": db.banners.count_documents({"domain": domain})}
        result["carts"] = {"total": db.carts.count_documents({"domain": domain})}
        result["payments"] = {"total": db.payments.count_documents({"domain": domain})}
        result["pendingDocuments"] = {"total": db.pendingdocuments.count_documents({"customerId": cid_obj})}

    except Exception as e:
        print(f"Warning: Collection extraction failed: {e}", file=sys.stderr)
        # Return partial/empty result instead of crashing
        if not result:
            result = {k: {} for k in ["products", "commerces", "promotions", "overrides", "orders",
                                      "categories", "segments", "coupons", "sellers", "banners",
                                      "carts", "payments", "pendingDocuments"]}

    return result


# ─────────────────────────────────────────────
# Extract integrations data
# ─────────────────────────────────────────────

def extract_integrations_data(integrations_client, domain: str, cid_obj) -> dict:
    """Extract segments, overrides, and user segments from integrations/yom-production."""
    result = {
        "segments": {"total": 0, "items": []},
        "overrides": {"total": 0, "items": []},
        "userSegments": {"total": 0, "items": []},
    }

    try:
        # Integrations cluster uses yom-production database
        # (Try yom-production first, fallback to yom-staging)
        if "yom-production" in integrations_client.list_database_names():
            db = integrations_client["yom-production"]
        elif "yom-staging" in integrations_client.list_database_names():
            db = integrations_client["yom-staging"]
        else:
            return result

        # Extract segments (search by domain or customerId)
        seg_total = db.segments.count_documents({"domain": domain})
        if seg_total == 0:
            # Try by customerId
            seg_total = db.segments.count_documents({"customerId": cid_obj})

        seg_items = []
        for s in db.segments.find({"domain": domain}).sort("name", 1).limit(50):
            seg_items.append(serialize({
                "name": s.get("name", ""),
                "code": s.get("code", ""),
                "active": s.get("active", True),
            }))
        result["segments"] = {"total": seg_total, "items": seg_items}

        # Extract overrides (search by customerId or domain)
        over_total = db.overrides.count_documents({"customerId": cid_obj})
        if over_total == 0:
            # Try by domain
            over_total = db.overrides.count_documents({"domain": domain})

        over_items = []
        for o in db.overrides.find({"customerId": cid_obj}).sort("createdAt", -1).limit(50):
            over_items.append(serialize({
                "productId": str(o.get("productId", "")),
                "price": o.get("price"),
                "discount": o.get("discount"),
                "enabled": o.get("enabled", True),
            }))
        result["overrides"] = {"total": over_total, "items": over_items}

        # Extract user segments (usersegments collection)
        useg_total = db.usersegments.count_documents({"customerId": cid_obj})
        if useg_total == 0:
            # Try by domain
            useg_total = db.usersegments.count_documents({"domain": domain})

        useg_items = []
        for us in db.usersegments.find({"customerId": cid_obj}).sort("createdAt", -1).limit(50):
            useg_items.append(serialize({
                "name": us.get("name", ""),
                "segmentId": str(us.get("segmentId", "")),
                "userCount": us.get("userCount", 0),
            }))
        result["userSegments"] = {"total": useg_total, "items": useg_items}

    except Exception as e:
        print(f"Warning: Integrations extraction failed: {e}", file=sys.stderr)

    return result


# ─────────────────────────────────────────────
# Main extraction
# ─────────────────────────────────────────────

def extract(client_filter: Optional[str] = None, full_extract: bool = False, staging_only: bool = False) -> dict:
    """Extract all data from MongoDB and return the qa-matrix structure.

    Args:
        client_filter: Filter by client name
        full_extract: Also extract products, commerces, etc.
        staging_only: Only extract staging clients (*.solopide.me)
    """
    print("Connecting to MongoDB clusters...")

    micro_client = None
    if MICRO_URI:
        micro_client = MongoClient(MICRO_URI)

    integrations_client = None
    if INTEGRATIONS_URI:
        integrations_client = MongoClient(INTEGRATIONS_URI)

    legacy_client = MongoClient(LEGACY_URI)

    if MICRO_URI:
        sites_db = micro_client["yom-stores"]
        promotions_db = micro_client["yom-promotions"]
        marketing_db = micro_client["b2b-marketing"]
    else:
        sites_db = legacy_client["yom-stores"]  # fallback to legacy for sites
        promotions_db = None
        marketing_db = None

    # Production cluster uses yom-production, staging cluster uses yom-staging
    available_dbs = legacy_client.list_database_names()
    if "yom-production" in available_dbs:
        legacy_db = legacy_client["yom-production"]
    elif "yom-staging" in available_dbs:
        legacy_db = legacy_client["yom-staging"]
    else:
        print("Error: neither yom-production nor yom-staging found in cluster", file=sys.stderr)
        sys.exit(1)

    # Get all sites
    sites = list(sites_db.sites.find({}))
    customers = list(legacy_db.customers.find({}))
    salesterms = list(legacy_db.salesterms.find({}))

    # Index legacy data
    cust_by_id = {str(c["_id"]): c for c in customers}
    st_by_cust = {str(s["customerId"]): s for s in salesterms if s.get("customerId")}
    st_by_domain = {s["domain"]: s for s in salesterms if s.get("domain")}

    result = {
        "extractedAt": datetime.now(timezone.utc).isoformat(),
        "totalSites": len(sites),
        "totalCustomers": len(customers),
        "totalSalesterms": len(salesterms),
        "fullExtract": full_extract,
        "clients": {},
    }

    for site in sites:
        domain = site.get("domain", "")

        # Staging domains (.solopide.me) are auto-discovered — no whitelist needed.
        # Production domains (.youorder.me) must be in REAL_CLIENTS to avoid noise.
        is_staging = domain.endswith(".solopide.me")
        if is_staging:
            if domain in STAGING_EXCLUDE_DOMAINS:
                continue
        else:
            if domain not in REAL_CLIENTS:
                continue

        # Derive display name: use REAL_CLIENTS if present, otherwise derive from slug
        if domain in REAL_CLIENTS:
            display_name = REAL_CLIENTS[domain]
        else:
            slug = domain.split(".")[0]
            display_name = slug.replace("-", " ").title() + " (staging)"

        # Filter by staging/production if requested
        if staging_only and not is_staging:
            continue
        if not staging_only and is_staging:
            continue

        # Apply client filter if specified
        if client_filter and client_filter.lower() not in display_name.lower():
            continue

        cid = str(site.get("customerId", ""))
        cid_obj = site.get("customerId")
        cust = cust_by_id.get(cid)
        st = st_by_cust.get(cid) or st_by_domain.get(domain)

        # Extract site variables (excluding branding)
        site_vars = {}
        for k, v in site.items():
            if k in EXCLUDE_FIELDS or k in ("name", "domain", "customerId", "currency"):
                continue
            if isinstance(v, dict):
                for sub_k, sub_v in flatten(v, k).items():
                    site_vars[sub_k] = serialize(sub_v)
            else:
                site_vars[k] = serialize(v)

        # Extract salesterms (flattened, with st. prefix for test conditions)
        st_vars = {}
        if st:
            for k, v in st.items():
                if k in ("_id", "__v", "domain", "customerId", "createdAt", "updatedAt"):
                    continue
                if isinstance(v, dict):
                    for sub_k, sub_v in flatten(v, k).items():
                        st_vars[sub_k] = serialize(sub_v)
                else:
                    st_vars[k] = serialize(v)

        # Merge for test evaluation (site vars + salesterms with st. prefix)
        merged_vars = dict(site_vars)
        for k, v in st_vars.items():
            merged_vars[f"st.{k}"] = v

        # Get active tests
        active_tests = get_active_tests(merged_vars)

        # Build client key from domain
        client_key = domain.replace(".youorder.me", "").replace(".solopide.me", "-staging")

        client_obj = {
            "name": display_name,
            "domain": domain,
            "customerId": cid,
            "currency": site.get("currency", ""),
            "inMaintenance": site.get("inMaintenance", False),
            "hasCustomer": cust is not None,
            "hasSalesterms": st is not None,
            "variables": site_vars,
            "salesterms": st_vars,
            "customer": serialize({
                k: v for k, v in (cust or {}).items()
                if k not in ("_id", "__v", "createdAt", "updatedAt", "owner")
            }),
            "activeTests": active_tests,
            "testCount": {
                "standard": len(active_tests["standard"]),
                "conditional": len(active_tests["conditional"]),
                "total": len(active_tests["standard"]) + len(active_tests["conditional"]),
            },
        }

        # Extract promotions and banners for QA validation (only if MICRO_URI available)
        if cid_obj and promotions_db is not None and marketing_db is not None:
            promo_data = extract_promotions_data(promotions_db, marketing_db, domain, cid_obj)
            client_obj["coupons"] = promo_data.get("coupons", [])
            client_obj["promotions"] = promo_data.get("promotions", [])
            client_obj["banners"] = promo_data.get("banners", [])
        else:
            client_obj["coupons"] = []
            client_obj["promotions"] = []
            client_obj["banners"] = []

        # Extract integrations data (segments, overrides, user segments)
        if cid_obj and integrations_client is not None:
            integrations_data = extract_integrations_data(integrations_client, domain, cid_obj)
            client_obj["integrations"] = integrations_data
        else:
            client_obj["integrations"] = {
                "segments": {"total": 0, "items": []},
                "overrides": {"total": 0, "items": []},
                "userSegments": {"total": 0, "items": []},
            }

        # Extract additional collections if --full flag is set
        if full_extract and cid_obj:
            client_obj["collections"] = extract_collections(legacy_db, domain, cid_obj)

        result["clients"][client_key] = client_obj

    if micro_client:
        micro_client.close()
    if integrations_client:
        integrations_client.close()
    legacy_client.close()

    print(f"Extracted {len(result['clients'])} clients")
    print(f"  - Databases: yom-stores, yom-promotions, b2b-marketing (MICRO)")
    print(f"  - Databases: yom-production (LEGACY)")
    if INTEGRATIONS_URI:
        print(f"  - Databases: segments, overrides, user-segments (INTEGRATIONS)")
    return result


def main():
    parser = argparse.ArgumentParser(description="Extract QA data from MongoDB")
    parser.add_argument("--cliente", type=str, help="Filter by client name")
    parser.add_argument("--output", type=str, default="data/qa-matrix.json",
                        help="Output file path (default: data/qa-matrix.json)")
    parser.add_argument("--full", action="store_true",
                        help="Also extract products, commerces, promotions, orders, etc. (slower)")
    parser.add_argument("--staging", action="store_true",
                        help="Only extract staging clients (*.solopide.me), ignore production")
    parser.add_argument("--env", type=str, choices=["production", "staging"], default="production",
                        help="MongoDB environment to connect to (default: production)")
    args = parser.parse_args()

    # Set module-level URIs based on --env
    global LEGACY_URI, MICRO_URI, INTEGRATIONS_URI
    LEGACY_URI, MICRO_URI, INTEGRATIONS_URI = _get_uris(args.env)

    if not LEGACY_URI:
        print(f"Error: MONGO_LEGACY{'_STAGING' if args.env == 'staging' else ''}_URI not configured in .env", file=sys.stderr)
        sys.exit(1)
    if not MICRO_URI:
        print(f"Warning: MONGO_MICRO{'_STAGING' if args.env == 'staging' else ''}_URI not set. Skipping promotions/banners.", file=sys.stderr)
    if not INTEGRATIONS_URI:
        print(f"Warning: MONGO_INTEGRATIONS{'_STAGING' if args.env == 'staging' else ''}_URI not set. Skipping segments/overrides.", file=sys.stderr)

    print(f"Connecting to MongoDB [{args.env.upper()}]...")

    # Adjust output path if staging
    output_path = args.output
    if args.staging and args.output == "data/qa-matrix.json":
        output_path = "data/qa-matrix-staging.json"

    data = extract(client_filter=args.cliente, full_extract=args.full, staging_only=args.staging)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nOutput: {output_path}")
    for key, client in data["clients"].items():
        test_info = f"{client['testCount']['total']} tests ({client['testCount']['standard']} std + {client['testCount']['conditional']} cond)"

        # If full extract, add collection stats
        if "collections" in client:
            col = client["collections"]
            col_info = []
            if col.get("products", {}).get("total"):
                col_info.append(f"prod={col['products']['total']}")
            if col.get("orders", {}).get("total"):
                col_info.append(f"orders={col['orders']['total']}")
            if col.get("commerces", {}).get("total"):
                col_info.append(f"comm={col['commerces']['total']}")
            col_info_str = " | " + ", ".join(col_info) if col_info else ""
        else:
            col_info_str = ""

        print(f"  {client['name']:25s} — {test_info}{col_info_str}")


if __name__ == "__main__":
    main()

"""
sync-clients.py

Generates tests/e2e/fixtures/clients.ts from data/qa-matrix.json
Ensures clients.ts is always in sync with MongoDB via the extractor.

Usage:
    # Staging (solopide.me — most common)
    python3 tools/sync-clients.py --input data/qa-matrix-staging.json

    # Prod (youorder.me — run extractor first)
    python3 tools/sync-clients.py

Workflow (staging):
    1. python3 data/mongo-extractor.py --env staging --output data/qa-matrix-staging.json
    2. python3 tools/sync-clients.py --input data/qa-matrix-staging.json
    3. cd tests/e2e && npx playwright test

Workflow (production):
    1. python3 data/mongo-extractor.py --env production   # → data/qa-matrix.json (gitignored)
    2. python3 tools/sync-clients.py

Note: data/qa-matrix.json is the prod matrix (gitignored). qa-matrix-staging.json is
committed and is the active matrix for day-to-day QA.
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone


def load_b2b_feature_status() -> dict:
    """Load data/b2b-feature-status.json if it exists. Returns variable→implemented map."""
    status_path = Path("data/b2b-feature-status.json")
    if not status_path.exists():
        return {}
    with open(status_path) as f:
        data = json.load(f)
    # Return {varName: bool} — only variables explicitly marked as not implemented
    return {
        var: info.get("implemented", True)
        for var, info in data.get("variables", {}).items()
    }


def load_qa_matrix(matrix_path: str = "data/qa-matrix.json") -> dict:
    """Load the qa-matrix.json file."""
    path = Path(matrix_path)
    if not path.exists():
        print(f"Error: {matrix_path} not found. Run: python3 data/mongo-extractor.py", file=sys.stderr)
        sys.exit(1)

    with open(path) as f:
        return json.load(f)


# ── Contract validation ────────────────────────────────────────────────────────

_CONTRACT_BOOL_FIELDS = {
    "anonymousAccess", "anonymousHideCart", "anonymousHidePrice",
    "disableCart", "disableCommerceEdit", "disableShowEstimatedDeliveryHour",
    "disableShowDiscount", "disableShowOffer",
    "editAddress", "enableAskDeliveryDate", "enableCoupons",
    "enableDialogNoSellReason", "enableInvoicesList", "enableOrderApproval",
    "enableOrderValidation", "enableSellerDiscount", "externalAccess",
    "hasMultiUnitEnabled", "hidePrices", "hideReceiptType",
    "hooks.cartShoppingHook", "hooks.getPendingDocumentsHook",
    "hooks.shippingHook", "hooks.stockHook", "hooks.updateTrafficLightHook",
    "inMaintenance", "includeTaxRateInPrices", "lazyLoadingPrices",
    "ordersRequireAuthorization", "ordersRequireVerification",
    "pendingDocuments", "pointsEnabled", "purchaseOrderEnabled",
    "showEmptyCategories", "showMinOne", "taxes.showSummary",
    "taxes.useTaxRate", "useMobileGps", "weightInfo",
}


def validate_client_variables(qa_matrix: dict) -> int:
    """Validate client variables against the contract schema.
    Non-blocking: prints [CONTRACT WARN] lines, never raises.
    Schema ref: data/schemas/client-variables.schema.json
    Bug ref: BAS-QA-006 (taxes.taxRate: 19 should be 0.19)
    """
    violations = 0
    for client_key, client_data in qa_matrix.get("clients", {}).items():
        variables = client_data.get("variables", {})
        for field in _CONTRACT_BOOL_FIELDS:
            value = variables.get(field)
            if value is None:
                continue
            if not isinstance(value, bool):
                print(
                    f"[CONTRACT WARN] {client_key} / {field}: "
                    f"expected bool, got {type(value).__name__} {value!r} "
                    f"(schema: data/schemas/client-variables.schema.json)"
                )
                violations += 1
        tax_rate = variables.get("taxes.taxRate")
        if tax_rate is not None:
            if isinstance(tax_rate, bool) or not isinstance(tax_rate, (int, float)):
                print(
                    f"[CONTRACT WARN] {client_key} / taxes.taxRate: "
                    f"expected number, got {type(tax_rate).__name__} {tax_rate!r} "
                    f"(schema: data/schemas/client-variables.schema.json)"
                )
                violations += 1
            elif not (0.0 <= float(tax_rate) <= 1.0):
                print(
                    f"[CONTRACT WARN] {client_key} / taxes.taxRate: "
                    f"value {tax_rate} out of range [0, 1] — BAS-QA-006: use 0.19 not 19 "
                    f"(schema: data/schemas/client-variables.schema.json)"
                )
                violations += 1
    if violations == 0:
        print("   Contract validation: OK (0 violations)")
    else:
        print(f"   Contract validation: {violations} violation(s) — see [CONTRACT WARN] lines above")
    return violations


def map_domain_to_baseurl(domain: str) -> str:
    """Map MongoDB domain to frontend baseURL.

    yom.me = production
    solopide.me = staging

    Some staging clients have a different MongoDB domain vs actual frontend URL.
    These overrides ensure clients.ts always points to the real deployed URL.
    """
    FRONTEND_URL_OVERRIDES = {
        # MongoDB domain          -> actual frontend URL
        "codelpa.solopide.me":    "https://beta-codelpa.solopide.me",
        "prisa.solopide.me":      "https://surtiventas.solopide.me",
    }
    if domain in FRONTEND_URL_OVERRIDES:
        return FRONTEND_URL_OVERRIDES[domain]
    return f"https://{domain}"


def format_conditional_tests(active_tests: dict) -> str:
    """Format conditional test list as comment."""
    if not active_tests.get("conditional"):
        return "// No conditional tests"
    tests = ", ".join(active_tests["conditional"][:10])
    if len(active_tests["conditional"]) > 10:
        tests += f", +{len(active_tests['conditional']) - 10} more"
    return f"// Conditional tests: {tests}"


def generate_clients_ts(qa_matrix: dict) -> str:
    """Generate TypeScript clients.ts from qa-matrix.json."""

    extracted_at = qa_matrix.get("extractedAt", datetime.now(timezone.utc).isoformat())
    b2b_feature_map = load_b2b_feature_status()

    header = f'''/**
 * AUTO-GENERATED by tools/sync-clients.py
 * Source: data/qa-matrix.json
 * Last sync: {extracted_at}
 *
 * DO NOT EDIT MANUALLY
 * To regenerate: python3 tools/sync-clients.py
 *
 * Flow:
 *   1. python3 data/mongo-extractor.py   # MongoDB → qa-matrix.json
 *   2. python3 tools/sync-clients.py     # qa-matrix.json → this file
 */

import {{ test as base, expect }} from '@playwright/test';

function creds(prefix: string) {{
  return {{
    email: process.env[`${{prefix}}_EMAIL`] || '',
    password: process.env[`${{prefix}}_PASSWORD`] || '',
  }};
}}

interface ClientConfig {{
  name: string;
  baseURL: string;
  loginPath: string;
  credentials: {{ email: string; password: string }};
  config: Record<string, any>;
  notImplementedInB2B: string[]; // Variables in MongoDB not yet implemented in B2B frontend
  coupons?: Array<{{ code: string; discount: any }}>; // From yom-promotions
  banners?: Array<{{ title: string; position: string }}>; // From b2b-marketing
  promotions?: Array<any>; // From yom-promotions
  integrations?: {{ segments: any; overrides: any; userSegments: any }}; // From integrations cluster
  defaultCommerce?: string; // Commerce to select after login (env: {{CLIENT}}_DEFAULT_COMMERCE)
}}

const clients: Record<string, ClientConfig> = {{
'''

    # Normalize client keys: strip "-staging" suffix and map prisa → surtiventas
    KEY_ALIASES = {
        "prisa-staging": "surtiventas",
        "prisa":         "surtiventas",
    }
    KEY_STRIP_SUFFIX = "-staging"

    # Active QA clients — only these are propagated to clients.ts.
    # Raw MongoDB keys (as they appear in qa-matrix-staging.json / qa-matrix.json).
    # Update this list when a contract ends or a new client is onboarded.
    # Inactive clients remain in the matrix JSON (data intact), but skip sync.
    ACTIVE_CLIENTS = {
        "prisur-staging",
        "prinorte-staging",
        "prisa-staging",            # aliased to "surtiventas" in clients.ts
        "bastien-staging",
        "marleycoffee-staging",
        "soprole-staging",
        "elmuneco-staging",
        "cedisur-staging",
        "codelpa-staging",
        "codelpa-peru-staging",
        "coexito-staging",
        "new-soprole-staging",
        "expressdent-staging",
        "globalwines-staging",
        "softys-cencocal-staging",
        "softys-dimak-staging",
        "sonrie-staging",
        # Production-matrix keys (used when syncing from qa-matrix.json)
        "surtiventas",
        "sonrie-prod",
    }

    client_entries = []
    skipped_inactive = []
    for raw_key, client_data in qa_matrix.get("clients", {}).items():
        if raw_key not in ACTIVE_CLIENTS:
            skipped_inactive.append(raw_key)
            continue
        client_key = raw_key.removesuffix(KEY_STRIP_SUFFIX)
        client_key = KEY_ALIASES.get(raw_key, KEY_ALIASES.get(client_key, client_key))
        domain = client_data.get("domain", "")
        name = client_data.get("name", "")
        baseurl = map_domain_to_baseurl(domain)
        variables = client_data.get("variables", {})
        coupons = client_data.get("coupons", [])
        banners = client_data.get("banners", [])
        promotions = client_data.get("promotions", [])
        integrations = client_data.get("integrations", {})
        active_tests = client_data.get("activeTests", {})

        # Determine login path
        login_path = "/auth/jwt/login"
        if domain in ("soprole.youorder.me", "soprole.solopide.me"):
            login_path = "/login"

        # Format config object
        config_items = []
        for key, value in sorted(variables.items()):
            # Escape keys with dots (e.g., hooks.shippingHook → "hooks.shippingHook")
            key_str = f'"{key}"' if '.' in key else key
            if isinstance(value, bool):
                config_items.append(f"      {key_str}: {str(value).lower()},")
            elif isinstance(value, str):
                # Use json.dumps to properly escape strings (handles quotes, newlines, etc.)
                config_items.append(f"      {key_str}: {json.dumps(value)},")
            elif isinstance(value, (int, float)):
                config_items.append(f"      {key_str}: {value},")
            elif isinstance(value, list):
                config_items.append(f"      {key_str}: {json.dumps(value)},")
            elif isinstance(value, dict):
                config_items.append(f"      {key_str}: {json.dumps(value)},")
            else:
                config_items.append(f"      {key_str}: {value},")

        config_str = "\n".join(config_items)

        # Format coupons array for tests
        coupons_str = "[]"
        if coupons:
            coupon_items = [
                f'    {{ code: "{c.get("code", "")}", discount: {json.dumps(c.get("discount", {}))} }}'
                for c in coupons[:3]
            ]
            coupons_str = f"[\n{', '.join(coupon_items)}\n  ]"

        # Format banners array for tests
        banners_str = "[]"
        if banners:
            banner_items = [
                f'    {{ title: "{b.get("title", "")}", position: "{b.get("position", "")}" }}'
                for b in banners[:3]
            ]
            banners_str = f"[\n{', '.join(banner_items)}\n  ]"

        # Format promotions array
        promotions_str = "[]"
        if promotions:
            promotions_str = json.dumps(promotions[:5])

        # Format integrations object
        integrations_str = "{ segments: [], overrides: [], userSegments: [] }"
        if integrations:
            segments = integrations.get("segments", {}).get("items", [])[:5]
            overrides = integrations.get("overrides", {}).get("items", [])[:5]
            user_segments = integrations.get("userSegments", {}).get("items", [])[:5]
            integrations_obj = {
                "segments": segments,
                "overrides": overrides,
                "userSegments": user_segments,
            }
            integrations_str = json.dumps(integrations_obj)

        # Compute notImplementedInB2B: vars in this client's config that are NOT in B2B
        not_in_b2b = []
        if b2b_feature_map:
            for var_name in variables:
                if b2b_feature_map.get(var_name) is False:
                    not_in_b2b.append(var_name)
        not_in_b2b_str = json.dumps(sorted(not_in_b2b))

        # Conditional tests comment
        conditional_comment = format_conditional_tests(active_tests)

        # Quote client keys that have hyphens or start with numbers (invalid TS identifiers)
        client_key_str = f'"{client_key}"' if '-' in client_key or client_key[0].isdigit() else client_key

        # defaultCommerce: optional env var {CLIENT_KEY_UPPER}_DEFAULT_COMMERCE
        env_key_upper = client_key.upper().replace('-', '_')
        default_commerce_line = f'    defaultCommerce: process.env["{env_key_upper}_DEFAULT_COMMERCE"],\n'

        entry = f'''  {client_key_str}: {{
    name: "{name}",
    baseURL: "{baseurl}",
    loginPath: "{login_path}",
    credentials: creds("{env_key_upper}"),
    notImplementedInB2B: {not_in_b2b_str},
    coupons: {coupons_str},
    banners: {banners_str},
    promotions: {promotions_str},
    integrations: {integrations_str},
    {default_commerce_line}    {conditional_comment}
    config: {{
{config_str}
    }},
  }},
'''
        client_entries.append(entry)

    clients_section = "".join(client_entries)

    footer = '''};

export default clients;
'''

    if skipped_inactive:
        print(f"   Skipped {len(skipped_inactive)} inactive clients: {', '.join(sorted(skipped_inactive))}")

    return header + clients_section + footer


def generate_b2b_variables_json(qa_matrix: dict, b2b_feature_map: dict) -> dict:
    """Generate public/data/b2b-variables.json for the dashboard."""
    SKIP_VARS = {"_id", "__v", "createdAt", "updatedAt", "domain", "customerId", "currency", "inMaintenance"}
    HOOK_PREFIX = "hooks."

    # Keep active allowlist in sync with generate_clients_ts.
    ACTIVE_CLIENTS = {
        "prisur-staging", "prinorte-staging", "prisa-staging", "bastien-staging",
        "marleycoffee-staging", "soprole-staging", "elmuneco-staging", "cedisur-staging",
        "codelpa-staging", "codelpa-peru-staging", "coexito-staging", "new-soprole-staging",
        "expressdent-staging", "globalwines-staging", "softys-cencocal-staging",
        "softys-dimak-staging", "sonrie-staging", "surtiventas", "sonrie-prod",
    }

    # {var: {clientKey: value}} — actual value per client
    var_client_values: dict = {}
    for raw_key, client_data in qa_matrix.get("clients", {}).items():
        if raw_key not in ACTIVE_CLIENTS:
            continue
        client_key = raw_key.removesuffix("-staging")
        for var, value in client_data.get("variables", {}).items():
            if var in SKIP_VARS or var.startswith(HOOK_PREFIX):
                continue
            if var not in var_client_values:
                var_client_values[var] = {}
            var_client_values[var][client_key] = value

    variables = {}
    for var in sorted(var_client_values):
        status = b2b_feature_map.get(var)
        implemented = None if status is None else status
        # Sort clients alphabetically, include actual value per client
        client_values = {k: var_client_values[var][k] for k in sorted(var_client_values[var])}
        variables[var] = {
            "clients": client_values,
            "implemented": implemented,
        }

    return {
        "generatedAt": qa_matrix.get("extractedAt", datetime.now(timezone.utc).isoformat()),
        "total": len(variables),
        "variables": variables,
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate clients.ts from qa-matrix.json")
    parser.add_argument(
        "--input",
        default="data/qa-matrix.json",
        help="Path to qa-matrix.json (default: data/qa-matrix.json)"
    )
    args = parser.parse_args()

    print(f"Loading {args.input}...")
    qa_matrix = load_qa_matrix(args.input)
    validate_client_variables(qa_matrix)
    b2b_feature_map = load_b2b_feature_status()

    print(f"Generating clients.ts from {len(qa_matrix.get('clients', {}))} clients...")
    clients_ts = generate_clients_ts(qa_matrix)

    output_path = Path("tests/e2e/fixtures/clients.ts")
    output_path.write_text(clients_ts)

    # Generate b2b-variables.json for dashboard
    b2b_vars = generate_b2b_variables_json(qa_matrix, b2b_feature_map)
    vars_path = Path("public/data/b2b-variables.json")
    vars_path.parent.mkdir(parents=True, exist_ok=True)
    vars_path.write_text(json.dumps(b2b_vars, indent=2))

    print(f"✅ Generated {output_path}")
    print(f"✅ Generated {vars_path} ({b2b_vars['total']} variables)")
    print(f"   {len(qa_matrix.get('clients', {}))} clients")
    print(f"   Last sync: {qa_matrix.get('extractedAt', 'unknown')}")


if __name__ == "__main__":
    main()

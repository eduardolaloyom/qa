#!/usr/bin/env python3
"""
b2b-feature-validator.py

Single check for each MongoDB config variable:
  - Is it in @yomcl/types Store type? (YOMCL/monorepo)
    → Yes → relevant for B2B (frontend or backend reads it) → implemented: true
    → No  → not B2B (mobile/backend-only) → implemented: false, skip tests

Why only one step:
  Many variables affect B2B via backend logic (e.g. hidePrices → API returns
  products without prices). The frontend never reads them directly but the
  feature IS present in the B2B experience. @yomcl/types Store is the contract
  that defines what belongs to the B2B product.

Usage:
    python3 tools/b2b-feature-validator.py --input data/qa-matrix-staging.json
    python3 tools/b2b-feature-validator.py --var confirmCartText
    python3 tools/b2b-feature-validator.py --skip-api   # use existing JSON only
    python3 tools/b2b-feature-validator.py --force      # re-check all

Output:
    data/b2b-feature-status.json
"""

import json
import re
import sys
import base64
import argparse
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime, timezone


B2B_REPO    = "YOMCL/b2b"
TYPES_REPO  = "YOMCL/monorepo"
STATUS_FILE = Path("data/b2b-feature-status.json")

SKIP_VARS = {
    "_id", "__v", "createdAt", "updatedAt", "domain", "customerId",
    "currency", "inMaintenance",
}
HOOK_PREFIX = "hooks."

STORE_TYPE_FILES = [
    "packages/types/src/store/store.ts",
    "packages/types/src/store/payment.ts",
    "packages/types/src/store/blocked-client-alert.ts",
    "packages/types/src/store/footer-custom-content.ts",
    "packages/types/src/store/contact.ts",
    "packages/types/src/store/discounts.ts",
    "packages/types/src/store/packaging-information.ts",
    "packages/types/src/store/product-detail-view-configuration.ts",
    "packages/types/src/store/shopping-detail.ts",
    "packages/types/src/store/suggestions.ts",
    "packages/types/src/store/synchronization.ts",
    "packages/types/src/store/wrong-prices.ts",
    "packages/types/src/store/background-sync.ts",
    "packages/types/src/taxes/store-taxes.ts",
]

NESTED_PREFIXES = {
    "payment", "blockedClientAlert", "footerCustomContent", "contact",
    "discountTypes", "packagingInformation", "productDetailViewConfiguration",
    "shoppingDetail", "suggestions", "synchronization", "wrongPrices", "taxes",
    "overdueDebtConfiguration",
}


def load_env_token() -> str:
    for env_path in [Path(".env"), Path("tests/e2e/.env"), Path(".claude/.env")]:
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if line.startswith("GITHUB_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def load_status_cache() -> dict:
    if STATUS_FILE.exists():
        with open(STATUS_FILE) as f:
            return json.load(f)
    return {"b2bRepo": B2B_REPO, "variables": {}}


def save_status(status: dict) -> None:
    status["generatedAt"] = datetime.now(timezone.utc).isoformat()
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f, indent=2)
    print(f"✅ Saved {STATUS_FILE}")


def gh_get_file(repo: str, path: str, token: str):
    url = f"https://api.github.com/repos/{repo}/contents/{urllib.parse.quote(path)}"
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("User-Agent", "YOM-QA-Validator/1.0")
    if token:
        req.add_header("Authorization", f"token {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            d = json.loads(resp.read())
            return base64.b64decode(d["content"]).decode()
    except Exception:
        return None


def extract_type_fields(content: str) -> set:
    fields = set()
    for line in content.splitlines():
        m = re.match(r'^\s+(\w+)\??:', line)
        if m:
            fields.add(m.group(1))
    return fields


def build_store_type_fields(token: str) -> set:
    print("📦 Loading @yomcl/types Store definition from monorepo...")
    all_fields = set()

    store_content = gh_get_file(TYPES_REPO, STORE_TYPE_FILES[0], token) or ""
    top_level = extract_type_fields(store_content)
    all_fields.update(top_level)

    for path in STORE_TYPE_FILES[1:]:
        content = gh_get_file(TYPES_REPO, path, token) or ""
        fields = extract_type_fields(content)
        stem = Path(path).stem
        stem_camel = re.sub(r'-(\w)', lambda m: m.group(1).upper(), stem)
        for prefix in NESTED_PREFIXES:
            if prefix.lower() in stem_camel.lower() or stem_camel.lower() in prefix.lower():
                for f in fields:
                    all_fields.add(f"{prefix}.{f}")
                break

    print(f"   → {len(all_fields)} fields in Store type\n")
    return all_fields


def is_in_store_type(var_name: str, store_fields: set) -> bool:
    if var_name in store_fields:
        return True
    prefix = var_name.split(".")[0]
    return prefix in store_fields


def extract_variables(qa_matrix: dict) -> list:
    seen = set()
    for client_data in qa_matrix.get("clients", {}).values():
        for key in client_data.get("variables", {}):
            if key not in SKIP_VARS and not key.startswith(HOOK_PREFIX):
                seen.add(key)
    return sorted(seen)


def main():
    parser = argparse.ArgumentParser(description="Validate B2B variables against @yomcl/types Store")
    parser.add_argument("--input", default="data/qa-matrix.json")
    parser.add_argument("--var", help="Check a single variable")
    parser.add_argument("--skip-api", action="store_true", help="Use existing JSON only")
    parser.add_argument("--force", action="store_true", help="Re-check all variables")
    args = parser.parse_args()

    token = load_env_token()
    if token:
        print(f"🔑 GitHub token found")
    else:
        print(f"⚠️  No GITHUB_TOKEN in .env")

    status = load_status_cache()
    cached_vars = status.get("variables", {})

    if args.skip_api:
        print_summary(cached_vars)
        return

    matrix_path = Path(args.input)
    if not matrix_path.exists():
        print(f"Error: {args.input} not found.", file=sys.stderr)
        sys.exit(1)

    with open(matrix_path) as f:
        qa_matrix = json.load(f)

    variables = [args.var] if args.var else extract_variables(qa_matrix)
    print(f"📋 {len(variables)} variables to check\n")

    store_fields = build_store_type_fields(token)

    to_check = [v for v in variables if args.force or v not in cached_vars]
    already_cached = len(variables) - len(to_check)
    if already_cached:
        print(f"   → {already_cached} already cached, checking {len(to_check)} new\n")

    if not to_check:
        print("   All cached. Use --force to re-check.")
        print_summary(cached_vars)
        return

    print("🔍 Checking against @yomcl/types Store:")
    for var in to_check:
        in_type = is_in_store_type(var, store_fields)
        if in_type:
            cached_vars[var] = {"implemented": True, "files": []}
            print(f"  ✓ {var}")
        else:
            cached_vars[var] = {"implemented": False, "files": [], "reason": "not in @yomcl/types Store — mobile/backend only"}
            print(f"  ✗ {var} — not in Store type")

    status["variables"] = cached_vars
    status["b2bRepo"] = B2B_REPO
    status["typesRepo"] = TYPES_REPO
    status["note"] = "Single step: @yomcl/types Store type check only"
    save_status(status)
    print()
    print_summary(cached_vars)


def print_summary(variables: dict) -> None:
    implemented     = [k for k, v in variables.items() if v.get("implemented") is True]
    not_implemented = [k for k, v in variables.items() if v.get("implemented") is False]

    print(f"\n📊 Summary:")
    print(f"   ✓ In @yomcl/types Store (B2B relevant):  {len(implemented)}")
    print(f"   ✗ Not in Store type (skip tests):        {len(not_implemented)}")

    if not_implemented:
        print(f"\n   ✗ Variables to skip ({len(not_implemented)}):")
        for v in sorted(not_implemented):
            print(f"     - {v}")
        print(f"\n   → These tests will be SKIPPED in Playwright.")


if __name__ == "__main__":
    main()

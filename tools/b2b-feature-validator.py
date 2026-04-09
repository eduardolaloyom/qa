#!/usr/bin/env python3
"""
b2b-feature-validator.py

Three-state check for each MongoDB config variable:

  implemented: false  → NOT in @yomcl/types Store → mobile/backend-only → SKIP tests
  implemented: null   → In Store type but not found in b2b@staging code → unknown
                        (could be backend-controlled OR a stub — dev team to confirm)
  implemented: true   → In Store type AND found in b2b@staging source code → confirmed

Only `false` variables are skipped in Playwright.
`null` variables run tests (backend-controlled features still affect B2B UX).

Usage:
    python3 tools/b2b-feature-validator.py --input data/qa-matrix-staging.json
    python3 tools/b2b-feature-validator.py --var confirmCartText
    python3 tools/b2b-feature-validator.py --skip-api        # use existing JSON only
    python3 tools/b2b-feature-validator.py --force           # re-check all
    python3 tools/b2b-feature-validator.py --refresh-source  # re-download b2b tarball

Output:
    data/b2b-feature-status.json
"""

import json
import re
import sys
import base64
import shutil
import tarfile
import argparse
import tempfile
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime, timezone


B2B_REPO     = "YOMCL/b2b"
B2B_BRANCH   = "staging"
TYPES_REPO   = "YOMCL/monorepo"
STATUS_FILE  = Path("data/b2b-feature-status.json")
SOURCE_CACHE = Path("data/.b2b-source-cache")

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


def download_b2b_source(token: str, refresh: bool = False) -> Path:
    src_dir = SOURCE_CACHE / "src"
    if src_dir.exists() and not refresh:
        print(f"📁 Using cached b2b source: {SOURCE_CACHE}")
        return SOURCE_CACHE

    print(f"⬇️  Downloading YOMCL/b2b@{B2B_BRANCH} tarball...")
    url = f"https://api.github.com/repos/{B2B_REPO}/tarball/{B2B_BRANCH}"
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("User-Agent", "YOM-QA-Validator/1.0")
    if token:
        req.add_header("Authorization", f"token {token}")

    tmp_tar = Path(tempfile.mktemp(suffix=".tar.gz"))
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            tmp_tar.write_bytes(resp.read())
        print(f"   Downloaded {tmp_tar.stat().st_size // 1024} KB")
    except Exception as e:
        print(f"❌ Failed to download tarball: {e}", file=sys.stderr)
        sys.exit(1)

    if SOURCE_CACHE.exists():
        shutil.rmtree(SOURCE_CACHE)
    SOURCE_CACHE.mkdir(parents=True)

    print(f"📦 Extracting to {SOURCE_CACHE}...")
    with tarfile.open(tmp_tar) as tar:
        tar.extractall(SOURCE_CACHE)
    tmp_tar.unlink()

    subdirs = [d for d in SOURCE_CACHE.iterdir() if d.is_dir()]
    if len(subdirs) == 1:
        extracted = subdirs[0]
        for item in extracted.iterdir():
            shutil.move(str(item), SOURCE_CACHE / item.name)
        extracted.rmdir()

    print(f"   ✅ Source ready\n")
    return SOURCE_CACHE


def extract_usestore_vars(source_dir: Path) -> dict:
    """
    Extract all variables/objects read from the store via useStore() across the codebase.
    Returns {varName: [files]}.

    Captures three patterns:
      1. const { foo, bar } = useStore();          → destructuring
      2. const store = useStore(); store.foo        → whole-object access
      3. const site = useStore(); site.foo          → alias access
    """
    src_path = source_dir / "src"
    if not src_path.exists():
        src_path = source_dir

    # Pattern 1: destructuring
    destructure_re = re.compile(r'const\s*\{([^}]+)\}\s*=\s*useStore\(\)')
    field_re = re.compile(r'(\w+)(?:\s*:\s*\w+)?')

    # Pattern 2 & 3: const ALIAS = useStore() → ALIAS.prop
    alias_re = re.compile(r'const\s+(\w+)\s*=\s*useStore\(\)')

    var_files: dict = {}

    def add(field, rel):
        if field not in var_files:
            var_files[field] = []
        if rel not in var_files[field]:
            var_files[field].append(rel)

    for ext in ("*.ts", "*.tsx"):
        for filepath in src_path.rglob(ext):
            if any(p in str(filepath) for p in ("__tests__", "__mocks__", ".test.", ".spec.", ".d.ts")):
                continue
            try:
                content = filepath.read_text(encoding="utf-8", errors="ignore")
                rel = str(filepath.relative_to(source_dir))

                # Pattern 1: destructuring
                for match in destructure_re.finditer(content):
                    for field_match in field_re.finditer(match.group(1)):
                        add(field_match.group(1), rel)

                # Pattern 2 & 3: alias.prop
                for alias_match in alias_re.finditer(content):
                    alias = alias_match.group(1)
                    prop_re = re.compile(r'\b' + re.escape(alias) + r'[\?\!]?\.(\w+)')
                    for prop_match in prop_re.finditer(content):
                        add(prop_match.group(1), rel)

            except Exception:
                continue

    return var_files


def search_in_local_source(var_name: str, usestore_vars: dict) -> tuple:
    """
    Check if var_name is accessed via useStore() in b2b source.

    For top-level vars (enablePayments): check if in usestore_vars directly.
    For nested vars (payment.walletEnabled): check if the parent object (payment)
    is in usestore_vars — meaning the component accesses the payment object
    and could access sub-fields.
    """
    top = var_name.split(".")[0]

    if var_name in usestore_vars:
        return (True, usestore_vars[var_name][:5])

    if top != var_name and top in usestore_vars:
        # Parent object is destructured — sub-fields are accessible
        return (True, usestore_vars[top][:5])

    return (False, [])


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
    parser = argparse.ArgumentParser(description="Validate B2B variables (3-state)")
    parser.add_argument("--input", default="data/qa-matrix.json")
    parser.add_argument("--var", help="Check a single variable")
    parser.add_argument("--skip-api", action="store_true", help="Use existing JSON only")
    parser.add_argument("--force", action="store_true", help="Re-check all variables")
    parser.add_argument("--refresh-source", action="store_true", help="Re-download b2b staging source")
    args = parser.parse_args()

    token = load_env_token()
    print(f"🔑 GitHub token {'found' if token else 'NOT FOUND — private repo access will fail'}")

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
    source_dir = download_b2b_source(token, refresh=args.refresh_source)

    print("🔎 Extracting useStore() destructuring from b2b source...")
    usestore_vars = extract_usestore_vars(source_dir)
    print(f"   → {len(usestore_vars)} variables/objects read via useStore(): {', '.join(sorted(usestore_vars.keys()))}\n")

    to_check = [v for v in variables if args.force or v not in cached_vars]
    already_cached = len(variables) - len(to_check)
    if already_cached:
        print(f"   → {already_cached} already cached, checking {len(to_check)} new\n")

    if not to_check:
        print("   All cached. Use --force to re-check.")
        print_summary(cached_vars)
        return

    print("🔍 Checking variables:")
    for var in to_check:
        in_type = is_in_store_type(var, store_fields)

        if not in_type:
            # false → not B2B at all, skip tests
            cached_vars[var] = {
                "implemented": False,
                "files": [],
                "reason": "not in @yomcl/types Store — mobile/backend only",
            }
            print(f"  ✗ {var} — not in Store type (skip)")
        else:
            # In Store type → check if frontend reads it
            found, files = search_in_local_source(var, usestore_vars)
            if found:
                # true → confirmed in frontend code
                cached_vars[var] = {"implemented": True, "files": files}
                leaf = var.split(".")[-1] if "." in var else var
                display = f"(→ '{leaf}')" if "." in var else ""
                print(f"  ✓ {var} {display}— confirmed in b2b code ({len(files)} file{'s' if len(files)!=1 else ''})")
            else:
                # null → in type but not found in frontend code
                # Could be backend-controlled OR a stub — don't skip tests
                cached_vars[var] = {
                    "implemented": None,
                    "files": [],
                    "reason": f"in @yomcl/types but not found in b2b@{B2B_BRANCH} code — may be backend-controlled or stub",
                }
                print(f"  ? {var} — in Store type but not in frontend code")

    status["variables"] = cached_vars
    status["b2bRepo"] = B2B_REPO
    status["b2bBranch"] = B2B_BRANCH
    status["typesRepo"] = TYPES_REPO
    status["note"] = "3-state: false=skip(not in type) | null=unknown | true=confirmed in frontend"
    save_status(status)
    print()
    print_summary(cached_vars)


def print_summary(variables: dict) -> None:
    confirmed = [k for k, v in variables.items() if v.get("implemented") is True]
    unknown   = [k for k, v in variables.items() if v.get("implemented") is None]
    skip      = [k for k, v in variables.items() if v.get("implemented") is False]

    print(f"\n📊 Summary:")
    print(f"   ✓ Confirmed in b2b frontend:        {len(confirmed)}")
    print(f"   ? In Store type, not in code:       {len(unknown)}  (backend-controlled or stub)")
    print(f"   ✗ Not in Store type (SKIP tests):   {len(skip)}")

    if skip:
        print(f"\n   ✗ Variables to skip ({len(skip)}):")
        for v in sorted(skip):
            print(f"     - {v}")
        print(f"\n   → These tests will be SKIPPED in Playwright.")


if __name__ == "__main__":
    main()

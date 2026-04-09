#!/usr/bin/env python3
"""
b2b-feature-validator.py

Checks which MongoDB config variables are actually implemented in the B2B frontend
repo (YOMCL/b2b) by searching via GitHub API Code Search.

Usage:
    python3 tools/b2b-feature-validator.py                        # all clients
    python3 tools/b2b-feature-validator.py --input data/qa-matrix-staging.json
    python3 tools/b2b-feature-validator.py --var confirmCartText  # single variable
    python3 tools/b2b-feature-validator.py --skip-api             # use existing JSON only

Output:
    data/b2b-feature-status.json

Notes:
    - GITHUB_TOKEN in .env (root) is optional but recommended (rate limit: 30 req/min with token, 10 without)
    - Existing b2b-feature-status.json is used as a cache — only unknown variables are re-checked
    - The JSON can be manually edited to override API results
"""

import json
import sys
import time
import argparse
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from datetime import datetime, timezone


B2B_REPO = "YOMCL/b2b"
STATUS_FILE = Path("data/b2b-feature-status.json")

# Variables that are infrastructure/internal and should be skipped
SKIP_VARS = {
    "_id", "__v", "createdAt", "updatedAt", "domain", "customerId",
    "currency", "inMaintenance",
}

# Variables that map to internal hooks — they exist as function calls, not string literals
HOOK_PREFIX = "hooks."


def load_env_token() -> str:
    """Try to load GITHUB_TOKEN from .env files."""
    for env_path in [Path(".env"), Path("tests/e2e/.env"), Path(".claude/.env")]:
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if line.startswith("GITHUB_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def load_status_cache() -> dict:
    """Load existing b2b-feature-status.json as cache."""
    if STATUS_FILE.exists():
        with open(STATUS_FILE) as f:
            return json.load(f)
    return {"b2bRepo": B2B_REPO, "variables": {}}


def save_status(status: dict) -> None:
    """Save b2b-feature-status.json."""
    status["generatedAt"] = datetime.now(timezone.utc).isoformat()
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f, indent=2)
    print(f"✅ Saved {STATUS_FILE}")


def extract_variables(qa_matrix: dict) -> list[str]:
    """Extract unique variable names from qa-matrix.json across all clients."""
    seen = set()
    for client_data in qa_matrix.get("clients", {}).values():
        for key in client_data.get("variables", {}):
            if key not in SKIP_VARS and not key.startswith(HOOK_PREFIX):
                seen.add(key)
    return sorted(seen)


def search_in_b2b(var_name: str, token: str) -> tuple[bool, list[str]]:
    """
    Search for var_name in YOMCL/b2b via GitHub Code Search API.
    Returns (found: bool, files: list[str])
    """
    query = urllib.parse.quote(f"{var_name} repo:{B2B_REPO}")
    url = f"https://api.github.com/search/code?q={query}&per_page=5"

    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("User-Agent", "YOM-QA-Validator/1.0")
    if token:
        req.add_header("Authorization", f"token {token}")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            items = data.get("items", [])
            files = [item.get("path", "") for item in items]
            return (len(items) > 0, files)
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print(f"  ⚠️  Rate limit reached — waiting 60s...")
            time.sleep(60)
            return search_in_b2b(var_name, token)  # retry once
        elif e.code == 422:
            # Validation failed — variable name too short or invalid query
            return (None, [])
        else:
            print(f"  ⚠️  HTTP {e.code} for {var_name}", file=sys.stderr)
            return (None, [])
    except Exception as e:
        print(f"  ⚠️  Error searching {var_name}: {e}", file=sys.stderr)
        return (None, [])


def main():
    parser = argparse.ArgumentParser(description="Validate B2B feature implementation for QA variables")
    parser.add_argument("--input", default="data/qa-matrix.json", help="Path to qa-matrix.json")
    parser.add_argument("--var", help="Check a single variable name")
    parser.add_argument("--skip-api", action="store_true", help="Skip API calls, use existing JSON only")
    parser.add_argument("--force", action="store_true", help="Re-check all variables even if cached")
    args = parser.parse_args()

    token = load_env_token()
    if token:
        print(f"🔑 GitHub token found — rate limit: 30 req/min")
    else:
        print(f"⚠️  No GITHUB_TOKEN found in .env — rate limit: 10 req/min (add GITHUB_TOKEN=... to .env)")

    # Load cache
    status = load_status_cache()
    cached_vars = status.get("variables", {})

    if args.skip_api:
        print(f"ℹ️  --skip-api: using existing {STATUS_FILE}")
        print_summary(cached_vars)
        return

    # Load qa-matrix
    matrix_path = Path(args.input)
    if not matrix_path.exists():
        print(f"Error: {args.input} not found. Run: python3 data/mongo-extractor.py", file=sys.stderr)
        sys.exit(1)

    with open(matrix_path) as f:
        qa_matrix = json.load(f)

    if args.var:
        variables = [args.var]
    else:
        variables = extract_variables(qa_matrix)

    print(f"📋 {len(variables)} variables to check in {B2B_REPO}")

    # Determine which to check (skip cached unless --force)
    to_check = [v for v in variables if args.force or v not in cached_vars]
    skip_count = len(variables) - len(to_check)

    if skip_count > 0:
        print(f"   → {skip_count} already cached, checking {len(to_check)} new ones")
    if not to_check:
        print("   All variables already cached. Use --force to re-check.")
        print_summary(cached_vars)
        return

    # Estimate time
    delay = 2.5 if not token else 2.0
    est_minutes = round(len(to_check) * delay / 60, 1)
    print(f"   ⏱  Estimated time: ~{est_minutes} min ({delay}s delay between requests)")
    print()

    # Check each variable
    for i, var_name in enumerate(to_check, 1):
        print(f"  [{i:02d}/{len(to_check):02d}] {var_name}... ", end="", flush=True)
        found, files = search_in_b2b(var_name, token)

        if found is None:
            print("⚠️  skipped (API error)")
            # Don't overwrite cache for errors
        elif found:
            print(f"✓ ({len(files)} file{'s' if len(files) != 1 else ''})")
            cached_vars[var_name] = {"implemented": True, "files": files}
        else:
            print(f"✗ NOT FOUND")
            cached_vars[var_name] = {"implemented": False, "files": []}

        time.sleep(delay)

    status["variables"] = cached_vars
    status["b2bRepo"] = B2B_REPO
    save_status(status)
    print()
    print_summary(cached_vars)


def print_summary(variables: dict) -> None:
    """Print a summary of implemented vs not implemented."""
    implemented = [k for k, v in variables.items() if v.get("implemented") is True]
    not_implemented = [k for k, v in variables.items() if v.get("implemented") is False]
    unknown = [k for k, v in variables.items() if v.get("implemented") is None]

    print(f"\n📊 Summary:")
    print(f"   ✓ Implemented in B2B:     {len(implemented)}")
    print(f"   ✗ NOT in B2B (no code):   {len(not_implemented)}")
    if unknown:
        print(f"   ? Unknown (API error):    {len(unknown)}")

    if not_implemented:
        print(f"\n⚠️  Variables NOT implemented in {B2B_REPO}:")
        for v in sorted(not_implemented):
            print(f"   - {v}")
        print(f"\n   These tests will be SKIPPED in Playwright.")
        print(f"   Edit data/b2b-feature-status.json manually to override.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Publish QA test results to GitHub Pages.

Copies Playwright reports to public/ and generates history JSON files.

Usage:
    python3 tools/publish-results.py [--date YYYY-MM-DD]

If --date is not provided, uses today's date.
"""

import json
import shutil
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional


def load_results(results_file: Path) -> dict:
    """Load Playwright JSON results."""
    if not results_file.exists():
        print(f"⚠️  No results.json found at {results_file}", file=sys.stderr)
        print("   Run tests first: npx playwright test", file=sys.stderr)
        return {}

    with open(results_file) as f:
        return json.load(f)


def copy_playwright_report(src: Path, dst: Path) -> None:
    """Copy entire Playwright HTML report."""
    if src.exists():
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f"✅ Copied Playwright report to {dst}")
    else:
        print(f"⚠️  Playwright report not found at {src}", file=sys.stderr)


def copy_test_results_artifacts(src: Path, dst: Path) -> None:
    """Copy screenshots and artifacts from test results."""
    if not src.exists():
        return

    dst.mkdir(parents=True, exist_ok=True)

    # Copy all .png screenshots
    png_count = 0
    for png_file in src.rglob("*.png"):
        rel_path = png_file.relative_to(src)
        dst_file = dst / rel_path.name  # Flatten to data/ root
        shutil.copy2(png_file, dst_file)
        png_count += 1

    if png_count > 0:
        print(f"✅ Copied {png_count} screenshot(s) to {dst}")


def flatten_tests(suite: dict, file_hint: str = "") -> list:
    """Recursively extract all tests from Playwright JSON suite structure."""
    tests = []
    file_name = suite.get("file", file_hint)
    for spec in suite.get("specs", []):
        for test in spec.get("tests", []):
            tests.append({"file": file_name, "status": test.get("status")})
    for sub in suite.get("suites", []):
        tests.extend(flatten_tests(sub, file_name))
    return tests


def extract_suite_stats(results: dict, suite_name: str) -> dict:
    """Extract stats for a specific suite from Playwright results."""
    all_tests = []
    for suite in results.get("suites", []):
        all_tests.extend(flatten_tests(suite))

    suite_tests = [t for t in all_tests if suite_name in t.get("file", "")]

    passed = sum(1 for t in suite_tests if t.get("status") in ("expected", "flaky"))
    failed = sum(1 for t in suite_tests if t.get("status") == "unexpected")
    skipped = sum(1 for t in suite_tests if t.get("status") == "skipped")

    return {
        "tests": len(suite_tests),
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
    }


def generate_run_json(results: dict, date: str) -> dict:
    """Generate the detailed run JSON."""
    # Only include suites that actually ran (tests > 0)
    all_tests_flat = []
    for suite in results.get("suites", []):
        all_tests_flat.extend(flatten_tests(suite))

    # Discover which spec files actually had tests
    ran_files = sorted(set(t.get("file", "") for t in all_tests_flat if t.get("file")))

    suites = []
    total_tests = 0
    total_passed = 0
    total_failed = 0

    for file_path in ran_files:
        suite_name = file_path.split("/")[-1] if "/" in file_path else file_path
        suite_tests = [t for t in all_tests_flat if t.get("file") == file_path]
        passed = sum(1 for t in suite_tests if t.get("status") in ("expected", "flaky"))
        failed = sum(1 for t in suite_tests if t.get("status") == "unexpected")
        suites.append({
            "name": suite_name,
            "tests": len(suite_tests),
            "passed": passed,
            "failed": failed,
            "reportUrl": "reports/index.html",
        })
        total_tests += len(suite_tests)
        total_passed += passed
        total_failed += failed

    # Calculate duration (in seconds from Playwright data)
    duration = 0
    if results.get("stats"):
        duration = int(results["stats"].get("duration", 0) / 1000)

    # Per-client stats derived from actual results
    codelpa_stats = extract_suite_stats(results, "codelpa.spec.ts")
    surtiventas_stats = extract_suite_stats(results, "surtiventas.spec.ts")

    clients = {
        "codelpa": {
            "name": "Codelpa",
            "url": "https://beta-codelpa.solopide.me",
            "tests": codelpa_stats["tests"],
            "passed": codelpa_stats["passed"],
            "failed": codelpa_stats["failed"],
            "reportUrl": "reports/index.html",
        },
        "surtiventas": {
            "name": "Surtiventas",
            "url": "https://surtiventas.solopide.me",
            "tests": surtiventas_stats["tests"],
            "passed": surtiventas_stats["passed"],
            "failed": surtiventas_stats["failed"],
            "reportUrl": "reports/index.html",
        },
    }

    return {
        "date": date,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total": total_tests,
        "passed": total_passed,
        "failed": total_failed,
        "duration": duration,
        "suites": suites,
        "clients": clients,
        "evidence": {
            "screenshots": [],
            "errors": [],
        },
    }


def update_history_index(history_dir: Path, date: str, run_json: dict) -> None:
    """Update history/index.json with the new run."""
    index_file = history_dir / "index.json"

    # Load existing index or create new
    if index_file.exists():
        with open(index_file) as f:
            index = json.load(f)
    else:
        index = {"runs": []}

    # Check if this date already exists
    existing_run = next((r for r in index["runs"] if r["date"] == date), None)
    new_run_entry = {
        "date": date,
        "total": run_json["total"],
        "passed": run_json["passed"],
        "failed": run_json["failed"],
        "duration": run_json["duration"],
    }

    if existing_run:
        # Update existing
        idx = index["runs"].index(existing_run)
        index["runs"][idx] = new_run_entry
    else:
        # Insert at beginning (most recent first)
        index["runs"].insert(0, new_run_entry)

    # Keep only last 30 days
    index["runs"] = index["runs"][:30]

    with open(index_file, "w") as f:
        json.dump(index, f, indent=2)


def main():
    """Main entry point."""
    # Parse date argument
    date = None
    if len(sys.argv) > 1:
        if sys.argv[1] == "--date" and len(sys.argv) > 2:
            date = sys.argv[2]
        else:
            print(f"Usage: python3 {sys.argv[0]} [--date YYYY-MM-DD]", file=sys.stderr)
            sys.exit(1)

    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    print(f"Publishing results for {date}...")

    # Paths
    project_root = Path(__file__).parent.parent
    results_file = project_root / "tests" / "e2e" / "playwright-report" / "results.json"
    src_report = project_root / "tests" / "e2e" / "playwright-report"
    src_test_results = project_root / "tests" / "e2e" / "test-results"

    dst_reports = project_root / "public" / "reports"
    dst_data = project_root / "public" / "data"
    history_dir = project_root / "public" / "history"

    # Ensure history directory exists
    history_dir.mkdir(parents=True, exist_ok=True)

    # Load results
    results = load_results(results_file)

    # Copy reports
    copy_playwright_report(src_report, dst_reports)

    # Copy artifacts
    copy_test_results_artifacts(src_test_results, dst_data)

    # Generate run JSON
    run_json = generate_run_json(results, date)

    # Write run details
    run_file = history_dir / f"{date}.json"
    with open(run_file, "w") as f:
        json.dump(run_json, f, indent=2)
    print(f"✅ Generated {run_file}")

    # Update history index
    update_history_index(history_dir, date, run_json)
    print(f"✅ Updated history/index.json")

    # Summary
    print(f"\n📊 Summary:")
    print(f"   Total: {run_json['total']}")
    print(f"   Passed: {run_json['passed']} ✅")
    print(f"   Failed: {run_json['failed']} ❌")
    print(f"   Duration: {run_json['duration']}s ({run_json['duration'] / 60:.1f}m)")
    print(f"\n✨ Dashboard ready: open public/index.html or visit GitHub Pages")


if __name__ == "__main__":
    main()

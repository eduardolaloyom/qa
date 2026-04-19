# Technology Stack

**Analysis Date:** 2026-04-19

## Languages

**Primary:**
- TypeScript — Playwright E2E specs, global teardown, fixtures (`tests/e2e/`)
- Python 3.9.6 — reporting pipeline tools (`tools/publish-results.py`, `data/mongo-extractor.py`)
- JavaScript (CommonJS) — live reporter Playwright plugin (`tools/live-reporter.js`)
- Bash — Maestro runner and HTML report generation (`tools/run-maestro.sh`)

**Secondary:**
- HTML/CSS/vanilla JS — dashboard frontend (`public/index.html`), Cowork reports (`public/qa-reports/*.html`), Maestro reports (`public/app-reports/*.html`)

## Runtime

**Environment:**
- Node.js v25.8.2 (runtime for Playwright and live-reporter.js)
- Python 3.9.6 (runtime for all pipeline scripts)

**Package Manager:**
- npm (root `package.json` uses workspaces; `tests/e2e/package.json` is the inner workspace)
- Lockfile: `package-lock.json` present at repo root

## Frameworks

**Core:**
- `@playwright/test` 1.52.0 — E2E test runner for B2B (`tests/e2e/b2b/`) and Admin (`tests/e2e/admin/`)
- Maestro 1.40.0+ (minimum enforced) — Android mobile flow runner (`tests/app/flows/`)

**Build/Dev:**
- `dotenv` ^16.4.0 — `.env` loading for Playwright fixtures

**Dashboard:**
- Chart.js (CDN, `https://cdn.jsdelivr.net/npm/chart.js`) — trend chart rendered in `public/index.html`
- `peaceiris/actions-gh-pages@v3` (GitHub Action) — deploys `public/` to GitHub Pages on push to `main`

## Reporting Pipeline Components

**`tools/live-reporter.js`:**
- Custom Playwright reporter (CommonJS, `module.exports = LiveReporter`)
- Implements `onBegin`, `onTestBegin`, `onTestEnd`, `onEnd` Playwright reporter hooks
- Writes real-time state to `public/live.json` atomically (write-to-tmp then rename)
- Pushes `live.json` to GitHub via Contents API every 10 seconds (`PUSH_INTERVAL_MS = 10_000`)
- Requires `GITHUB_TOKEN` env var; silently skips push if absent
- Caches the SHA of the remote file to avoid redundant GET requests on each push

**`tools/publish-results.py`:**
- Pure Python 3, no external dependencies (stdlib only: `json`, `re`, `shutil`, `pathlib`, `collections`, `datetime`)
- Reads `tests/e2e/playwright-report/results.json` (Playwright JSON reporter output)
- Copies Playwright HTML report to `public/reports/{slug}/` (per-client) or `public/reports/`
- Copies PNG screenshots from `tests/e2e/test-results/` to `public/data/`
- Generates `public/history/{YYYY-MM-DD}.json` — full run detail with per-client stats, failure groups, pending B2B items
- Updates `public/history/index.json` — rolling 30-day index (most-recent-first)
- Merges results when called multiple times on the same date (accumulates clients/suites)
- Seeds new-day runs with prior-day client results so dashboard stays populated
- Classifies failures into categories: `bug`, `ux`, `ambiente`, `flaky` with owner (`dev`/`qa`) and actionable text
- Redacts secrets (Bearer tokens, sk- keys, GitHub tokens, AWS keys, JWTs, MongoDB URIs) from error text before writing to public files
- Args: `--date YYYY-MM-DD`, `--results-file PATH`, `--client SLUG`

**`tests/e2e/global-teardown.ts`:**
- TypeScript, runs automatically after every Playwright suite (configured in `playwright.config.ts`)
- Kills any process holding port 8080 (cleanup of dev server)
- Calls `python3 tools/publish-results.py` via `execSync`
- If not in CI (`process.env.CI` is unset): stages `public/`, commits `chore: publish playwright results {date}`, and pushes (with `git pull --rebase` on rejection)
- Reads the generated `public/history/{date}.json` to detect failures and print a triage hint

**`tools/run-maestro.sh`:**
- Bash script; inline Python used for flow execution loop and HTML report generation
- Config lookup: prefers `tests/app/config/config.{cliente}.yaml` (new format), falls back to `tests/app/config/env.{cliente}.yaml` (legacy)
- Runs flows from `tests/app/flows/{cliente}-session.yaml` (single session) or `tests/app/flows/{cliente}-NN-*.yaml` (individual flows)
- Retry logic: 3 attempts for individual flows; 1 attempt for session flows
- Interactive mode (`--interactive`): prompts tester with 30-second timeout (m=manual-pass, r=retry, s=skip)
- Output: writes `QA/{Cliente}/{DATE}/maestro.log`, then generates `public/app-reports/{cliente}-{date}.html`
- Updates `public/app-reports/manifest.json` with per-run metadata (client, date, health%, verdict, passed/failed/skipped/manual)
- Health score: `(passed + manual_pass) / (total - skipped) * 100`; verdict: LISTO ≥100%, CON OBSERVACIONES ≥70%, BLOQUEADO <70%

## Key Dependencies

**Critical:**
- `pymongo[srv]` — required by `data/mongo-extractor.py` to connect to MongoDB Atlas clusters; not in `package.json` (installed via pip)
- `pyyaml` — required by `tools/run-maestro.sh` inline Python for config and flow YAML parsing

**Infrastructure:**
- `@playwright/test` 1.52.0 — pinned in `tests/e2e/package.json`

## Configuration

**Environment:**
- `.env` at repo root (gitignored): loaded by `data/mongo-extractor.py` via custom `_load_env()` and by Playwright fixtures via `dotenv`
- `.env.example` at repo root: documents the 6 MongoDB URI vars and usage
- `tests/app/config/config.{cliente}.yaml` or `tests/app/config/env.{cliente}.yaml`: per-client Maestro environment variables

**Playwright Config:**
- `tests/e2e/playwright.config.ts`: defines projects (b2b, admin), reporter list (includes `tools/live-reporter.js`), globalTeardown, and webServer
- Reporter list must include `['./../../tools/live-reporter.js']` for live dashboard to activate

**Build:**
- No build step; TypeScript is executed directly by `npx playwright test`
- `public/` directory is the deployment artifact — fully static, committed to git

## Platform Requirements

**Development:**
- macOS (ADB path hardcoded: `~/Library/Android/sdk/platform-tools` in `run-maestro.sh`)
- Android device connected via USB with debugging enabled (Maestro flows)
- `brew install openjdk@17` for Maestro/ADB Java requirement
- `GITHUB_TOKEN` env var for live dashboard pushes

**Production:**
- GitHub Pages: deployed from `public/` via `peaceiris/actions-gh-pages@v3` on push to `main`
- Trigger: workflow at `.github/workflows/deploy-qa-dashboard.yml`, path filter `public/**`
- No server-side code; dashboard is 100% static (HTML + fetch from same-origin JSON)

---

*Stack analysis: 2026-04-19*

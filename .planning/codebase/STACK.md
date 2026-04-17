# Technology Stack

**Analysis Date:** 2026-04-17

## Languages

**Primary:**
- TypeScript 5.x - Playwright E2E tests (`tests/e2e/b2b/*.spec.ts`, `tests/e2e/admin/*.spec.ts`, `tests/e2e/fixtures/*.ts`)
- Python 3.9+ - Data extraction and automation scripts (`data/mongo-extractor.py`, `tools/sync-clients.py`, `tools/publish-results.py`)
- YAML - Maestro flow definitions (`tests/app/flows/*.yaml`, `tests/app/config/*.yaml`)
- Bash - Shell automation scripts (`tools/run-qa.sh`, `tools/run-maestro.sh`)
- JavaScript - Reporting and configuration (`tools/live-reporter.js`)

**Secondary:**
- HTML/CSS - Dashboard and report generation (`tools/report/generate-grouped-report.py`)

## Runtime

**Environment:**
- Node.js 20+ (Playwright tests and package management)
- Python 3.9+ (Data extraction pipelines and automation)
- Maestro CLI (APP mobile testing on Android devices)

**Package Manager:**
- npm (Node.js dependencies)
- pip (Python dependencies)
- Lockfile: `package-lock.json` present (at root and `tests/e2e/`)

## Frameworks

**Core Testing:**
- Playwright `^1.52.0` - E2E testing framework for B2B web and Admin UI
  - Config: `tests/e2e/playwright.config.ts`
  - Projects: `b2b`, `admin`
  - Reporters: HTML, JSON, list, custom live-reporter

**APP Mobile:**
- Maestro - Flow-based automation for Android testing
  - Flows stored in: `tests/app/flows/`
  - Configuration: `tests/app/config/config.{CLIENT}.yaml`

**Data Access:**
- pymongo `[srv]` - MongoDB connection and data extraction
  - Used in: `data/mongo-extractor.py`
  - Connects to 3 clusters: legacy, microservices, integrations

**Build/Dev:**
- dotenv `^16.4.0` - Environment variable management
  - Loaded in Playwright and Python scripts

## Key Dependencies

**Critical:**
- `@playwright/test` `^1.52.0` - E2E automation, screenshot/video capture, parallel execution
  - Used for regression tests across 17 clients (B2B and Admin interfaces)
  - Configured with 4 workers, retries in CI, long timeouts (30s action, 60s navigation, 120s test)

- `pymongo[srv]` - MongoDB Atlas connectivity
  - Extracts configuration from 3 MongoDB clusters
  - Used in: `mongo-extractor.py` (mandatory step before test execution)

**Infrastructure:**
- dotenv - Configuration from `.env` files
  - MongoDB URIs (legacy, micro, integrations)
  - Client credentials (email/password)
  - Base URLs (B2B, Admin)

## Configuration

**Environment:**
- `.env` file (not committed) - Contains MongoDB URIs and client credentials
  - Template: `.env.example` provides structure
  - Three MongoDB clusters configured:
    - `MONGO_LEGACY_URI` - Products, orders, customers, salesterms
    - `MONGO_MICRO_URI` - Feature flags, promotions, banners
    - `MONGO_INTEGRATIONS_URI` - Segments, overrides, user segments
  - Support for staging vs production via `--env` flag in extractor

- `tests/e2e/.env` - Playwright-specific configuration
  - BASE_URL: tienda.youorder.me (default)
  - ADMIN_URL: admin.youorder.me
  - Client credentials: `{CLIENT}_EMAIL`, `{CLIENT}_PASSWORD`

- `tests/app/config/config.{CLIENT}.yaml` - Maestro app configuration
  - App-specific environment settings per client

**Build:**
- `playwright.config.ts` - Playwright test configuration
  - Global setup/teardown: `global-setup.ts`, `global-teardown.ts`
  - Fully parallel execution with 4 workers
  - Timeouts: action 30s, navigation 60s, test 120s, expect 15s
  - Screenshot on failure, video on first retry, trace on first retry
  - Multi-project: `b2b` (Chrome), `admin` (Chrome)

- `package.json` (root) - Project metadata and workspace configuration
  - Workspaces: `tests/e2e`

- `package.json` (`tests/e2e/`) - E2E test scripts
  - test, test:headed, test:ui, test:debug, test:login, test:catalog, test:cart, test:checkout, test:prices
  - report (show-report)

## Platform Requirements

**Development:**
- macOS / Linux (development environment)
- 4+ GB RAM (Playwright parallel workers)
- Chrome/Chromium (via Playwright install)
- Android device or emulator (Maestro APP tests)
- MongoDB Atlas credentials

**Production:**
- Deployment: GitHub Pages (dashboard)
- CI/CD: GitHub Actions (workflow: `deploy-qa-dashboard.yml`)
  - Triggered on `public/**` changes
  - Uses `peaceiris/actions-gh-pages@v3` for deployment

**Testing:**
- Chrome/Chromium desktop (B2B and Admin web)
- Real Android device with Maestro (APP mobile)
- Network access to YOM staging and production environments

## Build Pipeline

**Test Execution Flow:**

```
1. Python: python3 data/mongo-extractor.py [--env staging|production]
   → Extracts site config from MongoDB clusters
   → Outputs: data/qa-matrix.json

2. Python: python3 tools/sync-clients.py
   → Generates: tests/e2e/fixtures/clients.ts (AUTO-GENERATED)
   → Validates B2B feature implementation status

3. TypeScript: cd tests/e2e && npx playwright test
   → Runs parametrized tests across all clients
   → Generates: playwright-report/results.json + HTML

4. Python: python3 tools/publish-results.py [--date YYYY-MM-DD]
   → Publishes to: public/qa-reports/{CLIENT}-{DATE}.html
   → Updates: public/manifest.json

5. Bash: ./tools/run-maestro.sh {CLIENT} [--env staging|production]
   → Executes Maestro flows for APP mobile
   → Generates: QA/{CLIENT}/{DATE}/maestro.log + HTML report
```

**GitHub Actions:**
- Triggered: Push to `main` with `public/**` changes
- Deploys: `public/` directory to GitHub Pages

---

*Stack analysis: 2026-04-17*

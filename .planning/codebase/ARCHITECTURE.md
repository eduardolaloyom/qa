# Architecture

**Analysis Date:** 2026-04-17

## Pattern Overview

**Overall:** Multi-layer, data-driven QA automation framework with AI-assisted testing as primary methodology.

**Key Characteristics:**
- Cowork (Claude AI) as primary QA validation tool; automated tests as regression verification
- MongoDB as single source of truth for client configuration → auto-generated test fixtures
- AI Specs framework providing standardized roles, workflows, and test standards
- Multi-client, multi-platform testing (B2B web, mobile APP, Admin portal)
- Session-based reporting with consolidated Cowork + Playwright results

## Layers

**Data Extraction & Configuration Layer:**
- Purpose: Connect to MongoDB and extract client configuration into QA matrix
- Location: `data/mongo-extractor.py`, `data/qa-matrix.json`, `data/b2b-feature-status.json`
- Contains: MongoDB connection logic (LEGACY, MICRO, INTEGRATIONS clusters), collection-specific parsers, environment variable mapping
- Depends on: MongoDB URIs from `.env`, client domain mappings
- Used by: `tools/sync-clients.py` to generate test fixtures

**Fixture & Configuration Sync Layer:**
- Purpose: Synchronize extracted MongoDB data into Playwright test fixtures
- Location: `tools/sync-clients.py`, `tests/e2e/fixtures/clients.ts` (AUTO-GENERATED)
- Contains: TypeScript client config objects (baseURL, credentials, MongoDB-sourced feature flags)
- Depends on: `data/qa-matrix.json`, `.env` credentials
- Used by: Playwright test specs via `createClientTest()` factory

**AI Specs Framework Layer:**
- Purpose: Define standardized roles, workflows, and test conventions
- Location: `ai-specs/.agents/`, `ai-specs/.commands/`, `ai-specs/specs/`
- Contains: 
  - Roles: `qa-coordinator.md`, `playwright-specialist.md`, `maestro-specialist.md`
  - Workflows: `/qa-plan-client`, `/run-playwright`, `/report-qa`, `/qa-improve`
  - Standards: `qa-standards.mdc`, `maestro-standards.mdc`, `admin-testing-standards.mdc`
- Depends on: Nothing (self-contained framework)
- Used by: Claude instructions (CLAUDE.md, COWORK.md) and orchestrators

**Playwright E2E Testing Layer (B2B Web):**
- Purpose: Automated regression testing for B2B tienda.youorder.me platform
- Location: `tests/e2e/b2b/`, `tests/e2e/fixtures/`, `tests/e2e/playwright.config.ts`
- Contains: 
  - 13 spec files: `login.spec.ts`, `cart.spec.ts`, `checkout.spec.ts`, `prices.spec.ts`, `coupons.spec.ts`, `promotions.spec.ts`, `payments.spec.ts`, `config-validation.spec.ts`, `mongo-data.spec.ts`, `payment-documents.spec.ts`, `step-pricing.spec.ts`, `catalog.spec.ts`, `orders.spec.ts` (3200+ lines total)
  - Fixtures: `multi-client-auth.ts` (client factory + helpers), `login.ts` (credential resolution), `clients.ts` (auto-generated)
  - Global setup/teardown: `global-setup.ts` (HTTP server for dashboard), `global-teardown.ts`
- Depends on: `clients.ts`, `.env` credentials, Playwright runtime
- Used by: CI/CD (npm run test), manual regression runs

**Maestro Mobile Testing Layer (Android APP):**
- Purpose: Test YOM seller mobile app user journeys
- Location: `tests/app/flows/`, `tests/app/config/`
- Contains: 
  - 13 YAML flows: `01-login.yaml`, `05-pedido.yaml`, `07-offline.yaml`, `10-descuentos.yaml`, etc. (2000+ lines)
  - Helpers: `helpers/login.yaml`, `helpers/sync.yaml`
  - Client-specific flows: `prinorte/` (11 Prinorte-specific test flows)
  - Master session: `prinorte-session.yaml` (end-to-end workflow composition)
- Depends on: Maestro CLI, Android device/emulator, `tests/app/config/config.yaml`
- Used by: Manual QA validation, Maestro CLI

**Manual Checklist Layer (Backend/Integration Testing):**
- Purpose: Comprehensive testing of backend services, ERP integrations, payment systems
- Location: `checklists/` (regresion, deuda-tecnica, servicios, funcional, admin, integraciones)
- Contains: 
  - Post-mortems: `checklist-regresion-postmortems.md` (PM1-PM7 regressions)
  - Tech debt: `checklist-deuda-tecnica-*.md` (payments, concurrency, migrations)
  - Integrations: `checklist-integraciones-erp.md`, `checklist-webhooks.md`, `checklist-fintech-khipu.md`
  - Functional: `checklist-carrito-b2b.md`, `checklist-pricing-engine.md`, `checklist-puesta-en-marcha-app.md`
- Depends on: Manual execution or API testing tools
- Used by: QA checklists, Cowork validation, coverage mapping

**Reporting & Results Layer:**
- Purpose: Consolidate test results from all platforms and generate client reports
- Location: `QA/{CLIENT}/{DATE}/`, `public/`, `ai-specs/.commands/report-qa.md`
- Contains:
  - Cowork sessions: `QA/{CLIENT}/{DATE}/cowork-session.md` (consolidated HANDOFFs)
  - QA reports: `QA/{CLIENT}/{DATE}/qa-report-{DATE}.md` (markdown report)
  - Dashboard: `public/index.html`, `public/qa-reports/`, `public/app-reports/`, `public/manifest.json`
  - Playwright reports: `tests/e2e/playwright-report/` (local HTML)
- Depends on: `tests/e2e/fixtures/clients.ts`, Cowork results, Playwright JSON results
- Used by: GitHub Pages dashboard, stakeholder communication

## Data Flow

**Primary Flow: MongoDB → Tests → Reports**

1. **Extraction:** `python3 data/mongo-extractor.py [--full] [--cliente X]`
   - Connects to MongoDB (LEGACY: yom-stores, yom-production; MICRO: yom-b2b; INTEGRATIONS: segments, overrides)
   - Extracts per-client: site variables, coupons, banners, promotions, integrations data
   - Outputs: `data/qa-matrix.json` (33 clients × 20+ MongoDB variables each)
   - Optional `--full` flag extracts 13 collections (products, orders, commerces, sellers, segments, coupons, promotions, etc.)

2. **Fixture Sync:** `python3 tools/sync-clients.py`
   - Reads: `data/qa-matrix.json` + `data/b2b-feature-status.json` (notImplementedInB2B flags)
   - Generates: `tests/e2e/fixtures/clients.ts` (TypeScript object)
   - Per-client: baseURL mapping (solopide.me vs youorder.me), credentials from env vars, config object with 20-40 flags

3. **Test Execution (Parallel):**
   - **Playwright:** `cd tests/e2e && npx playwright test --project=b2b` → runs all 13 specs across all 17 clients (13 specs × 17 clients = 221 tests) → `playwright-report/index.html`
   - **Maestro:** Manual `maestro test tests/app/flows/` or per-client sessions (e.g., `prinorte-session.yaml`) → PASS/FAIL per flow
   - **Cowork:** Claude manual testing via `COWORK.md` → 4 modes (A/B/C/D) per client session

4. **Result Collection:**
   - Playwright JSON: `tests/e2e/playwright-report/results.json`
   - Cowork: `QA/{CLIENT}/{DATE}/cowork-session.md` (one file per day, all modes concatenated)
   - Maestro: stdout/Maestro dashboard (not persisted in repo)

5. **Report Generation:** `/report-qa {CLIENT} {DATE}`
   - Reads: `QA/{CLIENT}/{DATE}/cowork-session.md` + playwright results + Maestro results
   - Generates: 
     - `QA/{CLIENT}/{DATE}/qa-report-{DATE}.md` (comprehensive markdown)
     - `public/qa-reports/{CLIENT}-{DATE}.html` (standalone HTML report)
     - Updates: `public/manifest.json` (new entry)
   - Result: GitHub Pages dashboard auto-refreshes

**State Management:**

- **MongoDB config** = source of truth for client feature flags (extracted once per week or on-demand)
- **qa-matrix.json** = cached extraction (4 hours old before re-extraction recommended)
- **clients.ts** = auto-generated, never manually edited
- **Test results** = ephemeral (Playwright), session-based (Cowork/Maestro)
- **Dashboard manifest** = persistent (append-only, never deleted)

## Key Abstractions

**ClientConfig (Fixture Model):**
- Purpose: Represents a single client with all MongoDB-derived flags and credentials
- Examples: `tests/e2e/fixtures/clients.ts` (entries for Bastien, Codelpa, Soprole, Surtiventas, etc.)
- Pattern: Key-value object with `name`, `baseURL`, `loginPath`, `credentials`, `config` (nested flags), `coupons`, `banners`, `promotions`, `integrations`
- Usage: Passed to `createClientTest(client)` factory to create parameterized test suite per client

**Test Factory (createClientTest):**
- Purpose: Creates Playwright test instance with authenticated page for a specific client
- Location: `tests/e2e/fixtures/multi-client-auth.ts`
- Pattern: Takes ClientConfig, returns test.extend<{ authedPage }> with:
  - Login helper (`loginHelper` from `login.ts`)
  - Commerce selector (`selectCommerceHelper` for price-gated clients)
  - Cart clear (`clearCartHelper` for session hygiene)
- Usage: Each spec file iterates clients and calls `createClientTest()` to generate N parameterized describe blocks

**Test Spec Pattern (Multi-client):**
- Purpose: Single spec file that runs across all clients with config-aware branching
- Example: `tests/e2e/b2b/cart.spec.ts` (100+ lines for one feature, multiplied by 17 clients)
- Pattern:
  ```typescript
  for (const [key, client] of Object.entries(clients)) {
    const test = createClientTest(client);
    test.describe(`Feature: ${client.name}`, () => {
      test('test name', async ({ authedPage: page }) => {
        // Use client.config.flagName to branch
      });
    });
  }
  ```
- Benefit: DRY — write once, run across all clients; config-dependent features auto-skip if flag not enabled

**Cowork Session:**
- Purpose: Consolidate all human QA findings from a single day into one file
- Location: `QA/{CLIENT}/{YYYY-MM-DD}/cowork-session.md`
- Pattern: 4 sections (Modo A, Modo B, Modo C, Modo D), each with HANDOFF block containing:
  - Flujos completados (list with ✓/✗)
  - Issues encontrados (list with ID, severity, description)
  - Staging blockers (cases that couldn't be tested and why)
  - Coverage (Tier 1/2/3 executed over total)
  - Process improvements (suggested tests/flags/playbook updates)
- Benefit: Single file per day (not per mode) avoids file fragmentation; `/report-qa` reads one file to consolidate

**MongoDB Collection Mapper:**
- Purpose: Abstract the multi-database layout (LEGACY + MICRO + INTEGRATIONS) into a unified client config
- Location: `data/mongo-extractor.py` (extract_collections function)
- Pattern: Per-collection lookup strategy (domain → yom-stores, customerId/ObjectId → yom-b2b or integrations)
- Examples: `sites` (domain), `products` (domain), `promotions` (customerId), `overrides` (ObjectId)

## Entry Points

**Playwright E2E (B2B):**
- Location: `tests/e2e/b2b/` (13 spec files)
- Triggers: `npm test`, `npx playwright test --project=b2b`, CI/CD workflows
- Responsibilities:
  1. Load `clients.ts` fixture
  2. For each client, instantiate authedPage with login + commerce selection
  3. Run feature-specific assertions (cart, checkout, prices, etc.)
  4. Capture failures as screenshots/videos
  5. Output JSON + HTML reports

**Maestro Mobile (APP):**
- Location: `tests/app/flows/` (13 YAML flows + client-specific subdirectories)
- Triggers: Manual `maestro test tests/app/flows/`, Maestro dashboard, scheduled runs
- Responsibilities:
  1. Launch Android app
  2. Execute YAML step sequence (tapOn, inputText, assertVisible, etc.)
  3. Wait for async UI states (animations, network)
  4. Detect failures (selector not found, assertion failed)
  5. Record video/screenshots

**Cowork QA (Human):**
- Location: COWORK.md (playbook) + claude.ai (execution)
- Triggers: User runs Cowork session with `/qa-plan-client {CLIENT}`
- Responsibilities:
  1. Read COWORK.md for modos A/B/C/D
  2. Execute UI flows manually (login, order, checkout, etc.)
  3. Validate visual config (banners, prices, availability)
  4. Document issues with ID, severity, steps
  5. Provide HANDOFF block to be saved by user

**Report Generation:**
- Location: `ai-specs/.commands/report-qa.md` (orchestration) + Python/TypeScript report generators
- Triggers: User runs `/report-qa {CLIENT} {DATE}` or scheduled post-QA session
- Responsibilities:
  1. Read `QA/{CLIENT}/{DATE}/cowork-session.md` (Cowork results)
  2. Locate Playwright JSON results + Maestro results
  3. Consolidate findings, detect regressions, categorize severity
  4. Generate `qa-report-{DATE}.md` + `qa-reports/{CLIENT}-{DATE}.html`
  5. Update `public/manifest.json` (GitHub Pages index)

## Error Handling

**Strategy:** Graceful degradation with non-blocking validation.

**Patterns:**

- **Login Failures:** `loginHelper()` uses fallback selectors (by name, then by role, then by attribute) to handle UI variations across staging environments
- **Element Not Visible:** Tests use `.isVisible({ timeout })` with `.catch(() => false)` to avoid hard failures on optional UI elements; annotate with `test.info().annotations.push({ type: 'warning' })`
- **Network Timeouts:** Playwright config sets `actionTimeout: 30s`, `navigationTimeout: 60s`; use `page.waitForResponse()` to explicitly wait for API responses
- **Maestro Flaky Flows:** Use `retry` with backoff, `pause` before assertions, `extendedWaitUntil` for async UI states
- **MongoDB Connection Loss:** `mongo-extractor.py` catches connection errors and returns empty result; re-run with `--full` to retry
- **Missing Credentials:** Specs skip tests for clients with empty `credentials.email` or `credentials.password`

## Cross-Cutting Concerns

**Logging:** 
- Playwright: built-in test output + `list` reporter shows pass/fail per test
- Maestro: YAML flow shows step-by-step execution; `--verbose` flag for debugging
- Cowork: Claude session logs (Slack integration possible via future enhancement)
- Python scripts: stdout to terminal, structured JSON to files

**Validation:**
- MongoDB config validation: `b2b-feature-status.json` flags variables not yet implemented in frontend (skip those tests)
- Fixture validation: `clients.ts` must have entries for all real clients; sync script logs missing clients
- Playwright multi-client: Config-conditional branching (skip tests for clients with flag=false)
- Maestro: Element selectors validated by `maestro studio` interactive inspector; fallback patterns for layout changes

**Authentication:**
- Credentials stored in `.env` (never in code) with pattern `{CLIENT}_EMAIL`, `{CLIENT}_PASSWORD`
- Login helper uses bounding box detection to distinguish MUI hidden inputs from visible ones
- Session tokens cached in browser context; Cowork may need manual re-login between modos if session expires
- Maestro uses device-level credentials from `tests/app/config/config.yaml` (env vars interpolated)

**Configuration Management:**
- Environment: baseURL mapped from `domain` (MongoDB) to actual frontend URL via `sync-clients.py` (e.g., codelpa.solopide.me → beta-codelpa.solopide.me)
- Feature flags: MongoDB extracted per-client; `b2b-feature-status.json` marks unimplemented flags
- Test selection: Specs branch on `client.config.flagName` to skip config-dependent tests
- Overrides: Manual edits to `data/b2b-feature-status.json` or `tests/e2e/fixtures/clients.ts` should trigger re-sync

---

*Architecture analysis: 2026-04-17*

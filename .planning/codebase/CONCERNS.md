# Codebase Concerns

**Analysis Date:** 2026-04-17

## Tech Debt

**QA Matrix stale / not maintained:**
- Issue: `data/qa-matrix.json` has empty `clients: {}` — was last extracted 2026-04-15. All fixture data comes from `qa-matrix-staging.json` (728KB), not production matrix.
- Files: `data/qa-matrix.json`, `data/qa-matrix-staging.json`
- Impact: Production client data is not synced. Staging-only matrix means missing production clients from test runs. Lost visibility into production config validation.
- Fix approach: Either resume regular MongoDB extraction to `qa-matrix.json` (via `mongo-extractor.py --full`) or drop the empty production matrix and document that QA uses staging-only baseline.

**Currency field missing in config-validation tests:**
- Issue: `tests/e2e/b2b/config-validation.spec.ts:176` skips currency validation with comment `// TODO: currency no está en clients.ts, usar campo correcto cuando se disponibilice`
- Files: `tests/e2e/b2b/config-validation.spec.ts` (line 175-200)
- Impact: No validation that B2B clients display correct currency symbol ($, S/, etc.). Tests pass even if currency is wrong.
- Fix approach: Add `currency` field to MongoDB extraction → `clients.ts` fixture, then enable the skipped test.

## Broken / Orphaned Files

**Deleted Maestro flows without replacement:**
- Issue: Git status shows 18 deleted prinorte flows (prinorte-01-login.yaml through prinorte-99-verify-off-features.yaml) as staged deletions. These were added in commit 6b86b77 (2026-04-14) but are now flagged as deleted.
- Files: 
  - `D tests/app/flows/prinorte-01-login.yaml`
  - `D tests/app/flows/prinorte-02-sync.yaml`
  - `D tests/app/flows/prinorte-03-comercios.yaml`
  - ... through prinorte-99
- Impact: Prinorte app QA is blocked — individual flows deleted but `tests/app/flows/prinorte-session.yaml` (untracked) not yet ready as replacement. APP testing pipeline broken.
- Fix approach: Either commit the deletion (finalize migration to prinorte-session.yaml) or restore the individual files. Resolve staging status immediately — active APP QA client affected.

**Empty .commands/update-docs.md:**
- Issue: `ai-specs/.commands/update-docs.md` is 1 line of boilerplate with no actual instructions.
- Files: `ai-specs/.commands/update-docs.md`
- Impact: Command is non-functional — references a nonexistent standards file. If a Claude instance calls this command, it gets no actionable guidance.
- Fix approach: Either populate with real documentation workflow or remove the command file entirely. Update `.manifest.json` if removed.

**Stale HTTP server PID file:**
- Issue: `.http-server.pid` contains PID 2591 from a previous test run (created 2026-04-17 09:19). Process likely no longer running. Cleanup trap in `run-live.sh` should handle this, but file persists.
- Files: `.http-server.pid`
- Impact: Low — run-live.sh cleans it up on exit. But if process crashed, file is orphaned and misleading.
- Fix approach: Add `.http-server.pid` to `.gitignore` (not committed anyway). Verify global-teardown.ts is actually cleaning this up.

**Untracked QA result directories accumulating:**
- Issue: `QA/Prinorte/2026-04-15/` exists with only `maestro.log` (153 bytes) — incomplete QA session. This accumulates stale test directories that pollute the repo.
- Files: `QA/Prinorte/2026-04-15/maestro.log`
- Impact: QA directory becomes cluttered with incomplete sessions. Makes it hard to find active/recent results. Not committed, but blocks clean git status.
- Fix approach: Add `QA/*/` to `.gitignore` or enforce cleaning by `/report-qa` workflow. Only committed results should be in version control.

## Missing Critical Features

**Playwright global setup/teardown not running cleanly:**
- Issue: `tests/e2e/global-setup.ts` spawns an HTTP server in detached mode and saves PID, but `global-teardown.ts` may not always run (e.g., if tests are killed or CI crashes). Server cleanup is unreliable.
- Files: `tests/e2e/global-setup.ts`, `tests/e2e/global-teardown.ts`
- Impact: Orphaned http.server processes left running after test failures. Port 8080 may be held, blocking next test run.
- Fix approach: Replace detached spawn with proper process management — either use a proper server package (http-server npm) or ensure teardown always runs via `finally` block.

**No production environment credentialing in Playwright:**
- Issue: All E2E tests are hardcoded to staging (`BASE_URL=https://*.solopide.me`). No production test pipeline. Credentials in `.env` only for staging clients.
- Files: `tests/e2e/.env`, `tests/e2e/playwright.config.ts`
- Impact: Zero visibility into production B2B or admin UI correctness. Config bugs in production go undetected until customer reports them.
- Fix approach: Add production environment support to `playwright.config.ts` with separate CI job. Require production credentials in `.env.production`.

## Security Considerations

**Credentials embedded in test helper:**
- Issue: `tests/e2e/fixtures/login.ts` likely contains hardcoded email/password for test users. Not visible in scope (not read), but common vulnerability.
- Files: `tests/e2e/fixtures/login.ts` (not analyzed due to secret content)
- Impact: If fixtures checked into version control, test credentials are exposed in git history.
- Fix approach: Verify all test credentials come from `.env` variables, never hardcoded. Add pre-commit hook to scan for common patterns (password=, email=) in test files.

**No secret masking in test reports:**
- Issue: `tools/publish-results.py` writes JSON reports to `public/` (committed to GitHub Pages). If a test error message contains an API token or auth header, it's published publicly.
- Files: `tools/publish-results.py`, `public/history/` (committed reports)
- Impact: Secrets accidentally published to GitHub Pages when tests fail with credential-related errors.
- Fix approach: Add secret masking in `publish-results.py` before writing JSON — redact patterns like `Authorization: Bearer ****` and API keys.

## Fragile Areas

**Config-validation spec has 100+ hardcoded test cases — brittle selector maintenance:**
- Issue: `tests/e2e/b2b/config-validation.spec.ts` is 1,762 lines with ~80 inline test() blocks. Each flag validation uses brittle CSS/text selectors that break when UI changes.
- Files: `tests/e2e/b2b/config-validation.spec.ts`
- Impact: High fragility — any B2B frontend CSS refactor breaks 20+ tests simultaneously. Selectors like `page.getByText(/mínimo:\s*1$/i)` will fail if label text changes slightly.
- Fix approach: 
  1. Extract selector constants to `fixtures/selectors.ts` (single source of truth)
  2. Add `data-testid` attributes to B2B components for all validated flags
  3. Split into per-feature files (cart.spec.ts, pricing.spec.ts, etc.) with <200 lines each

**Maestro flows depend on hardcoded UI steps without abstraction:**
- Issue: `tests/app/flows/prinorte/*.yaml` files have inline tap/swipe/type steps with no helper layers. One UI change requires editing multiple YAML files.
- Files: `tests/app/flows/prinorte/*.yaml`
- Impact: APP tests brittle — UI refactor = multiple manual YAML edits. No code reuse.
- Fix approach: Create Maestro helper library in `tests/app/helpers/` with common actions (login, selectCommerce, addToCart) as reusable YAML includes or functions.

**Live reporter not handling concurrent test runs:**
- Issue: `tools/live-reporter.js` writes to a single `public/live.json` file. If two test suites run in parallel, writes race and corrupt the state.
- Files: `tools/live-reporter.js`
- Impact: Live dashboard shows garbage data during parallel test runs. Concurrent test execution breaks the live reporter.
- Fix approach: Use file locks or separate live JSON per client (e.g., `live-{clientKey}.json`), then aggregate in dashboard.

## Performance Bottlenecks

**Large config-validation spec runs slow (80+ tests sequentially):**
- Issue: `config-validation.spec.ts` iterates over all clients and runs sequential tests. With 15-20 active clients, this is 80+ tests × 30s each = 40+ minutes for one spec.
- Files: `tests/e2e/b2b/config-validation.spec.ts` (loops per-client)
- Impact: Full B2B test suite takes 60+ minutes. Feedback loop slow for developers.
- Fix approach:
  1. Extract into separate spec per client (`codelpa.spec.ts`, `surtiventas.spec.ts`, etc.) to enable parallelization
  2. Or use `test.describe.parallel()` to run client suites in parallel
  3. Add `--reporter=dot` for faster console feedback

## Test Coverage Gaps

**No validation of B2B payment integrations (Khipu, Webpay, Stripe):**
- Issue: `config-validation.spec.ts` checks if payment sections exist, but doesn't validate that payment flows work end-to-end or that the correct gateway is wired.
- Files: `tests/e2e/b2b/config-validation.spec.ts` (enablePayments checks only visibility)
- Impact: Payment bugs in staging go undetected. Config says Khipu enabled but Webpay integration actually active = silent failure.
- Fix approach: Add `payments.spec.ts` that:
  - Mock each payment provider's webhook
  - Place order through each enabled payment type
  - Assert correct provider endpoint is called

**No validation of admin panel configuration:**
- Issue: QA focuses on B2B storefront and APP. Admin panel tests exist (`tests/e2e/admin/`) but have no client-specific config validation.
- Files: `tests/e2e/admin/` (exists but coverage unclear)
- Impact: Admin config bugs (e.g., broken coupon code UI for specific clients) discovered too late.
- Fix approach: Extend `config-validation.spec.ts` pattern to admin specs — validate per-client settings in admin panel match MongoDB config.

**Prinorte APP flows not integrated with CI pipeline:**
- Issue: `tests/app/flows/prinorte/` flows exist but are run manually via `tools/run-maestro.sh`. No nightly CI job.
- Files: `tools/run-maestro.sh`, `tests/app/flows/prinorte/`
- Impact: APP regressions aren't caught automatically. Prinorte breaks and QA discovers it a week later.
- Fix approach: Add `.github/workflows/app-maestro.yml` to run APP flows nightly for Prinorte (and other app-enabled clients).

## Dependencies at Risk

**Playwright version pinning unclear:**
- Issue: `package.json` likely has `@playwright/test: "^1.x.y"`. Minor version bumps can introduce breaking locator changes or timeout behavior shifts.
- Files: `package.json` (not read due to scope, but critical)
- Impact: Tests flake unexpectedly after Playwright minor upgrade. No explicit version lock.
- Fix approach: Use exact semver (e.g., `"@playwright/test": "1.47.0"`) in package.json. Test upgrades in separate branch before applying.

**Maestro SDK version not locked:**
- Issue: `tools/run-maestro.sh` downloads Maestro SDK at runtime. If Maestro releases breaking changes, flows fail without warning.
- Files: `tools/run-maestro.sh` (lines 80+, where SDK is installed)
- Impact: APP tests suddenly fail due to SDK incompatibility. No clear error message.
- Fix approach: Pin Maestro SDK version in `run-maestro.sh` and document minimum/maximum compatible versions.

## Scaling Limits

**QA matrix extraction takes too long for 60+ clients:**
- Issue: `data/mongo-extractor.py` extracts all 60 clients every time. MongoDB aggregation queries grow quadratically as client count increases.
- Files: `data/mongo-extractor.py`
- Impact: Full extraction takes 10+ minutes. Incremental updates not supported.
- Fix approach: Implement incremental extraction (only changed clients since last run) using MongoDB's `modifiedDate` field.

**Dashboard history accumulation unbounded:**
- Issue: `tools/publish-results.py` keeps last 30 days of history in `public/history/`. After 1 year, directory becomes 365 files. GitHub Pages performance may degrade.
- Files: `tools/publish-results.py` (lines 632), `public/history/`
- Impact: Dashboard load time increases. Git repo size grows with artifact history.
- Fix approach: Archive old history to separate branch (`history-archive`) or object storage (S3). Keep only last 90 days in GitHub Pages.

## Issues with Automation & Orchestration

**Global setup/teardown race conditions with LIVE mode:**
- Issue: `run-live.sh` starts HTTP server in global setup, but `live-reporter.js` writes to same `public/live.json` during tests. If teardown runs before reporter finishes, state is lost.
- Files: `tools/run-live.sh`, `tests/e2e/global-setup.ts`, `tests/e2e/global-teardown.ts`, `tools/live-reporter.js`
- Impact: Live dashboard shows incomplete results if tests finish just as teardown kills the server.
- Fix approach: Add explicit wait in teardown for reporter to flush (check if `live.json` has `running: false`).

## Documentation / Maintainability

**update-docs.md command is a stub:**
- Issue: `ai-specs/.commands/update-docs.md` points to nonexistent `ai-specs/specs/documentation-standards.mdc`.
- Files: `ai-specs/.commands/update-docs.md`
- Impact: Documentation workflow undefined. Specs lack standards guidance.
- Fix approach: Either create `documentation-standards.mdc` with real guidelines or remove the command.

**Checklist index outdated:**
- Issue: `checklists/INDICE.md` exists but is 131 lines — hasn't been updated to match current checklist files. New checklists added without updating index.
- Files: `checklists/INDICE.md`
- Impact: QA team can't discover checklists. Test coverage gaps hidden.
- Fix approach: Auto-generate INDICE.md from checklist files using a Python script run before each commit (pre-commit hook).

---

*Concerns audit: 2026-04-17*

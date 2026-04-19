# Run Playwright

Execute Playwright E2E tests across configured clients and generate results.

## Usage

```bash
/run-playwright b2b          # Run B2B tests (*.solopide.me staging clients)
/run-playwright admin        # Run Admin tests (admin.youorder.me)
```

## Steps

1. **Adopt Playwright Specialist role** (see `ai-specs/.agents/playwright-specialist.md`)

2. **Verify prerequisites**
   - Check `.env` has credentials per client: `{CLIENTE}_EMAIL`, `{CLIENTE}_PASSWORD`
   - Run `sync-clients.py --input data/qa-matrix-staging.json` if clients.ts is stale
   - Confirm `tests/e2e/fixtures/clients.ts` is populated (non-empty clients object)

3. **Execute tests**
   ```bash
   # B2B project (active staging clients — credentials in .env)
   npx playwright test --project=b2b
   
   # Admin project
   npx playwright test --project=admin
   
   # Debug mode (headed browser)
   npx playwright test --project=b2b --headed
   ```

4. **Collect results**
   - Parse test output for pass/fail counts
   - Extract failure reasons (assertion, timeout, auth)
   - Note client-specific failures (config issue vs. code bug)

5. **Generate report**
   - Create `QA/{CLIENT}/{DATE}/playwright-report.html`
   - Summarize findings: critical failures, deprecations, data inconsistencies
   - Link failures to Linear tickets if known regressions

6. **Prioritize failures**
   - **P0 (Critical)**: Auth broken, payment gateway down, checkout impossible
   - **P1 (High)**: Config validation fails, multi-client discrepancy
   - **P2 (Medium)**: Assertion timeouts, stale selectors
   - **P3 (Low)**: Cosmetic, formatting, non-critical paths

## Expected Output

- `test-results/` folder with detailed JSON reports
- HTML summary in `public/grouped-report.html`
- Failure logs linking to `qa-matrix.json` entries

## Debugging

If tests fail:

1. Check `.env` credentials: `{CLIENTE}_EMAIL` / `{CLIENTE}_PASSWORD` por cliente activo
2. Verify MongoDB config is current (run `mongo-extractor.py --input data/qa-matrix-staging.json`)
3. Check if selectors need updating (UI changed? run `playwright codegen {URL}`)
4. Look for timeout issues (staging performance, network)

## Key Documents

- `tests/e2e/fixtures/clients.ts` — Auto-generated client data
- `tests/e2e/fixtures/login.ts` — Authentication logic
- `qa-master-guide.md` — Expected behavior per feature

# Testing Patterns

**Analysis Date:** 2026-04-17

## Test Framework

### Runner

**Playwright** (primary E2E framework)
- Version: `^1.52.0` (from `package.json`)
- Config file: `tests/e2e/playwright.config.ts`
- Projects: `b2b` (B2B specs) and `admin` (Admin specs)

**Maestro** (APP mobile automation)
- Runs YAML-based flows
- Config: `tests/app/config/config.yaml`
- Flows: `tests/app/flows/`

**Manual checklists** (QA validation)
- Format: Markdown tables
- Location: `checklists/{category}/`

### Run Commands

**All Playwright tests:**
```bash
npx playwright test
```

**B2B only:**
```bash
npx playwright test --project=b2b
```

**Admin only:**
```bash
npx playwright test --project=admin
```

**Watch mode (local development):**
```bash
npx playwright test --watch
```

**With coverage/reporting:**
```bash
npx playwright test --reporter=html
open playwright-report/index.html
```

**Maestro all flows:**
```bash
maestro test tests/app/flows/
```

**Maestro single flow:**
```bash
maestro test tests/app/flows/05-pedido.yaml
```

**Maestro with config override:**
```bash
maestro test --config tests/app/config/config.yaml tests/app/flows/
```

## Test File Organization

### Playwright Directory Structure

```
tests/e2e/
├── b2b/                          # B2B tienda.youorder.me tests
│   ├── cart.spec.ts
│   ├── catalog.spec.ts
│   ├── checkout.spec.ts
│   ├── login.spec.ts
│   ├── mongo-data.spec.ts
│   ├── orders.spec.ts
│   ├── payment-validation.spec.ts
│   └── promotions.spec.ts
├── admin/                        # Admin admin.youorder.me tests
│   ├── login.spec.ts
│   ├── orders.spec.ts
│   ├── reports.spec.ts
│   └── stores.spec.ts
├── fixtures/                     # Shared authentication, clients, helpers
│   ├── clients.ts                # AUTO-GENERATED from MongoDB
│   ├── multi-client-auth.ts      # Factory for per-client test context
│   ├── login.ts                  # Login helper function
│   └── b2b-feature.ts            # Feature validation helper
├── global-setup.ts               # Runs before all tests (start local HTTP server)
├── global-teardown.ts            # Runs after all tests (publish results, git push)
├── .env                          # Environment variables (BASE_URL, credentials)
└── playwright.config.ts          # Playwright configuration
```

### Maestro Directory Structure

```
tests/app/flows/
├── helpers/
│   ├── login.yaml                # Reusable login flow
│   └── sync.yaml                 # Data sync helper
├── prinorte/                     # Client-specific flows (e.g., Prinorte)
│   ├── 01-comercios.yaml
│   ├── 02-catalogo.yaml
│   ├── 03-pedido.yaml
│   ├── 04-filtros.yaml
│   └── ...
├── 01-login.yaml                 # Generic APP login (Tier 1)
├── 05-pedido.yaml                # Generic APP order (Tier 1)
├── 09-concurrencia.yaml          # Concurrent order handling
└── prinorte-session.yaml         # Master flow orchestrating helpers

tests/app/config/
├── config.yaml                   # Maestro configuration
└── env.example.yaml              # Environment variables template
```

### Checklist Directory Structure

```
checklists/
├── INDICE.md                     # Coverage map (which test covers what)
├── regresion/
│   └── checklist-regresion-postmortems.md  # PM1-PM7 cases
├── deuda-tecnica/
│   ├── checklist-deuda-tecnica-general.md
│   ├── checklist-deuda-tecnica-pagos.md
│   └── ...
├── servicios/
│   ├── checklist-integraciones-erp.md
│   └── checklist-webhooks.md
└── funcional/
    └── (client-specific checklists)
```

## Test Structure

### Playwright Spec Structure (AAA Pattern)

**Standard multi-client test:**

```typescript
import { createClientTest, expect } from '../fixtures/multi-client-auth';
import clients from '../fixtures/clients';

for (const [key, client] of Object.entries(clients)) {
  const test = createClientTest(client);
  test.describe(`C2 — Carrito de compras: ${client.name}`, () => {

    test.beforeEach(async ({ authedPage: page }) => {
      // Arrange: navigate and wait for state
      try {
        await page.goto(`${client.baseURL}/products`, { waitUntil: 'domcontentloaded' });
      } catch {
        await page.waitForTimeout(2000);
        await page.goto(`${client.baseURL}/products`, { waitUntil: 'domcontentloaded' });
      }
      await expect(page.getByRole('button', { name: 'Agregar' }).first()).toBeVisible({ timeout: 30_000 });
    });

    test(`${key}: C2-05 Agregar producto al carro`, async ({ authedPage: page }) => {
      // Arrange (done in beforeEach)

      // Act: user action + capture response
      const [response] = await Promise.all([
        page.waitForResponse(resp => resp.url().includes('/cart') && resp.request().method() === 'POST'),
        page.getByRole('button', { name: 'Agregar' }).first().click(),
      ]);

      // Assert: validate response and UI
      expect(response.ok()).toBeTruthy();
      const body = await response.json();
      expect(body).toBeTruthy();
    });

    test(`${key}: C2-06 Cantidad mínima — sistema corrige o bloquea`, async ({ authedPage: page }) => {
      // Conditional skip: check client flag
      const hasMinUnit = client.config.showMinOne || client.config.minUnit || client.config.limitAddingByStock;
      if (!hasMinUnit) {
        test.skip(true, `C2-06: ${client.name} no tiene MinUnit/showMinOne configurado`);
        return;
      }

      // Test logic...
    });
  });
}
```

**Key observations:**
- `beforeEach` contains shared setup (navigate, wait for visibility)
- Test names include case ID (`C2-05`) and description
- `Promise.all([waitForResponse(...), action()])` to synchronize network + UI
- Conditional logic checked early with `test.skip()` for client-specific features
- Retry logic in beforeEach: catches first navigate, waits, retries on staging sites

### Playwright Test Types

**Type 1: Multi-client regression** (most common)
- Runs same test on all 17+ clients
- Validates feature works consistently across clients
- Examples: `cart.spec.ts`, `checkout.spec.ts`, `promotions.spec.ts`
- Pattern: loop over `clients`, skip if feature not configured

**Type 2: Single-client/environment validation**
- Tests admin or environment-specific features
- Example: `tests/e2e/admin/login.spec.ts`
- Pattern: hardcoded URLs, environment variables

**Type 3: MongoDB data validation**
- Validates that live MongoDB config (coupons, promotions) works in frontend
- Example: `mongo-data.spec.ts` — applies real coupon codes from `client.coupons` array
- Pattern: checks `if (client.coupons && client.coupons.length > 0)` before running

### Maestro Flow Structure

**Login helper (reusable):**

```yaml
appId: ${APP_PACKAGE}
---
# Solo pasos de login — clearState y launchApp los hace el master flow

- tapOn:
    text: ".*[Ee]mail.*|.*[Cc]orreo.*"
- inputText: ${TEST_SELLER_EMAIL}
- tapOn:
    text: ".*[Cc]ontraseña.*|.*[Pp]assword.*|.*[Cc]lave.*"
- inputText: ${TEST_SELLER_PASSWORD}
- pressKey: Enter

# Esperar que la animación de login procese
- waitForAnimationToEnd

# Samsung Pass popup — handle conditionally
- runFlow:
    when:
      visible:
        text: ".*Samsung Pass.*"
    commands:
      - tapOn:
          text: ".*[Cc]ancelar.*"
          optional: true

# Wait for login success (multiple success signals)
- extendedWaitUntil:
    visible:
      text: ".*[Cc]omercio.*|.*SINCRONIZAR.*|.*ACTUALIZAR.*"
    timeout: 25000

# Dismiss version update popup if appeared
- runFlow:
    when:
      visible:
        text: ".*ACTUALIZAR.*|.*[Nn]ueva.*versi[oó]n.*"
    commands:
      - tapOn:
          text: "CANCELAR"
          optional: true
      - waitForAnimationToEnd
```

**Master session flow (orchestrates helpers):**

```yaml
appId: ${APP_PACKAGE}
name: "PRINORTE: Sesión Vendedor Completa"
---

# Single app launch for entire session
- clearState
- launchApp

# Run reusable helpers
- runFlow: helpers/login.yaml
- runFlow: helpers/sync.yaml

# Run feature flows
- runFlow: prinorte/01-comercios.yaml
- runFlow: prinorte/02-catalogo.yaml
- runFlow: prinorte/03-pedido.yaml

# Feature OFF verification
- runFlow: prinorte/06-features-off.yaml
```

**Async handling patterns:**

```yaml
# After login or network operation — wait for animation
- tapOn:
    id: "login_button"
- waitForAnimationToEnd

# Wait for async load with timeout
- tapOn:
    id: "sync_button"
- extendedWaitUntil:
    visible:
      id: "sync_complete_icon"
    timeout: 10000

# Explicit pause before assertion
- pause:
    duration: 1000
- assertVisible:
    id: "commerce_list_item"
```

### Checklist Structure

**Post-mortem checklist example:**

```markdown
## PM-1: Cupones — Creación de orden con cupón (yom-api)

> **Incidente:** Import mal hecho rompió creación de órdenes con cupones.

| # | Caso | Resultado esperado | Plataforma | Estado |
|---|------|-------------------|-----------|--------|
| PM1-01 | Crear orden con cupón de producto | Orden creada, descuento aplicado | B2B / API | PENDIENTE |
| PM1-02 | Crear orden con cupón de orden | Orden creada, descuento en total | B2B / API | PENDIENTE |
| PM1-03 | Crear orden sin cupón | Orden creada normalmente | B2B / API | PENDIENTE |
| PM1-04 | Cupón inválido o expirado | Error claro, orden no se crea con descuento | B2B / API | PENDIENTE |
| PM1-05 | Cupón ya usado (límite de uso) | Rechazado con mensaje claro | B2B / API | PENDIENTE |
```

**Status symbols:**
- `PENDIENTE` — Not tested
- `✓` — Pass
- `✗` — Fail (with Linear issue link if applicable)
- `⏳` — In progress
- `⚠` — Partial/known limitation

## Mocking

### Playwright Mocking Approach

**No explicit mocking framework** — tests use real API calls and responses.

**Network response capture (verification, not stubbing):**

```typescript
const [response] = await Promise.all([
  page.waitForResponse(resp => resp.url().includes('/cart') && resp.request().method() === 'POST'),
  addButton.click(),
]);
expect(response.ok()).toBeTruthy();
const body = await response.json();
expect(body).toBeTruthy();
```

**Rationale:** Tests are for **regression detection**, not isolation. They validate that the real API responds correctly.

### What to Test (Real)

- Login with real credentials (from `client.credentials`)
- Cart operations (real API)
- Checkout flow (real API)
- Real coupon codes (from MongoDB via `client.coupons`)
- Real promotions (from MongoDB via pricing)

### What NOT to Test

- Unit-level logic (not QA focus)
- Individual backend services in isolation
- Test doubles/stubs (contradicts regression detection goal)

## Fixtures and Test Data

### Fixture: clients.ts (Auto-Generated)

**Structure:**

```typescript
const clients = {
  codelpa: {
    name: 'Codelpa',
    slug: 'codelpa',
    baseURL: 'https://codelpa.solopide.me',
    loginPath: '/auth/jwt/login',
    credentials: {
      email: 'test@codelpa.cl',
      password: process.env.CODELPA_PASSWORD,
    },
    config: {
      showMinOne: true,
      minUnit: 1,
      enableCoupons: true,
      enablePaymentDocumentsB2B: false,
      // ... 20+ more flags
    },
    coupons: [
      { code: 'CODELPA10', type: 'order', discount: 10 },
      // ...
    ],
    promotions: [ /* live promotion data */ ],
    notImplementedInB2B: ['enableKhipu', 'customField2'],
  },
  // ... 16+ more clients
};
```

**Generation:**

```bash
python3 tools/sync-clients.py --mongo-uri "mongodb://..." --output tests/e2e/fixtures/clients.ts
```

**Rules:**
- Never manually edit `clients.ts`
- Always regenerate after MongoDB config changes
- Contains real client credentials (from env vars at runtime)

### Fixture: loginHelper

**Usage:**

```typescript
export async function loginHelper(
  page: Page,
  email: string,
  password: string,
  loginPath: string = '/auth/jwt/login',
  baseURL?: string
)
```

**Key logic:**
- Detects MUI hidden inputs via bounding box size (0x0 inputs)
- Uses `fill()` + `pressSequentially()` fallback for React onChange
- Submits with `Enter` key (avoids ambiguity with "Iniciar sesión" button)
- Waits for redirect away from login URL (45-second timeout)

**When to use:**
- Admin specs that don't use multi-client fixture
- Whenever you need manual login in a test
- NOT in B2B multi-client specs (use `createClientTest` instead)

### Fixture: createClientTest (Factory)

**Usage:**

```typescript
for (const [key, client] of Object.entries(clients)) {
  const test = createClientTest(client);
  test.describe(`Feature: ${client.name}`, () => {
    test('case', async ({ authedPage: page }) => { ... });
  });
}
```

**What it does:**
1. Creates a new browser context with `client.baseURL`
2. Launches a new page
3. Calls `loginHelper()` with client credentials
4. Selects default commerce if configured (e.g., for Bastien where prices need commerce selection)
5. **Clears cart** to avoid stale state from previous sessions
6. Provides `authedPage` context to test
7. Closes context after test

**Cart clearing behavior:**
- Navigates to `/cart`
- Clicks "Eliminar todos" button if visible
- Best-effort — doesn't fail if button not found

**Default commerce selection:**
- Some clients (e.g., Bastien) require selecting a commerce to see prices
- If `client.defaultCommerce` is set, calls `selectCommerceHelper()`
- Optional — skipped if not configured

## Coverage

### Target Coverage

**Tier 1 (Critical, must pass before deployment):**
- Authentication: login, session management
- Cart: add, modify, delete products
- Checkout: order creation, payment
- APP: basic flows (05-pedido, 01-login)

**Tier 2 (High priority, regression detection):**
- Post-mortems (PM1-PM7): known failures that happened in production
- Client-specific configurations (payment methods, promotions, domain rules)
- Price calculations, discounts, coupon application
- Multi-client config validation

**Tier 3 (Low priority, edge cases):**
- UX refinements, minor features
- Non-critical error paths
- Accessibility (not currently tested)

### Coverage Mapping

**Reference file:** `checklists/INDICE.md`

Example entry:
```markdown
| Feature | Checklist | Playwright | Maestro | Status |
|---------|-----------|-----------|---------|--------|
| Auth | checklist-puesta-en-marcha-app.md | login.spec.ts | 01-login.yaml | ✓ |
| Order | checklist-puesta-en-marcha-app.md | checkout.spec.ts | 05-pedido.yaml | ✓ |
| Coupons | checklist-regresion-postmortems.md (PM1) | coupons.spec.ts | N/A | ✓ |
```

**When to update:**
- After creating new test
- After linking test to post-mortem or checklist

### Coverage Gaps (Known)

**Accessibility:** No automated WCAG testing.

**E2E Admin:** Only 4 basic tests (`login.spec.ts`). Admin features not comprehensively covered.

**Offline Maestro:** `07-offline.yaml` exists but requires device airplane mode (manual setup).

**Concurrency Maestro:** `09-concurrencia.yaml` covers UI behavior but not true simultaneous execution (requires 2 app instances).

## Common Patterns

### Async Testing (Playwright)

**Pattern 1: Capture network response during action**

```typescript
const [response] = await Promise.all([
  page.waitForResponse(resp => 
    resp.url().includes('/cart') && resp.request().method() === 'POST'
  ),
  button.click(),
]);
expect(response.ok()).toBeTruthy();
```

**Pattern 2: Wait for element visibility**

```typescript
await expect(page.getByRole('button', { name: 'Agregar' }).first())
  .toBeVisible({ timeout: 30_000 });
```

**Pattern 3: Conditional visibility check (safe)**

```typescript
const isVisible = await page.getByText(/success/i).isVisible({ timeout: 3_000 }).catch(() => false);
if (isVisible) {
  // Element exists
}
```

### Error Testing (Playwright)

**Pattern: Negative test case**

```typescript
test(`${key}: C2-06 Cantidad mínima — sistema corrige o bloquea`, async ({ authedPage: page }) => {
  const quantityInput = page.locator('input[type="number"]').first();
  await quantityInput.fill('0');
  await quantityInput.press('Tab');
  await page.waitForTimeout(500);

  const value = await quantityInput.inputValue();
  const corrected = parseInt(value) > 0;
  expect(corrected, `${client.name}: permitió cantidad 0 sin corrección`).toBe(true);
});
```

**Pattern: Admin login with wrong password**

```typescript
test('ADM-03: Login con contraseña incorrecta muestra error', async ({ page }) => {
  // ... fill form with wrong credentials ...
  await button.click();

  const errorVisible = await page.getByText(/[Ii]ncorrect|[Ii]nválid|[Ee]rror/).isVisible({ timeout: 10_000 }).catch(() => false);
  expect(errorVisible).toBeTruthy();
});
```

### Error Testing (Maestro)

**Pattern: Conditional flow execution**

```yaml
- runFlow:
    when:
      visible:
        text: ".*Samsung Pass.*"
    commands:
      - tapOn:
          text: "Cancelar"
          optional: true
```

If popup appears, tap cancel. If popup doesn't appear, skip the commands.

**Pattern: Retry logic**

```yaml
- retry:
    maxRetries: 3
    delay: 2000
    action:
      tapOn:
        id: "sync_button"

- assertVisible:
    id: "success_banner"
```

Tap button up to 3 times with 2-second delays between attempts.

## Global Setup/Teardown

### Global Setup (`global-setup.ts`)

**Runs before all tests:**

1. Skip if `process.env.CI` (GitHub Actions environment)
2. Start Python HTTP server on port 8080 (serves `public/` directory for live dashboard)
3. Write server PID to `.http-server.pid` file
4. Wait 600ms for server startup
5. Attempt to open `http://localhost:8080` in browser (IDE/local dev only)

**Purpose:** Serves live test results dashboard during local development.

### Global Teardown (`global-teardown.ts`)

**Runs after all tests:**

1. Kill HTTP server (using saved PID)
2. Delete `.http-server.pid` file
3. Delete `public/live.json` (temporary results)
4. Run `python3 tools/publish-results.py` (publish final results to GitHub Pages)
5. If not in CI:
   - Stage `public/` changes
   - Commit with message: `"chore: publish playwright results {DATE}"`
   - Push to remote (with `git pull --rebase` fallback)

**Purpose:** Publishes test results to dashboard and updates git.

## Test Execution Context

### Playwright Config (`playwright.config.ts`)

**Key settings:**

```typescript
{
  globalSetup: './global-setup.ts',
  globalTeardown: './global-teardown.ts',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,      // Fail if test.only() left in CI
  retries: process.env.CI ? 2 : 1,   // 2 retries in CI, 1 locally
  workers: 4,                         // 4 parallel workers
  reporter: [
    ['html', { open: 'never' }],
    ['json', { outputFile: 'playwright-report/results.json' }],
    ['list'],
    // Live reporter (only local)
  ],
  use: {
    baseURL: process.env.BASE_URL || 'https://tienda.youorder.me',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
    actionTimeout: 30_000,           // 30s to resolve slow staging sites
    navigationTimeout: 60_000,       // 60s for page load
  },
  timeout: 120_000,                  // 2 min per test
  expect: {
    timeout: 15_000,                 // 15s for assertions
  },
  projects: [
    { name: 'b2b', testDir: './b2b', use: { ...devices['Desktop Chrome'] } },
    { name: 'admin', testDir: './admin', use: { baseURL: process.env.ADMIN_URL, ...devices['Desktop Chrome'] } },
  ],
}
```

**Why long timeouts:**
- Staging sites have high latency
- Multi-client setup adds authentication overhead
- Timeouts prevent flakiness from network delays (not test bugs)

---

*Testing analysis: 2026-04-17*

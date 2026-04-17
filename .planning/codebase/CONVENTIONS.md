# Coding Conventions

**Analysis Date:** 2026-04-17

## Naming Patterns

### Files

**Playwright specs (B2B and Admin):**
- Pattern: `{feature}.spec.ts`
- Examples: `cart.spec.ts`, `checkout.spec.ts`, `promotions.spec.ts`, `login.spec.ts`
- Location: `tests/e2e/b2b/` or `tests/e2e/admin/`

**Maestro flows (APP mobile):**
- Pattern: `{NN}-{feature}.yaml` where NN is sequential two-digit number
- Examples: `01-login.yaml`, `05-pedido.yaml`, `09-concurrencia.yaml`
- Helper flows: `helpers/{name}.yaml` (e.g., `helpers/login.yaml`, `helpers/sync.yaml`)
- Session master flows: `{client}-session.yaml` (e.g., `prinorte-session.yaml`)

**Checklists (manual test cases):**
- Pattern: `checklist-{category}-{area}.md`
- Examples: `checklist-regresion-postmortems.md`, `checklist-deuda-tecnica-pagos.md`
- Location: `checklists/{category}/`

**Fixture and helper modules:**
- Pattern: descriptive lowercase with hyphens
- Examples: `multi-client-auth.ts`, `login.ts`, `b2b-feature.ts`

### Functions and Variables

**Test names in Playwright:**
- Prefix with Tier/Case ID: `C2-05`, `PM5-01`, `ADM-01`
- Pattern: `{PREFIX}: {Human-readable description}`
- Example: `C2-05 Agregar producto al carro`
- Use backticks in template literals for client keys: `` ${key}: C2-05 Agregar ... ``

**Test names in Maestro flows:**
- Format: `{NN} - {Feature Name}` in YAML comments
- Example: `# 05 - Crear Pedido`

**Helper functions:**
- camelCase: `loginHelper`, `selectCommerceHelper`, `clearCartHelper`, `loginIfNeeded`
- Suffix: `Helper` for reusable authentication/setup functions

**Variables:**
- camelCase for JavaScript: `baseURL`, `authedPage`, `couponCode`
- SCREAMING_SNAKE_CASE for env variables: `TEST_SELLER_EMAIL`, `ADMIN_PASSWORD`
- Placeholder syntax in flows: `${VAR_NAME}` (e.g., `${SELLER_EMAIL}`)

### Types and Interfaces

**TypeScript interfaces:**
- PascalCase: `ClientConfig`
- Suffix `Config` for configuration objects
- Example: `interface ClientConfig { ... }`

**Client keys in object destructuring:**
- lowercase with hyphens: `codelpa`, `seis-sur`, `surtiventas`
- Variable name: `key` when iterating `Object.entries(clients)`

## Code Style

### Formatting

**No dedicated linter config found** — relies on IDE defaults and manual consistency. Pattern observed:
- 2-space indentation (consistent throughout test files)
- Single quotes for strings in TypeScript/JavaScript
- Template literals for interpolation

**Playwright test structure (consistent across all specs):**
```typescript
import { createClientTest, expect } from '../fixtures/multi-client-auth';
import clients from '../fixtures/clients';

for (const [key, client] of Object.entries(clients)) {
  const test = createClientTest(client);
  test.describe(`{TIER} — {Feature}: ${client.name}`, () => {
    test.beforeEach(async ({ authedPage: page }) => {
      // Setup (navigate, wait for elements)
    });

    test(`${key}: {ID} {Description}`, async ({ authedPage: page }) => {
      // Arrange
      // Act
      // Assert
    });
  });
}
```

**Playwright test patterns:**
- Use `test.skip(condition, message)` for conditional skips with client flags
- Use `Promise.all([waitForResponse(...), click()])` to capture network responses
- Use `.first()`, `.nth(i)`, `.count()` to handle multiple matching elements
- Error handling: `.catch(() => false)` for graceful timeout handling

### Import Organization

**Order in Playwright specs:**

1. Playwright test imports
   ```typescript
   import { createClientTest, expect } from '../fixtures/multi-client-auth';
   ```

2. Fixture/client imports
   ```typescript
   import clients from '../fixtures/clients';
   ```

3. Optional feature-specific helpers
   ```typescript
   import { skipIfNotInB2B } from '../fixtures/b2b-feature';
   ```

**Import style:**
- Relative paths from current file location
- Named imports: `{ createClientTest, expect }`
- Default imports: `import clients from ...`

### Path Aliases

**Environment variables:**
- `process.env.BASE_URL` — B2B base URL (default: `https://tienda.youorder.me`)
- `process.env.ADMIN_URL` — Admin base URL (default: `https://admin.youorder.me`)
- `process.env.CI` — Set in GitHub Actions (skip certain operations)
- Client-specific: `process.env.{SLUG}_COMMERCE_EMAIL`, `process.env.{SLUG}_COMMERCE_PASSWORD`
  - Slugs convert hyphens to underscores: `seis-sur` → `SEIS_SUR_PASSWORD`

**Maestro env vars (in flows and config):**
- Reference via `${VAR_NAME}` syntax
- Provided at runtime via shell env or YAML config file
- Examples: `${APP_PACKAGE}`, `${TEST_SELLER_EMAIL}`, `${TEST_SELLER_PASSWORD}`

## Error Handling

### Pattern: Graceful Fallback

Most Playwright code uses `.catch(() => false)` after `.isVisible()` or `.boundingBox()`:

```typescript
const emailIsReal = emailBox !== null && emailBox.width > 10 && emailBox.height > 10;
const emailInput = emailIsReal ? emailByName : page.getByRole('textbox', { name: /correo|email/i }).first();
```

**Why:** MUI hidden inputs (opacity:0) need bounding box detection. Tests must tolerate UI variations across staging/production.

### Pattern: Skip with Context

```typescript
if (!hasMinUnit) {
  test.skip(true, `C2-06: ${client.name} no tiene MinUnit/showMinOne configurado`);
  return;
}
```

Tests skip conditionally based on client config, not hard failures. Reasons are explicit.

### Pattern: Best-Effort Setup

```typescript
try {
  await page.goto(`${baseURL}/cart`, { waitUntil: 'domcontentloaded' });
  const deleteAll = page.getByRole('button', { name: /eliminar todos/i });
  if (await deleteAll.isVisible({ timeout: 5_000 }).catch(() => false)) {
    await deleteAll.click();
  }
} catch {
  // Cart clear is best-effort — don't fail the test if it errors
}
```

Helper functions use try/catch to prevent cascade failures. Comments explain why.

### Pattern: Promise.all for Response Capture

```typescript
const [response] = await Promise.all([
  page.waitForResponse(resp => resp.url().includes('/cart') && resp.request().method() === 'POST'),
  addButton.click(),
]);
expect(response.ok()).toBeTruthy();
```

Avoids race conditions when capturing network responses alongside clicks.

## Logging

**No structured logging framework** — uses browser console via Playwright:
- Screenshot on failure: `page.screenshot({ path: '...', fullPage: true })`
- Annotations in test results: `test.info().annotations.push({ type: 'info', description: '...' })`
- Screenshots stored in `test-results/` directory

**Example annotation pattern:**
```typescript
test.info().annotations.push({
  type: 'info',
  description: `${priceCount} precios visibles en catálogo — promotions respondiendo`,
});
```

## Comments

### JSDoc/TSDoc

**Used in Playwright fixture files** (`tests/e2e/fixtures/`):

```typescript
/**
 * Login helper — navigates directly to loginPath and submits credentials.
 * Uses Enter key to submit (avoids ambiguity with header "Iniciar sesión" button).
 */
export async function loginHelper(
  page: Page,
  email: string,
  password: string,
  loginPath: string = '/auth/jwt/login',
  baseURL?: string
) { ... }
```

**When to comment:**
- Always on exported functions explaining behavior and parameters
- Inline when logic is non-obvious (e.g., "MUI hidden inputs have 0x0 size")
- Not on self-documenting test cases (test names are clear enough)

### Test Documentation

**Spec files include narrative comments:**

```typescript
/**
 * PM5 — Regresión de promotions
 * Fuente: Post-mortem "Servicio de promotions con exceso de carga"
 *
 * Incidente: Promotions colapsó por pocos pods → catálogo, carrito y precios caídos.
 */
```

**Maestro flows include YAML comments:**

```yaml
# {NN} - {Feature Name}
# Tests: {what this validates}
# Related: {checklist ID or ticket reference}
```

## Function Design

### Size

**Playwright helpers:**
- `loginHelper`: 30-50 lines (handles MUI detection, retry logic, wait states)
- `selectCommerceHelper`: 30 lines (navigation, modal handling, wait)
- `clearCartHelper`: 15 lines (best-effort cart clear)

**Test functions:**
- Individual tests: 10-40 lines
- Reusable setup (`addProducts`): 15-20 lines, extracted and called multiple times

### Parameters

**loginHelper signature:**
```typescript
async function loginHelper(
  page: Page,                     // Playwright Page
  email: string,                  // User email
  password: string,               // User password
  loginPath: string = '/auth/jwt/login',  // Optional, defaults to standard
  baseURL?: string                // Optional, constructs full URL
)
```

**createClientTest (factory):**
```typescript
function createClientTest(client: ClientConfig) {
  return base.extend<{ authedPage: typeof base['prototype']['page'] }>({ ... })
}
```

Uses Playwright's fixture extension pattern — no positional args, extends base test context.

### Return Values

- Helpers return `void` (they perform side effects on `page`)
- Fixtures return extended test context (implicit via `use()`)
- Network capture returns response object: `const [response] = await Promise.all([...])`

## Module Design

### Exports

**Fixture modules export functions and test contexts:**

`tests/e2e/fixtures/multi-client-auth.ts`:
- Exports helper functions: `selectCommerceHelper`, `clearCartHelper`, `loginHelper`
- Exports factory: `createClientTest`
- Re-exports: `expect` from `@playwright/test`

`tests/e2e/fixtures/login.ts`:
- Single export: `loginHelper` function

**No barrel files** (`index.ts`) — each fixture imported directly by path.

### Barrel Files

Not used in test codebase. Each spec imports what it needs:
```typescript
import { createClientTest, expect } from '../fixtures/multi-client-auth';
import clients from '../fixtures/clients';
```

## Multi-Client Pattern

**Core pattern in all B2B specs:**

```typescript
for (const [key, client] of Object.entries(clients)) {
  const test = createClientTest(client);
  test.describe(`{FEATURE}: ${client.name}`, () => {
    // Each test runs for every client
    test(`${key}: {CASE}`, async ({ authedPage: page }) => { ... });
  });
}
```

- `clients` is auto-generated from MongoDB via `sync-clients.py`
- `key` is the client slug (e.g., `codelpa`, `seis-sur`)
- Each test runs once per client with client-specific credentials and config
- Tests validate that client config (payment methods, promotions, domain rules) works correctly

**Conditional tests by config:**

```typescript
const hasMinUnit = client.config.showMinOne || client.config.minUnit;
if (!hasMinUnit) {
  test.skip(true, `${client.name} no tiene MinUnit configurado`);
  return;
}
```

Skips tests if client doesn't have the feature enabled.

---

*Convention analysis: 2026-04-17*

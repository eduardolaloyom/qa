# Phase 2: Config Validation Refactor — Research

**Researched:** 2026-04-17
**Domain:** Playwright TypeScript test organization / config validation specs
**Confidence:** HIGH — full source code available, no external unknowns

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| REQ-03 | `tests/e2e/b2b/config-validation.spec.ts` (1,762 lines) must be split into per-feature spec files, each under 300 lines, independently runnable | Test inventory below maps 65 `test()` blocks to 6 feature groups of 8–15 tests each |
| REQ-04 | Replace inline text-based selectors with extracted constants so one UI change requires one file edit | Top 10 brittle selectors catalogued below; extraction to `selectors.ts` is the right strategy |
</phase_requirements>

---

## Summary

`config-validation.spec.ts` is a single 1,762-line file containing 65 `test()` blocks (plus 1 `test.skip`), all wrapped in a `for (const [key, client] of Object.entries(clients))` loop. Every test uses `{ browser }` fixture directly — **not** the `authedPage` fixture from `multi-client-auth.ts`. This means the file manages its own `browser.newContext()` / `context.close()` lifecycle internally, which is correct but makes it inconsistent with newer specs like `promotions.spec.ts`.

The logical groupings are clear from comments in the file itself: access control, product catalog/prices, cart/checkout (largest group, ~20 tests), orders/approval, navigation/UI features, and miscellaneous feature flags. Each group maps to 8–15 tests, all fitting comfortably under 300 lines per spec file.

**Primary recommendation:** Create 6 feature spec files under `tests/e2e/b2b/config-validation/`, extract a shared `selectors.ts` constants file, and copy the two shared helpers (`loginIfNeeded` and `addOneProductToCart`) into a shared helper module imported by all six files.

---

## Inventory: 65 Tests by Feature Group

### Group 1: Access Control (5 tests) — `cv-access.spec.ts`
| Line | Flag |
|------|------|
| 26 | `anonymousAccess` |
| 206 | `inMaintenance` |
| 230 | `anonymousHideCart` |
| 255 | `anonymousHidePrice` |
| 1460 | `loginButtons.facebook` |
| 1483 | `loginButtons.google` |

6 tests. Estimated ~180 lines.

### Group 2: Product Catalog & Prices (9 tests) — `cv-catalog.spec.ts`
| Line | Flag |
|------|------|
| 44 | `hidePrices` |
| 389 | `lazyLoadingPrices` |
| 447 | `enableChooseSaleUnit` |
| 653 | `hasStockEnabled` |
| 873 | `hasMultiUnitEnabled` |
| 897 | `hasNoSaleFilter` |
| 944 | `packagingInformation.hidePackagingInformationB2B` |
| 1261 | `weightInfo` |
| 1289 | `showEmptyCategories` |
| 1531 | `hasMultipleBusinessUnit` |
| 1556 | `enablePriceOracle` |
| 1163 | `uploadOrderFileWithMinUnits` |
| 800 | `enableDistributionCentersSelector` |

13 tests. Estimated ~270 lines.

### Group 3: Cart & Checkout (14 tests) — `cv-cart.spec.ts`
| Line | Flag |
|------|------|
| 69 | `disableCart` |
| 104 | `enableCoupons` |
| 141 | `hideReceiptType` |
| 477 | `enableAskDeliveryDate` |
| 510 | `orderObservations` |
| 608 | `purchaseOrderEnabled` |
| 824 | `editAddress` |
| 921 | `limitAddingByStock` |
| 1044 | `hasTransportCode` |
| 1092 | `disableShowEstimatedDeliveryHour` |
| 1738 | `hasSingleDistributionCenter` |
| 1712 | `disableObservationInput` |
| 1437 | `shoppingDetail.lastOrder` |
| 427 | `enableMassiveOrderSend` |

14 tests. Estimated ~290 lines.

### Group 4: Payments & Discounts (10 tests) — `cv-payments.spec.ts`
| Line | Flag |
|------|------|
| 288 | `enablePayments` |
| 565 | `disablePayments` |
| 631 | `enableSellerDiscount` |
| 679 | `taxes.showSummary` |
| 349 | `includeTaxRateInPrices` |
| 1115 | `enablePaymentsCollection` |
| 1140 | `hasTransferPaymentType` |
| 1213 | `discountTypes.enableOrderDiscountType` |
| 1236 | `discountTypes.enableProductDiscountType` |
| 1387 | `payment.enableNewPaymentModule` |
| 1581 | `paymentsWithoutAccount` |

11 tests. Estimated ~280 lines.

### Group 5: Orders (7 tests) — `cv-orders.spec.ts`
| Line | Flag |
|------|------|
| 324 | `ordersRequireAuthorization` |
| 971 | `ordersRequireVerification` |
| 996 | `enableOrderValidation` |
| 1019 | `enableOrderApproval` |
| 1067 | `hasVoucherPrinterEnabled` |
| 1411 | `shareOrderNewDesign` |
| 1659 | `enableInvoicesList` |
| 1631 | `enablePaymentDocumentsB2B` |
| 1684 | `disableCommerceEdit` |

9 tests. Estimated ~220 lines.

### Group 6: Navigation & UI Features (9 tests) — `cv-ui-features.spec.ts`
| Line | Flag |
|------|------|
| 704 | `pendingDocuments` |
| 728 | `pointsEnabled` |
| 752 | `enableTask` |
| 776 | `enableCreditNotes` |
| 847 | `showMinOne` |
| 544 | `footerCustomContent.useFooterCustomContent` |
| 1317 | `externalAccess` |
| 1341 | `blockedClientAlert.enableBlockedClientAlert` |
| 1367 | `useNewPromotions` |
| 1188 | `enableBetaButtons` |
| 1506 | `suggestions.hide` |
| 1604 | `enableNewUI` |

12 tests. Estimated ~250 lines.

**Total: 65 active tests + 1 skipped (`currency`) across 6 files.**

---

## Architecture Patterns

### Project Structure After Split

```
tests/e2e/b2b/
├── config-validation/
│   ├── helpers.ts               # loginIfNeeded + addOneProductToCart
│   ├── selectors.ts             # All brittle text/class selectors as named constants
│   ├── cv-access.spec.ts        # 6 tests: anonymousAccess, inMaintenance, login buttons
│   ├── cv-catalog.spec.ts       # 13 tests: hidePrices, stock, units, categories
│   ├── cv-cart.spec.ts          # 14 tests: cart, checkout fields, observations
│   ├── cv-payments.spec.ts      # 11 tests: payments, discounts, taxes
│   ├── cv-orders.spec.ts        # 9 tests: order approval/verification, invoices
│   └── cv-ui-features.spec.ts   # 12 tests: nav links, footer, UI flags
└── config-validation.spec.ts    # DELETE after migration
```

### Shared Helper Module (`config-validation/helpers.ts`)

The two internal helpers in `config-validation.spec.ts` must be extracted to a shared module — they are used in 30+ tests across all groups:

```typescript
// tests/e2e/b2b/config-validation/helpers.ts
import { expect, Page } from '@playwright/test';
import { loginHelper } from '../../fixtures/login';

export async function loginIfNeeded(page: Page, client: ClientConfig): Promise<void> {
  await page.goto(client.baseURL);
  await page.waitForLoadState('domcontentloaded');
  if (!client.config.anonymousAccess) {
    await loginHelper(page, client.credentials.email, client.credentials.password, client.loginPath, client.baseURL);
  }
}

export async function addOneProductToCart(page: Page, client: ClientConfig): Promise<void> {
  await page.goto(`${client.baseURL}/products`);
  await page.waitForLoadState('domcontentloaded');
  const addBtn = page.getByRole('button', { name: 'Agregar' }).first();
  await expect(addBtn).toBeVisible({ timeout: 20_000 });
  await addBtn.click();
  await page.waitForTimeout(800);
  await page.goto(`${client.baseURL}/cart`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(500);
}
```

Note: In the original, both helpers close over `client` via the `test.describe` scope. When moved to a shared module they must accept `client` as a parameter.

### Per-Spec File Template

Each split file follows this exact pattern — no deviations:

```typescript
// tests/e2e/b2b/config-validation/cv-{group}.spec.ts
import { test, expect } from '@playwright/test';
import { loginHelper } from '../../fixtures/login';
import { skipIfNotInB2B } from '../../fixtures/b2b-feature';
import clients from '../../fixtures/clients';
import { loginIfNeeded, addOneProductToCart } from './helpers';
import { SELECTORS } from './selectors';

for (const [key, client] of Object.entries(clients)) {
  test.describe(`Config validation — {Group}: ${client.name}`, () => {
    // tests here
  });
}
```

The `{ browser }` fixture approach (manual context lifecycle) is kept as-is in all split files — do not migrate to `authedPage` fixture during this phase. That would be a separate concern.

---

## Top 10 Brittle Selectors

These are the worst offenders — broad regex or class fragments that break on any UI text change:

| Rank | Test | Selector | Why It's Brittle |
|------|------|----------|-----------------|
| 1 | `hidePrices` / `anonymousHidePrice` / `lazyLoadingPrices` | `'text=/\\$\\s*[\\d.,]+/'` | Matches any dollar amount on page including random text nodes |
| 2 | `inMaintenance` | `getByText(/mantenimiento\|maintenance\|en construcción/i)` | 3-language OR, will match any nav/header containing word |
| 3 | `enablePayments` / `disablePayments` | `'[class*="payment" i], [class*="pago" i]'` | Matches any element with "payment" in class — could be nav links |
| 4 | `enableCoupons` | `getByPlaceholder(/cup[oó]n/i).or(getByText(/ingresar cup[oó]n/i)).or(getByRole('button', { name: /aplicar/i }))` | Three-way OR; "aplicar" matches any "apply" button on the page |
| 5 | `enableSellerDiscount` | `getByText(/descuento.*vendedor\|seller.*discount\|descuento.*adicional/i)` | "descuento" appears in promo banners, cart summaries, etc. |
| 6 | `orderObservations` | `getByPlaceholder(/observaci[oó]n\|comentario\|nota/i)` | "nota" matches any note/tooltip visible on cart page |
| 7 | `pointsEnabled` | `getByText(/puntos\|points\|fidelidad\|loyalty/i)` | "puntos" matches promotional text, product descriptions |
| 8 | `enableTask` | `getByRole('link', { name: /tarea\|task/i }).or(getByText(/mis tareas\|tareas/i))` | "tareas" could appear in any help text or footer |
| 9 | `enableCreditNotes` | `getByRole('link', { name: /nota.*cr[eé]dito\|credit.*note/i }).or(getByText(/notas de cr[eé]dito/i))` | Broad — could appear in documentation sections |
| 10 | `useNewPromotions` | `getByText(/promoci[oó]n\|oferta\|descuento/i).first()` | "oferta" appears all over any promo-enabled store |

### Selectors Constants File (`config-validation/selectors.ts`)

```typescript
// tests/e2e/b2b/config-validation/selectors.ts
// Source of truth for all UI text patterns used in config-validation specs.
// One change here fixes all specs that use that selector.

export const SELECTORS = {
  // Prices
  PRICE_PATTERN: /\$\s*[\d.,]+/,

  // Maintenance
  MAINTENANCE_TEXT: /mantenimiento|maintenance|en construcción/i,

  // Cart / Checkout
  ADD_BUTTON_LABEL: 'Agregar',
  COUPON_PLACEHOLDER: /cup[oó]n/i,
  COUPON_LABEL: /ingresar cup[oó]n/i,
  APPLY_BUTTON: /aplicar/i,
  RECEIPT_TYPE_TEXT: /tipo de recibo|boleta|factura/i,
  DELIVERY_DATE_TEXT: /fecha de entrega|fecha pedido|delivery date/i,
  OBSERVATIONS_PLACEHOLDER: /observaci[oó]n|comentario|nota/i,
  PURCHASE_ORDER_PLACEHOLDER: /orden de compra|purchase order|o\.c\./i,
  TRANSPORT_CODE_TEXT: /c[oó]digo de transporte/i,
  DELIVERY_HOUR_TEXT: /hora.*entrega|entrega.*hora|estimated.*hour|delivery.*hour/i,
  TRANSFER_OPTION_TEXT: /transferencia/i,
  MASSIVE_SEND_TEXT: /envío masivo|enviar masivo|massive|masivo/i,

  // Orders
  APPROVAL_PENDING_TEXT: /pendiente|aprobación|autorización|autorizar/i,
  VERIFICATION_TEXT: /verificaci[oó]n|verificar|verify/i,
  PRINT_VOUCHER_TEXT: /imprimir|print|voucher/i,
  SHARE_ORDER_TEXT: /compartir|share/i,
  LAST_ORDER_TEXT: /[uú]ltimo pedido|último orden|last order/i,

  // Navigation UI
  PENDING_DOCS_TEXT: /documentos pendientes|pending.*doc/i,
  POINTS_TEXT: /puntos|points|fidelidad|loyalty/i,
  TASK_LINK_TEXT: /tarea|task/i,
  CREDIT_NOTES_TEXT: /nota.*cr[eé]dito|credit.*note/i,
  SELLER_DISCOUNT_TEXT: /descuento.*vendedor|seller.*discount|descuento.*adicional/i,
  PROMO_TEXT: /promoci[oó]n|oferta|descuento/i,
  EXTERNAL_ACCESS_TEXT: /acceso externo|external access/i,
  BLOCKED_CLIENT_TEXT: /bloqueado para compras|tu comercio.*bloqueado|blocked.*purchase/i,
  SUGGESTIONS_TEXT: /sugerencia|suggested/i,
  BUSINESS_UNIT_TEXT: /unidad de negocio|business unit/i,

  // Payments
  PAYMENTS_CLASS: '[class*="payment" i], [class*="pago" i]',
  PAYMENT_COLLECTIONS_TEXT: /cobro|colecta|collection/i,
  TAX_SUMMARY_CLASS: '[class*="tax-summary" i], [class*="taxSummary" i], [class*="tax-breakdown" i]',

  // Catalog
  STOCK_TEXT: /\b(en stock|sin stock|agotado)\b/i,
  PACKAGING_TEXT: /empaque|packaging|embalaje|contenido neto/i,
  DC_TEXT: /centro.*distribución|distribution.*center|bodega/i,
  NO_SALE_TEXT: /sin venta|no.*sale|no venta/i,
  WEIGHT_TEXT: /peso|weight|\d+\s*kg|\d+\s*g\b/i,

  // Login
  FB_BUTTON: /facebook/i,
  GOOGLE_BUTTON: /google/i,

  // Cart icon
  CART_ARIA: '[class*="cart" i], [aria-label*="carro" i], [aria-label*="carrito" i], a[href*="/cart"], [data-testid*="cart" i]',
};
```

---

## Shared Setup Pattern

### What's Shared Across Tests

| Shared Element | Used By | Extraction Strategy |
|---------------|---------|-------------------|
| `for (const [key, client] of Object.entries(clients))` loop | All 65 tests | Repeated verbatim in each split file (no way to factor out the Playwright `test.describe` wrapping) |
| `loginIfNeeded(page)` | ~45 tests | Extract to `helpers.ts` with `client` as explicit parameter |
| `addOneProductToCart(page)` | ~20 tests | Extract to `helpers.ts` with `client` as explicit parameter |
| `browser.newContext()` / `context.close()` | 65 tests | Keep inline per-test — do not refactor |
| `skipIfNotInB2B(client, ...)` | ~50 tests | Already in `b2b-feature.ts`, import unchanged |

### What Does NOT Need to Change

- `{ browser }` fixture usage — keep as-is
- Context creation pattern (`browser.newContext()` / `context.close()`) — keep inline
- Individual test assertions — copy verbatim from original
- Import of `loginHelper` from `../../fixtures/login` — keep path adjusted for subdir

---

## Client Parameterization

The spec iterates over `clients` from `tests/e2e/fixtures/clients.ts` (3,444 lines, auto-generated, 17+ clients). Key facts:

1. `clients` is a `Record<string, ClientConfig>` — `Object.entries` gives `[key, client]` pairs.
2. Every config flag is in `client.config: Record<string, any>` — accessed as `client.config.flagName` or `client.config['flag.name']` for dotted paths.
3. `defaultCommerce` is optional — used in `anonymousHidePrice` test to skip.
4. `notImplementedInB2B: string[]` — used by `skipIfNotInB2B` to skip tests for unimplemented flags.
5. When the loop runs for N clients and each file has M tests, total test count = N × M per file.

The split files must keep the identical loop pattern — Playwright discovers tests at parse time so the loop must be at the top level of the file.

---

## Inter-Test Dependencies

**There are NO inter-test dependencies.** Each test:
- Creates its own browser context (`browser.newContext()`)
- Closes it in the same test body (`context.close()`)
- Does not share page state, cookies, or localStorage across tests

This means every split file is independently runnable with `npx playwright test config-validation/cv-{group}.spec.ts` without any ordering requirements.

One conditional nesting exists: `anonymousHideCart` and `anonymousHidePrice` are inside `if (client.config.anonymousAccess === true)`. This is a static filter on client config, not a test ordering dependency. In the split, move these to `cv-access.spec.ts` and wrap them the same way.

---

## Common Pitfalls

### Pitfall 1: Relative Import Paths Break When Moving to Subdirectory
**What goes wrong:** Files move from `tests/e2e/b2b/` to `tests/e2e/b2b/config-validation/`, so `../fixtures/clients` must become `../../fixtures/clients`.
**How to avoid:** Verify all import paths in each new file. Check: `../../fixtures/login`, `../../fixtures/b2b-feature`, `../../fixtures/clients`.

### Pitfall 2: `loginIfNeeded` Closes Over `client` in Original
**What goes wrong:** In the original file, `loginIfNeeded` is defined inside `test.describe`, closing over `client` from the loop. If extracted naively as a module function without adding `client` as a parameter, TypeScript will error.
**How to avoid:** Signature must be `loginIfNeeded(page: Page, client: ClientConfig)` in the shared helper. All call sites update to `loginIfNeeded(page, client)`.

### Pitfall 3: `addOneProductToCart` Has Same Closure Issue
**What goes wrong:** Same as above — it references `client.baseURL` from closure.
**How to avoid:** Signature must be `addOneProductToCart(page: Page, client: ClientConfig)`.

### Pitfall 4: Deleting Original File Removes Coverage
**What goes wrong:** Deleting `config-validation.spec.ts` before all 65 tests are confirmed in split files causes silent coverage regression.
**How to avoid:** Run `npx playwright test --list` before and after migration and diff the test names. Delete original only when the count matches exactly.

### Pitfall 5: `test.describe` Title Collision
**What goes wrong:** If two split files use the same describe title (`Config validation: ${client.name}`), test report disambiguates by file path but the HTML report may look confusing.
**How to avoid:** Use group-qualified titles: `Config validation — Access: ${client.name}`, `Config validation — Cart: ${client.name}`, etc.

### Pitfall 6: `currency` `test.skip` Must Be Preserved
**What goes wrong:** The `test.skip` for `currency` at line 176 is intentional (TODO comment). If it gets dropped during migration, technical debt is lost.
**How to avoid:** Include it in `cv-catalog.spec.ts` as-is.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Selector constants | A custom selector registry class | Plain `export const SELECTORS = {}` object in `selectors.ts` | Zero overhead, typed, tree-shakeable |
| Shared browser context lifecycle | A custom test fixture that wraps context | Keep inline `browser.newContext()` pattern — no fixture needed | Fixtures add complexity; inline pattern is already correct and consistent across all 65 tests |
| Client iteration | A helper that wraps the for loop | Plain `for...of` in each file | Playwright requires test declarations at parse time; dynamic wrapping breaks test discovery |

---

## Code Examples

### How Each Split File Should Start

```typescript
// tests/e2e/b2b/config-validation/cv-cart.spec.ts
import { test, expect } from '@playwright/test';
import { skipIfNotInB2B } from '../../fixtures/b2b-feature';
import clients from '../../fixtures/clients';
import { loginIfNeeded, addOneProductToCart } from './helpers';
import { SELECTORS } from './selectors';

for (const [key, client] of Object.entries(clients)) {
  test.describe(`Config validation — Cart: ${client.name}`, () => {

    test(`${key}: disableCart=${client.config.disableCart}`, async ({ browser }) => {
      skipIfNotInB2B(client, 'disableCart');
      const context = await browser.newContext();
      const page = await context.newPage();
      await loginIfNeeded(page, client);

      await page.goto(`${client.baseURL}/products`);
      await page.waitForLoadState('domcontentloaded');

      const addButtons = page.getByRole('button', { name: SELECTORS.ADD_BUTTON_LABEL });

      if (client.config.disableCart) {
        await page.waitForTimeout(3_000);
        expect(await addButtons.count()).toBe(0);
        await page.goto(`${client.baseURL}/cart`);
        await page.waitForLoadState('domcontentloaded');
        expect(page.url()).not.toMatch(/\/cart$/);
      } else {
        await expect(addButtons.first()).toBeVisible({ timeout: 20_000 });
        expect(await addButtons.count()).toBeGreaterThan(0);
        await page.goto(`${client.baseURL}/cart`);
        await page.waitForLoadState('domcontentloaded');
        await expect(page).toHaveURL(/cart/);
      }

      await context.close();
    });

    // ... remaining cart tests
  });
}
```

### Playwright Config — No Changes Needed

`playwright.config.ts` uses `testDir: './b2b'` for the `b2b` project. Playwright discovers spec files recursively, so placing new files in `./b2b/config-validation/` will be picked up automatically. No config change is needed.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Single monolithic spec | Per-feature split files in subdirectory | This phase | Playwright CLI can run a single feature group: `npx playwright test config-validation/cv-cart` |
| Inline brittle selectors | Named constants in `selectors.ts` | This phase | One UI text change = one file edit |
| Helpers defined as closures inside `test.describe` | Exported functions in `helpers.ts` with explicit params | This phase | Importable, testable, reusable across future specs |

---

## Open Questions

1. **Should `config-validation.spec.ts` be deleted or kept as a redirect/barrel?**
   - What we know: It must be removed to avoid double-running all 65 × N_clients tests
   - What's unclear: Whether CI references it by explicit path anywhere
   - Recommendation: Search for any CI scripts or npm scripts referencing the file before deleting

2. **ClientConfig type is defined twice** (in `clients.ts` and `multi-client-auth.ts`) with different shapes. `helpers.ts` will need to import or inline a compatible type.
   - Recommendation: Use `import type { ... }` from `clients.ts` or use `any` for the client param initially to avoid circular deps.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Playwright 1.x (TypeScript) |
| Config file | `tests/e2e/playwright.config.ts` |
| Quick run command | `npx playwright test --project=b2b config-validation/cv-access --list` |
| Full suite command | `npx playwright test --project=b2b config-validation/` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-03 | All 65 tests exist in split files | structural | `npx playwright test --list --project=b2b 2>&1 | grep "config-validation"` count matches | ❌ Wave 0 |
| REQ-03 | Each split file < 300 lines | structural | `wc -l tests/e2e/b2b/config-validation/*.spec.ts` | ❌ Wave 0 |
| REQ-03 | Each file independently runnable | smoke | `npx playwright test --project=b2b config-validation/cv-access.spec.ts` | ❌ Wave 0 |
| REQ-04 | No inline regex selectors remain in split files | structural | `grep -r "getByText(/" tests/e2e/b2b/config-validation/ | grep -v selectors.ts` returns 0 | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `npx playwright test --project=b2b --list 2>&1 | grep "config-validation" | wc -l`
- **Per wave merge:** `npx playwright test --project=b2b config-validation/` (dry run or single-client smoke)
- **Phase gate:** All 6 split files exist, line counts confirmed, original file deleted

### Wave 0 Gaps
- [ ] `tests/e2e/b2b/config-validation/helpers.ts` — shared `loginIfNeeded` + `addOneProductToCart`
- [ ] `tests/e2e/b2b/config-validation/selectors.ts` — all regex constants
- [ ] `tests/e2e/b2b/config-validation/cv-access.spec.ts` — 6 tests
- [ ] `tests/e2e/b2b/config-validation/cv-catalog.spec.ts` — 13 tests
- [ ] `tests/e2e/b2b/config-validation/cv-cart.spec.ts` — 14 tests
- [ ] `tests/e2e/b2b/config-validation/cv-payments.spec.ts` — 11 tests
- [ ] `tests/e2e/b2b/config-validation/cv-orders.spec.ts` — 9 tests
- [ ] `tests/e2e/b2b/config-validation/cv-ui-features.spec.ts` — 12 tests

---

## Sources

### Primary (HIGH confidence)
- `/Users/lalojimenez/qa/tests/e2e/b2b/config-validation.spec.ts` — full source read, all 1,762 lines
- `/Users/lalojimenez/qa/tests/e2e/fixtures/clients.ts` — first 100 lines (structure confirmed)
- `/Users/lalojimenez/qa/tests/e2e/playwright.config.ts` — full source
- `/Users/lalojimenez/qa/tests/e2e/fixtures/login.ts` — full source
- `/Users/lalojimenez/qa/tests/e2e/fixtures/b2b-feature.ts` — full source
- `/Users/lalojimenez/qa/tests/e2e/fixtures/multi-client-auth.ts` — full source
- `/Users/lalojimenez/qa/.planning/REQUIREMENTS.md` — REQ-03, REQ-04

---

## Metadata

**Confidence breakdown:**
- Test inventory (65 tests, 6 groups): HIGH — counted from source
- Shared helper extraction strategy: HIGH — both helpers confirmed as closures in source
- Selector brittleness ranking: HIGH — directly read from source
- Playwright subdirectory discovery: HIGH — `testDir: './b2b'` in config confirms recursive discovery
- Line count estimates per file: MEDIUM — based on line ranges in source; actual depends on comments retained

**Research date:** 2026-04-17
**Valid until:** Indefinite — based on static source files; re-read source if `clients.ts` is regenerated

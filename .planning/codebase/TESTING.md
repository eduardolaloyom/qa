# Testing Patterns — QA Execution Landscape

**Analysis Date:** 2026-04-19

---

## Execution Order (Mandatory)

```
1. Playwright  →  regression E2E, runs unattended
2. Cowork      →  visual/UX validation, human-driven via claude.ai
3. Maestro     →  APP mobile flows on real Android device
4. Checklists  →  manual backend/service validation
```

**Gate rule:** If Playwright finds a P0 (auth broken, checkout impossible), stop — do not continue with Cowork until resolved.

---

## 1. Playwright E2E

### Runner Configuration

**Config:** `tests/e2e/playwright.config.ts`

```typescript
workers: 4               // parallel workers
retries: CI ? 2 : 1      // 1 retry locally, 2 on CI
timeout: 120_000          // per-test timeout (ms)
actionTimeout: 30_000
navigationTimeout: 60_000
```

**Projects:**

| Project | Test dir | Base URL |
|---------|----------|----------|
| `b2b` | `tests/e2e/b2b/` | `process.env.BASE_URL` or `https://tienda.youorder.me` |
| `admin` | `tests/e2e/admin/` | `process.env.ADMIN_URL` or `https://admin.youorder.me` |

**Reporters (local):**
- `html` — `tests/e2e/playwright-report/index.html` (never auto-opens)
- `json` — `tests/e2e/playwright-report/results.json` (input for `publish-results.py`)
- `list` — terminal output
- `tools/live-reporter.js` — live dashboard at `localhost:8080` (local only, not on CI)

**Run commands:**
```bash
# Run all B2B tests
npx playwright test --project=b2b

# Run all Admin tests
npx playwright test --project=admin

# Run specific client only
npx playwright test --project=b2b --grep "bastien"

# Headed browser (debug)
npx playwright test --project=b2b --headed

# Publish results to GitHub Pages
python3 tools/publish-results.py
python3 tools/publish-results.py --client sonrie --results-file tests/e2e/playwright-report/results-sonrie.json
```

### B2B Specs (`tests/e2e/b2b/`)

| Spec | What it covers | Origin |
|------|---------------|--------|
| `catalog.spec.ts` | Catalogue load, search, categories | Cowork C2 |
| `cart.spec.ts` | Cart quantities, minimum amounts | Cowork C2 |
| `checkout.spec.ts` | Checkout, double-click guard, order history | Cowork C2 |
| `prices.spec.ts` | Pricing, discounts, taxes, coupon field | Cowork C3 |
| `orders.spec.ts` | Order history, order load | Cowork C2 |
| `coupons.spec.ts` | Invalid coupon, order-level coupon, loading state | Post-mortem PM1/PM2 |
| `step-pricing.spec.ts` | Stepped pricing, quantity changes, broken prices | Post-mortem PM4 |
| `promotions.spec.ts` | Catalogue with promotions, totals, timeout | Post-mortem PM5 |
| `payments.spec.ts` | Payment history, negative amounts, tax documents | Tech debt |
| `payment-documents.spec.ts` | C7 — document access when flag=true, hidden when flag=false | Config-conditional |
| `mongo-data.spec.ts` | Coupons, banners, promotions from MongoDB | Operational data |
| `multi-client.spec.ts` | Multiple clients in parallel | Multi-tenant regression |
| `config-validation/cv-access.spec.ts` | Anonymous access, login, maintenance mode | Config validation |
| `config-validation/cv-catalog.spec.ts` | Filters, categories, search | Config validation |
| `config-validation/cv-cart.spec.ts` | Min order, units, coupons | Config validation |
| `config-validation/cv-payments.spec.ts` | Payment methods, purchase orders, history | Config validation |
| `config-validation/cv-orders.spec.ts` | Order confirmation, dispatch, tracking | Config validation |
| `config-validation/cv-ui-features.spec.ts` | Banners, discounts, prices, language | Config validation |

Config-validation suite runs ~65 tests across 6 files, all multi-client (17 staging clients).

### Admin Specs (`tests/e2e/admin/`)

| Spec | What it covers | Checklist |
|------|---------------|-----------|
| `login.spec.ts` | Login, error handling, protected routes | `checklists/funcional/checklist-admin-acceso.md` |
| `orders.spec.ts` | Order list, detail, payments | `checklists/funcional/checklist-admin-ordenes.md` |
| `stores.spec.ts` | Admin config → B2B reflection | `checklists/funcional/checklist-admin-reportes.md` |
| `reports.spec.ts` | Reports and exports (pending) | `checklists/funcional/checklist-admin-reportes.md` |

### Skip Strategy for Inactive Clients

Clients without credentials in `.env` are auto-skipped at fixture level — no manual test.skip() required:

```typescript
// tests/e2e/fixtures/multi-client-auth.ts
testInfo.skip(
  !client.credentials.email,
  `No credentials for ${client.name} — client inactive or not configured`
);
```

**To activate a client:** add `{SLUG_UPPER}_EMAIL` and `{SLUG_UPPER}_PASSWORD` to `.env`. Client entry is already present in `clients.ts` (auto-generated from MongoDB).

### Fixture Pattern — `createClientTest`

**Source:** `tests/e2e/fixtures/multi-client-auth.ts`

Each test that needs an authenticated session uses `createClientTest(client)`:

```typescript
// In a spec file:
for (const [key, client] of Object.entries(clients)) {
  const test = createClientTest(client);
  test.describe(`${key}: My feature`, () => {
    test('does something', async ({ authedPage }) => {
      // authedPage is already logged in, commerce selected, cart cleared
    });
  });
}
```

`authedPage` fixture automatically:
1. Creates browser context with client's `baseURL`
2. Calls `loginHelper` (uses Enter to submit, not button click)
3. Selects `defaultCommerce` if configured (for price-gated clients like Bastien)
4. Calls `clearCartHelper` to remove stale cart state from prior sessions or Cowork runs

### Clients Data Source

**`tests/e2e/fixtures/clients.ts`** — AUTO-GENERATED, never edit manually.

Regenerate after MongoDB changes:
```bash
python3 data/mongo-extractor.py --env staging --output data/qa-matrix-staging.json
python3 tools/sync-clients.py --input data/qa-matrix-staging.json
```

Each client entry contains:
- `baseURL` — staging URL (`https://{slug}.solopide.me`)
- `loginPath` — `/auth/jwt/login`
- `credentials` — loaded from env vars at runtime
- `config` — all MongoDB feature flags for that client
- `notImplementedInB2B` — flags not yet in frontend (tests auto-skip with annotation)
- `coupons`, `banners`, `promotions` — operational data from MongoDB
- `integrations` — segments, overrides, user segments
- `defaultCommerce` — commerce name to select after login (optional)

### Publishing Playwright Results to Dashboard

**Script:** `tools/publish-results.py`

Flow:
1. Reads `tests/e2e/playwright-report/results.json`
2. Copies HTML report to `public/reports/{client_slug}/`
3. Generates `public/history/{YYYY-MM-DD}.json` (per-run detail, merges if already exists for today)
4. Updates `public/history/index.json` (last 30 days index)
5. Seeds new-day runs with clients from previous days so dashboard stays populated

Failure classification logic in `tools/publish-results.py` auto-categorizes errors into: `bug`, `ux`, `ambiente`, `flaky`. Secrets are redacted before writing to GitHub Pages.

---

## 2. Cowork (claude.ai)

### What Cowork Validates

Cowork is the **primary QA tool**. It validates what Playwright cannot: UX correctness, visual flag reflection, multi-step flows with real data.

**Source of truth:** `COWORK.md` (paste at start of every claude.ai session)

### Modes

| Mode | Cases covered | Approximate time |
|------|--------------|-----------------|
| **A — Login + Purchase** | C1 (login), C2 (full purchase flow) | ~20 min |
| **B — Prices + Config** | C3 (prices/discounts), flag validation table, PM regressions | ~20 min |
| **C — Documents** | C7 — only if `enablePaymentDocumentsB2B=true` | ~10 min |
| **D — Tier 2** | C5 (recommendations), C9 (order tracking), C10 (blocked commerce), A2/A3 (Admin) | ~25 min |
| **FULL** | All modes in order | ~70 min |

**Mode logic:**
- After Mode B: if `enablePaymentDocumentsB2B=false` → skip Mode C, go directly to D
- Mode D Admin (A2/A3): only if access to `admin.youorder.me` is available
- After any mode → produce HANDOFF block, save with Claude Code

### Cases by Mode

**Mode A:**
- `C1-01` Login exitoso
- `C1-02` Login fallido — wrong password
- `C1-03` Login fallido — user doesn't exist
- `C1-05` Blocked commerce login
- `C1-07` Session persistence
- `C1-08` Logout
- `C2-01` Catalogue loads with products
- `C2-04` Product photos (no broken images)
- `C2-02` Search by name
- `C2-05` Add to cart
- `C2-06` Minimum quantity enforcement
- `C2-11` Create order (staging: ≤ $100.000 CLP; production: `BLOQUEADO-PROD`)
- `C2-12` Double-submit guard
- `C2-13` Order appears in history

**Mode B:**
- `C3-01` Base price visible
- `C3-02` Discounted price with badge
- `C3-14` Valid coupon
- `C3-15` Expired/invalid coupon
- `C3-17/18` Segment pricing
- Flag validation for all ~26 MongoDB flags (table in `COWORK.md` section 4)
- PM2, PM5, PM7 regression checks (post-mortems)

**Mode C:**
- `C7-10` Invoices visible in `/orders`
- `C7-11` Documents option in sidebar menu
- `C7-12` Pending documents badge
- `C7-INV` Menu link hidden when flag=false

**Mode D:**
- `C5-01/02/03` Recommendations section
- `C9-01/02/03` Order tracking / status timeline
- `C10-01/02` Blocked commerce — cannot purchase
- `A2-01/02/03` Admin: commerce management
- `A3-01/02/03` Admin: store configuration

### Issue Reporting Format (Cowork)

```
{CLIENTE}-QA-{NNN} | {SEVERIDAD} | {ID caso} | {Descripción}
Pasos para reproducir: {pasos exactos}
Esperado: {qué debería pasar}
Actual: {qué pasó}
Screenshot: [adjuntar]
```

### Veredicto Final

At end of all modes, Cowork produces:

```
## VEREDICTO: {CLIENTE} — {FECHA}

| Flujo | Estado | Issues |
|-------|--------|--------|
| C1 Login | ✓ PASS / ✗ FAIL | — |
...

VEREDICTO FINAL: LISTO / CON CONDICIONES / NO APTO

Justificación: {una línea}
Issues encontrados: {lista de IDs}
Staging blockers: {qué no se pudo testear y por qué}
Próximos pasos: {qué debe hacerse antes de producción}
```

---

## 3. Maestro (APP Mobile)

### Setup Requirements

- Android device connected via USB with USB debugging enabled
- Maestro >= 1.40.0 (`brew upgrade maestro`)
- Java 17 (`brew install openjdk@17`)
- ADB (`~/Library/Android/sdk/platform-tools/`)

**Run command:**
```bash
./tools/run-maestro.sh prinorte
./tools/run-maestro.sh prinorte --skip-to 04-filtros
./tools/run-maestro.sh prinorte --interactive
./tools/run-maestro.sh prinorte --env staging    # default: production
```

### Session-Based Pattern

Since 2026-04-17, each client uses a **session file** that orchestrates subflows without restarting the app between tests. This is the required pattern for new clients.

**Session file:** `tests/app/flows/{cliente}-session.yaml`

```yaml
appId: ${APP_PACKAGE}
name: "PRINORTE: Sesión Vendedor Completa"
---
- clearState
- launchApp
- runFlow: helpers/login.yaml
- runFlow: helpers/sync.yaml
- runFlow: prinorte/01-comercios.yaml
- runFlow: prinorte/03-pedido.yaml
# ... more subflows
```

**Subflow directory:** `tests/app/flows/{cliente}/NN-{feature}.yaml`

**Retry behavior:**
- Session flows (`{cliente}-session.yaml`): max 1 attempt (app restart too costly)
- Individual flows: max 3 automatic attempts

### Prinorte Flows (Only Active Client)

**Session:** `tests/app/flows/prinorte-session.yaml`
**Subflows:** `tests/app/flows/prinorte/`

| Flow | What it validates |
|------|-----------------|
| `helpers/login.yaml` | Vendor login (Samsung Pass workaround, version popup) |
| `helpers/sync.yaml` | Data sync + popup dismissal |
| `prinorte/01-comercios.yaml` | Commerce selection, city/channel verification |
| `prinorte/02-catalogo.yaml` | Product catalogue, photos, promo badge, units |
| `prinorte/03-pedido.yaml` | Full order flow — STOP before confirm (production) |
| `prinorte/04-filtros.yaml` | Filters: "sin venta" filter apply/clear |
| `prinorte/05-crear-comercio.yaml` | New commerce form, fields, regions |
| `prinorte/06-features-off.yaml` | Verify disabled features absent from UI |
| `prinorte/07-bloqueado.yaml` | Blocked commerce cannot place orders |
| `prinorte/08-datos-comercio.yaml` | Commerce detail: credit, balance, payment method |
| `prinorte/09-cuentas.yaml` | Bank accounts form and bank selector |
| `prinorte/10-pedidos.yaml` | Order history: list, amounts, detail |
| `prinorte/11-cobranza.yaml` | Collections tab: receivables and documents |
| `prinorte/12-precios-fotos.yaml` | Product prices and photos |

### Client Config

**`tests/app/config/config.{cliente}.yaml`** — preferred format (minimal vars):

```yaml
env:
  APP_PACKAGE: "me.youorder.yomventas"
  TEST_SELLER_EMAIL: "..."
  TEST_SELLER_PASSWORD: "..."
```

**`tests/app/config/env.{cliente}.yaml`** — legacy format (all vars injected as `--env` flags, 100+ vars). New clients should use `config.{cliente}.yaml`.

Config file is never committed. Template: `tests/app/config/config.example.yaml`.

### Maestro Output and Dashboard

`tools/run-maestro.sh` automatically after all flows:
1. Writes raw log to `QA/{CLIENTE}/{FECHA}/maestro.log`
2. Generates `public/app-reports/{client_slug}-{FECHA}.html` (self-contained HTML)
3. Updates `public/app-reports/manifest.json` (deduplicates by `client_slug` + `date`)

Dashboard reads `manifest.json` every 10 seconds via GitHub API.

### Legacy Flows (`tests/app/flows/_legacy/`)

Moved 2026-04-19. Not executable with current setup — require a generic `env.yaml` that no longer exists. Useful as reference for building new client flows.

| Flow | Cases |
|------|-------|
| `08-pagos.yaml` | Collections and payments (tech debt) |
| `09-concurrencia.yaml` | Race conditions (tech debt) |
| `10-descuentos.yaml` | Discounts in order (PM3) |
| `11-guion-comercial.yaml` | Commercial script (Growth) |
| `12-contacto-cliente.yaml` | Customer contact (Growth) |
| `13-tareas-growth.yaml` | Task management (Growth) |

---

## 4. Manual Checklists

### Index

**Source:** `checklists/INDICE.md`

### Categories

**Regression (post-mortems):** `checklists/regresion/`

| ID | Incident | Automated test |
|----|----------|---------------|
| PM1 | Coupon error on order | `coupons.spec.ts` |
| PM2 | Order-level coupons not supported B2B | `coupons.spec.ts` |
| PM3 | APP discount crash | `prinorte/09-promociones.yaml` (in session) |
| PM4 | Step pricing Soprole | `step-pricing.spec.ts` |
| PM5 | Promotions section collapsed | `promotions.spec.ts` |
| PM6 | Missing MongoDB indexes | Manual / API only |
| PM7 | Cheerio not pinned | Manual / CI only |

**Technical debt:** `checklists/deuda-tecnica/`

| Area | Automated test |
|------|---------------|
| Payments (paymentDocuments/Items) | `payments.spec.ts` + `08-pagos.yaml` (legacy) |
| Race conditions (background threading) | `09-concurrencia.yaml` (legacy) |
| MongoDB migration | Manual (at migration time) |
| Node.js upgrade | Manual (at migration time) |
| SSR migration | Manual (at migration time) |

**Services (backend integrations):** `checklists/servicios/` — all manual, no E2E equivalent

| Checklist | Service |
|-----------|---------|
| `checklist-integraciones-erp.md` | ERP + retry logic (ERP-01 to ERP-42) |
| `checklist-webhooks.md` | 13 webhooks |
| `checklist-fintech-khipu.md` | Khipu payment integration (KHP-01 to KHP-47) |
| `checklist-integration-validator.md` | Lambda Integration Validator (IV-01 to IV-53) |

**Functional:** `checklists/funcional/`

| Checklist | Automated test |
|-----------|---------------|
| `checklist-pricing-engine.md` | `prices.spec.ts` (partial) |
| `checklist-carrito-b2b.md` | `cart.spec.ts` (partial) |
| `checklist-eventos-ga4-b2b.md` | Pending E2E (62 events) |
| `checklist-puesta-en-marcha-app.md` | Maestro flows 01–12 |
| `checklist-admin-acceso.md` | `admin/login.spec.ts` |
| `checklist-admin-ordenes.md` | `admin/orders.spec.ts` |

**Pre-production (new client):** `checklists/integraciones/checklist-preproduccion-cliente.md`
Used during onboarding and after tech debt re-validation. Covers MongoDB config, catalogue, users, ERP, tax documents.

### When to Use Checklists

- **Regression checklists:** run at start of each client QA cycle alongside Playwright
- **Services checklists:** run when there are ERP/webhook/Khipu changes or client reports integration issues
- **Pre-production checklist:** mandatory for every new client before go-live
- **Functional checklists:** use to identify coverage gaps; the automated specs are the primary execution path

---

## 5. Active Clients

Clients with credentials in `.env` have active Playwright coverage. The rest are skipped automatically.

**Clients with APP coverage (Maestro):** Prinorte, Surtiventas, CoExito

**Check active clients:**
```bash
# Lists clients with non-empty EMAIL in .env
grep "_EMAIL=" tests/e2e/.env | grep -v "^#" | grep -v '=$'
```

**Skip behavior:** `testInfo.skip(!client.credentials.email, ...)` in `tests/e2e/fixtures/multi-client-auth.ts` — any client with empty `EMAIL` env var is skipped with a clear reason message.

---

## 6. When NOT to Re-Extract MongoDB

Skip `mongo-extractor.py` and run Playwright directly when:
- `data/qa-matrix-staging.json` is less than 7 days old **AND**
- No client config changes occurred since last extraction

```bash
# Check age of matrix file
ls -la /Users/lalojimenez/qa/data/qa-matrix-staging.json
```

---

## 7. Generating Reports

**When to generate a full report** (`/report-qa {CLIENTE} {FECHA}`):
- After a complete Cowork session (all planned modes done)
- At close of a QA week

**When NOT to generate a full report:**
- Quick debugging — read `playwright-report/index.html` directly
- Mid-session — use HANDOFF blocks accumulated in `cowork-session.md`

**`/report-qa` produces:**
1. `QA/{CLIENTE}/{FECHA}/qa-report-{FECHA}.md` — full markdown report
2. `public/qa-reports/{client_slug}-{FECHA}.html` — standalone HTML for dashboard
3. Updates `public/manifest.json` — adds entry, dashboard auto-updates

---

*Testing analysis: 2026-04-19*

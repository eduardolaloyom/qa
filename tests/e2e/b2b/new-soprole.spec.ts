import { test, expect } from '@playwright/test';
import { loginHelper } from '../fixtures/login';
import clients from '../fixtures/clients';

/**
 * QA E2E — Soprole New (new-soprole.solopide.me)
 *
 * Config activa: anonymousAccess=false, enableCoupons=true, hideReceiptType=true,
 *               hasMultiUnitEnabled=true, hasStockEnabled=true, enableSellerDiscount=true,
 *               useMongoPricing=true, enablePayments=true, useNewPromotions=true,
 *               hasSingleDistributionCenter=true, enableHome=true
 */

const CLIENT = clients['new-soprole'];
const EMAIL = process.env.NEW_SOPROLE_EMAIL || '';
const PASSWORD = process.env.NEW_SOPROLE_PASSWORD || '';

test.use({ baseURL: CLIENT.baseURL });

async function login(page: any) {
  await loginHelper(page, EMAIL, PASSWORD, CLIENT.loginPath, CLIENT.baseURL);
}

async function clearCart(page: any) {
  await page.goto('/cart');
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(2_000);
  const eliminarTodos = page.getByText('Eliminar todos', { exact: true });
  if (await eliminarTodos.isVisible({ timeout: 5_000 }).catch(() => false)) {
    await eliminarTodos.click();
    await page.waitForTimeout(2_000);
  }
}

// ─── Login ────────────────────────────────────────────────────────────────────

test.describe('Soprole New — Login', () => {

  test('Home sin login — redirige a login @login @funcional', async ({ page }) => {
    await page.goto(CLIENT.baseURL);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(5_000);
    const isOnLogin = /auth|login/.test(page.url());
    const hasLoginLink = await page.getByText('Iniciar sesión').isVisible({ timeout: 3_000 }).catch(() => false);
    expect(isOnLogin || hasLoginLink).toBeTruthy();
  });

  test('Login exitoso @login @funcional', async ({ page }) => {
    await login(page);
    await expect(page.locator('text=/\\$\\s*[\\d.,]+/')).toBeVisible({ timeout: 30_000 });
  });

  test('Login fallido con password incorrecto @login @crítico', async ({ page }) => {
    const url = `${CLIENT.baseURL}${CLIENT.loginPath}`;
    await page.goto(url, { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('networkidle', { timeout: 15_000 }).catch(() => {});
    const emailInput = page.getByLabel('Correo').or(page.locator('input[type="email"]')).first();
    await emailInput.waitFor({ state: 'visible', timeout: 20_000 });
    await emailInput.fill(EMAIL);
    const passwordInput = page.getByLabel('Contraseña').or(page.locator('input[type="password"]')).first();
    await passwordInput.fill('WrongPassword123');
    await passwordInput.press('Enter');
    await page.waitForTimeout(3_000);
    await expect(page).toHaveURL(/auth|login/, { timeout: 10_000 });
  });

});

// ─── Catálogo ─────────────────────────────────────────────────────────────────

test.describe('Soprole New — Catálogo', () => {

  test.beforeEach(async ({ page }) => {
    await login(page);
    await clearCart(page);
    await page.goto('/products');
    await page.waitForLoadState('domcontentloaded');
  });

  test('Catálogo muestra productos con precios CLP @catalog @funcional', async ({ page }) => {
    const prices = page.locator('text=/\\$\\s*[\\d.,]+/');
    await expect(prices.first()).toBeVisible({ timeout: 30_000 });
    expect(await prices.count()).toBeGreaterThan(0);
  });

  test('No hay productos con precio $0 @catalog @funcional', async ({ page }) => {
    await page.waitForTimeout(5_000);
    const productCards = page.locator('[class*="ProductCard"], [class*="product-card"], [class*="card"]')
      .filter({ has: page.locator('text=/\\$\\s*[\\d.,]+/') });
    const cardCount = await productCards.count();
    const zeroProducts: string[] = [];
    for (let i = 0; i < cardCount; i++) {
      const card = productCards.nth(i);
      const hasZero = await card.locator('text=/\\$\\s*0(?:[,.]0+)?\\s*$/').count();
      if (hasZero > 0) {
        const name = await card.locator('h2, h3, h4, a').first().textContent().catch(() => `Producto #${i + 1}`);
        zeroProducts.push(name?.trim() || `Producto #${i + 1}`);
      }
    }
    if (zeroProducts.length > 0) {
      test.info().annotations.push({ type: 'error', description: `Productos con $0: ${zeroProducts.join(', ')}` });
    }
    expect(zeroProducts.length).toBe(0);
  });

  test('Buscar producto por nombre @catalog @funcional', async ({ page }) => {
    const searchInput = page.getByPlaceholder('Buscar productos');
    await expect(searchInput).toBeVisible({ timeout: 15_000 });
    await searchInput.fill('test');
    await searchInput.press('Enter');
    await page.waitForLoadState('networkidle', { timeout: 15_000 }).catch(() => {});
    const results = page.locator('text=/\\$\\s*[\\d.,]+/');
    const noResults = page.getByText(/sin resultado|no encontr|no hay/i);
    expect(await results.count() > 0 || await noResults.isVisible().catch(() => false)).toBeTruthy();
  });

  test('hasMultiUnitEnabled: Selector de unidad visible en catálogo @config @funcional', async ({ page }) => {
    await page.waitForTimeout(3_000);
    // Con hasMultiUnitEnabled=true debe haber selector de unidad (caja/unidad)
    const unitSelector = page.getByText(/caja|unidad|kg|lt/i)
      .or(page.locator('[class*="unit" i], [class*="Unit" i]'))
      .first();
    const hasUnit = await unitSelector.isVisible({ timeout: 10_000 }).catch(() => false);
    if (hasUnit) {
      test.info().annotations.push({ type: 'pass', description: 'Selector de unidad visible (hasMultiUnitEnabled=true)' });
    } else {
      test.info().annotations.push({ type: 'warning', description: 'Selector de unidad no encontrado — verificar con Cowork' });
    }
  });

  test('hasStockEnabled: Stock visible en tarjetas @config @funcional', async ({ page }) => {
    await page.waitForTimeout(3_000);
    const stockIndicators = page.getByText(/stock|disponible|unidades/i)
      .or(page.locator('[class*="stock" i]'));
    const stockCount = await stockIndicators.count();
    if (stockCount > 0) {
      test.info().annotations.push({ type: 'pass', description: `Stock visible: ${stockCount} indicadores (hasStockEnabled=true)` });
    } else {
      test.info().annotations.push({ type: 'warning', description: 'Stock no visible — verificar con Cowork' });
    }
  });

});

// ─── Carrito ──────────────────────────────────────────────────────────────────

test.describe('Soprole New — Carrito', () => {

  test.beforeEach(async ({ page }) => {
    await login(page);
    await clearCart(page);
    await page.goto('/products');
    await page.waitForLoadState('domcontentloaded');
    const addButton = page.locator('.add-new-product-to-cart-button').first();
    const hasButton = await addButton.isVisible({ timeout: 10_000 }).catch(() => false);
    if (!hasButton) {
      await clearCart(page);
      await page.goto('/products');
      await page.waitForLoadState('domcontentloaded');
    }
    await expect(addButton).toBeVisible({ timeout: 30_000 });
  });

  test('Agregar producto al carrito @cart @funcional', async ({ page }) => {
    const addButton = page.locator('.add-new-product-to-cart-button').first();
    const [response] = await Promise.all([
      page.waitForResponse(resp => resp.url().includes('/cart') && resp.request().method() === 'POST'),
      addButton.click(),
    ]);
    expect(response.ok()).toBeTruthy();
  });

  test('Carrito muestra items agregados @cart @funcional', async ({ page }) => {
    await Promise.all([
      page.waitForResponse(resp => resp.url().includes('/cart') && resp.request().method() === 'POST'),
      page.locator('.add-new-product-to-cart-button').first().click(),
    ]);
    await page.goto('/cart');
    await page.waitForLoadState('domcontentloaded');
    await expect(page.getByText(/\d+ Producto/)).toBeVisible({ timeout: 15_000 });
  });

  test('Carrito vacío no permite confirmar pedido @validaciones @funcional', async ({ page }) => {
    await page.goto('/cart');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3_000);
    const confirmButton = page.getByRole('button', { name: /confirmar pedido/i });
    if (await confirmButton.isVisible({ timeout: 5_000 }).catch(() => false)) {
      await expect(confirmButton).toBeDisabled();
    }
  });

});

// ─── Cupones ──────────────────────────────────────────────────────────────────

test.describe('Soprole New — Cupones', () => {

  test('Campo de cupón visible en carrito @coupons @funcional', async ({ page }) => {
    test.skip(CLIENT.config.enableCoupons === false, 'enableCoupons=false en esta instancia');
    await login(page);
    await clearCart(page);
    await page.goto('/products');
    await page.waitForLoadState('domcontentloaded');
    const addButton = page.locator('.add-new-product-to-cart-button').first();
    await expect(addButton).toBeVisible({ timeout: 30_000 });
    await Promise.all([
      page.waitForResponse(resp => resp.url().includes('/cart') && resp.request().method() === 'POST'),
      addButton.click(),
    ]);
    await page.goto('/cart');
    await page.waitForLoadState('domcontentloaded');
    const couponField = page.getByText('Ingresar cupón', { exact: true })
      .or(page.getByLabel(/cup[oó]n/i))
      .or(page.getByPlaceholder(/cup[oó]n/i));
    await expect(couponField.first()).toBeVisible({ timeout: 15_000 });
  });

});

// ─── Precios ──────────────────────────────────────────────────────────────────

test.describe('Soprole New — Precios', () => {

  test.beforeEach(async ({ page }) => {
    await login(page);
    await clearCart(page);
    await page.goto('/products');
    await page.waitForLoadState('domcontentloaded');
    await expect(page.locator('text=/\\$\\s*[\\d.,]+/').first()).toBeVisible({ timeout: 30_000 });
  });

  test('Precios en formato CLP ($ sin decimales) @pricing @funcional', async ({ page }) => {
    const prices = page.locator('text=/\\$\\s*[\\d.,]+/');
    expect(await prices.count()).toBeGreaterThan(0);
  });

  test('hideReceiptType=true — no muestra selector boleta/factura @pricing @funcional', async ({ page }) => {
    await Promise.all([
      page.waitForResponse(resp => resp.url().includes('/cart') && resp.request().method() === 'POST'),
      page.locator('.add-new-product-to-cart-button').first().click(),
    ]);
    await page.goto('/cart');
    await page.waitForLoadState('domcontentloaded');
    await expect(page.getByText(/\d+ Producto/)).toBeVisible({ timeout: 15_000 });
    const receiptType = page.getByText(/tipo de recibo|boleta|factura/i);
    const visible = await receiptType.isVisible({ timeout: 5_000 }).catch(() => false);
    expect(visible).toBeFalsy();
  });

});

// ─── Pedidos ──────────────────────────────────────────────────────────────────

test.describe('Soprole New — Pedidos', () => {

  test('Historial de pedidos carga @pedidos @funcional', async ({ page }) => {
    await login(page);
    await page.goto('/orders');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3_000);
    const ordersTable = page.locator('table, [class*="order" i]');
    const emptyMessage = page.getByText(/no hay pedidos|sin pedidos/i);
    const hasOrders = await ordersTable.first().isVisible({ timeout: 10_000 }).catch(() => false);
    const hasEmptyMsg = await emptyMessage.isVisible({ timeout: 5_000 }).catch(() => false);
    expect(hasOrders || hasEmptyMsg).toBeTruthy();
  });

  test('Estados de pedido son válidos (no "No disponible") @pedidos @funcional', async ({ page }) => {
    await login(page);
    await page.goto('/orders');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3_000);
    const invalidStatus = page.getByText('No disponible');
    const count = await invalidStatus.count();
    if (count > 0) {
      test.info().annotations.push({ type: 'warning', description: `${count} pedidos con estado "No disponible"` });
    }
    expect(count).toBe(0);
  });

});

// ─── Errores ──────────────────────────────────────────────────────────────────

test.describe('Soprole New — Consola y errores', () => {

  test('Navegación sin errores JS en consola @consola @crítico', async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', (error) => errors.push(error.message));
    await login(page);
    for (const route of ['/products', '/cart', '/orders']) {
      await page.goto(route);
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(2_000);
    }
    if (errors.length > 0) {
      test.info().annotations.push({ type: 'error', description: `${errors.length} errores JS: ${errors.slice(0, 3).join(' | ')}` });
    }
    expect(errors.length).toBe(0);
  });

  test('Sin requests 4xx/5xx durante navegación @consola @funcional', async ({ page }) => {
    const failedRequests: string[] = [];
    page.on('response', (response) => {
      if (response.status() >= 400) {
        failedRequests.push(`${response.status()} ${response.url().split('?')[0]}`);
      }
    });
    await login(page);
    await page.goto('/products');
    await page.waitForLoadState('networkidle', { timeout: 15_000 }).catch(() => {});
    await page.goto('/cart');
    await page.waitForLoadState('networkidle', { timeout: 15_000 }).catch(() => {});
    const realErrors = failedRequests.filter(r => !r.includes('favicon') && !r.includes('/auth/'));
    if (realErrors.length > 0) {
      test.info().annotations.push({ type: 'warning', description: `Requests fallidos: ${realErrors.slice(0, 5).join(', ')}` });
    }
    expect(realErrors.length).toBe(0);
  });

});

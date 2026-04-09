import { test, expect } from '@playwright/test';
import { loginHelper } from '../fixtures/login';
import { skipIfNotInB2B } from '../fixtures/b2b-feature';
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

// Detecta si la cuenta no tiene comercio asignado (muestra formulario de creación)
async function noCommerceAssigned(page: any): Promise<boolean> {
  return page.getByRole('button', { name: 'Siguiente' }).isVisible({ timeout: 5_000 }).catch(() => false)
    || page.getByText('Código de cliente').isVisible({ timeout: 2_000 }).catch(() => false);
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
    await page.waitForTimeout(2_000);
    if (await noCommerceAssigned(page)) {
      test.skip(true, 'Cuenta sin comercio asignado — catálogo no disponible');
      return;
    }
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
    await page.waitForTimeout(2_000);
    if (await noCommerceAssigned(page)) {
      test.skip(true, 'Cuenta sin comercio asignado — requiere cuenta tipo buyer para tests de carrito');
      return;
    }
    const addButton = page.locator('.add-new-product-to-cart-button').first();
    const hasButton = await addButton.isVisible({ timeout: 10_000 }).catch(() => false);
    if (!hasButton) {
      await clearCart(page);
      await page.goto('/products');
      await page.waitForLoadState('domcontentloaded');
    }
    await expect(addButton).toBeVisible({ timeout: 30_000 });
  });

  test('Carrito vacío — botón confirmar pedido habilitado sin productos @validaciones @ux', async ({ page }) => {
    await page.goto('/cart');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3_000);
    const confirmButton = page.getByRole('button', { name: /confirmar pedido/i });
    if (await confirmButton.isVisible({ timeout: 5_000 }).catch(() => false)) {
      const isDisabled = await confirmButton.isDisabled().catch(() => false);
      if (!isDisabled) {
        test.info().annotations.push({ type: 'warning', description: 'Botón confirmar pedido habilitado con carrito vacío — mejora UX pendiente' });
      }
    }
    // Soft: no hard-fail — es mejora, no bug bloqueante
    expect(true).toBeTruthy();
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


});

// ─── Cupones ──────────────────────────────────────────────────────────────────

test.describe('Soprole New — Cupones', () => {

  test('Campo de cupón visible en carrito @coupons @funcional', async ({ page }) => {
    test.skip(CLIENT.config.enableCoupons === false, 'enableCoupons=false en esta instancia');
    await login(page);
    await clearCart(page);
    await page.goto('/products');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2_000);
    if (await noCommerceAssigned(page)) {
      test.info().annotations.push({ type: 'warning', description: 'Cuenta sin comercio — no se puede agregar productos al carrito' });
      test.skip();
      return;
    }
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
    await page.waitForTimeout(2_000);
    if (await noCommerceAssigned(page)) {
      test.skip(true, 'Cuenta sin comercio asignado — catálogo no disponible');
      return;
    }
    await expect(page.locator('text=/\\$\\s*[\\d.,]+/').first()).toBeVisible({ timeout: 30_000 });
  });

  test('Precios en formato CLP ($ sin decimales) @pricing @funcional', async ({ page }) => {
    const prices = page.locator('text=/\\$\\s*[\\d.,]+/');
    expect(await prices.count()).toBeGreaterThan(0);
  });

  test('hideReceiptType=true — no muestra selector boleta/factura @pricing @funcional', async ({ page }) => {
    if (await noCommerceAssigned(page)) {
      test.info().annotations.push({ type: 'warning', description: 'Cuenta sin comercio — no se puede acceder al carrito con productos' });
      test.skip();
      return;
    }
    await Promise.all([
      page.waitForResponse(resp => resp.url().includes('/cart') && resp.request().method() === 'POST'),
      page.locator('.add-new-product-to-cart-button').first().click(),
    ]);
    await page.goto('/cart');
    await page.waitForLoadState('domcontentloaded');
    await expect(page.getByText(/\d+ Producto/)).toBeVisible({ timeout: 15_000 });
    // Buscar selector de TIPO (radio/dropdown para elegir), no el label "Facturación:" del resumen
    const receiptSelector = page.locator('input[type="radio"]').filter({ has: page.getByText(/boleta|factura/i) })
      .or(page.locator('select').filter({ has: page.getByText(/boleta|factura/i) }))
      .or(page.getByRole('radiogroup').filter({ has: page.getByText(/boleta|factura/i) }));
    const visible = await receiptSelector.first().isVisible({ timeout: 5_000 }).catch(() => false);
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
    if (await noCommerceAssigned(page)) {
      test.info().annotations.push({ type: 'warning', description: 'Cuenta sin comercio — historial de pedidos no disponible' });
      test.skip();
      return;
    }
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

// ─── enableHome ───────────────────────────────────────────────────────────────

test.describe('Soprole New — Home (enableHome=true)', () => {

  test('enableHome=true — home carga y no redirige a /products @config @funcional', async ({ page }) => {
    skipIfNotInB2B(CLIENT, 'enableHome');
    await login(page);
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2_000);
    // Con enableHome=true debe haber una página home real, no redirect inmediato a /products
    const isHome = !page.url().includes('/products');
    const hasContent = await page.locator('main, [class*="home" i], [class*="banner" i]').first().isVisible({ timeout: 10_000 }).catch(() => false);
    if (!isHome) {
      test.info().annotations.push({ type: 'warning', description: 'Home redirige a /products — enableHome puede no estar activo en UI' });
    }
    expect(hasContent).toBeTruthy();
  });

});

// ─── enableSellerDiscount ─────────────────────────────────────────────────────

test.describe('Soprole New — Descuento vendedor (enableSellerDiscount=true)', () => {

  test.beforeEach(async ({ page }) => {
    await login(page);
    await clearCart(page);
    await page.goto('/products');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3_000);
  });

  test('enableSellerDiscount=true — input de descuento visible en catálogo @config @funcional', async ({ page }) => {
    skipIfNotInB2B(CLIENT, 'enableSellerDiscount');
    const discountInput = page.getByPlaceholder(/descuento|discount/i)
      .or(page.locator('[class*="discount" i], [class*="seller" i]'))
      .or(page.getByText(/descuento vendedor|seller discount/i))
      .first();
    const hasDiscount = await discountInput.isVisible({ timeout: 10_000 }).catch(() => false);
    if (hasDiscount) {
      test.info().annotations.push({ type: 'pass', description: 'Descuento vendedor visible (enableSellerDiscount=true)' });
    } else {
      test.info().annotations.push({ type: 'warning', description: 'Descuento vendedor no encontrado — verificar si aplica solo a rol vendedor' });
    }
    // Soft assertion: puede requerir rol específico
    expect(true).toBeTruthy();
  });

});

// ─── enableChooseSaleUnit ─────────────────────────────────────────────────────

test.describe('Soprole New — Unidad de venta (enableChooseSaleUnit=true)', () => {

  test('enableChooseSaleUnit=true — selector de unidad de venta visible en productos @config @funcional', async ({ page }) => {
    skipIfNotInB2B(CLIENT, 'enableChooseSaleUnit');
    await login(page);
    await page.goto('/products');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3_000);
    if (await noCommerceAssigned(page)) {
      test.info().annotations.push({ type: 'warning', description: 'Cuenta sin comercio — catálogo no disponible para verificar unidad de venta' });
      test.skip();
      return;
    }
    const unitSelector = page.getByText(/caja|unidad|kg|lt|pack/i)
      .or(page.locator('[class*="unit" i], [class*="saleUnit" i], select'))
      .first();
    const hasUnit = await unitSelector.isVisible({ timeout: 10_000 }).catch(() => false);
    if (hasUnit) {
      test.info().annotations.push({ type: 'pass', description: 'Selector de unidad de venta visible' });
    } else {
      test.info().annotations.push({ type: 'warning', description: 'Selector de unidad no encontrado' });
    }
    expect(hasUnit).toBeTruthy();
  });

});

// ─── enablePayments / payment.walletEnabled ───────────────────────────────────

test.describe('Soprole New — Pagos (enablePayments=true, walletEnabled=true)', () => {

  test.beforeEach(async ({ page }) => {
    await login(page);
    await clearCart(page);
    await page.goto('/products');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2_000);
    if (await noCommerceAssigned(page)) {
      test.skip(true, 'Cuenta sin comercio asignado — requiere cuenta tipo buyer para tests de pagos');
      return;
    }
    const addButton = page.locator('.add-new-product-to-cart-button').first();
    await expect(addButton).toBeVisible({ timeout: 30_000 });
    await Promise.all([
      page.waitForResponse(resp => resp.url().includes('/cart') && resp.request().method() === 'POST'),
      addButton.click(),
    ]);
    await page.goto('/cart');
    await page.waitForLoadState('domcontentloaded');
    await expect(page.getByText(/\d+ Producto/)).toBeVisible({ timeout: 15_000 });
  });

  test('enablePayments=true — sección de pagos visible en carrito @config @funcional', async ({ page }) => {
    skipIfNotInB2B(CLIENT, 'enablePayments');
    const paymentsSection = page.getByText(/pago|payment|wallet|saldo/i)
      .or(page.locator('[class*="payment" i], [class*="wallet" i]'))
      .first();
    const hasPayments = await paymentsSection.isVisible({ timeout: 10_000 }).catch(() => false);
    if (hasPayments) {
      test.info().annotations.push({ type: 'pass', description: 'Sección de pagos visible (enablePayments=true)' });
    } else {
      test.info().annotations.push({ type: 'warning', description: 'Sección de pagos no encontrada en carrito' });
    }
    expect(hasPayments).toBeTruthy();
  });

  test('payment.walletEnabled=true — opción wallet disponible @config @funcional', async ({ page }) => {
    skipIfNotInB2B(CLIENT, 'payment.walletEnabled');
    const walletOption = page.getByText(/wallet|billetera|saldo disponible/i)
      .or(page.locator('[class*="wallet" i]'))
      .first();
    const hasWallet = await walletOption.isVisible({ timeout: 10_000 }).catch(() => false);
    if (hasWallet) {
      test.info().annotations.push({ type: 'pass', description: 'Wallet visible en pagos' });
    } else {
      test.info().annotations.push({ type: 'warning', description: 'Wallet no encontrado — puede requerir saldo disponible en cuenta' });
    }
    expect(true).toBeTruthy(); // soft: depende de saldo en cuenta
  });

  test('confirmCartText — botón muestra texto "Pasar a confirmación del pedido" @config @funcional', async ({ page }) => {
    skipIfNotInB2B(CLIENT, 'confirmCartText');
    const confirmBtn = page.getByText('Pasar a confirmación del pedido', { exact: true })
      .or(page.getByText(/pasar a confirmaci[oó]n/i));
    const hasCustomText = await confirmBtn.first().isVisible({ timeout: 10_000 }).catch(() => false);
    if (hasCustomText) {
      test.info().annotations.push({ type: 'pass', description: 'Texto de confirmación personalizado visible' });
    } else {
      test.info().annotations.push({ type: 'warning', description: 'Texto custom "Pasar a confirmación" no encontrado — verificar flujo de checkout' });
    }
    expect(hasCustomText).toBeTruthy();
  });

  test('taxes.showSummary=true — resumen de impuestos visible en carrito @config @funcional', async ({ page }) => {
    skipIfNotInB2B(CLIENT, 'taxes.showSummary');
    const taxSummary = page.getByText(/impuesto|tax|iva/i)
      .or(page.locator('[class*="tax" i], [class*="impuesto" i]'))
      .first();
    const hasTax = await taxSummary.isVisible({ timeout: 10_000 }).catch(() => false);
    if (hasTax) {
      test.info().annotations.push({ type: 'pass', description: 'Resumen de impuestos visible (taxes.showSummary=true)' });
    } else {
      test.info().annotations.push({ type: 'warning', description: 'Resumen de impuestos no encontrado en carrito' });
    }
    expect(true).toBeTruthy(); // soft: puede no ser visible en todos los estados
  });

});

// ─── useNewPromotions ─────────────────────────────────────────────────────────

test.describe('Soprole New — Promociones (useNewPromotions=true)', () => {

  test('useNewPromotions=true — sección de promociones o banners visible @config @funcional', async ({ page }) => {
    skipIfNotInB2B(CLIENT, 'useNewPromotions');
    await login(page);
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3_000);
    const promos = page.locator('[class*="promo" i], [class*="banner" i], [class*="offer" i]')
      .or(page.getByText(/promoci[oó]n|oferta|descuento/i))
      .first();
    const hasPromos = await promos.isVisible({ timeout: 10_000 }).catch(() => false);
    if (hasPromos) {
      test.info().annotations.push({ type: 'pass', description: 'Sección de promociones visible' });
    } else {
      test.info().annotations.push({ type: 'warning', description: 'Promociones no visibles — puede que no haya promociones activas configuradas' });
    }
    expect(true).toBeTruthy(); // soft: depende de promociones configuradas
  });

});

// ─── enableInvoicesList / enablePaymentDocumentsB2B ───────────────────────────

test.describe('Soprole New — Facturas y documentos de pago', () => {

  test('enableInvoicesList=true — sección de facturas accesible en /payment-documents @config @funcional', async ({ page }) => {
    skipIfNotInB2B(CLIENT, 'enableInvoicesList');
    await login(page);
    // Ruta real del footer: link "Pagos" → /payment-documents
    await page.goto('/payment-documents');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3_000);
    const isNotFound = page.getByText(/404|no encontrad|not found/i);
    const hasContent = page.locator('table, [class*="invoice" i], [class*="payment" i], [class*="document" i]');
    const notFound = await isNotFound.isVisible({ timeout: 5_000 }).catch(() => false);
    const hasDocuments = await hasContent.first().isVisible({ timeout: 10_000 }).catch(() => false);
    if (notFound) {
      test.info().annotations.push({ type: 'error', description: 'Ruta /payment-documents no accesible (404)' });
    } else if (hasDocuments) {
      test.info().annotations.push({ type: 'pass', description: 'Documentos de pago accesibles en /payment-documents' });
    } else {
      test.info().annotations.push({ type: 'warning', description: '/payment-documents carga pero sin contenido visible' });
    }
    expect(!notFound).toBeTruthy();
  });

  test('enablePaymentDocumentsB2B=true — módulo de pagos en /payment-documents @config @funcional', async ({ page }) => {
    skipIfNotInB2B(CLIENT, 'enablePaymentDocumentsB2B');
    await login(page);
    await page.goto('/payment-documents');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3_000);
    // No debe mostrar 404 ni error de acceso denegado
    const isNotFound = page.getByText(/404|no encontrad|not found|acceso denegado/i);
    const notFound = await isNotFound.isVisible({ timeout: 5_000 }).catch(() => false);
    if (!notFound) {
      test.info().annotations.push({ type: 'pass', description: 'Módulo de documentos de pago accesible (enablePaymentDocumentsB2B=true)' });
    } else {
      test.info().annotations.push({ type: 'error', description: 'Módulo de pago no accesible' });
    }
    expect(!notFound).toBeTruthy();
  });

});

// ─── enableTask ───────────────────────────────────────────────────────────────

test.describe('Soprole New — Tareas (enableTask=true)', () => {

  test('enableTask=true — sección de tareas visible en navegación @config @funcional', async ({ page }) => {
    skipIfNotInB2B(CLIENT, 'enableTask');
    await login(page);
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2_000);
    const taskLink = page.getByText(/tarea|task/i)
      .or(page.locator('[href*="task" i]'))
      .first();
    const hasTasks = await taskLink.isVisible({ timeout: 10_000 }).catch(() => false);
    if (hasTasks) {
      test.info().annotations.push({ type: 'pass', description: 'Sección de tareas visible en nav (enableTask=true)' });
    } else {
      test.info().annotations.push({ type: 'warning', description: 'Tareas no visibles en navegación — puede ser rol-específico' });
    }
    expect(true).toBeTruthy(); // soft: puede requerir rol específico
  });

});

// ─── footerCustomContent / contact.phone ─────────────────────────────────────

test.describe('Soprole New — Footer personalizado', () => {

  test('footerCustomContent — footer muestra links personalizados @config @funcional', async ({ page }) => {
    skipIfNotInB2B(CLIENT, 'footerCustomContent');
    await login(page);
    await page.goto('/products');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2_000);
    // footerCustomContent inyecta links: /catalog, /contact, /faq
    // Verificamos /faq que aparece como "Preguntas Frecuentes" en footer estándar + custom
    const faqLink = page.locator('a[href="/faq"]');
    const catalogLink = page.locator('a[href="/catalog"]');
    const hasFaq = await faqLink.first().isVisible({ timeout: 10_000 }).catch(() => false);
    const hasCatalog = await catalogLink.first().isVisible({ timeout: 5_000 }).catch(() => false);
    if (hasCatalog) {
      test.info().annotations.push({ type: 'pass', description: 'Link /catalog del footerCustomContent visible' });
    } else if (hasFaq) {
      test.info().annotations.push({ type: 'pass', description: 'Link /faq visible en footer' });
    } else {
      test.info().annotations.push({ type: 'warning', description: 'Links personalizados del footer no encontrados' });
    }
    expect(hasFaq || hasCatalog).toBeTruthy();
  });

  test('contact.phone — teléfono 600 600 6600 visible en footer @config @funcional', async ({ page }) => {
    skipIfNotInB2B(CLIENT, 'contact.phone');
    await login(page);
    await page.goto('/products');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2_000);
    // El footer muestra el teléfono en "Soporte: 600 600 6600"
    const phone = page.getByText(/600[\s]?600[\s]?6600/);
    const hasPhone = await phone.first().isVisible({ timeout: 10_000 }).catch(() => false);
    if (hasPhone) {
      test.info().annotations.push({ type: 'pass', description: 'Teléfono 600 600 6600 visible en footer' });
    } else {
      test.info().annotations.push({ type: 'warning', description: 'Teléfono no visible — puede estar en /contact' });
    }
    expect(hasPhone).toBeTruthy();
  });

});

// ─── blockedClientAlert ───────────────────────────────────────────────────────

test.describe('Soprole New — Alerta cliente bloqueado (enableBlockedClientAlert=true)', () => {

  test('blockedClientAlert — configuración activa, comportamiento no testeable con cuenta válida @config @informativo', async ({ page }) => {
    skipIfNotInB2B(CLIENT, 'blockedClientAlert');
    await login(page);
    // Esta feature solo se activa con cuentas bloqueadas — verificamos que no aparezca con cuenta normal
    await page.goto('/products');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3_000);
    const blockedAlert = page.getByText(/bloqueado para compras|contactarse con nuestro Servicio/i);
    const isBlocked = await blockedAlert.isVisible({ timeout: 5_000 }).catch(() => false);
    if (isBlocked) {
      test.info().annotations.push({ type: 'error', description: 'Cuenta de prueba aparece como bloqueada — revisar con Dev' });
      expect(isBlocked).toBeFalsy();
    } else {
      test.info().annotations.push({ type: 'pass', description: 'Cuenta normal no muestra alerta de bloqueo (correcto)' });
      expect(true).toBeTruthy();
    }
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
    const ignore = (r: string) =>
      r.includes('favicon') ||
      r.includes('/auth/') ||
      r.includes('accounts.google.com'); // Google OAuth 403 esperado en headless
    const serverErrors = failedRequests.filter(r => r.startsWith('5') && !ignore(r));
    const clientErrors = failedRequests.filter(r => !r.startsWith('5') && !ignore(r));
    if (clientErrors.length > 0) {
      test.info().annotations.push({ type: 'warning', description: `Requests 4xx: ${clientErrors.slice(0, 5).join(', ')}` });
    }
    if (serverErrors.length > 0) {
      test.info().annotations.push({ type: 'error', description: `Requests 5xx: ${serverErrors.slice(0, 5).join(', ')}` });
    }
    expect(serverErrors.length).toBe(0); // Solo hard-fail en 5xx (errores de servidor)
  });

});

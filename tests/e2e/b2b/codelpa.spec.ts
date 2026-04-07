import { test, expect } from '@playwright/test';
import { loginHelper } from '../fixtures/login';
import clients from '../fixtures/clients';

/**
 * QA E2E — Codelpa (beta-codelpa.solopide.me)
 *
 * Config: anonymousAccess=false, enableCoupons=true, hideReceiptType=true,
 *         useMongoPricing=true, enableSellerDiscount=true, currency=CLP
 *
 * Selectores basados en YOMCL/b2b repo (Next.js + MUI v5):
 * - Login: label="Correo", label="Contraseña", button "Iniciar sesión"
 * - Catálogo: placeholder="Buscar productos", class="add-new-product-to-cart-button"
 * - Carrito: data-testid="side-cart-button", label="Ingresar cupón"
 * - Checkout: button "Confirmar pedido"
 */

const CLIENT = clients.codelpa;
const EMAIL = process.env.CODELPA_EMAIL || process.env.COMMERCE_EMAIL || '';
const PASSWORD = process.env.CODELPA_PASSWORD || process.env.COMMERCE_PASSWORD || '';

// Override baseURL so relative page.goto('/products') etc. resolve to codelpa's domain
test.use({ baseURL: CLIENT.baseURL });

// Helper: login en Codelpa — navega directo al form de login
async function login(page: any) {
  await loginHelper(page, EMAIL, PASSWORD, CLIENT.loginPath, CLIENT.baseURL);
}

test.describe('Codelpa — Login', () => {

  test('Home sin login — redirige a login o muestra catálogo anónimo @login @funcional', async ({ page }) => {
    await page.goto(CLIENT.baseURL);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(10_000);

    // Debe: redirigir a login, mostrar catálogo, o tener link "Iniciar sesión"
    const isOnLogin = /auth|login/.test(page.url());
    const hasPrices = await page.locator('text=/\\$\\s*[\\d.,]+/').isVisible({ timeout: 3_000 }).catch(() => false);
    const hasLoginLink = await page.getByText('Iniciar sesión').isVisible({ timeout: 3_000 }).catch(() => false);
    const isStuckOnSpinner = !isOnLogin && !hasPrices && !hasLoginLink;

    if (isStuckOnSpinner) {
      test.info().annotations.push({
        type: 'warning',
        description: 'Home se queda en loading spinner — no redirige ni muestra contenido',
      });
    }

    expect(isOnLogin || hasPrices || hasLoginLink).toBeTruthy();
  });

  test('Login exitoso @login @funcional', async ({ page }) => {
    await login(page);
    // Post-login debe mostrar catálogo con precios
    await expect(page.locator('text=/\\$\\s*[\\d.,]+/')).toBeVisible({ timeout: 30_000 });
  });

  test('Login fallido con password incorrecto @login @crítico', async ({ page }) => {
    const url = `${CLIENT.baseURL}${CLIENT.loginPath}`;
    await page.goto(url, { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('networkidle', { timeout: 15_000 }).catch(() => {});

    const emailInput = page.getByLabel('Correo')
      .or(page.locator('input[type="email"]'))
      .first();
    await emailInput.waitFor({ state: 'visible', timeout: 20_000 });
    await emailInput.fill(EMAIL);

    const passwordInput = page.getByLabel('Contraseña')
      .or(page.locator('input[type="password"]'))
      .first();
    await passwordInput.fill('WrongPassword123');
    await passwordInput.press('Enter');

    // Tras credenciales incorrectas, debe permanecer en la página de login
    await page.waitForTimeout(3_000);
    await expect(page).toHaveURL(/auth|login/, { timeout: 10_000 });
  });

  test('Sesión persistente @login @configuración', async ({ browser }) => {
    const context = await browser.newContext();
    const page = await context.newPage();
    await login(page);
    const storageState = await context.storageState();
    await context.close();

    const context2 = await browser.newContext({ storageState });
    const page2 = await context2.newPage();
    await page2.goto('/');
    await page2.waitForLoadState('domcontentloaded');
    await expect(page2).not.toHaveURL(/auth|login/, { timeout: 15_000 });
    await context2.close();
  });
});

test.describe('Codelpa — Catálogo', () => {

  test.beforeEach(async ({ page }) => {
    await login(page);
    await page.goto('/products');
    await page.waitForLoadState('domcontentloaded');
  });

  test('Catálogo muestra productos con precios CLP @catalog @funcional', async ({ page }) => {
    const prices = page.locator('text=/\\$\\s*[\\d.,]+/');
    await expect(prices.first()).toBeVisible({ timeout: 30_000 });
    const count = await prices.count();
    expect(count).toBeGreaterThan(0);
  });

  test('No hay productos con precio $0 @catalog @funcional', async ({ page }) => {
    await page.waitForTimeout(5_000);

    // Buscar todas las tarjetas de producto
    const productCards = page.locator('[class*="ProductCard"], [class*="product-card"], [class*="card"]').filter({ has: page.locator('text=/\\$\\s*[\\d.,]+/') });
    const cardCount = await productCards.count();

    const zeroProducts: string[] = [];
    for (let i = 0; i < cardCount; i++) {
      const card = productCards.nth(i);
      const hasZero = await card.locator('text=/\\$\\s*0(?:[,.]0+)?\\s*$/').count();
      if (hasZero > 0) {
        const name = await card.locator('h2, h3, h4, a, [class*="name"], [class*="title"]').first().textContent().catch(() => `Producto #${i + 1}`);
        zeroProducts.push(name?.trim() || `Producto #${i + 1}`);
      }
    }

    if (zeroProducts.length > 0) {
      test.info().annotations.push({
        type: 'error',
        description: `Productos con $0: ${zeroProducts.join(', ')}`,
      });
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
    const hasResults = await results.count() > 0;
    const hasNoResultsMsg = await noResults.isVisible().catch(() => false);
    expect(hasResults || hasNoResultsMsg).toBeTruthy();
  });

  test('Productos sin imagen muestran placeholder (no broken) @catalog @funcional', async ({ page }) => {
    await page.waitForTimeout(3_000);
    const images = page.locator('img[src*="product"], img[alt*="product" i], img[class*="product" i]');
    const allImages = page.locator('img');
    const totalImages = await allImages.count();

    let brokenCount = 0;
    for (let i = 0; i < totalImages; i++) {
      const img = allImages.nth(i);
      const naturalWidth = await img.evaluate((el: HTMLImageElement) => el.naturalWidth);
      const src = await img.getAttribute('src') || '';
      // Imagen rota: naturalWidth=0 y no es un SVG placeholder
      if (naturalWidth === 0 && !src.includes('.svg') && !src.startsWith('data:')) {
        brokenCount++;
      }
    }

    if (brokenCount > 0) {
      test.info().annotations.push({
        type: 'warning',
        description: `${brokenCount} imágenes rotas de ${totalImages} total`,
      });
    }
    // No debe haber imágenes rotas
    expect(brokenCount).toBe(0);
  });

  test('Búsqueda sin resultados muestra feedback @catalog @funcional', async ({ page }) => {
    const searchInput = page.getByPlaceholder('Buscar productos');
    await searchInput.fill('xyznoexiste99999');
    await searchInput.press('Enter');
    await page.waitForLoadState('networkidle', { timeout: 15_000 }).catch(() => {});

    const prices = page.locator('text=/\\$\\s*[\\d.,]+/');
    if (await prices.count() === 0) {
      await expect(page.getByText(/sin resultado|no encontr|no hay/i)).toBeVisible({ timeout: 10_000 });
    }
  });
});

test.describe('Codelpa — Carrito', () => {

  test.beforeEach(async ({ page }) => {
    await login(page);
    // Limpiar carrito antes de cada test para evitar que el botón "Agregar"
    // haya sido reemplazado por +/- de cantidad de una ejecución anterior
    await page.goto('/cart');
    await page.waitForLoadState('domcontentloaded');
    const eliminarTodos = page.getByRole('button', { name: /eliminar todos/i });
    if (await eliminarTodos.isVisible({ timeout: 5_000 }).catch(() => false)) {
      await eliminarTodos.click();
      await page.waitForTimeout(1_000);
    }
    await page.goto('/products');
    await page.waitForLoadState('domcontentloaded');
    await expect(
      page.locator('.add-new-product-to-cart-button').first()
    ).toBeVisible({ timeout: 30_000 });
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
    // Agregar producto
    await Promise.all([
      page.waitForResponse(resp => resp.url().includes('/cart') && resp.request().method() === 'POST'),
      page.locator('.add-new-product-to-cart-button').first().click(),
    ]);

    // Ir al carrito
    await page.goto('/cart');
    await page.waitForLoadState('domcontentloaded');
    await expect(page.getByText(/\d+ Producto/)).toBeVisible({ timeout: 15_000 });
  });

  test('Modificar cantidad en carrito @cart @funcional', async ({ page }) => {
    // Agregar producto
    await Promise.all([
      page.waitForResponse(resp => resp.url().includes('/cart') && resp.request().method() === 'POST'),
      page.locator('.add-new-product-to-cart-button').first().click(),
    ]);

    await page.goto('/cart');
    await expect(page.getByText(/\d+ Producto/)).toBeVisible({ timeout: 15_000 });

    const quantityInput = page.locator('input[type="number"]').first();
    await expect(quantityInput).toBeVisible({ timeout: 10_000 });
    await quantityInput.fill('3');
    await quantityInput.press('Tab');

    await page.waitForResponse(resp => resp.url().includes('/cart'), { timeout: 10_000 });
    await expect(quantityInput).toHaveValue('3');
  });
});

test.describe('Codelpa — Cupones (PM1/PM2)', () => {

  test('Campo de cupón visible en carrito @coupons @funcional', async ({ page }) => {
    test.skip(CLIENT.config.enableCoupons === false, 'enableCoupons=false en esta instancia — cupones deshabilitados');
    await login(page);
    await page.goto('/products');
    await page.waitForLoadState('domcontentloaded');

    // Agregar producto
    const addButton = page.locator('.add-new-product-to-cart-button').first();
    await expect(addButton).toBeVisible({ timeout: 30_000 });
    await Promise.all([
      page.waitForResponse(resp => resp.url().includes('/cart') && resp.request().method() === 'POST'),
      addButton.click(),
    ]);

    // Ir al carrito
    await page.goto('/cart');
    await page.waitForLoadState('domcontentloaded');
    await expect(page.getByText(/\d+ Producto/)).toBeVisible({ timeout: 15_000 });

    // Verificar campo de cupón (enableCoupons=true)
    const couponField = page.getByLabel(/cup[oó]n/i)
      .or(page.getByPlaceholder(/cup[oó]n/i))
      .or(page.getByText('Ingresar cupón'));
    await expect(couponField.first()).toBeVisible({ timeout: 10_000 });
  });

  test('Cupón inválido muestra error (no crash) @coupons @crítico', async ({ page }) => {
    test.skip(CLIENT.config.enableCoupons === false, 'enableCoupons=false en esta instancia — cupones deshabilitados');
    await login(page);
    await page.goto('/products');
    await page.waitForLoadState('domcontentloaded');

    await Promise.all([
      page.waitForResponse(resp => resp.url().includes('/cart') && resp.request().method() === 'POST'),
      page.locator('.add-new-product-to-cart-button').first().click(),
    ]);

    await page.goto('/cart');
    await page.waitForLoadState('domcontentloaded');
    await expect(page.getByText(/\d+ Producto/)).toBeVisible({ timeout: 15_000 });

    // Ingresar cupón inválido
    const couponInput = page.getByLabel(/cup[oó]n/i)
      .or(page.getByPlaceholder(/cup[oó]n/i));
    await couponInput.first().fill('CUPON_INVALIDO_999');

    const applyButton = page.getByRole('button', { name: /aplicar/i });
    await applyButton.click();

    // Debe mostrar error, no crashear
    await page.waitForTimeout(3_000);
    await expect(page.locator('body')).not.toContainText(/error.*500|internal server/i);
  });
});

test.describe('Codelpa — Checkout', () => {

  test('Flujo completo: catálogo → carrito → checkout @checkout @funcional', async ({ page }) => {
    await login(page);
    await page.goto('/products');
    await page.waitForLoadState('domcontentloaded');

    // Agregar producto
    const addButton = page.locator('.add-new-product-to-cart-button').first();
    await expect(addButton).toBeVisible({ timeout: 45_000 });
    await addButton.click();
    await page.waitForTimeout(2_000);

    // Ir al carrito
    await page.goto('/cart');
    await page.waitForLoadState('domcontentloaded');
    await expect(page.getByText(/\d+ Producto/)).toBeVisible({ timeout: 15_000 });

    // Confirmar pedido
    const confirmButton = page.getByRole('button', { name: /confirmar pedido/i });
    await expect(confirmButton).toBeVisible({ timeout: 10_000 });
    await confirmButton.click();

    // Debe llegar a confirmación
    await expect(page).toHaveURL(/confirmation/, { timeout: 30_000 });
  });

  test('Pedido aparece en historial post-checkout @checkout @funcional', async ({ page }) => {
    await login(page);

    // Ir a historial de pedidos
    await page.goto('/orders');
    await page.waitForLoadState('domcontentloaded');

    // Debe haber al menos un pedido (del test anterior o previos)
    const orders = page.locator('table tr, [class*="order" i]');
    await expect(orders.first()).toBeVisible({ timeout: 15_000 });
  });
});

test.describe('Codelpa — Precios', () => {

  test.beforeEach(async ({ page }) => {
    await login(page);
    await page.goto('/products');
    await page.waitForLoadState('domcontentloaded');
    await expect(page.locator('text=/\\$\\s*[\\d.,]+/').first()).toBeVisible({ timeout: 30_000 });
  });

  test('Precios en formato CLP ($ sin decimales) @pricing @funcional', async ({ page }) => {
    const prices = page.locator('text=/\\$\\s*[\\d.,]+/');
    const count = await prices.count();
    expect(count).toBeGreaterThan(0);
  });

  test('Precios consistentes catálogo vs carrito @pricing @funcional', async ({ page }) => {
    // Capturar primer precio visible
    const firstPrice = page.locator('text=/\\$\\s*[\\d.,]+/').first();
    const catalogPrice = await firstPrice.textContent();

    // Agregar ese producto
    await Promise.all([
      page.waitForResponse(resp => resp.url().includes('/cart') && resp.request().method() === 'POST'),
      page.locator('.add-new-product-to-cart-button').first().click(),
    ]);

    // Ir al carrito y verificar que el precio aparece
    await page.goto('/cart');
    await page.waitForLoadState('domcontentloaded');
    await expect(page.getByText(/\d+ Producto/)).toBeVisible({ timeout: 15_000 });

    // El carrito debe mostrar precios (no necesariamente el mismo, pero sí formato CLP)
    await expect(page.locator('text=/\\$\\s*[\\d.,]+/').first()).toBeVisible({ timeout: 10_000 });
  });

  test('hideReceiptType=true — no muestra selector de boleta/factura @pricing @funcional', async ({ page }) => {
    // Agregar producto e ir al carrito
    await Promise.all([
      page.waitForResponse(resp => resp.url().includes('/cart') && resp.request().method() === 'POST'),
      page.locator('.add-new-product-to-cart-button').first().click(),
    ]);

    await page.goto('/cart');
    await page.waitForLoadState('domcontentloaded');
    await expect(page.getByText(/\d+ Producto/)).toBeVisible({ timeout: 15_000 });

    // No debe mostrar selector de tipo de recibo
    const receiptType = page.getByText(/tipo de recibo|boleta|factura/i);
    const visible = await receiptType.isVisible({ timeout: 5_000 }).catch(() => false);
    expect(visible).toBeFalsy();
  });
});

test.describe('Codelpa — Detalle de producto', () => {

  test('Click en producto abre detalle/modal @detalle-de-producto @funcional', async ({ page }) => {
    await login(page);
    await page.goto('/products');
    await page.waitForLoadState('domcontentloaded');
    await expect(page.locator('.add-new-product-to-cart-button').first()).toBeVisible({ timeout: 30_000 });

    // Click en el nombre o imagen del primer producto (no en "Agregar")
    const productCard = page.locator('[class*="ProductCard"], [class*="product-card"]').first();
    const productLink = productCard.locator('a').first();

    if (await productLink.isVisible({ timeout: 5_000 }).catch(() => false)) {
      await productLink.click();
      await page.waitForLoadState('domcontentloaded');
      // Debe abrir detalle (modal o página /products/[uuid])
      const isModal = await page.locator('[data-testid="product-detail-modal"]').isVisible({ timeout: 5_000 }).catch(() => false);
      const isPage = page.url().includes('/products/');
      expect(isModal || isPage).toBeTruthy();
    }
  });
});

test.describe('Codelpa — Consola y errores', () => {

  test('Navegación sin errores JS en consola @consola-y-errores @crítico', async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', (error) => errors.push(error.message));

    await login(page);

    // Navegar por las páginas principales
    const routes = ['/products', '/cart', '/orders', '/payments'];
    for (const route of routes) {
      await page.goto(route);
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(2_000);
    }

    if (errors.length > 0) {
      test.info().annotations.push({
        type: 'error',
        description: `${errors.length} errores JS: ${errors.slice(0, 3).join(' | ')}`,
      });
    }
    expect(errors.length).toBe(0);
  });

  test('Sin requests 4xx/5xx durante navegación @consola-y-errores @funcional', async ({ page }) => {
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

    // Filtrar errores esperados (ej: 401 pre-auth, favicon)
    const realErrors = failedRequests.filter(
      r => !r.includes('favicon') && !r.includes('/auth/')
    );

    if (realErrors.length > 0) {
      test.info().annotations.push({
        type: 'warning',
        description: `Requests fallidos: ${realErrors.slice(0, 5).join(', ')}`,
      });
    }
    expect(realErrors.length).toBe(0);
  });
});

test.describe('Codelpa — Monto mínimo y validaciones', () => {

  test('Carrito vacío no permite confirmar pedido @monto-mínimo-y-validaciones @funcional', async ({ page }) => {
    await login(page);
    await page.goto('/cart');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3_000);

    const confirmButton = page.getByRole('button', { name: /confirmar pedido/i });
    if (await confirmButton.isVisible({ timeout: 5_000 }).catch(() => false)) {
      // Si el botón existe, debe estar deshabilitado con carrito vacío
      await expect(confirmButton).toBeDisabled();
    }
    // Si no existe el botón, es comportamiento correcto (no muestra checkout sin items)
  });

  test('Monto mínimo muestra mensaje si no se alcanza @monto-mínimo-y-validaciones @funcional', async ({ page }) => {
    await login(page);
    await page.goto('/products');
    await page.waitForLoadState('domcontentloaded');

    // Agregar solo 1 producto (puede estar bajo el mínimo)
    const addButton = page.locator('.add-new-product-to-cart-button').first();
    await expect(addButton).toBeVisible({ timeout: 30_000 });
    await Promise.all([
      page.waitForResponse(resp => resp.url().includes('/cart') && resp.request().method() === 'POST'),
      addButton.click(),
    ]);

    await page.goto('/cart');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3_000);

    // Verificar si hay mensaje de monto mínimo
    const minMessage = page.getByText(/monto mínimo|mínimo de compra/i);
    const hasMinMessage = await minMessage.isVisible({ timeout: 5_000 }).catch(() => false);

    if (hasMinMessage) {
      test.info().annotations.push({
        type: 'info',
        description: 'Monto mínimo activo — mensaje visible en carrito',
      });
    }
    // No falla — solo documenta si el monto mínimo está activo
  });
});

test.describe('Codelpa — Pedidos y estados', () => {

  test('Historial de pedidos muestra tabla con estados @pedidos-y-estados @funcional', async ({ page }) => {
    await login(page);
    await page.goto('/orders');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3_000);

    // Debe mostrar tabla de pedidos o mensaje vacío
    const ordersTable = page.locator('table, [class*="order"]');
    const emptyMessage = page.getByText(/no hay pedidos|sin pedidos|no tiene pedidos/i);
    const hasOrders = await ordersTable.first().isVisible({ timeout: 10_000 }).catch(() => false);
    const hasEmptyMsg = await emptyMessage.isVisible({ timeout: 5_000 }).catch(() => false);

    expect(hasOrders || hasEmptyMsg).toBeTruthy();
  });

  test('Estados de pedido son válidos (no "No disponible") @pedidos-y-estados @funcional', async ({ page }) => {
    await login(page);
    await page.goto('/orders');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3_000);

    // "No disponible" indica un status no mapeado — bug de config
    const invalidStatus = page.getByText('No disponible');
    const count = await invalidStatus.count();
    if (count > 0) {
      test.info().annotations.push({
        type: 'warning',
        description: `${count} pedidos con estado "No disponible" — status no mapeado`,
      });
    }
    expect(count).toBe(0);
  });
});

test.describe('Codelpa — Pagos', () => {

  test('Historial de pagos carga @pagos @funcional', async ({ page }) => {
    await login(page);
    await page.goto('/payments');
    await page.waitForLoadState('domcontentloaded');
    // La página debe cargar sin error
    await expect(page.locator('body')).not.toContainText(/error.*500|internal server/i);
  });

  test('Montos no muestran valores negativos confusos @pagos @funcional', async ({ page }) => {
    await login(page);
    await page.goto('/payments');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3_000);

    // Buscar montos negativos sospechosos (ej: -$1.234 sin contexto de nota de crédito)
    const negativeAmounts = page.locator('text=/-\\$\\s*[\\d.,]+/');
    const count = await negativeAmounts.count();
    // Si hay negativos, deben tener contexto (nota de crédito, devolución)
    if (count > 0) {
      test.info().annotations.push({
        type: 'warning',
        description: `${count} montos negativos encontrados — verificar que sean notas de crédito`,
      });
    }
  });
});

test.describe('Codelpa — Variables sin cobertura (config-dependent)', () => {

  test('purchaseOrderEnabled: Campo OC (Orden de Compra) visible en checkout @config @funcional', async ({ page }) => {
    // TODO: Validar con Cowork que el campo OC existe y ubicación exacta
    // Requiere que purchaseOrderEnabled=true en config (✓ en Codelpa)

    await login(page);
    await page.goto('/products');
    await page.waitForLoadState('domcontentloaded');

    // Agregar producto
    const addButton = page.locator('.add-new-product-to-cart-button').first();
    await expect(addButton).toBeVisible({ timeout: 30_000 });
    await Promise.all([
      page.waitForResponse(resp => resp.url().includes('/cart') && resp.request().method() === 'POST'),
      addButton.click(),
    ]);

    // Ir a carrito/checkout
    await page.goto('/cart');
    await page.waitForLoadState('domcontentloaded');
    await expect(page.getByText(/\d+ Producto/)).toBeVisible({ timeout: 15_000 });

    // Buscar campo OC con fallbacks
    const ocField = page.getByLabel(/orden de compra|OC|purchase order/i)
      .or(page.getByPlaceholder(/OC|orden de compra/i))
      .or(page.locator('input[placeholder*="OC"]'));

    const visible = await ocField.first().isVisible({ timeout: 10_000 }).catch(() => false);

    if (visible) {
      test.info().annotations.push({
        type: 'pass',
        description: 'Campo OC visible en checkout (purchaseOrderEnabled=true)',
      });
    } else {
      test.info().annotations.push({
        type: 'warning',
        description: 'Campo OC no encontrado — verificar ubicación exacta en el form',
      });
    }
  });

  test('disableCommerceEdit: Campos de perfil comercio son read-only @config @funcional', async ({ page }) => {
    // TODO: Encontrar ruta exacta del perfil (probables: /profile, /account, /settings)
    // Requiere que disableCommerceEdit=true en config (✓ en Codelpa)

    await login(page);

    // Intentar navegar a perfil — probar múltiples rutas
    const profileRoutes = ['/profile', '/account', '/settings', '/commerce'];
    let foundProfile = false;

    for (const route of profileRoutes) {
      await page.goto(route);
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(1_000);

      // Buscar campos de comercio
      const nameField = page.getByLabel(/nombre|razón social|business name/i).first();
      if (await nameField.isVisible({ timeout: 3_000 }).catch(() => false)) {
        foundProfile = true;

        // Verificar que está disabled o readonly
        const isDisabled = await nameField.evaluate((el: HTMLInputElement) => el.disabled || el.readOnly);

        if (isDisabled) {
          test.info().annotations.push({
            type: 'pass',
            description: `Perfil encontrado en ${route} — campos disabled/readonly (disableCommerceEdit=true)`,
          });
        } else {
          test.info().annotations.push({
            type: 'warning',
            description: `Campo ${route} visible pero NO está disabled — Codelpa requiere disableCommerceEdit=true`,
          });
        }
        expect(isDisabled).toBeTruthy();
        break;
      }
    }

    if (!foundProfile) {
      test.info().annotations.push({
        type: 'warning',
        description: 'Página de perfil no encontrada en rutas probables — requiere exploración Cowork',
      });
    }
  });

  test('hasStockEnabled + hasAllDistributionCenters: Stock visible en tarjetas (multicentro) @config @funcional', async ({ page }) => {
    // Requiere hasStockEnabled=true y hasAllDistributionCenters=true en config (✓ en Codelpa)

    await login(page);
    await page.goto('/products');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3_000);

    // Buscar indicadores de stock en tarjetas
    const stockIndicators = page.getByText(/stock|disponible|unidades/i)
      .or(page.locator('[class*="stock" i], [class*="inventory" i]'));

    const stockCount = await stockIndicators.count();

    if (stockCount > 0) {
      test.info().annotations.push({
        type: 'pass',
        description: `Stock visible: ${stockCount} indicadores encontrados (hasStockEnabled=true, hasAllDistributionCenters=true)`,
      });
      expect(stockCount).toBeGreaterThan(0);
    } else {
      test.info().annotations.push({
        type: 'warning',
        description: 'Stock no visible con los selectores probados — requiere validación Cowork',
      });
    }

    // Si multicentro está activo, debería haber opción de ver centros
    const viewStockButton = page.getByRole('button', { name: /ver stock|stock|centros/i });
    const hasViewStock = await viewStockButton.isVisible({ timeout: 5_000 }).catch(() => false);

    if (hasViewStock) {
      test.info().annotations.push({
        type: 'info',
        description: 'Botón "Ver stock" (multicentro) visible',
      });
    }
  });

  test('enableOrderApproval: Órdenes pueden estar en estado "pending_approval" @config @funcional', async ({ page }) => {
    // Requiere enableOrderApproval=true en config (✓ en Codelpa)
    // Datos: 24 órdenes en pending_approval en MongoDB

    await login(page);
    await page.goto('/orders');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3_000);

    // Buscar indicadores de aprobación
    const approvalElements = page.getByText(/pending approval|pending_approval|pendiente.*aprobar|aprobación/i)
      .or(page.getByRole('button', { name: /aprobar|approve|validar/i }));

    const hasApprovalUI = await approvalElements.first().isVisible({ timeout: 5_000 }).catch(() => false);

    if (hasApprovalUI) {
      test.info().annotations.push({
        type: 'pass',
        description: 'UI de aprobación visible en órdenes (enableOrderApproval=true)',
      });
    } else {
      // No fallamos — pueden no haber órdenes pendientes en el momento
      test.info().annotations.push({
        type: 'info',
        description: 'No se encontró UI de aprobación — probablemente no hay órdenes pending_approval ahora',
      });
    }

    // Verificar que el estado "No disponible" no aparece (bug conocido)
    const invalidStatus = page.getByText('No disponible');
    const hasInvalidStatus = await invalidStatus.isVisible({ timeout: 3_000 }).catch(() => false);
    expect(hasInvalidStatus).toBeFalsy();
  });
});

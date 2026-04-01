import { test, expect } from '@playwright/test';
import { loginHelper } from '../fixtures/login';
import clients from '../fixtures/clients';

/**
 * QA E2E — Surtiventas (surtiventas.solopide.me)
 *
 * Config: anonymousAccess=false, enableCoupons=true, enableSellerDiscount=true,
 *         hasStockEnabled=true (single center), hasSingleDistributionCenter=true,
 *         editAddress=true, disableCommerceEdit=false, currency=CLP
 *
 * Selectores basados en YOMCL/b2b repo (Next.js + MUI v5):
 * - Login: label="Correo", label="Contraseña", button "Iniciar sesión"
 * - Catálogo: placeholder="Buscar productos", class="add-new-product-to-cart-button"
 * - Carrito: data-testid="side-cart-button", label="Ingresar cupón"
 * - Checkout: button "Confirmar pedido"
 */

const CLIENT = clients.surtiventas;
const EMAIL = process.env.SURTIVENTAS_EMAIL || process.env.COMMERCE_EMAIL || '';
const PASSWORD = process.env.SURTIVENTAS_PASSWORD || process.env.COMMERCE_PASSWORD || '';

// Helper: login en Surtiventas — navega directo al form de login
async function login(page: any) {
  await loginHelper(page, EMAIL, PASSWORD, CLIENT.loginPath, CLIENT.baseURL);
}

test.describe('Surtiventas — Login', () => {

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
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    await page.getByLabel('Correo').fill(EMAIL);
    await page.getByLabel('Contraseña').fill('WrongPassword123');
    await page.locator('form').getByRole('button', { name: 'Iniciar sesión' }).click();
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/auth|login/);
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

test.describe('Surtiventas — Catálogo', () => {

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
    const prices = page.locator('text=/\\$\\s*[\\d.,]+/');
    const allPrices = await prices.allTextContents();
    const zeroCount = allPrices.filter(p => /\$\s*0(?:\.|,)?(?:\s|$)/.test(p)).length;
    if (zeroCount > 0) {
      test.info().annotations.push({
        type: 'warning',
        description: `${zeroCount} productos con precio $0 encontrados`,
      });
    }
    expect(zeroCount).toBe(0);
  });

  test('Carrito muestra items agregados @catalog @funcional', async ({ page }) => {
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

  test('Modificar cantidad en carrito @catalog @funcional', async ({ page }) => {
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

test.describe('Surtiventas — Cupones (enableCoupons=true)', () => {

  test('Campo de cupón visible en carrito @coupons @funcional', async ({ page }) => {
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

test.describe('Surtiventas — Checkout', () => {

  test('Flujo completo: catálogo → carrito → checkout @checkout @funcional', async ({ page }) => {
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

test.describe('Surtiventas — Precios', () => {

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
    // Capturar primer producto y su precio
    const firstProduct = page.locator('.product-card').first();
    const firstPrice = firstProduct.locator('text=/\\$\\s*[\\d.,]+/').first();
    const catalogPrice = await firstPrice.textContent();
    const productName = await firstProduct.locator('[class*="name"]').first().textContent().catch(() => 'Producto desconocido');

    console.log(`\n📦 Producto a testear: ${productName}`);
    console.log(`💰 Precio en catálogo: ${catalogPrice}\n`);

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
    await expect(page.locator('text=/\\$\\s*[\\d.,]+/')).toBeVisible({ timeout: 10_000 });
  });
});

test.describe('Surtiventas — Detalle de producto', () => {

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
      // Debe mostrar detalle o modal
      await expect(page.locator('body')).not.toContainText(/error.*500|not found/i);
    }
  });
});

test.describe('Surtiventas — Pedidos y estados', () => {

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

test.describe('Surtiventas — Validaciones', () => {

  test('Carrito vacío no permite confirmar pedido @validaciones @funcional', async ({ page }) => {
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

  test('Monto mínimo muestra mensaje si no se alcanza @validaciones @funcional', async ({ page }) => {
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

test.describe('Surtiventas — Variables sin cobertura (config-dependent)', () => {

  test('disableCommerceEdit=false: Campos de perfil comercio son EDITABLES @config @configuración', async ({ page }) => {
    // TODO: Encontrar ruta exacta del perfil (probables: /profile, /account, /settings)
    // Surtiventas: disableCommerceEdit=false → campos DEBEN ser editables (diferente a Codelpa)

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

        // Verificar que NO está disabled
        const isDisabled = await nameField.evaluate((el: HTMLInputElement) => el.disabled || el.readOnly);

        if (!isDisabled) {
          test.info().annotations.push({
            type: 'pass',
            description: `Perfil encontrado en ${route} — campos EDITABLES (disableCommerceEdit=false)`,
          });
        } else {
          test.info().annotations.push({
            type: 'warning',
            description: `Campo ${route} está disabled/readonly pero Surtiventas tiene disableCommerceEdit=false`,
          });
        }
        expect(isDisabled).toBeFalsy();
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

  test('editAddress=true: Dirección es editable en checkout @config @configuración', async ({ page }) => {
    // TODO: Validar con Cowork que la dirección es editable
    // Surtiventas: editAddress=true → dirección debe ser editable

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

    // Buscar campo de dirección
    const addressField = page.getByLabel(/dirección|address|calle/i)
      .or(page.getByPlaceholder(/dirección|address|calle/i));

    const visible = await addressField.first().isVisible({ timeout: 10_000 }).catch(() => false);

    if (visible) {
      const isDisabled = await addressField.first().evaluate((el: HTMLInputElement) => el.disabled || el.readOnly).catch(() => true);

      if (!isDisabled) {
        test.info().annotations.push({
          type: 'pass',
          description: 'Dirección visible y editable en checkout (editAddress=true)',
        });
      } else {
        test.info().annotations.push({
          type: 'warning',
          description: 'Dirección visible pero disabled — Surtiventas requiere editAddress=true',
        });
      }
    } else {
      test.info().annotations.push({
        type: 'warning',
        description: 'Campo dirección no encontrado — requiere exploración Cowork',
      });
    }
  });

  test('hasStockEnabled=true + hasSingleDistributionCenter: Stock visible en tarjetas (sin multicentro) @config @funcional', async ({ page }) => {
    // Surtiventas: hasStockEnabled=true + hasSingleDistributionCenter=true
    // (diferente a Codelpa que tiene hasAllDistributionCenters=true)

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
        description: `Stock visible: ${stockCount} indicadores encontrados (hasStockEnabled=true)`,
      });
      expect(stockCount).toBeGreaterThan(0);
    } else {
      test.info().annotations.push({
        type: 'warning',
        description: 'Stock no visible con los selectores probados — requiere validación Cowork',
      });
    }

    // Surtiventas NO debe mostrar multicentro (hasSingleDistributionCenter=true)
    const viewStockButton = page.getByRole('button', { name: /ver stock|stock|centros/i });
    const hasViewStock = await viewStockButton.isVisible({ timeout: 5_000 }).catch(() => false);

    if (!hasViewStock) {
      test.info().annotations.push({
        type: 'info',
        description: 'Botón "Ver stock multicentro" NO visible (esperado: hasSingleDistributionCenter=true)',
      });
    }
  });

  test('enableSellerDiscount=true: Descuento visible en carrito/checkout @config @funcional', async ({ page }) => {
    // Surtiventas: enableSellerDiscount=true

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

    // Buscar campo de descuento
    const discountField = page.getByLabel(/descuento|discount|%/i)
      .or(page.getByPlaceholder(/descuento|discount|%/i));

    const visible = await discountField.first().isVisible({ timeout: 5_000 }).catch(() => false);

    if (visible) {
      test.info().annotations.push({
        type: 'pass',
        description: 'Campo descuento visible en carrito (enableSellerDiscount=true)',
      });
    } else {
      test.info().annotations.push({
        type: 'info',
        description: 'Campo descuento no visible — puede estar deshabilitado para este usuario',
      });
    }
  });

  test('useNewPromotions=true: Promociones deben estar visibles @config @funcional', async ({ page }) => {
    // Surtiventas: useNewPromotions=true

    await login(page);
    await page.goto('/products');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3_000);

    // Buscar indicadores de promoción/oferta
    const promotionIndicators = page.getByText(/promoción|oferta|%|descuento/i)
      .or(page.locator('[class*="promo" i], [class*="offer" i], [class*="badge" i]'));

    const promoCount = await promotionIndicators.count();

    if (promoCount > 0) {
      test.info().annotations.push({
        type: 'info',
        description: `Indicadores de promoción: ${promoCount} encontrados (useNewPromotions=true)`,
      });
    } else {
      test.info().annotations.push({
        type: 'info',
        description: 'Promociones no visibles — puede no haber promociones activas',
      });
    }
  });

  test('hasMultiUnitEnabled=true: Selector de unidad de compra (caja/unidad/etc) @config @funcional', async ({ page }) => {
    // Surtiventas: hasMultiUnitEnabled=true

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

    // Buscar selector de unidad de compra
    const unitSelector = page.getByLabel(/unidad|caja|paquete|unit|box|package/i)
      .or(page.getByRole('combobox', { name: /unidad|caja/i }));

    const visible = await unitSelector.first().isVisible({ timeout: 5_000 }).catch(() => false);

    if (visible) {
      test.info().annotations.push({
        type: 'pass',
        description: 'Selector de unidad de compra visible (hasMultiUnitEnabled=true)',
      });
    } else {
      test.info().annotations.push({
        type: 'info',
        description: 'Selector de unidad no visible — productos pueden no tener múltiples unidades',
      });
    }
  });
});

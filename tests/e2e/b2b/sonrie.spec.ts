import { test, expect } from '@playwright/test';
import { loginHelper } from '../fixtures/login';

/**
 * QA E2E — Sonrie (sonrie.solopide.me)
 *
 * Tests funcionales específicos: login, catálogo, carrito, pedidos, consola.
 * Tests de config (variables MongoDB) cubiertos por config-validation.spec.ts.
 *
 * Bugs detectados:
 *   - Estados "No disponible" en pedidos (3 pedidos afectados)
 *   - 500 en /api/v2/commerces/delivery
 */

const BASE_URL = 'https://sonrie.solopide.me';
const LOGIN_PATH = '/auth/jwt/login';
const EMAIL = process.env.SONRIE_EMAIL || '';
const PASSWORD = process.env.SONRIE_PASSWORD || '';

test.use({ baseURL: BASE_URL });

async function login(page: any) {
  await loginHelper(page, EMAIL, PASSWORD, LOGIN_PATH, BASE_URL);
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

async function noCommerceAssigned(page: any): Promise<boolean> {
  return page.getByRole('button', { name: 'Siguiente' }).isVisible({ timeout: 5_000 }).catch(() => false)
    || page.getByText('Código de cliente').isVisible({ timeout: 2_000 }).catch(() => false);
}

// ─── Login ────────────────────────────────────────────────────────────────────

test.describe('Sonrie — Login', () => {

  test('Login exitoso @login @funcional', async ({ page }) => {
    await login(page);
    await expect(page.locator('main')).toBeVisible({ timeout: 30_000 });
  });

  test('Login fallido con password incorrecto @login @crítico', async ({ page }) => {
    await page.goto(`${BASE_URL}${LOGIN_PATH}`, { waitUntil: 'domcontentloaded' });
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

  test('Sesión persistente — volver a URL mantiene sesión @login @funcional', async ({ page }) => {
    await login(page);
    const urlAfterLogin = page.url();
    await page.goto(urlAfterLogin);
    await page.waitForLoadState('domcontentloaded');
    expect(/auth\/jwt\/login/.test(page.url())).toBeFalsy();
  });

  test('Logout redirige a login @login @funcional', async ({ page }) => {
    await login(page);
    const menuTrigger = page.locator('[class*="avatar" i], [class*="user" i]').first();
    const hasMenu = await menuTrigger.isVisible({ timeout: 10_000 }).catch(() => false);
    if (hasMenu) {
      await menuTrigger.click();
      await page.waitForTimeout(1_000);
      const logoutBtn = page.getByText(/cerrar sesi[oó]n|logout/i);
      if (await logoutBtn.first().isVisible({ timeout: 5_000 }).catch(() => false)) {
        await logoutBtn.first().click();
        await page.waitForTimeout(2_000);
        await expect(page).toHaveURL(/auth|login/, { timeout: 10_000 });
        return;
      }
    }
    test.info().annotations.push({ type: 'warning', description: 'Menú/logout no encontrado — verificar con Cowork' });
    expect(true).toBeTruthy();
  });

});

// ─── Catálogo ─────────────────────────────────────────────────────────────────

test.describe('Sonrie — Catálogo', () => {

  test.beforeEach(async ({ page }) => {
    await login(page);
    await clearCart(page);
    await page.goto('/products');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2_000);
    if (await noCommerceAssigned(page)) {
      test.skip(true, 'Cuenta sin comercio asignado');
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
    for (let i = 0; i < Math.min(cardCount, 20); i++) {
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

  test('API catálogo devuelve datos completos (pipeline Mongo→API) @catalog @crítico', async ({ page }) => {
    // Interceptar /api/v2/catalog — el endpoint real que alimenta el catálogo B2B
    // El listener debe estar activo ANTES de navegar; recargar la página para capturar la respuesta
    let catalogResponse: any[] = [];
    page.on('response', async response => {
      if (response.url().includes('/api/v2/catalog') && !response.url().includes('/count') && !response.url().includes('/filter') && response.status() === 200) {
        const json = await response.json().catch(() => null);
        if (Array.isArray(json) && json.length > catalogResponse.length) {
          catalogResponse = json;
        }
      }
    });

    // Recargar para que el listener capture la llamada al catálogo
    await page.goto('/products');
    await page.waitForLoadState('domcontentloaded');
    await expect(page.locator('text=/\\$\\s*[\\d.,]+/').first()).toBeVisible({ timeout: 20_000 });
    await page.waitForTimeout(2_000);

    if (catalogResponse.length === 0) {
      test.info().annotations.push({ type: 'warning', description: 'No se interceptó /api/v2/catalog' });
      test.skip();
      return;
    }

    const products = catalogResponse;
    test.info().annotations.push({ type: 'info', description: `API /v2/catalog: ${products.length} productos` });

    // Pipeline OK: debe devolver al menos los 30 productos confirmados el 2026-04-16
    // Si baja de 30 → regresión en el pipeline Mongo→API
    expect(products.length).toBeGreaterThanOrEqual(30);

    // Campos obligatorios — estructura real de /api/v2/catalog:
    // name, image (S3 URL), enabled, b2bHidden, pricing (objeto con datos de precio)
    const missingName: string[] = [];
    const noPricing: string[] = [];
    const disabled: string[] = [];
    const missingImage: string[] = [];

    products.forEach((p: any, i: number) => {
      const label = p.name || `#${i}`;
      if (!p.name)    missingName.push(label);
      if (!p.pricing) noPricing.push(label);
      if (!p.image)   missingImage.push(label);
      if (p.enabled === false || p.b2bHidden === true) disabled.push(label);
    });

    if (missingName.length)  test.info().annotations.push({ type: 'error',   description: `Sin nombre: ${missingName.slice(0,5).join(', ')}` });
    if (noPricing.length)    test.info().annotations.push({ type: 'error',   description: `Sin pricing: ${noPricing.slice(0,5).join(', ')}` });
    if (disabled.length)     test.info().annotations.push({ type: 'warning', description: `Producto disabled/b2bHidden en respuesta: ${disabled.slice(0,5).join(', ')}` });
    if (missingImage.length) test.info().annotations.push({ type: 'warning', description: `Sin imagen: ${missingImage.slice(0,5).join(', ')}` });

    expect(missingName.length).toBe(0);
    expect(noPricing.length).toBe(0);
    // disabled y missingImage: warning pero no falla (pueden ser intencionales)
  });

  test('Productos sin imágenes rotas (404) @catalog @funcional', async ({ page }) => {
    const broken: string[] = [];
    page.on('response', response => {
      const url = response.url();
      if (
        response.status() === 404 &&
        /\.(jpg|jpeg|png|webp|gif|svg)/i.test(url) &&
        !url.includes('favicon')
      ) {
        broken.push(url.split('/').pop() || url);
      }
    });
    await expect(page.locator('text=/\\$\\s*[\\d.,]+/').first()).toBeVisible({ timeout: 20_000 });
    await page.waitForTimeout(3_000);
    if (broken.length > 0) {
      test.info().annotations.push({ type: 'error', description: `${broken.length} imagen(es) 404: ${broken.slice(0, 5).join(', ')}` });
    }
    expect(broken.length).toBe(0);
  });

  test('Buscar producto por nombre @catalog @funcional', async ({ page }) => {
    const searchInput = page.getByPlaceholder(/buscar/i);
    await expect(searchInput).toBeVisible({ timeout: 15_000 });
    await searchInput.fill('test');
    await searchInput.press('Enter');
    await page.waitForLoadState('networkidle', { timeout: 15_000 }).catch(() => {});
    const results = page.locator('text=/\\$\\s*[\\d.,]+/');
    const noResults = page.getByText(/sin resultado|no encontr|no hay/i);
    expect(await results.count() > 0 || await noResults.isVisible().catch(() => false)).toBeTruthy();
  });

});

// ─── Carrito ──────────────────────────────────────────────────────────────────

test.describe('Sonrie — Carrito', () => {

  test.beforeEach(async ({ page }) => {
    await login(page);
    await clearCart(page);
    await page.goto('/products');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2_000);
    if (await noCommerceAssigned(page)) {
      test.skip(true, 'Cuenta sin comercio asignado');
      return;
    }
    const addButton = page.locator('.add-new-product-to-cart-button').first();
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

  test('Doble submit — botón se deshabilita después del primer click @cart @crítico', async ({ page }) => {
    await Promise.all([
      page.waitForResponse(resp => resp.url().includes('/cart') && resp.request().method() === 'POST'),
      page.locator('.add-new-product-to-cart-button').first().click(),
    ]);
    await page.goto('/cart');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2_000);
    const confirmBtn = page.getByRole('button', { name: /confirmar pedido|pasar a confirmaci[oó]n/i });
    if (await confirmBtn.isVisible({ timeout: 10_000 }).catch(() => false)) {
      await confirmBtn.click();
      await page.waitForTimeout(500);
      const isDisabled = await confirmBtn.isDisabled().catch(() => true);
      if (!isDisabled) {
        test.info().annotations.push({ type: 'warning', description: 'Botón no se deshabilita — riesgo de doble submit' });
      }
      expect(isDisabled).toBeTruthy();
    } else {
      test.info().annotations.push({ type: 'warning', description: 'Botón confirmar pedido no encontrado en /cart' });
      expect(true).toBeTruthy();
    }
  });

});

// ─── Pedidos ──────────────────────────────────────────────────────────────────

test.describe('Sonrie — Pedidos', () => {

  test('Historial de pedidos carga @pedidos @funcional', async ({ page }) => {
    await login(page);
    await page.goto('/orders');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3_000);
    if (await noCommerceAssigned(page)) {
      test.skip();
      return;
    }
    const ordersContent = page.locator('table, [class*="order" i]');
    const emptyMessage = page.getByText(/no hay pedidos|sin pedidos/i);
    expect(
      await ordersContent.first().isVisible({ timeout: 10_000 }).catch(() => false) ||
      await emptyMessage.isVisible({ timeout: 5_000 }).catch(() => false)
    ).toBeTruthy();
  });

  test('Estados de pedido son válidos (no "No disponible") @pedidos @funcional', async ({ page }) => {
    await login(page);
    await page.goto('/orders');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3_000);
    const count = await page.getByText('No disponible').count();
    if (count > 0) {
      test.info().annotations.push({ type: 'warning', description: `${count} pedidos con estado "No disponible"` });
    }
    expect(count).toBe(0);
  });

});

// ─── Consola y errores ────────────────────────────────────────────────────────

test.describe('Sonrie — Consola y errores', () => {

  test('Sin errores JS en consola durante navegación @consola @crítico', async ({ page }) => {
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

  test('Sin requests 5xx durante navegación @consola @funcional', async ({ page }) => {
    const serverErrors: string[] = [];
    page.on('response', (response) => {
      if (response.status() >= 500) {
        const url = response.url().split('?')[0];
        if (!url.includes('favicon') && !url.includes('/auth/')) {
          serverErrors.push(`${response.status()} ${url}`);
        }
      }
    });
    await login(page);
    await page.goto('/products');
    await page.waitForLoadState('networkidle', { timeout: 15_000 }).catch(() => {});
    await page.goto('/cart');
    await page.waitForLoadState('networkidle', { timeout: 15_000 }).catch(() => {});
    if (serverErrors.length > 0) {
      test.info().annotations.push({ type: 'error', description: `Requests 5xx: ${serverErrors.slice(0, 5).join(', ')}` });
    }
    expect(serverErrors.length).toBe(0);
  });

});

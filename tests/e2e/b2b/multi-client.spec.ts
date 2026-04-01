import { test, expect } from '@playwright/test';
import { loginHelper } from '../fixtures/login';
import clients from '../fixtures/clients';

// Correr los flujos críticos contra cada cliente
for (const [key, client] of Object.entries(clients)) {
  test.describe(`${client.name} (${client.baseURL})`, () => {

    // ── LOGIN ──
    test(`${key}: Login exitoso`, async ({ browser }) => {
      const context = await browser.newContext();
      const page = await context.newPage();

      await page.goto(client.baseURL);
      await page.waitForLoadState('domcontentloaded');

      // Si anonymousAccess=true, ir directo al login path
      // Si anonymousAccess=false, ya debería redirigir a login
      if (client.config.anonymousAccess) {
        await page.goto(`${client.baseURL}${client.loginPath}`);
        await page.waitForLoadState('domcontentloaded');
      } else {
        await page.waitForLoadState('domcontentloaded');
      }

      // Login con helper robusto
      await loginHelper(page, client.credentials.email, client.credentials.password, client.loginPath, client.baseURL);

      await context.close();
    });

    // ── ACCESO ANÓNIMO ──
    if (client.config.anonymousAccess) {
      test(`${key}: Acceso anónimo muestra catálogo`, async ({ browser }) => {
        const context = await browser.newContext();
        const page = await context.newPage();
        await page.goto(client.baseURL);
        await expect(page).not.toHaveURL(/auth|login/);
        await expect(page.locator('text=/\\$\\s*[\\d.,]+/')).toBeVisible({ timeout: 15_000 });
        await context.close();
      });
    } else {
      test(`${key}: Sin acceso anónimo redirige a login`, async ({ browser }) => {
        const context = await browser.newContext();
        const page = await context.newPage();
        await page.goto(client.baseURL);
        // Debe redirigir a login
        await expect(page).toHaveURL(/auth|login/, { timeout: 15_000 });
        await context.close();
      });
    }

    // ── CATÁLOGO ──
    test(`${key}: Catálogo muestra productos con precios`, async ({ browser }) => {
      const context = await browser.newContext();
      const page = await context.newPage();
      await page.goto(client.baseURL);
      await page.waitForLoadState('domcontentloaded');

      // Login si es necesario
      if (!client.config.anonymousAccess) {
        await loginHelper(page, client.credentials.email, client.credentials.password, client.loginPath, client.baseURL);
      }

      // Verificar precios visibles
      if (!client.config.hidePrices) {
        await expect(page.locator('text=/\\$\\s*[\\d.,]+/')).toBeVisible({ timeout: 30_000 });
      }

      await context.close();
    });

    // ── CARRITO ──
    if (!client.config.disableCart) {
      test(`${key}: Agregar producto al carro`, async ({ browser }) => {
        const context = await browser.newContext();
        const page = await context.newPage();
        await page.goto(client.baseURL);
        await page.waitForLoadState('domcontentloaded');

        // Login
        if (!client.config.anonymousAccess) {
          await loginHelper(page, client.credentials.email, client.credentials.password, client.loginPath, client.baseURL);
        }

        // Ir a productos
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');

        // Agregar producto
        const addButton = page.getByRole('button', { name: 'Agregar' }).first();
        await addButton.waitFor({ timeout: 30_000 });

        const [response] = await Promise.all([
          page.waitForResponse(resp => resp.url().includes('/cart') && resp.request().method() === 'POST'),
          addButton.click(),
        ]);

        expect(response.ok()).toBeTruthy();

        await context.close();
      });
    }

    // ── PRECIOS $0 ──
    test(`${key}: No hay productos con precio $0`, async ({ browser }) => {
      const context = await browser.newContext();
      const page = await context.newPage();
      await page.goto(client.baseURL);
      await page.waitForLoadState('domcontentloaded');

      // Login si necesario
      if (!client.config.anonymousAccess) {
        await loginHelper(page, client.credentials.email, client.credentials.password, client.loginPath, client.baseURL);
      }

      // Ir a catálogo de productos
      await page.goto(`${client.baseURL}/products`);
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(5000);

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

      await context.close();
    });
  });
}

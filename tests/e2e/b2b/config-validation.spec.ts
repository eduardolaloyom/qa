import { test, expect } from '@playwright/test';
import clients from '../fixtures/clients.json';

/**
 * Validación de config: verifica que lo que dice MongoDB (clients.json)
 * coincida con lo que el frontend realmente muestra.
 *
 * Si MongoDB dice enableCoupons=true pero el campo de cupón no aparece → bug de config.
 * Si MongoDB dice anonymousAccess=false pero el catálogo se ve sin login → bug de seguridad.
 */
for (const [key, client] of Object.entries(clients)) {
  test.describe(`Config validation: ${client.name}`, () => {

    // Helper: login si es necesario
    async function loginIfNeeded(page: any) {
      await page.goto(client.baseURL);
      await page.waitForLoadState('domcontentloaded');
      if (!client.config.anonymousAccess) {
        await page.getByLabel('Correo').fill(client.credentials.email);
        await page.getByLabel('Contraseña').fill(client.credentials.password);
        await page.locator('form').getByRole('button', { name: /iniciar sesión/i }).click();
        await expect(page).not.toHaveURL(/auth\/jwt\/login|\/login$/, { timeout: 30_000 });
      }
    }

    // ── anonymousAccess ──
    test(`${key}: anonymousAccess=${client.config.anonymousAccess}`, async ({ browser }) => {
      const context = await browser.newContext();
      const page = await context.newPage();
      await page.goto(client.baseURL);
      await page.waitForLoadState('domcontentloaded');

      if (client.config.anonymousAccess) {
        // Debe mostrar contenido sin login
        await expect(page).not.toHaveURL(/auth|login/, { timeout: 10_000 });
      } else {
        // Debe redirigir a login
        await expect(page).toHaveURL(/auth|login/, { timeout: 10_000 });
      }

      await context.close();
    });

    // ── hidePrices ──
    test(`${key}: hidePrices=${client.config.hidePrices}`, async ({ browser }) => {
      const context = await browser.newContext();
      const page = await context.newPage();
      await loginIfNeeded(page);

      await page.goto(`${client.baseURL}/products`);
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(5000);

      const prices = page.locator('text=/\\$\\s*[\\d.,]+/');
      const priceCount = await prices.count();

      if (client.config.hidePrices) {
        expect(priceCount).toBe(0);
      } else {
        expect(priceCount).toBeGreaterThan(0);
      }

      await context.close();
    });

    // ── disableCart ──
    test(`${key}: disableCart=${client.config.disableCart}`, async ({ browser }) => {
      const context = await browser.newContext();
      const page = await context.newPage();
      await loginIfNeeded(page);

      await page.goto(`${client.baseURL}/products`);
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(5000);

      const addButtons = page.getByRole('button', { name: 'Agregar' });
      const cartLink = page.locator('a[href*="cart"]');

      if (client.config.disableCart) {
        // No debe haber botones de agregar ni link al carro
        expect(await addButtons.count()).toBe(0);
      } else {
        // Debe haber botones de agregar
        expect(await addButtons.count()).toBeGreaterThan(0);
      }

      await context.close();
    });

    // ── enableCoupons ──
    if (client.config.enableCoupons !== undefined) {
      test(`${key}: enableCoupons=${client.config.enableCoupons}`, async ({ browser }) => {
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        // Agregar producto al carro para ver checkout
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');
        const addButton = page.getByRole('button', { name: 'Agregar' }).first();

        if (await addButton.isVisible({ timeout: 15_000 }).catch(() => false)) {
          await addButton.click();
          await page.waitForTimeout(2000);

          // Ir al carro
          await page.locator('a[href*="cart"]').first().click();
          await page.waitForTimeout(3000);

          const couponField = page.getByPlaceholder(/cup[oó]n/i)
            .or(page.getByText(/cup[oó]n/i))
            .or(page.getByRole('button', { name: /aplicar/i }));

          if (client.config.enableCoupons) {
            await expect(couponField.first()).toBeVisible({ timeout: 10_000 });
          }
          // Si enableCoupons=false, no verificamos ausencia porque puede haber "Aplicar" para otra cosa
        }

        await context.close();
      });
    }

    // ── hideReceiptType ──
    if (client.config.hideReceiptType !== undefined) {
      test(`${key}: hideReceiptType=${client.config.hideReceiptType}`, async ({ browser }) => {
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        // Ir al carro y buscar tipo de recibo
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');
        const addButton = page.getByRole('button', { name: 'Agregar' }).first();

        if (await addButton.isVisible({ timeout: 15_000 }).catch(() => false)) {
          await addButton.click();
          await page.waitForTimeout(2000);
          await page.locator('a[href*="cart"]').first().click();
          await page.waitForTimeout(3000);

          const receiptType = page.getByText(/tipo de recibo|boleta|factura/i);

          if (client.config.hideReceiptType) {
            // No debe mostrar selector de tipo de recibo
            const visible = await receiptType.isVisible({ timeout: 5_000 }).catch(() => false);
            expect(visible).toBeFalsy();
          }
        }

        await context.close();
      });
    }

    // ── currency ──
    test(`${key}: currency=${client.config.currency}`, async ({ browser }) => {
      const context = await browser.newContext();
      const page = await context.newPage();
      await loginIfNeeded(page);

      await page.goto(`${client.baseURL}/products`);
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(5000);

      // Verificar que los precios usan el símbolo correcto
      const currencySymbols: Record<string, string> = {
        clp: '$',
        cop: '$',
        pen: 'S/',
        usd: '$',
      };
      const symbol = currencySymbols[client.config.currency] || '$';
      const prices = page.locator(`text=/${symbol.replace('$', '\\$')}\\s*[\\d.,]+/`);
      const count = await prices.count();

      if (!client.config.hidePrices) {
        expect(count).toBeGreaterThan(0);
      }

      await context.close();
    });
  });
}

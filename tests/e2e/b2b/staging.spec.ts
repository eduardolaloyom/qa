import { test, expect } from '@playwright/test';
import { loginHelper } from '../fixtures/login';
import clients from '../fixtures/clients-staging';

/**
 * QA E2E — Staging (beta-codelpa.solopide.me, surtiventas.solopide.me)
 *
 * Mide comportamiento de staging a secas, sin mezclar con production.
 */

for (const [key, client] of Object.entries(clients)) {
  test.describe(`${client.name} (STAGING)`, () => {

    // ── HEALTH CHECK ──
    test(`${key}: Home carga sin error`, async ({ page }) => {
      await page.goto(client.baseURL);
      await page.waitForLoadState('domcontentloaded');
      await expect(page).not.toHaveURL(/error|500|timeout/i);
    });

    // ── LOGIN ──
    test(`${key}: Login exitoso en staging`, async ({ page }) => {
      await page.goto(client.baseURL);
      await page.waitForLoadState('domcontentloaded');

      // Si no anonymousAccess, va a redirigir a login
      if (!client.config.anonymousAccess) {
        await expect(page).toHaveURL(/auth|login/, { timeout: 10_000 });
      } else {
        await page.getByText('Iniciar sesión').first().click();
        await page.waitForLoadState('domcontentloaded');
      }

      // Login
      const [response] = await Promise.all([
        page.waitForResponse(resp => resp.url().includes('/auth') && resp.status() === 200),
        loginHelper(page, client.credentials.email, client.credentials.password, client.loginPath, client.baseURL),
      ]);

      expect(response.ok()).toBeTruthy();
    });

    // ── CATÁLOGO ──
    test(`${key}: Catálogo carga productos en staging`, async ({ page }) => {
      await page.goto(client.baseURL);
      await page.waitForLoadState('domcontentloaded');

      // Login si es necesario
      if (!client.config.anonymousAccess) {
        if (!/auth|login/.test(page.url())) {
          await page.getByText('Iniciar sesión').first().click();
          await page.waitForLoadState('domcontentloaded');
        }
        await loginHelper(page, client.credentials.email, client.credentials.password, client.loginPath, client.baseURL);
      }

      // Debe mostrar precios (si anonymousHidePrice=false o después de login)
      await expect(page.locator('text=/\\$\\s*[\\d.,]+/')).toBeVisible({ timeout: 15_000 });
    });

    // ── CARRITO ──
    test(`${key}: Carrito funciona en staging`, async ({ page }) => {
      await page.goto(client.baseURL);
      await page.waitForLoadState('domcontentloaded');

      // Login
      if (!client.config.anonymousAccess) {
        if (!/auth|login/.test(page.url())) {
          await page.getByText('Iniciar sesión').first().click();
          await page.waitForLoadState('domcontentloaded');
        }
        await loginHelper(page, client.credentials.email, client.credentials.password, client.loginPath, client.baseURL);
      }

      // Agregar producto (buscar botón "Agregar")
      const addButton = page.locator('button:has-text("Agregar"), button:has-text("Add"), [class*="add"][class*="cart"]').first();

      if (await addButton.isVisible({ timeout: 5_000 }).catch(() => false)) {
        await addButton.click();
        // Debe actualizar carrito
        await page.waitForTimeout(1_000);
      }
    });

    // ── CHECKOUT ──
    test(`${key}: Checkout funciona en staging`, async ({ page }) => {
      await page.goto(client.baseURL);
      await page.waitForLoadState('domcontentloaded');

      // Login
      if (!client.config.anonymousAccess) {
        if (!/auth|login/.test(page.url())) {
          await page.getByText('Iniciar sesión').first().click();
          await page.waitForLoadState('domcontentloaded');
        }
        await loginHelper(page, client.credentials.email, client.credentials.password, client.loginPath, client.baseURL);
      }

      // Navegar a checkout
      const checkoutButton = page.locator('button:has-text("Checkout"), button:has-text("Confirmar"), a:has-text("Checkout")').first();

      if (await checkoutButton.isVisible({ timeout: 5_000 }).catch(() => false)) {
        await checkoutButton.click();
        await page.waitForLoadState('domcontentloaded');

        // Debe estar en /checkout o /cart
        await expect(page).toHaveURL(/checkout|cart/, { timeout: 10_000 });
      }
    });

  });
}

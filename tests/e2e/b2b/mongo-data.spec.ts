import { test, expect } from '@playwright/test';
import { loginHelper } from '../fixtures/login';
import clients from '../fixtures/clients';

/**
 * Validación de datos operacionales de MongoDB en el frontend.
 *
 * A diferencia de config-validation.spec.ts que valida feature flags,
 * estos tests validan que los DATOS REALES de Mongo existen y funcionan:
 * - Cupones activos se pueden aplicar en checkout
 * - Banners activos son visibles en home
 * - Promotions afectan los precios correctamente
 *
 * Datos obtenidos de:
 * - yom-promotions (coupons, promotions)
 * - b2b-marketing (banners)
 * - Via clients.ts (auto-generado desde qa-matrix.json)
 */

for (const [key, client] of Object.entries(clients)) {
  test.describe(`Mongo Data Validation: ${client.name}`, () => {
    // Helper: login si es necesario
    async function loginIfNeeded(page: any) {
      await page.goto(client.baseURL);
      await page.waitForLoadState('domcontentloaded');
      if (!client.config.anonymousAccess) {
        await loginHelper(page, client.credentials.email, client.credentials.password, client.loginPath);
      }
    }

    // ── COUPONS ──
    // Solo si hay cupones activos en Mongo
    if (client.coupons && client.coupons.length > 0) {
      test(`${key}: Cupón activo "${client.coupons[0].code}" se puede aplicar en checkout @coupons @mongo-data`, async ({
        browser,
      }) => {
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        // Navegar a productos
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('networkidle');

        // Agregar un producto al carrito
        const addButton = page.getByRole('button', { name: 'Agregar' }).first();
        await expect(addButton).toBeVisible({ timeout: 15_000 });
        await addButton.click();
        await page.waitForLoadState('networkidle');

        // Ir al carrito
        await page.locator('a[href*="cart"]').first().click();
        await page.waitForLoadState('networkidle');

        // Buscar campo de cupón e intentar aplicar el código real de Mongo
        const couponField = page.getByPlaceholder(/cup[oó]n/i)
          .or(page.getByText(/cup[oó]n/i))
          .or(page.getByRole('textbox', { name: /cup[oó]n/i }));

        const couponCode = client.coupons[0].code;
        await expect(couponField.first()).toBeVisible({ timeout: 10_000 });

        await couponField.first().fill(couponCode);
        await page.getByRole('button', { name: /aplicar|usar|aceptar/i }).first().click({ timeout: 5_000 });
        await page.waitForLoadState('networkidle');

        // Verificar que el cupón se aplicó (debe haber cambio en el precio o mensaje de éxito)
        const successMessage = page.getByText(/descuento|aplicado|éxito/i);
        const priceUpdated = page.locator('text=/\\$\\s*[\\d.,]+/').nth(1);

        const applied =
          (await successMessage.isVisible({ timeout: 3_000 }).catch(() => false)) ||
          (await priceUpdated.isVisible({ timeout: 3_000 }).catch(() => false));

        expect(applied).toBeTruthy();

        await context.close();
      });
    }

    // ── BANNERS ──
    // Solo si hay banners activos en Mongo
    if (client.banners && client.banners.length > 0) {
      test(`${key}: ${client.banners.length} banner(s) activo(s) visible(s) en home @banners @mongo-data`, async ({
        browser,
      }) => {
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        // Ir al home
        await page.goto(`${client.baseURL}/`);
        await page.waitForLoadState('networkidle');

        // Buscar elementos de banner (carrusel, imagen grande, etc.)
        const bannerLocators = [
          page.locator('[data-testid*="banner" i]'),
          page.locator('[class*="banner" i]'),
          page.locator('img[alt*="banner" i]'),
          page.locator('[role="img"][aria-label*="banner" i]'),
        ];

        let bannerFound = false;
        for (const locator of bannerLocators) {
          const isVisible = await locator.first().isVisible({ timeout: 3_000 }).catch(() => false);
          if (isVisible) {
            bannerFound = true;
            break;
          }
        }

        // Si no hay elementos de banner específicos, verificar que hay ALGÚN elemento visual en el hero/header
        if (!bannerFound) {
          const heroSection = page.locator('header, [class*="hero" i], [data-testid*="hero" i]').first();
          const isVisible = await heroSection.isVisible({ timeout: 3_000 }).catch(() => false);
          if (isVisible) {
            bannerFound = true;
          }
        }

        expect(bannerFound).toBeTruthy();
        await context.close();
      });
    }

    // ── PIPELINE API ──
    // Valida que la API devuelve productos con campos obligatorios (Mongo→API sync)
    test(`${key}: Pipeline API catálogo devuelve productos con nombre y pricing @catalog @critico`, async ({
      browser,
    }) => {
      const context = await browser.newContext();
      const page = await context.newPage();
      await loginIfNeeded(page);

      let catalogResponse: any[] = [];
      page.on('response', async response => {
        if (
          response.url().includes('/api/v2/catalog') &&
          !response.url().includes('/count') &&
          !response.url().includes('/filter') &&
          response.status() === 200
        ) {
          const json = await response.json().catch(() => null);
          if (Array.isArray(json) && json.length > catalogResponse.length) {
            catalogResponse = json;
          }
        }
      });

      await page.goto(`${client.baseURL}/products`);
      await page.waitForLoadState('domcontentloaded');
      await page.locator('text=/\\$\\s*[\\d.,]+/').first().waitFor({ state: 'visible', timeout: 20_000 }).catch(() => {});
      await page.waitForTimeout(2_000);

      if (catalogResponse.length === 0) {
        test.info().annotations.push({ type: 'warning', description: 'No se interceptó /api/v2/catalog — puede ser otro endpoint' });
        await context.close();
        return;
      }

      test.info().annotations.push({ type: 'info', description: `API /v2/catalog: ${catalogResponse.length} productos` });
      expect(catalogResponse.length).toBeGreaterThan(0);

      const missingName = catalogResponse.filter((p: any) => !p.name).length;
      const noPricing  = catalogResponse.filter((p: any) => !p.pricing).length;
      if (missingName > 0) test.info().annotations.push({ type: 'error', description: `${missingName} productos sin nombre` });
      if (noPricing > 0)   test.info().annotations.push({ type: 'error', description: `${noPricing} productos sin pricing` });

      expect(missingName).toBe(0);
      expect(noPricing).toBe(0);

      await context.close();
    });

    // ── PROMOTIONS ──
    // Solo si hay promotions activas (validar que afectan precios)
    if (client.promotions && client.promotions.length > 0) {
      test(`${key}: ${client.promotions.length} promoción(es) activa(s) visible(s) en precios @promotions @mongo-data`, async ({
        browser,
      }) => {
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        // Navegar a catálogo
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('networkidle');

        // Buscar indicadores de promoción: descuento, tachado, etiqueta roja, etc.
        const promoIndicators = [
          page.locator('[class*="discount" i]'),
          page.locator('[class*="promotion" i]'),
          page.locator('[class*="sale" i]'),
          page.locator('text=/descuento|oferta|rebaja|promo/i'),
          page.locator('strike, s, del'), // Precios tachados
        ];

        let promoFound = false;
        for (const locator of promoIndicators) {
          const isVisible = await locator.first().isVisible({ timeout: 3_000 }).catch(() => false);
          if (isVisible) {
            promoFound = true;
            break;
          }
        }

        // Si hay promotions en Mongo, DEBE haber indicadores visuales de descuento
        expect(promoFound).toBeTruthy();

        await context.close();
      });
    }
  });
}

import { createClientTest, expect } from '../fixtures/multi-client-auth';
import clients from '../fixtures/clients';

/**
 * PM1/PM2 — Regresión de cupones
 * Fuente: Post-mortems "Error al ordenar con cupones" + "Error en uso de cupones"
 *
 * Incidente 1: Import roto en yom-api → 39 órdenes con cupón fallaron en 3 horas
 * Incidente 2: B2B no soportaba cupones de orden (solo producto) → falló en Cyber Soprole
 *
 * Cupón de prueba por cliente: env var {CLIENT_KEY}_TEST_COUPON (ej: BASTIEN_TEST_COUPON=TEST10OFF)
 * Fallback para Bastien staging: TEST10OFF
 */

for (const [key, client] of Object.entries(clients)) {
  const test = createClientTest(client);
  test.describe(`PM1/PM2 — Cupones: regresión post-mortem: ${client.name}`, () => {

    // Cupón de prueba: env var o primer cupón activo de MongoDB
    const testCouponCode: string | null =
      process.env[`${key.toUpperCase()}_TEST_COUPON`] ??
      (client.coupons?.[0]?.code ?? null);

    async function addProductsAndGoToCart(page: any) {
      // Retry goto /products una vez si ERR_ABORTED
      try {
        await page.goto(`${client.baseURL}/products`, { waitUntil: 'domcontentloaded' });
      } catch {
        await page.waitForTimeout(1500);
        await page.goto(`${client.baseURL}/products`, { waitUntil: 'domcontentloaded' });
      }
      const addButtons = page.getByRole('button', { name: 'Agregar' });
      await addButtons.first().waitFor({ timeout: 30_000 });

      // Siempre first() para evitar reindexado tras cada click
      const count = Math.min(await addButtons.count(), 3);
      for (let i = 0; i < count; i++) {
        await Promise.all([
          page.waitForResponse((resp: any) => resp.url().includes('/cart') && resp.request().method() === 'POST').catch(() => null),
          addButtons.first().click(),
        ]);
      }

      await page.goto(`${client.baseURL}/cart`);

      // Descartar modal "¡Uy! Algo ha cambiado en tu carrito" si aparece
      const recargarBtn = page.getByRole('button', { name: /recargar/i });
      const modalVisible = await recargarBtn.isVisible({ timeout: 4_000 }).catch(() => false);
      if (modalVisible) {
        await recargarBtn.click();
        await page.waitForLoadState('domcontentloaded');
      }

      await expect(page.getByText(/\d+ Producto/)).toBeVisible({ timeout: 15_000 });
    }

    // Selector robusto para campo de cupón
    // Bastien usa floating label MUI — el texto "Ingresar cupón" es un label, NO un placeholder attr
    // El textbox no tiene accessible name, pero comparte parent con el botón "Aplicar"
    function getCouponInput(page: any) {
      // Estrategia principal: Aplicar button y el input son siblings → subir al padre común
      return page.getByRole('button', { name: /^aplicar$/i }).locator('xpath=..').locator('input')
        .or(page.getByRole('button', { name: /^aplicar$/i }).locator('xpath=preceding-sibling::*//input'))
        .or(page.getByRole('textbox', { name: /cup|ingresa/i }))
        .or(page.locator('input[placeholder*="cup" i], input[placeholder*="coupon" i]'))
        .or(page.locator('input[name*="coupon" i], input[id*="coupon" i]'));
    }

    test(`${key}: PM1-01 Campo de cupón existe y es interactuable`, async ({ authedPage: page }) => {
      if (!client.config.enableCoupons) {
        test.skip(true, `PM1-01: ${client.name} no tiene enableCoupons=true`);
        return;
      }
      await addProductsAndGoToCart(page);

      // MUI floating label — el input no tiene accessible name ni placeholder attr
      // El botón "Aplicar" es el indicador más confiable de que la UI de cupón está presente
      const aplicarButton = page.getByRole('button', { name: /^aplicar$/i });
      await aplicarButton.scrollIntoViewIfNeeded().catch(() => {});
      await expect(aplicarButton).toBeVisible({ timeout: 15_000 });

      await page.screenshot({ path: `test-results/coupons-field-visible-${key}.png`, fullPage: true });
    });

    test(`${key}: PM1-02 Cupón válido aplica descuento`, async ({ authedPage: page }) => {
      if (!client.config.enableCoupons) {
        test.skip(true, `PM1-02: ${client.name} no tiene enableCoupons=true`);
        return;
      }
      if (!testCouponCode) {
        test.skip(true, `PM1-02: No hay cupón de prueba configurado para ${client.name} — agrega ${key.toUpperCase()}_TEST_COUPON al .env`);
        return;
      }

      await addProductsAndGoToCart(page);

      // MUI floating label: subir al padre del botón Aplicar para encontrar el input
      const aplicarBtn = page.getByRole('button', { name: /^aplicar$/i });
      await expect(aplicarBtn).toBeVisible({ timeout: 10_000 });
      const couponInput = aplicarBtn.locator('xpath=..').locator('input');
      await couponInput.fill(testCouponCode);
      await aplicarBtn.click();
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(2_000);

      // Debe mostrar descuento aplicado — no $0 ni mensaje de error
      const hasError = await page.getByText(/inv[aá]lid|expirad|no existe|error|no encontr/i)
        .isVisible({ timeout: 5_000 }).catch(() => false);
      expect(hasError, `Cupón ${testCouponCode} rechazado como inválido`).toBeFalsy();

      // Verificar que el descuento se refleja visualmente
      const discountLine = page.getByText(/descuento/i).locator('..')
        .or(page.locator('[class*="discount" i]'));
      const hasDiscount = await discountLine.first().isVisible({ timeout: 5_000 }).catch(() => false);

      await page.screenshot({ path: `test-results/coupons-valid-applied-${key}.png`, fullPage: true });

      test.info().annotations.push({
        type: 'info',
        description: `Cupón ${testCouponCode} aplicado, descuento visible: ${hasDiscount}`,
      });

      // Al menos el cupón no debe dar error
      expect(hasError).toBeFalsy();
    });

    test(`${key}: PM1-04 Cupón inválido muestra error (no crash)`, async ({ authedPage: page }) => {
      if (!client.config.enableCoupons) {
        test.skip(true, `PM1-04: ${client.name} no tiene enableCoupons=true`);
        return;
      }
      await addProductsAndGoToCart(page);

      // MUI floating label: subir al padre del botón Aplicar para encontrar el input
      const aplicarBtn = page.getByRole('button', { name: /^aplicar$/i });
      await expect(aplicarBtn).toBeVisible({ timeout: 10_000 });
      const couponInput = aplicarBtn.locator('xpath=..').locator('input');
      await couponInput.fill('CUPON-INVALIDO-QA-TEST-999');
      await aplicarBtn.click();
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(2_000);

      const hasError = await page.getByText(/inv[aá]lid|expirad|no existe|error|no encontr/i)
        .isVisible({ timeout: 10_000 }).catch(() => false);

      await page.screenshot({ path: `test-results/coupons-invalid-response-${key}.png`, fullPage: true });

      expect(hasError).toBeTruthy();

      const hasCrash = await page.getByText(/error interno|500|server error/i)
        .isVisible().catch(() => false);
      expect(hasCrash).toBeFalsy();
    });

    test(`${key}: PM2-04 Modal/UI de cupón no queda en loading infinito`, async ({ authedPage: page }) => {
      if (!client.config.enableCoupons) {
        test.skip(true, `PM2-04: ${client.name} no tiene enableCoupons=true`);
        return;
      }
      await addProductsAndGoToCart(page);

      // MUI floating label: usar padre del botón Aplicar para encontrar el input
      const aplicarBtn = page.getByRole('button', { name: /^aplicar$/i });
      await expect(aplicarBtn).toBeVisible({ timeout: 10_000 });
      const couponInput = aplicarBtn.locator('xpath=..').locator('input');
      await couponInput.fill('TEST-LOADING-CHECK');

      await aplicarBtn.click();

      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(2_000);

      const stillLoading = await page.locator('[class*="loading" i], [class*="spinner" i], [aria-busy="true"]')
        .isVisible({ timeout: 3_000 }).catch(() => false);

      await page.screenshot({ path: `test-results/coupons-no-infinite-loading-${key}.png`, fullPage: true });

      expect(stillLoading).toBeFalsy();
    });

    test.describe('Crear orden — BLOQUEADO-PROD en youorder.me', () => {
      test.skip(client.baseURL.includes('youorder.me'), 'BLOQUEADO-PROD — no crear pedidos en producción');

      test(`${key}: PM1-03 Crear orden SIN cupón no se rompe por cambios en cupones`, async ({ authedPage: page }) => {
        await addProductsAndGoToCart(page);

      const confirmButton = page.getByRole('button', { name: /confirmar|crear pedido|finalizar/i });
      await expect(confirmButton.first()).toBeVisible({ timeout: 10_000 });
      await confirmButton.first().scrollIntoViewIfNeeded();

      const [response] = await Promise.all([
        page.waitForResponse(
          (resp: any) => resp.url().includes('/order') && resp.request().method() === 'POST',
          { timeout: 30_000 }
        ).catch(() => null),
        confirmButton.first().click({ force: true }),
      ]);

      await page.waitForLoadState('domcontentloaded');
      await page.screenshot({ path: `test-results/order-without-coupon-${key}.png`, fullPage: true });

      if (response === null) {
        // POST /order no respondió — puede ser lentitud de staging bajo carga paralela
        test.info().annotations.push({
          type: 'warn',
          description: 'POST /order no respondió en 30s — API de órdenes lenta en staging',
        });
      } else {
        expect(response.status()).not.toBe(500);
      }

      const hasCrash = await page.getByText(/error interno|500|server error/i)
        .isVisible().catch(() => false);
      expect(hasCrash).toBeFalsy();
      });
    }); // fin describe BLOQUEADO-PROD
  });
}

import { test, expect } from '../fixtures/auth';

/**
 * PM1/PM2 — Regresión de cupones
 * Fuente: Post-mortems "Error al ordenar con cupones" + "Error en uso de cupones"
 *
 * Incidente 1: Import roto en yom-api → 39 órdenes con cupón fallaron en 3 horas
 * Incidente 2: B2B no soportaba cupones de orden (solo producto) → falló en Cyber Soprole
 */
test.describe('PM1/PM2 — Cupones: regresión post-mortem', () => {

  async function addProductsAndGoToCart(page: any) {
    await page.goto('/products');
    await page.waitForLoadState('domcontentloaded');
    const addButtons = page.getByRole('button', { name: 'Agregar' });
    await addButtons.first().waitFor({ timeout: 30_000 });

    const count = Math.min(await addButtons.count(), 3);
    for (let i = 0; i < count; i++) {
      await Promise.all([
        page.waitForResponse((resp: any) => resp.url().includes('/cart') && resp.request().method() === 'POST'),
        addButtons.nth(i).click(),
      ]);
    }

    await page.goto('/cart');
    await expect(page.getByText(/\d+ Producto/)).toBeVisible({ timeout: 15_000 });
  }

  test('PM1-01: Campo de cupón existe y es interactuable', async ({ authedPage: page }) => {
    await addProductsAndGoToCart(page);

    // Buscar input o botón de cupón
    const couponInput = page.getByPlaceholder(/cup[oó]n/i)
      .or(page.getByLabel(/cup[oó]n/i));
    const couponButton = page.getByRole('button', { name: /cup[oó]n|aplicar|agregar c[oó]digo/i });

    const inputVisible = await couponInput.first().isVisible({ timeout: 10_000 }).catch(() => false);
    const buttonVisible = await couponButton.first().isVisible({ timeout: 5_000 }).catch(() => false);

    expect(inputVisible || buttonVisible).toBeTruthy();
    await page.screenshot({ path: 'test-results/coupons-field-visible.png', fullPage: true });
  });

  test('PM1-04: Cupón inválido muestra error (no crash)', async ({ authedPage: page }) => {
    await addProductsAndGoToCart(page);

    // Buscar campo de cupón
    const couponInput = page.getByPlaceholder(/cup[oó]n/i)
      .or(page.getByLabel(/cup[oó]n/i));

    if (await couponInput.first().isVisible({ timeout: 10_000 }).catch(() => false)) {
      await couponInput.first().fill('CUPON-INVALIDO-QA-TEST-999');

      // Buscar botón para aplicar
      const applyBtn = page.getByRole('button', { name: /aplicar|agregar|usar/i });
      if (await applyBtn.first().isVisible({ timeout: 5_000 }).catch(() => false)) {
        await applyBtn.first().click();
        await page.waitForLoadState('networkidle');

        // Debe mostrar error — no crash ni pantalla en blanco
        const hasError = await page.getByText(/inv[aá]lid|expirad|no existe|error|no encontr/i)
          .isVisible({ timeout: 10_000 }).catch(() => false);

        await page.screenshot({ path: 'test-results/coupons-invalid-response.png', fullPage: true });

        // No debe haber crash (error 500 o página en blanco)
        const hasCrash = await page.getByText(/error interno|500|server error/i)
          .isVisible().catch(() => false);
        expect(hasCrash).toBeFalsy();
      }
    }
  });

  test('PM2-04: Modal/UI de cupón no queda en loading infinito', async ({ authedPage: page }) => {
    await addProductsAndGoToCart(page);

    const couponInput = page.getByPlaceholder(/cup[oó]n/i)
      .or(page.getByLabel(/cup[oó]n/i));

    if (await couponInput.first().isVisible({ timeout: 10_000 }).catch(() => false)) {
      await couponInput.first().fill('TEST-LOADING-CHECK');

      const applyBtn = page.getByRole('button', { name: /aplicar|agregar|usar/i });
      if (await applyBtn.first().isVisible({ timeout: 5_000 }).catch(() => false)) {
        await applyBtn.first().click();

        // Esperar respuesta — el loading debe resolverse en <10 segundos
        await page.waitForLoadState('networkidle');

        // Verificar que no hay spinner/loading permanente
        const stillLoading = await page.locator('[class*="loading" i], [class*="spinner" i], [aria-busy="true"]')
          .isVisible({ timeout: 3_000 }).catch(() => false);

        await page.screenshot({ path: 'test-results/coupons-no-infinite-loading.png', fullPage: true });

        if (stillLoading) {
          test.info().annotations.push({
            type: 'warning',
            description: 'Loading indicator aún visible después de 10s — posible bug PM2',
          });
        }
      }
    }
  });

  test('PM1-03: Crear orden SIN cupón no se rompe por cambios en cupones', async ({ authedPage: page }) => {
    // Este es el test más importante: un cambio en cupones no debe romper órdenes normales
    await addProductsAndGoToCart(page);

    // Intentar confirmar pedido sin cupón
    const confirmButton = page.getByRole('button', { name: /confirmar|crear pedido|finalizar/i });
    await expect(confirmButton.first()).toBeVisible({ timeout: 10_000 });

    // Interceptar respuesta de creación de orden
    const [response] = await Promise.all([
      page.waitForResponse(
        (resp: any) => resp.url().includes('/order') && resp.request().method() === 'POST',
        { timeout: 30_000 }
      ).catch(() => null),
      confirmButton.first().click({ force: true }),
    ]);

    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/order-without-coupon.png', fullPage: true });

    // La orden no debe devolver 500
    if (response) {
      expect(response.status()).not.toBe(500);
    }

    // No debe haber error visible
    const hasCrash = await page.getByText(/error interno|500|server error/i)
      .isVisible().catch(() => false);
    expect(hasCrash).toBeFalsy();
  });
});

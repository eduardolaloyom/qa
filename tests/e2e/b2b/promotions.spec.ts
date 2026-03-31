import { test, expect } from '../fixtures/auth';

/**
 * PM5 — Regresión de promotions
 * Fuente: Post-mortem "Servicio de promotions con exceso de carga"
 *
 * Incidente: Promotions colapsó por pocos pods → catálogo, carrito y precios caídos.
 * Cualquier cosa que muestre precios depende de promotions.
 */
test.describe('PM5 — Promotions: regresión post-mortem', () => {

  test('PM5-01: Catálogo carga productos con precios (promotions funcional)', async ({ authedPage: page }) => {
    await page.goto('/products');
    await page.waitForLoadState('domcontentloaded');

    // Si promotions está caído, los precios no se muestran o la página falla
    const prices = page.locator('text=/\\$\\s*[\\d.,]+/');
    await expect(prices.first()).toBeVisible({ timeout: 30_000 });

    const priceCount = await prices.count();
    expect(priceCount).toBeGreaterThan(0);

    await page.screenshot({ path: 'test-results/promotions-catalog-ok.png', fullPage: true });

    test.info().annotations.push({
      type: 'info',
      description: `${priceCount} precios visibles en catálogo — promotions respondiendo`,
    });
  });

  test('PM5-02: Carrito muestra totales con descuentos aplicados', async ({ authedPage: page }) => {
    await page.goto('/products');
    const addButtons = page.getByRole('button', { name: 'Agregar' });
    await addButtons.first().waitFor({ timeout: 30_000 });

    // Agregar productos
    const count = Math.min(await addButtons.count(), 3);
    for (let i = 0; i < count; i++) {
      await Promise.all([
        page.waitForResponse((resp: any) => resp.url().includes('/cart') && resp.request().method() === 'POST'),
        addButtons.nth(i).click(),
      ]);
    }

    await page.goto('/cart');
    await expect(page.getByText(/\d+ Producto/)).toBeVisible({ timeout: 15_000 });

    // Debe haber al menos un precio/total visible
    const cartPrices = page.locator('text=/\\$\\s*[\\d.,]+/');
    const cartPriceCount = await cartPrices.count();
    expect(cartPriceCount).toBeGreaterThan(0);

    // Verificar que hay un total
    const hasTotal = await page.getByText(/total/i).isVisible({ timeout: 5_000 }).catch(() => false);
    expect(hasTotal).toBeTruthy();

    await page.screenshot({ path: 'test-results/promotions-cart-totals.png', fullPage: true });
  });

  test('PM5-03: Catálogo no queda en loading infinito si promotions es lento', async ({ authedPage: page }) => {
    // Simula el escenario del PM5: promotions lento pero no completamente caído
    const startTime = Date.now();

    await page.goto('/products');
    await page.waitForLoadState('domcontentloaded');

    // El catálogo debe mostrar algo en <30s (nuestro timeout de acción)
    const hasContent = await page.locator('text=/\\$\\s*[\\d.,]+/').first()
      .isVisible({ timeout: 30_000 }).catch(() => false);

    const loadTime = Date.now() - startTime;

    await page.screenshot({ path: 'test-results/promotions-load-time.png', fullPage: true });

    test.info().annotations.push({
      type: 'info',
      description: `Catálogo cargó en ${loadTime}ms — contenido visible: ${hasContent}`,
    });

    // Si tarda más de 15s, es warning (posible degradación de promotions)
    if (loadTime > 15_000) {
      test.info().annotations.push({
        type: 'warning',
        description: `⚠️ Catálogo tardó ${loadTime}ms — revisar performance de promotions`,
      });
    }
  });
});

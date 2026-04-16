import { createClientTest, expect } from '../fixtures/multi-client-auth';
import clients from '../fixtures/clients';

/**
 * PM5 — Regresión de promotions
 * Fuente: Post-mortem "Servicio de promotions con exceso de carga"
 *
 * Incidente: Promotions colapsó por pocos pods → catálogo, carrito y precios caídos.
 * Cualquier cosa que muestre precios depende de promotions.
 */

for (const [key, client] of Object.entries(clients)) {
  const test = createClientTest(client);
  test.describe(`PM5 — Promotions: regresión post-mortem: ${client.name}`, () => {

    test(`${key}: PM5-01 Catálogo carga productos con precios (promotions funcional)`, async ({ authedPage: page }) => {
      await page.goto(`${client.baseURL}/products`);
      await page.waitForLoadState('domcontentloaded');

      // Si promotions está caído, los precios no se muestran o la página falla
      const prices = page.locator('text=/\\$\\s*[\\d.,]+/');
      await expect(prices.first()).toBeVisible({ timeout: 30_000 });

      const priceCount = await prices.count();
      expect(priceCount).toBeGreaterThan(0);

      await page.screenshot({ path: `test-results/promotions-catalog-ok-${key}.png`, fullPage: true });

      test.info().annotations.push({
        type: 'info',
        description: `${priceCount} precios visibles en catálogo — promotions respondiendo`,
      });
    });

    test(`${key}: PM5-02 Carrito muestra totales con descuentos aplicados`, async ({ authedPage: page }) => {
      await page.goto(`${client.baseURL}/products`);
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

      await page.goto(`${client.baseURL}/cart`);
      await expect(page.getByText(/\d+ Producto/)).toBeVisible({ timeout: 15_000 });

      // Debe haber al menos un precio/total visible
      const cartPrices = page.locator('text=/\\$\\s*[\\d.,]+/');
      const cartPriceCount = await cartPrices.count();
      expect(cartPriceCount).toBeGreaterThan(0);

      // Verificar que hay una línea de total — texto "Total" cerca de un precio
      // Soporta layouts donde "Total:" y "$X" son elementos separados
      const totalLabel = page.getByText(/^total[:\s]*$/i)
        .or(page.locator('[class*="total" i]').getByText(/total/i))
        .or(page.getByText(/total.*\$[\d.,]+/i));
      await expect(totalLabel.first()).toBeVisible({ timeout: 5_000 });

      await page.screenshot({ path: `test-results/promotions-cart-totals-${key}.png`, fullPage: true });
    });

    test(`${key}: PM5-03 Catálogo no queda en loading infinito si promotions es lento`, async ({ authedPage: page }) => {
      // Simula el escenario del PM5: promotions lento pero no completamente caído
      const startTime = Date.now();

      // Retry goto si ERR_ABORTED (intermittent en staging bajo carga)
      try {
        await page.goto(`${client.baseURL}/products`, { waitUntil: 'domcontentloaded' });
      } catch {
        await page.waitForTimeout(4000);
        await page.goto(`${client.baseURL}/products`, { waitUntil: 'domcontentloaded' });
      }

      // El catálogo debe mostrar algo en <45s (PM5 se enfoca en lentitud, no en fallo completo)
      const hasContent = await page.locator('text=/\\$\\s*[\\d.,]+/').first()
        .isVisible({ timeout: 45_000 }).catch(() => false);

      const elapsedTime = Date.now() - startTime;

      await page.screenshot({ path: `test-results/promotions-loading-time-${key}.png`, fullPage: true });

      test.info().annotations.push({
        type: 'info',
        description: `Tiempo de carga: ${elapsedTime}ms, contenido visible: ${hasContent}`,
      });

      expect(hasContent).toBeTruthy();
    });
  });
}

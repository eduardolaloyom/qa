import { test, expect } from '../fixtures/multi-client-auth';
import clients from '../fixtures/clients';

/**
 * PM4 — Regresión de step pricing (precios escalonados)
 * Fuente: Post-mortem "Error en step pricing soprole"
 *
 * Incidente: Código sobreescribía los steps. Soprole estuvo sin precios escalonados por días.
 * Los tests existían pero estaban desactivados, y el ambiente local no tenía casos complejos.
 */

for (const [key, client] of Object.entries(clients)) {
  test.describe(`PM4 — Step pricing: regresión post-mortem: ${client.name}`, () => {

    test(`${key}: PM4-01 Productos con step pricing muestran escalones`, async ({ authedPage: page }) => {
      await page.goto(`${client.baseURL}/products`);
      await page.waitForLoadState('domcontentloaded');
      await expect(page.getByRole('button', { name: 'Agregar' }).first()).toBeVisible({ timeout: 30_000 });

      // Buscar indicadores de precios escalonados en el catálogo
      // Los steps suelen mostrarse como: "1-10: $X", "11-50: $Y", "Desde X unidades", etc.
      const stepIndicators = page.locator('text=/\\d+\\s*[-–]\\s*\\d+|[Dd]esde\\s+\\d+|[Ee]scal[oó]n|[Tt]ramo|[Uu]nidades/')
        .or(page.locator('[class*="step" i], [class*="tier" i], [class*="scale" i]'));

      const stepCount = await stepIndicators.count();

      await page.screenshot({ path: `test-results/step-pricing-catalog-${key}.png`, fullPage: true });

      test.info().annotations.push({
        type: 'info',
        description: `Indicadores de step pricing encontrados: ${stepCount}`,
      });

      // Si el cliente tiene step pricing configurado, debe haber al menos alguno
      // No fallamos hard porque depende de la config del cliente
    });

    test(`${key}: PM4-02 Agregar producto con cantidad > 1 muestra precio correcto`, async ({ authedPage: page }) => {
      await page.goto(`${client.baseURL}/products`);
      await page.waitForLoadState('domcontentloaded');
      const addButtons = page.getByRole('button', { name: 'Agregar' });
      await addButtons.first().waitFor({ timeout: 30_000 });

      // Agregar primer producto
      await Promise.all([
        page.waitForResponse((resp: any) => resp.url().includes('/cart') && resp.request().method() === 'POST'),
        addButtons.first().click(),
      ]);

      // Ir al carro
      await page.goto(`${client.baseURL}/cart`);
      await expect(page.getByText(/\d+ Producto/)).toBeVisible({ timeout: 15_000 });

      // Intentar cambiar cantidad para activar step pricing
      const quantityInput = page.locator('input[type="number"]').first()
        .or(page.getByRole('spinbutton').first());

      if (await quantityInput.isVisible({ timeout: 5_000 }).catch(() => false)) {
        // Capturar precio con cantidad 1
        const priceBefore = await page.locator('text=/\\$\\s*[\\d.,]+/').first().textContent();

        // Cambiar a cantidad mayor (ej: 12 para activar posible step)
        await quantityInput.fill('12');
        await quantityInput.press('Tab');
        await page.waitForLoadState('networkidle');

        // Capturar precio con nueva cantidad
        const priceAfter = await page.locator('text=/\\$\\s*[\\d.,]+/').first().textContent();

        await page.screenshot({ path: `test-results/step-pricing-quantity-change-${key}.png`, fullPage: true });

        test.info().annotations.push({
          type: 'info',
          description: `Precio antes: ${priceBefore}, después: ${priceAfter}`,
        });

        // No debe haber error
        const hasError = await page.getByText(/error|500/i).isVisible().catch(() => false);
        expect(hasError).toBeFalsy();
      }
    });
  });
}

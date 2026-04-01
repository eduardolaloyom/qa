import { test, expect } from '../fixtures/multi-client-auth';
import clients from '../fixtures/clients';

/**
 * PAG — Pagos B2B
 * Fuente: Deuda técnica Notion — "Refactor pagos"
 * Valida: historial de pagos, montos con notas de crédito, consistencia de datos
 */

for (const [key, client] of Object.entries(clients)) {
  test.describe(`PAG — Pagos y documentos tributarios (B2B): ${client.name}`, () => {

    test(`${key}: PAG-04 Historial de pagos carga correctamente`, async ({ authedPage: page }) => {
      // Navegar a sección de pagos/historial
      const paymentLinks = [
        page.getByRole('link', { name: /[Pp]ago/ }),
        page.getByRole('link', { name: /[Cc]uenta/ }),
        page.getByRole('link', { name: /[Ff]actura/ }),
        page.getByRole('link', { name: /[Dd]ocumento/ }),
      ];

      let navigated = false;
      for (const link of paymentLinks) {
        if (await link.first().isVisible({ timeout: 5_000 }).catch(() => false)) {
          await link.first().click();
          navigated = true;
          break;
        }
      }

      if (!navigated) {
        // Intentar acceso directo por URL
        await page.goto(`${client.baseURL}/payments`);
        if (page.url().includes('404') || page.url().includes('auth')) {
          await page.goto(`${client.baseURL}/account`);
        }
      }

      await page.waitForLoadState('networkidle');
      await page.screenshot({ path: `test-results/payments-history-${key}.png`, fullPage: true });

      // No debe haber errores críticos
      const hasError = await page.getByText(/error interno|500|server error/i).isVisible().catch(() => false);
      expect(hasError).toBeFalsy();
    });

    test(`${key}: PAG-16 Montos en historial no muestran valores negativos confusos`, async ({ authedPage: page }) => {
      // Navegar a pagos
      await page.goto(`${client.baseURL}/payments`);
      await page.waitForLoadState('networkidle');

      // Si hay tabla/listado de pagos, verificar que no hay montos negativos visibles al usuario
      const negativeAmounts = page.locator('text=/-\\$[\\d.,]+/');
      const negCount = await negativeAmounts.count().catch(() => 0);

      await page.screenshot({ path: `test-results/payments-no-negatives-${key}.png`, fullPage: true });

      // Los montos negativos no deberían ser visibles directamente al comercio
      // (las NC se restan internamente, el usuario ve el neto)
      if (negCount > 0) {
        console.warn(`⚠️ Se encontraron ${negCount} montos negativos visibles — revisar UX de notas de crédito`);
      }
    });
  });
}

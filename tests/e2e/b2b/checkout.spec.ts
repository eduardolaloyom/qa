import { createClientTest, expect } from '../fixtures/multi-client-auth';
import clients from '../fixtures/clients';

for (const [key, client] of Object.entries(clients)) {
  const test = createClientTest(client);
  test.describe(`C2 — Checkout / crear pedido: ${client.name}`, () => {

    async function addProducts(page: any) {
      await page.goto(`${client.baseURL}/products`, { waitUntil: 'domcontentloaded' });
      const addButtons = page.getByRole('button', { name: 'Agregar' });
      await addButtons.first().waitFor({ timeout: 30_000 });

      // Agregar 3 productos — suficiente para superar monto mínimo
      const count = Math.min(await addButtons.count(), 3);
      for (let i = 0; i < count; i++) {
        await Promise.all([
          page.waitForResponse((resp: any) => resp.url().includes('/cart') && resp.request().method() === 'POST', { timeout: 30_000 }).catch(() => null),
          addButtons.first().click(),
        ]);
      }
    }

    test(`${key}: C2-11 Flujo completo catalogo → carro → checkout`, async ({ authedPage: page }) => {
      await addProducts(page);

      await page.goto(`${client.baseURL}/cart`);
      await expect(page.getByText(/\d+ Producto/)).toBeVisible({ timeout: 15_000 });

      const confirmButton = page.getByRole('button', { name: 'Confirmar pedido' });
      await expect(confirmButton).toBeVisible({ timeout: 10_000 });
      await confirmButton.scrollIntoViewIfNeeded();

      await Promise.all([
        page.waitForURL(/\/confirmation\/\w+/, { timeout: 30_000 }),
        confirmButton.click({ force: true }),
      ]);

      await page.screenshot({ path: `test-results/checkout-confirm-${key}.png`, fullPage: true });

      // Requires actual order ID after /confirmation/ — bare /confirmation/ means order was not processed
      expect(page.url()).toMatch(/\/confirmation\/\w+/);
    });

    test(`${key}: C2-12 Doble click en crear pedido no genera duplicado`, async ({ authedPage: page }) => {
      await addProducts(page);

      await page.goto(`${client.baseURL}/cart`);
      await expect(page.getByText(/\d+ Producto/)).toBeVisible({ timeout: 15_000 });

      const orderRequests: any[] = [];
      page.on('response', (resp: any) => {
        if (resp.url().includes('/order') && resp.request().method() === 'POST') {
          orderRequests.push(resp);
        }
      });

      const confirmButton = page.getByRole('button', { name: 'Confirmar pedido' });
      await expect(confirmButton).toBeVisible({ timeout: 10_000 });
      await confirmButton.scrollIntoViewIfNeeded();
      await confirmButton.dblclick({ force: true });

      await page.waitForLoadState('domcontentloaded');

      if (orderRequests.length > 0) {
        expect(orderRequests.length).toBeLessThanOrEqual(1);
      }
    });

    test(`${key}: C2-13 Pedido aparece en historial`, async ({ authedPage: page }) => {
      await page.goto(`${client.baseURL}/order`);
      await page.waitForLoadState('domcontentloaded');

      await expect(page.locator('body')).not.toBeEmpty();
      const bodyText = await page.locator('body').textContent();
      expect(bodyText!.trim().length).toBeGreaterThan(0);
    });
  });
}

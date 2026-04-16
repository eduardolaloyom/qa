import { createClientTest, expect } from '../fixtures/multi-client-auth';
import clients from '../fixtures/clients';

for (const [key, client] of Object.entries(clients)) {
  const test = createClientTest(client);

  test.describe(`Pedidos: ${client.name}`, () => {

    test(`${key}: Historial de pedidos carga @orders @funcional`, async ({ authedPage: page }) => {
      await page.goto(`${client.baseURL}/orders`);
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(3_000);
      const hasOrders = await page.locator('table, [class*="order" i]').first().isVisible({ timeout: 10_000 }).catch(() => false);
      const hasEmpty = await page.getByText(/no hay pedidos|sin pedidos/i).isVisible({ timeout: 5_000 }).catch(() => false);
      expect(hasOrders || hasEmpty).toBeTruthy();
    });

    test(`${key}: Estados de pedido son válidos (no "No disponible") @orders @funcional`, async ({ authedPage: page }) => {
      await page.goto(`${client.baseURL}/orders`);
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(3_000);
      const count = await page.getByText('No disponible').count();
      if (count > 0) {
        test.info().annotations.push({ type: 'warning', description: `${count} pedidos con estado "No disponible"` });
      }
      expect(count).toBe(0);
    });

  });
}

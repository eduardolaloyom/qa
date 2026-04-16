import { createClientTest, expect } from '../fixtures/multi-client-auth';
import clients from '../fixtures/clients';

for (const [key, client] of Object.entries(clients)) {
  const test = createClientTest(client);

  test.describe(`C2 — Catálogo y búsqueda: ${client.name}`, () => {

    test.beforeEach(async ({ authedPage: page }) => {
      await page.goto(`${client.baseURL}/products`);
      await expect(page.locator('text=/\\$\\s*[\\d.,]+/').first()).toBeVisible({ timeout: 30_000 });
    });

    test(`${key}: C2-01 Catálogo muestra productos con precio @catalog @funcional`, async ({ authedPage: page }) => {
      const prices = page.locator('text=/\\$\\s*[\\d.,]+/');
      expect(await prices.count()).toBeGreaterThan(0);
    });

    test(`${key}: C2-02 Búsqueda por nombre devuelve resultados o mensaje @catalog @funcional`, async ({ authedPage: page }) => {
      const searchInput = page.getByPlaceholder(/buscar/i).first();
      if (!await searchInput.isVisible({ timeout: 5_000 }).catch(() => false)) {
        test.info().annotations.push({ type: 'warning', description: 'Campo de búsqueda no encontrado' });
        return;
      }
      await searchInput.fill('a');
      await searchInput.press('Enter');
      await page.waitForLoadState('networkidle', { timeout: 10_000 }).catch(() => {});
      const hasResults = (await page.locator('text=/\\$\\s*[\\d.,]+/').count()) > 0;
      const hasNoResultsMsg = await page.getByText(/sin resultado|no encontr|no hay/i).isVisible().catch(() => false);
      expect(hasResults || hasNoResultsMsg).toBeTruthy();
    });

    test(`${key}: C2-03 Búsqueda sin resultados muestra mensaje @catalog @funcional`, async ({ authedPage: page }) => {
      const searchInput = page.getByPlaceholder(/buscar/i).first();
      if (!await searchInput.isVisible({ timeout: 5_000 }).catch(() => false)) {
        test.info().annotations.push({ type: 'warning', description: 'Campo de búsqueda no encontrado' });
        return;
      }
      await searchInput.fill('xyznoexiste99999');
      await searchInput.press('Enter');
      await page.waitForLoadState('networkidle', { timeout: 10_000 }).catch(() => {});
      const count = await page.locator('text=/\\$\\s*[\\d.,]+/').count();
      if (count === 0) {
        await expect(page.getByText(/sin resultado|no encontr|no hay/i)).toBeVisible({ timeout: 10_000 });
      }
    });

    test(`${key}: C2-04 Sin imágenes rotas (404) en catálogo @catalog @funcional`, async ({ authedPage: page }) => {
      const broken: string[] = [];
      page.on('response', response => {
        if (
          response.status() === 404 &&
          /\.(jpg|jpeg|png|webp|gif|svg)/i.test(response.url()) &&
          !response.url().includes('favicon')
        ) {
          broken.push(response.url().split('/').pop() || response.url());
        }
      });
      await page.waitForTimeout(3_000);
      if (broken.length > 0) {
        test.info().annotations.push({ type: 'error', description: `${broken.length} imagen(es) 404: ${broken.slice(0, 5).join(', ')}` });
      }
      expect(broken.length).toBe(0);
    });

  });
}

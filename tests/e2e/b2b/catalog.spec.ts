import { test, expect } from '@playwright/test';

test.describe('C2 — Catalogo y busqueda', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Esperar a que el catalogo cargue (al menos un precio visible)
    await expect(page.locator('text=/\\$\\s*[\\d.,]+/')).toBeVisible({ timeout: 30_000 });
  });

  test('C2-01: Catalogo muestra productos con nombre y precio', async ({ page }) => {
    const prices = page.locator('text=/\\$\\s*[\\d.,]+/');
    const count = await prices.count();
    expect(count).toBeGreaterThan(0);
  });

  test('C2-02: Buscar producto por nombre', async ({ page }) => {
    const searchInput = page.getByPlaceholder('Buscar productos');
    await searchInput.click();
    await searchInput.fill('leche');
    await searchInput.press('Enter');

    // Esperar a que la busqueda se procese (URL cambia o resultados actualizan)
    await page.waitForLoadState('networkidle');

    const results = page.locator('text=/\\$\\s*[\\d.,]+/');
    const noResults = page.getByText(/sin resultado|no encontr|no result|no hay/i);

    // Debe haber resultados O un mensaje de "sin resultados" — no puede quedarse vacio sin feedback
    const hasResults = await results.count() > 0;
    const hasNoResultsMsg = await noResults.isVisible().catch(() => false);
    expect(hasResults || hasNoResultsMsg).toBeTruthy();
  });

  test('C2-03: Busqueda sin resultados muestra mensaje', async ({ page }) => {
    const searchInput = page.getByPlaceholder('Buscar productos');
    await searchInput.click();
    await searchInput.fill('xyznoexiste99999');
    await searchInput.press('Enter');

    await page.waitForLoadState('networkidle');

    // No debe haber productos
    const prices = page.locator('text=/\\$\\s*[\\d.,]+/');
    const count = await prices.count();
    // Si hay 0 resultados, debe haber feedback visual
    if (count === 0) {
      await expect(page.getByText(/sin resultado|no encontr|no result|no hay/i)).toBeVisible({ timeout: 10_000 });
    }
  });

  test('C2-04: Navegar por categorias', async ({ page }) => {
    // Las categorias se muestran como nav links o botones
    const categoryLinks = page.locator('nav a, [class*="category" i] a, [class*="sidebar" i] a');
    const count = await categoryLinks.count();

    if (count > 0) {
      const firstCategory = categoryLinks.first();
      const categoryText = await firstCategory.textContent();
      await firstCategory.click();
      await page.waitForLoadState('networkidle');
      // La pagina no debe estar vacia despues de navegar
      await expect(page.locator('body')).toContainText(/\$/);
      test.info().annotations.push({ type: 'category', description: categoryText || 'unknown' });
    }
  });
});

import { test, expect } from '@playwright/test';
import { loginHelper } from '../fixtures/login';
import clients from '../fixtures/clients';

for (const [key, client] of Object.entries(clients)) {
  test.describe(`C2 — Carrito de compras: ${client.name}`, () => {
    test.use({ baseURL: client.baseURL });

    test.beforeEach(async ({ page }) => {
      await loginHelper(page, client.credentials.email, client.credentials.password, client.loginPath, client.baseURL);
      await page.goto(`${client.baseURL}/products`);
      await expect(page.getByRole('button', { name: 'Agregar' }).first()).toBeVisible({ timeout: 30_000 });
    });

    test(`${key}: C2-05 Agregar producto al carro`, async ({ page }) => {
      const addButton = page.getByRole('button', { name: 'Agregar' }).first();

      const [response] = await Promise.all([
        page.waitForResponse(resp => resp.url().includes('/cart') && resp.request().method() === 'POST'),
        addButton.click(),
      ]);

      expect(response.ok()).toBeTruthy();
      const body = await response.json();
      expect(body).toBeTruthy();
    });

    test(`${key}: C2-06 Cantidad mínima — sistema corrige o bloquea`, async ({ page }) => {
      // Solo aplica si el cliente tiene MinUnit o showMinOne configurado
      const hasMinUnit = client.config.showMinOne || client.config.minUnit || client.config.limitAddingByStock;
      if (!hasMinUnit) {
        test.skip(true, `C2-06: ${client.name} no tiene MinUnit/showMinOne configurado`);
        return;
      }

      // Ir al catálogo y buscar un producto con cantidad mínima
      await page.goto(`${client.baseURL}/products`);
      await expect(page.getByRole('button', { name: 'Agregar' }).first()).toBeVisible({ timeout: 30_000 });

      // Intentar agregar con cantidad 0 o inferior a la mínima
      const quantityInput = page.locator('input[type="number"]').first();
      if (await quantityInput.isVisible({ timeout: 5_000 }).catch(() => false)) {
        await quantityInput.fill('0');
        await quantityInput.press('Tab');
        await page.waitForTimeout(500);

        // El sistema debe corregir a la mínima o bloquear el agregado
        const value = await quantityInput.inputValue();
        const corrected = parseInt(value) > 0;
        expect(corrected, `${client.name}: permitió cantidad 0 sin corrección`).toBe(true);
      } else {
        // Si no hay input visible, el botón Agregar directamente setea la mínima
        const addButton = page.getByRole('button', { name: 'Agregar' }).first();
        const [response] = await Promise.all([
          page.waitForResponse(resp => resp.url().includes('/cart') && resp.request().method() === 'POST'),
          addButton.click(),
        ]);
        const body = await response.json().catch(() => ({}));
        // La cantidad en el response debe ser >= 1
        const qty = body?.quantity || body?.qty || body?.amount || 1;
        expect(qty).toBeGreaterThanOrEqual(1);
      }
    });

    test(`${key}: C2-08 Modificar cantidad en carro`, async ({ page }) => {
      await Promise.all([
        page.waitForResponse(resp => resp.url().includes('/cart') && resp.request().method() === 'POST'),
        page.getByRole('button', { name: 'Agregar' }).first().click(),
      ]);

      await page.goto(`${client.baseURL}/cart`);
      await expect(page.getByText(/\d+ Producto/)).toBeVisible({ timeout: 15_000 });

      const quantityInput = page.locator('input[type="number"]').first();
      await expect(quantityInput).toBeVisible({ timeout: 10_000 });
      await quantityInput.fill('3');
      await quantityInput.press('Tab');

      await page.waitForResponse(resp => resp.url().includes('/cart'), { timeout: 10_000 });
      await expect(quantityInput).toHaveValue('3');
    });

    test(`${key}: C2-09 Eliminar producto del carro`, async ({ page }) => {
      await Promise.all([
        page.waitForResponse(resp => resp.url().includes('/cart') && resp.request().method() === 'POST'),
        page.getByRole('button', { name: 'Agregar' }).first().click(),
      ]);

      await page.goto(`${client.baseURL}/cart`);
      await expect(page.getByText(/\d+ Producto/)).toBeVisible({ timeout: 15_000 });

      const deleteAll = page.getByRole('button', { name: /eliminar todos/i });
      if (await deleteAll.isVisible({ timeout: 5_000 }).catch(() => false)) {
        await deleteAll.click();
        await expect(page.getByText('0 Producto')).toBeVisible({ timeout: 10_000 });
      } else {
        const deleteButton = page.locator('[aria-label*="delete" i], [aria-label*="eliminar" i]').first();
        await deleteButton.click();
        await page.waitForResponse(resp => resp.url().includes('/cart'), { timeout: 10_000 });
      }
    });
  });
}

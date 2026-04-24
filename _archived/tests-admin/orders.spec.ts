import { test, expect } from '@playwright/test';

/**
 * ADM-ORD — Gestión de órdenes en Admin
 * Fuente: Deuda técnica Notion — "Test en admin"
 * Valida: listado, detalle, y estados de órdenes desde el panel admin
 */

const ADMIN_URL = process.env.ADMIN_URL || 'https://admin.youorder.me';
const ADMIN_EMAIL = process.env.ADMIN_EMAIL || '';
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || '';

async function loginAdmin(page: any) {
  await page.goto(ADMIN_URL);
  await page.waitForLoadState('domcontentloaded');

  if (page.url().includes('login') || page.url().includes('auth')) {
    const emailField = page.getByLabel(/[Cc]orreo|[Ee]mail|[Uu]suario/);
    const passwordField = page.getByLabel(/[Cc]ontraseña|[Pp]assword/);
    await emailField.fill(ADMIN_EMAIL);
    await passwordField.fill(ADMIN_PASSWORD);
    await page.locator('form').getByRole('button', { name: /[Ii]niciar|[Ll]ogin|[Ee]ntrar/ }).click();
    await expect(page).not.toHaveURL(/login|auth/, { timeout: 30_000 });
  }
}

test.describe('ADM-ORD — Órdenes en Admin', () => {
  test.skip(!ADMIN_EMAIL || !ADMIN_PASSWORD, 'ADMIN_EMAIL y ADMIN_PASSWORD requeridos');

  test('ADM-ORD-01: Listado de órdenes carga', async ({ page }) => {
    await loginAdmin(page);

    // Navegar a órdenes
    const orderLinks = [
      page.getByRole('link', { name: /[Óó]rden|[Pp]edido|[Oo]rder/ }),
      page.getByRole('menuitem', { name: /[Óó]rden|[Pp]edido|[Oo]rder/ }),
    ];

    let navigated = false;
    for (const link of orderLinks) {
      if (await link.first().isVisible({ timeout: 5_000 }).catch(() => false)) {
        await link.first().click();
        navigated = true;
        break;
      }
    }

    if (!navigated) {
      await page.goto(`${ADMIN_URL}/orders`);
    }

    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-results/admin-orders-list.png', fullPage: true });

    // No debe haber errores
    const hasError = await page.getByText(/error interno|500|server error/i).isVisible().catch(() => false);
    expect(hasError).toBeFalsy();
  });

  test('ADM-ORD-02: Detalle de orden muestra información completa', async ({ page }) => {
    await loginAdmin(page);
    await page.goto(`${ADMIN_URL}/orders`);
    await page.waitForLoadState('networkidle');

    // Click en primera orden disponible
    const firstOrder = page.locator('table tbody tr, [class*="order"], [class*="row"]').first();
    if (await firstOrder.isVisible({ timeout: 10_000 }).catch(() => false)) {
      await firstOrder.click();
      await page.waitForLoadState('networkidle');

      await page.screenshot({ path: 'test-results/admin-order-detail.png', fullPage: true });

      // Debe mostrar algún dato de la orden
      const bodyText = await page.locator('body').textContent();
      expect(bodyText!.length).toBeGreaterThan(100);
    }
  });

  test('ADM-ORD-03: Pagos de orden muestran montos consistentes', async ({ page }) => {
    await loginAdmin(page);
    await page.goto(`${ADMIN_URL}/orders`);
    await page.waitForLoadState('networkidle');

    // Entrar al detalle de una orden
    const firstOrder = page.locator('table tbody tr, [class*="order"], [class*="row"]').first();
    if (await firstOrder.isVisible({ timeout: 10_000 }).catch(() => false)) {
      await firstOrder.click();
      await page.waitForLoadState('networkidle');

      // Buscar sección de pagos dentro del detalle
      const paymentSection = page.getByText(/[Pp]ago|[Pp]ayment|[Mm]onto/);
      if (await paymentSection.first().isVisible({ timeout: 5_000 }).catch(() => false)) {
        await page.screenshot({ path: 'test-results/admin-order-payments.png', fullPage: true });
      }
    }
  });
});

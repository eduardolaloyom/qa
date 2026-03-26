import { test as base, expect } from '@playwright/test';

const EMAIL = process.env.COMMERCE_EMAIL || '';
const PASSWORD = process.env.COMMERCE_PASSWORD || '';
const BASE_URL = process.env.BASE_URL || 'https://tienda.youorder.me';

async function login(page: any) {
  await page.goto(BASE_URL);
  await page.waitForLoadState('domcontentloaded');

  // Si ya estamos logueados (no estamos en /auth), salir
  if (!page.url().includes('/auth')) {
    const loginLink = page.getByText('Iniciar sesión').first();
    if (!await loginLink.isVisible({ timeout: 3_000 }).catch(() => false)) return;
    await loginLink.click();
    await page.waitForLoadState('domcontentloaded');
  }

  await page.getByLabel('Correo').fill(EMAIL);
  await page.getByLabel('Contraseña').fill(PASSWORD);
  await page.locator('form').getByRole('button', { name: 'Iniciar sesión' }).click();
  await expect(page).not.toHaveURL(/auth\/jwt\/login/, { timeout: 30_000 });
}

/**
 * Custom fixture that provides an authenticated page.
 * Handles login with fresh browser context per test.
 */
export const test = base.extend<{ authedPage: ReturnType<typeof base['page']> }>({
  authedPage: async ({ browser }, use) => {
    const context = await browser.newContext({ baseURL: BASE_URL });
    const page = await context.newPage();
    await login(page);
    await use(page);
    await context.close();
  },
});

export { expect };

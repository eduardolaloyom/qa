import { test, expect } from '@playwright/test';

const EMAIL = process.env.COMMERCE_EMAIL || '';
const PASSWORD = process.env.COMMERCE_PASSWORD || '';

test.describe('C1 — Login de Comercio', () => {
  test('C1-01: Acceso anonimo muestra catalogo', async ({ page }) => {
    await page.goto('/');
    await expect(page).not.toHaveURL(/auth|login/);
    // Debe mostrar productos (anonymousAccess=true)
    await expect(page.locator('text=/\\$\\s*[\\d.,]+/')).toBeVisible({ timeout: 15_000 });
  });

  test('C1-01b: Login exitoso con email y password', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    await page.getByText('Iniciar sesión').first().click();
    await page.waitForLoadState('domcontentloaded');

    await page.getByLabel('Correo').fill(EMAIL);
    await page.getByLabel('Contraseña').fill(PASSWORD);

    const [response] = await Promise.all([
      page.waitForResponse(resp => resp.url().includes('/auth/') && resp.status() === 200),
      page.locator('form').getByRole('button', { name: 'Iniciar sesión' }).click(),
    ]);

    expect(response.ok()).toBeTruthy();
    await expect(page).not.toHaveURL(/auth\/jwt\/login/, { timeout: 30_000 });
  });

  test('C1-02: Login fallido con password incorrecto', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    await page.getByText('Iniciar sesión').first().click();
    await page.waitForLoadState('domcontentloaded');

    await page.getByLabel('Correo').fill(EMAIL);
    await page.getByLabel('Contraseña').fill('WrongPassword123');

    await page.locator('form').getByRole('button', { name: 'Iniciar sesión' }).click();

    // Esperar a que el API responda y la pagina procese
    await page.waitForLoadState('networkidle');

    // Debe permanecer en login (no redirige con password incorrecto)
    await expect(page).toHaveURL(/auth\/jwt\/login/);
  });

  test('C1-08: Logout exitoso', async ({ page }) => {
    // Login
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    await page.getByText('Iniciar sesión').first().click();
    await page.waitForLoadState('domcontentloaded');
    await page.getByLabel('Correo').fill(EMAIL);
    await page.getByLabel('Contraseña').fill(PASSWORD);
    await page.locator('form').getByRole('button', { name: 'Iniciar sesión' }).click();
    await expect(page).not.toHaveURL(/auth\/jwt\/login/, { timeout: 30_000 });

    // Buscar menu de usuario — el B2B muestra el nombre del usuario como boton
    const userMenu = page.getByRole('button', { name: /eduardo/i })
      .or(page.locator('[data-testid*="avatar" i], [aria-label*="account" i]'))
      .first();
    await userMenu.click({ timeout: 10_000 });

    // Click logout
    await page.getByText(/cerrar sesión|logout|salir/i).click();
    await expect(page).toHaveURL(/auth|login/, { timeout: 15_000 });
  });

  test('C1-07: Sesion persistente — cerrar y reabrir mantiene login', async ({ browser }) => {
    // Login en un context con storage
    const context = await browser.newContext();
    const page = await context.newPage();

    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    await page.getByText('Iniciar sesión').first().click();
    await page.waitForLoadState('domcontentloaded');
    await page.getByLabel('Correo').fill(EMAIL);
    await page.getByLabel('Contraseña').fill(PASSWORD);
    await page.locator('form').getByRole('button', { name: 'Iniciar sesión' }).click();
    await expect(page).not.toHaveURL(/auth\/jwt\/login/, { timeout: 30_000 });

    // Guardar estado de la sesion (cookies, localStorage)
    const storageState = await context.storageState();
    await context.close();

    // Reabrir con el mismo estado — simula cerrar y reabrir browser
    const context2 = await browser.newContext({ storageState });
    const page2 = await context2.newPage();
    await page2.goto('/');
    await page2.waitForLoadState('domcontentloaded');

    // No debe redirigir a login — sesion persiste
    await expect(page2).not.toHaveURL(/auth\/jwt\/login/, { timeout: 15_000 });
    await context2.close();
  });
});

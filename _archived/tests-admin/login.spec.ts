import { test, expect } from '@playwright/test';

/**
 * ADM-AUTH — Login en Admin
 * Fuente: Deuda técnica Notion — "Test en admin"
 * Primer spec E2E para admin.youorder.me — base para expandir cobertura
 */

const ADMIN_URL = process.env.ADMIN_URL || 'https://admin.youorder.me';
const ADMIN_EMAIL = process.env.ADMIN_EMAIL || '';
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || '';

test.describe('ADM-AUTH — Login Admin', () => {

  test('ADM-01: Página de login carga correctamente', async ({ page }) => {
    await page.goto(ADMIN_URL);
    await page.waitForLoadState('domcontentloaded');

    // Debe mostrar formulario de login
    const loginForm = page.locator('form');
    await expect(loginForm).toBeVisible({ timeout: 15_000 });

    await page.screenshot({ path: 'test-results/admin-login-page.png', fullPage: true });
  });

  test('ADM-02: Login con credenciales válidas', async ({ page }) => {
    test.skip(!ADMIN_EMAIL || !ADMIN_PASSWORD, 'ADMIN_EMAIL y ADMIN_PASSWORD requeridos');

    await page.goto(ADMIN_URL);
    await page.waitForLoadState('domcontentloaded');

    // Llenar formulario
    const emailField = page.getByLabel(/[Cc]orreo|[Ee]mail|[Uu]suario/);
    const passwordField = page.getByLabel(/[Cc]ontraseña|[Pp]assword/);

    await emailField.fill(ADMIN_EMAIL);
    await passwordField.fill(ADMIN_PASSWORD);

    // Submit
    await page.locator('form').getByRole('button', { name: /[Ii]niciar|[Ll]ogin|[Ee]ntrar/ }).click();

    // Debe salir de la página de login
    await expect(page).not.toHaveURL(/login|auth/, { timeout: 30_000 });

    await page.screenshot({ path: 'test-results/admin-logged-in.png', fullPage: true });
  });

  test('ADM-03: Login con contraseña incorrecta muestra error', async ({ page }) => {
    await page.goto(ADMIN_URL);
    await page.waitForLoadState('domcontentloaded');

    const emailField = page.getByLabel(/[Cc]orreo|[Ee]mail|[Uu]suario/);
    const passwordField = page.getByLabel(/[Cc]ontraseña|[Pp]assword/);

    await emailField.fill('test@youorder.me');
    await passwordField.fill('contraseña-incorrecta-123');

    await page.locator('form').getByRole('button', { name: /[Ii]niciar|[Ll]ogin|[Ee]ntrar/ }).click();

    // Debe mostrar mensaje de error
    const errorVisible = await page.getByText(/[Ii]ncorrect|[Ii]nválid|[Ee]rror|[Ff]allid/).isVisible({ timeout: 10_000 }).catch(() => false);
    expect(errorVisible).toBeTruthy();
  });

  test('ADM-04: Acceso a ruta protegida sin sesión redirige a login', async ({ page }) => {
    // Intentar acceder directamente a una ruta protegida
    await page.goto(`${ADMIN_URL}/dashboard`);
    await page.waitForLoadState('networkidle');

    // Debe redirigir a login
    expect(page.url()).toMatch(/login|auth/);
  });
});

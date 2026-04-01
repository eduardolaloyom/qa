import { expect, Page } from '@playwright/test';

/**
 * Unified login helper with robust selector fallbacks.
 *
 * Handles two login flows:
 * 1. Modal login: Click "Iniciar sesión" button → fills modal → submit
 * 2. Direct login page: Navigate to loginPath → fills form → submit
 *
 * Tries multiple selector strategies to find email/password fields.
 */
export async function loginHelper(
  page: Page,
  email: string,
  password: string,
  loginPath: string = '/auth/jwt/login',
  baseURL?: string
) {
  const url = baseURL ? `${baseURL}${loginPath}` : loginPath;

  // First, try to navigate to login path
  await page.goto(url);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(1000);

  // Strategy 1: Try to find email input by name="email" (most reliable)
  let emailInput = page.locator('input[name="email"]').first();
  let isVisible = await emailInput.isVisible({ timeout: 2000 }).catch(() => false);

  // Strategy 2: If not found, try by name attributes, then other selectors
  if (!isVisible) {
    emailInput = page.getByLabel('Correo')
      .or(page.getByPlaceholder(/correo|email/i))
      .or(page.locator('input[type="email"]'))
      .or(page.locator('input[type="text"][placeholder*="email" i]'))
      .or(page.locator('input[placeholder*="correo" i]'))
      .or(page.locator('input[name="email"]'))
      .first();
    isVisible = await emailInput.isVisible({ timeout: 2000 }).catch(() => false);
  }

  // Strategy 3: If still not found, the login might be in a modal on home page
  // Click "Iniciar sesión" button and wait for modal to appear
  if (!isVisible) {
    if (baseURL) {
      await page.goto(baseURL); // Go to home
    } else {
      await page.goto('/');
    }
    await page.waitForLoadState('domcontentloaded');

    const loginButton = page.getByText(/iniciar sesión/i).first();
    if (await loginButton.isVisible({ timeout: 5000 }).catch(() => false)) {
      await loginButton.click();
      await page.waitForTimeout(1500); // Wait for modal animation

      // Now look for email input in modal
      emailInput = page.locator('input[name="email"]')
        .or(page.locator('input[type="email"]'))
        .or(page.locator('input[placeholder*="email" i]'))
        .or(page.locator('input[placeholder*="correo" i]'))
        .first();
    }
  }

  // Password input — search by name first, then other strategies
  let passwordInput = page.locator('input[name="password"]').first();
  isVisible = await passwordInput.isVisible({ timeout: 2000 }).catch(() => false);

  if (!isVisible) {
    passwordInput = page.getByLabel('Contraseña')
      .or(page.getByPlaceholder(/contraseña|password/i))
      .or(page.locator('input[type="password"]'))
      .or(page.locator('input[name="password"]'))
      .first();
  }

  // Fill email and password
  await emailInput.fill(email);
  await passwordInput.fill(password);

  // Submit button (usually in a form, but could be a button outside)
  const submitButton = page.locator('button[type="submit"]')
    .or(page.locator('form button'))
    .or(page.getByRole('button', { name: /iniciar sesión|login|ingresar/i }))
    .first();

  await submitButton.click();

  // Wait for redirect — user is logged in
  await expect(page).not.toHaveURL(/auth\/jwt\/login|\/login$/, { timeout: 30_000 });
}

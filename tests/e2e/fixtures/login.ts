import { expect, Page } from '@playwright/test';

/**
 * Login helper — navigates directly to loginPath and submits credentials.
 * Uses Enter key to submit (avoids ambiguity with header "Iniciar sesión" button).
 */
export async function loginHelper(
  page: Page,
  email: string,
  password: string,
  loginPath: string = '/auth/jwt/login',
  baseURL?: string
) {
  const url = baseURL ? `${baseURL}${loginPath}` : loginPath;

  // Navigate to login page and wait for network to settle
  await page.goto(url, { waitUntil: 'domcontentloaded' });
  await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});

  // Direct name selectors — confirmed working via diagnostic (2 inputs: email + password)
  const emailInput = page.locator('input[name="email"]').first();
  const passwordInput = page.locator('input[name="password"]').first();

  await emailInput.waitFor({ state: 'visible', timeout: 45000 });

  // fill() triggers React onChange in MUI inputs on these staging sites
  await emailInput.click();
  await emailInput.fill(email);

  // Fallback: if fill didn't update the field, use pressSequentially
  if (await emailInput.inputValue() === '') {
    await emailInput.pressSequentially(email, { delay: 30 });
  }

  await passwordInput.click();
  await passwordInput.fill(password);

  if (await passwordInput.inputValue() === '') {
    await passwordInput.pressSequentially(password, { delay: 30 });
  }

  await passwordInput.press('Enter');

  // Wait for redirect away from login page
  await expect(page).not.toHaveURL(/auth\/jwt\/login|\/login$/, { timeout: 45_000 });
}

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

  // Navigate to login page — use domcontentloaded to avoid hanging on staging sites with long-polling
  await page.goto(url, { waitUntil: 'domcontentloaded' });

  // Resolve email input: use bounding box size to detect MUI hidden inputs (opacity:0, 0x0)
  const emailByName = page.locator('input[name="email"]').first();
  const emailBox = await emailByName.boundingBox().catch(() => null);
  const emailIsReal = emailBox !== null && emailBox.width > 10 && emailBox.height > 10;
  const emailInput = emailIsReal
    ? emailByName
    : page.getByRole('textbox', { name: /correo|email/i }).first();

  // Resolve password input: same approach
  const pwByName = page.locator('input[name="password"]').first();
  const pwBox = await pwByName.boundingBox().catch(() => null);
  const pwIsReal = pwBox !== null && pwBox.width > 10 && pwBox.height > 10;
  const passwordInput = pwIsReal
    ? pwByName
    : page.locator('input[type="password"]').first();

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

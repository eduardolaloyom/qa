import { test as base, expect } from '@playwright/test';
import { loginHelper } from './login';

interface ClientConfig {
  name: string;
  baseURL: string;
  loginPath: string;
  credentials: { email: string; password: string };
  config: Record<string, any>;
  defaultCommerce?: string;
  [key: string]: any;
}

/**
 * Selects a commerce after login via the user menu modal.
 * Required for clients where prices are $0 without a commerce selected (e.g. Bastien).
 */
export async function selectCommerceHelper(page: any, commerceName: string) {
  await page.locator('text=Eduardo').first().click();
  await page.waitForTimeout(300);

  // "Seleccionar comercio" may not appear if already selected or the UI changed
  const hasSelectCommerce = await page.locator('text=Seleccionar comercio').isVisible({ timeout: 5_000 }).catch(() => false);
  if (!hasSelectCommerce) {
    // Close the dropdown and continue — commerce may already be selected or not required
    await page.keyboard.press('Escape');
    return;
  }

  await page.locator('text=Seleccionar comercio').click();
  await page.waitForTimeout(800);

  // Use the modal-scoped input (avoids strict mode violation when page also has "Buscar comercio")
  const dialogInput = page.getByRole('dialog').locator('input[placeholder="Buscar comercio"]');
  const fallbackInput = page.locator('input[placeholder="Buscar comercio"]').first();
  const searchInput = (await dialogInput.count()) > 0 ? dialogInput : fallbackInput;
  await searchInput.waitFor({ state: 'visible', timeout: 10_000 });

  // Click + pressSequentially to reliably trigger React autocomplete onChange
  await searchInput.click();
  await searchInput.clear();
  await searchInput.pressSequentially(commerceName, { delay: 60 });
  await page.waitForTimeout(1500);

  const option = page.locator('[role="option"]').first();
  await option.waitFor({ state: 'visible', timeout: 12_000 });
  await option.click();
  await page.waitForTimeout(1000);
}

/**
 * Clears the cart before each test to avoid stale state from previous sessions or Cowork runs.
 * Navigates to /cart and clicks "Eliminar todos" if the button is present.
 */
export async function clearCartHelper(page: any, baseURL: string) {
  try {
    await page.goto(`${baseURL}/cart`, { waitUntil: 'domcontentloaded' });
    const deleteAll = page.getByRole('button', { name: /eliminar todos/i });
    if (await deleteAll.isVisible({ timeout: 5_000 }).catch(() => false)) {
      await deleteAll.click();
      await page.waitForTimeout(1_000);
    }
  } catch {
    // Cart clear is best-effort — don't fail the test if it errors
  }
}

/**
 * Factory: creates a test instance with authedPage for a specific client.
 * Usage in specs:
 *
 *   for (const [key, client] of Object.entries(clients)) {
 *     const test = createClientTest(client);
 *     test.describe(...) { ... }
 *   }
 */
export function createClientTest(client: ClientConfig) {
  return base.extend<{ authedPage: typeof base['prototype']['page'] }>({
    authedPage: async ({ browser }, use) => {
      const context = await browser.newContext({ baseURL: client.baseURL });
      const page = await context.newPage();
      await loginHelper(page, client.credentials.email, client.credentials.password, client.loginPath, client.baseURL);

      // Select default commerce if configured (required for price-gated clients like Bastien)
      if (client.defaultCommerce) {
        await selectCommerceHelper(page, client.defaultCommerce);
      }

      // Clear cart to avoid stale state from previous sessions/Cowork runs
      await clearCartHelper(page, client.baseURL);

      await use(page);
      await context.close();
    },
  });
}

export { expect };

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
 * Tries multiple strategies: "Eliminar todos" button, per-item delete buttons, API call.
 */
export async function clearCartHelper(page: any, baseURL: string) {
  try {
    await page.goto(`${baseURL}/cart`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2_000);

    // Strategy 1: "Eliminar todos" / "Limpiar carrito" / "Vaciar" button
    const deleteAllSelectors = [
      page.getByRole('button', { name: /eliminar todos/i }),
      page.getByRole('button', { name: /limpiar carrito/i }),
      page.getByRole('button', { name: /vaciar carrito/i }),
      page.getByText(/eliminar todos/i),
    ];
    for (const btn of deleteAllSelectors) {
      if (await btn.isVisible({ timeout: 2_000 }).catch(() => false)) {
        await btn.click();
        await page.waitForTimeout(1_500);
        // Handle confirmation modal if appears
        const confirm = page.getByRole('button', { name: /confirmar|aceptar|sí|yes/i });
        if (await confirm.isVisible({ timeout: 2_000 }).catch(() => false)) {
          await confirm.click();
          await page.waitForTimeout(1_000);
        }
        return;
      }
    }

    // Strategy 2: per-item delete buttons (aria-label or trash icon)
    const deleteButtons = page.locator('[aria-label*="eliminar" i], [aria-label*="delete" i], [aria-label*="remove" i], button[class*="delete" i], button[class*="trash" i]');
    const count = await deleteButtons.count();
    for (let i = 0; i < count; i++) {
      await deleteButtons.first().click({ force: true }).catch(() => {});
      await page.waitForTimeout(500);
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
    authedPage: async ({ browser }: { browser: import('@playwright/test').Browser }, use: (page: import('@playwright/test').Page) => Promise<void>, testInfo: import('@playwright/test').TestInfo) => {
      testInfo.skip(!client.credentials.email, `No credentials for ${client.name} — client inactive or not configured`);
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

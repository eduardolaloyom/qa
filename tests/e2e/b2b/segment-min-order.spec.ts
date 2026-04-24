/**
 * Segment-based minimum order — Soprole
 *
 * Tests for the per-segment minimum order feature (requested by Soprole).
 * Current behavior: single global minTotalPrice=48000 from salesterms.
 * New behavior: segment can override that value; max wins if user is in multiple segments.
 *
 * PREREQUISITES before un-skipping:
 *   1. Feature implemented + feature flag variable created (see staging-requirements below)
 *   2. Staging data configured per QA/Soprole/staging-requirements-segment-min-order.md
 *   3. .env populated with the 3 test user credentials below
 *
 * .env vars needed:
 *   SOPROLE_SEGMENT_HIGH_EMAIL / SOPROLE_SEGMENT_HIGH_PASSWORD
 *     → user assigned to a segment with minOrder=80000
 *   SOPROLE_SEGMENT_MULTI_EMAIL / SOPROLE_SEGMENT_MULTI_PASSWORD
 *     → user assigned to two segments: minOrder=60000 and minOrder=80000
 *   SOPROLE_SEGMENT_NONE_EMAIL / SOPROLE_SEGMENT_NONE_PASSWORD
 *     → user with no segment assignment (fallback test)
 */

import { test, expect } from '@playwright/test';

const BASE_URL = 'https://soprole.solopide.me';
const GLOBAL_MIN = 48_000;
const SEGMENT_HIGH_MIN = 80_000;
const SEGMENT_A_MIN = 60_000;

// ─── helpers ──────────────────────────────────────────────────────────────────

async function loginAs(page: any, email: string, password: string) {
  await page.goto(`${BASE_URL}/login`);
  await page.getByPlaceholder(/correo|email/i).fill(email);
  await page.getByPlaceholder(/contraseña|password/i).fill(password);
  await page.keyboard.press('Enter');
  await page.waitForURL(/\/(products|home|catalog)/, { timeout: 20_000 });
}

async function interceptSalesterms(page: any): Promise<number | null> {
  // Intercepts the cart or salesterms API response and returns the resolved minTotalPrice.
  // Exact endpoint path depends on backend implementation — update once known.
  return new Promise((resolve) => {
    let resolved = false;
    page.on('response', async (resp: any) => {
      if (resolved) return;
      const url = resp.url();
      if (
        (url.includes('/salesterms') || url.includes('/cart/config') || url.includes('/site/config')) &&
        resp.status() === 200
      ) {
        try {
          const json = await resp.json();
          const minOrder =
            json?.minTotalPrice ??
            json?.order?.minTotalPrice ??
            json?.data?.minTotalPrice ??
            null;
          if (minOrder !== null) {
            resolved = true;
            resolve(minOrder);
          }
        } catch {
          // non-JSON response, ignore
        }
      }
    });
    setTimeout(() => { if (!resolved) resolve(null); }, 15_000);
  });
}

async function getCartMinWarning(page: any): Promise<string | null> {
  // Returns text of the minimum order warning shown in the cart, if visible.
  const warning = page.locator('[class*="min-order" i], [class*="minOrder" i], [class*="minimum-order" i]')
    .or(page.getByText(/monto mínimo|pedido mínimo|minimum order/i));
  try {
    await warning.first().waitFor({ timeout: 8_000 });
    return await warning.first().textContent();
  } catch {
    return null;
  }
}

// ─── Baseline (runs today — no feature needed) ────────────────────────────────

test.describe('Soprole — Pedido mínimo global (baseline)', () => {

  test('usuario sin segmento ve mínimo global de $48.000', async ({ page }) => {
    const email = process.env.SOPROLE_SEGMENT_NONE_EMAIL || process.env.SOPROLE_EMAIL || '';
    const password = process.env.SOPROLE_SEGMENT_NONE_PASSWORD || process.env.SOPROLE_PASSWORD || '';
    test.skip(!email, 'SOPROLE_EMAIL not set in .env');

    const minOrderPromise = interceptSalesterms(page);
    await loginAs(page, email, password);
    await page.goto(`${BASE_URL}/cart`);
    await page.waitForLoadState('domcontentloaded');

    const resolvedMin = await minOrderPromise;
    if (resolvedMin !== null) {
      expect(resolvedMin).toBe(GLOBAL_MIN);
    } else {
      // API shape unknown — fall back to UI assertion
      // Just confirm the cart page loads and does not show a segment-based higher minimum
      await expect(page.locator('body')).not.toContainText(String(SEGMENT_HIGH_MIN));
    }
  });

});

// ─── New feature tests (skip until implemented) ───────────────────────────────

test.describe('Soprole — Pedido mínimo por segmento', () => {

  test('usuario en segmento con mínimo=80.000 → API devuelve 80.000', async ({ page }) => {
    test.skip(true, 'Feature not implemented — remove skip once deployed to staging');
    const email = process.env.SOPROLE_SEGMENT_HIGH_EMAIL || '';
    const password = process.env.SOPROLE_SEGMENT_HIGH_PASSWORD || '';
    test.skip(!email, 'SOPROLE_SEGMENT_HIGH_EMAIL not set');

    const minOrderPromise = interceptSalesterms(page);
    await loginAs(page, email, password);
    await page.goto(`${BASE_URL}/cart`);
    await page.waitForLoadState('domcontentloaded');

    const resolvedMin = await minOrderPromise;
    expect(resolvedMin).toBe(SEGMENT_HIGH_MIN);
  });

  test('usuario en segmento con mínimo=80.000 → UI bloquea carrito bajo ese monto', async ({ page }) => {
    test.skip(true, 'Feature not implemented — remove skip once deployed to staging');
    const email = process.env.SOPROLE_SEGMENT_HIGH_EMAIL || '';
    const password = process.env.SOPROLE_SEGMENT_HIGH_PASSWORD || '';
    test.skip(!email, 'SOPROLE_SEGMENT_HIGH_EMAIL not set');

    await loginAs(page, email, password);

    // Add one low-value product (total will be < 80.000 but possibly > 48.000)
    await page.goto(`${BASE_URL}/products`);
    const addBtn = page.getByRole('button', { name: 'Agregar' });
    await addBtn.first().waitFor({ timeout: 20_000 });
    await addBtn.first().click();
    await page.goto(`${BASE_URL}/cart`);
    await page.waitForLoadState('domcontentloaded');

    const warning = await getCartMinWarning(page);
    expect(warning).not.toBeNull();
    // Warning should mention the segment minimum, not the global one
    expect(warning).toMatch(/80\.?000|80,000|\$80/);

    const confirmBtn = page.getByRole('button', { name: /confirmar pedido/i });
    await expect(confirmBtn).toBeDisabled({ timeout: 5_000 });
  });

  test('usuario en segmento sin mínimo definido → usa mínimo global de $48.000', async ({ page }) => {
    test.skip(true, 'Feature not implemented — remove skip once deployed to staging');
    const email = process.env.SOPROLE_SEGMENT_NONE_EMAIL || '';
    const password = process.env.SOPROLE_SEGMENT_NONE_PASSWORD || '';
    test.skip(!email, 'SOPROLE_SEGMENT_NONE_EMAIL not set');

    const minOrderPromise = interceptSalesterms(page);
    await loginAs(page, email, password);
    await page.goto(`${BASE_URL}/cart`);
    await page.waitForLoadState('domcontentloaded');

    const resolvedMin = await minOrderPromise;
    expect(resolvedMin).toBe(GLOBAL_MIN);
  });

  test('usuario en dos segmentos (60k y 80k) → aplica el mayor (80.000)', async ({ page }) => {
    test.skip(true, 'Feature not implemented — remove skip once deployed to staging');
    const email = process.env.SOPROLE_SEGMENT_MULTI_EMAIL || '';
    const password = process.env.SOPROLE_SEGMENT_MULTI_PASSWORD || '';
    test.skip(!email, 'SOPROLE_SEGMENT_MULTI_EMAIL not set');

    const minOrderPromise = interceptSalesterms(page);
    await loginAs(page, email, password);
    await page.goto(`${BASE_URL}/cart`);
    await page.waitForLoadState('domcontentloaded');

    const resolvedMin = await minOrderPromise;
    // Must be the max of the two segment values, not the lower one
    expect(resolvedMin).toBe(SEGMENT_HIGH_MIN);
    expect(resolvedMin).not.toBe(SEGMENT_A_MIN);
    expect(resolvedMin).not.toBe(GLOBAL_MIN);
  });

  test('feature flag OFF → siempre aplica mínimo global aunque haya segmento', async ({ page }) => {
    test.skip(true, 'Feature not implemented — remove skip once deployed to staging');
    // This test requires a Soprole staging instance with the feature flag disabled.
    // If the flag is site-level, create a second test site or toggle it manually.
    // Dev must clarify the flag name so we can add it to ClientConfig.
    const email = process.env.SOPROLE_SEGMENT_HIGH_EMAIL || '';
    const password = process.env.SOPROLE_SEGMENT_HIGH_PASSWORD || '';
    test.skip(!email, 'SOPROLE_SEGMENT_HIGH_EMAIL not set');

    // Assumes feature flag is currently OFF for soprole-flagoff.solopide.me
    const FLAG_OFF_URL = process.env.SOPROLE_FLAGOFF_URL || BASE_URL;

    const minOrderPromise = interceptSalesterms(page);
    await page.goto(`${FLAG_OFF_URL}/login`);
    await page.getByPlaceholder(/correo|email/i).fill(email);
    await page.getByPlaceholder(/contraseña|password/i).fill(password);
    await page.keyboard.press('Enter');
    await page.waitForURL(/\/(products|home|catalog)/, { timeout: 20_000 });
    await page.goto(`${FLAG_OFF_URL}/cart`);
    await page.waitForLoadState('domcontentloaded');

    const resolvedMin = await minOrderPromise;
    expect(resolvedMin).toBe(GLOBAL_MIN);
  });

});

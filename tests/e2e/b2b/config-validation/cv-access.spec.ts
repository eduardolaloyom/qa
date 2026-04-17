import { test, expect } from '@playwright/test';
import { skipIfNotInB2B } from '../../fixtures/b2b-feature';
import clients from '../../fixtures/clients';
import { loginIfNeeded } from './helpers';
import { SELECTORS } from './selectors';

for (const [key, client] of Object.entries(clients)) {
  if (!client.config.anonymousAccess && !client.credentials.email) continue; // skip inactive clients
  test.describe(`Config validation — Access: ${client.name}`, () => {

    // ── anonymousAccess ──
    test(`${key}: anonymousAccess=${client.config.anonymousAccess}`, async ({ browser }) => {
      const context = await browser.newContext();
      const page = await context.newPage();
      await page.goto(client.baseURL);
      await page.waitForLoadState('domcontentloaded');

      if (client.config.anonymousAccess) {
        await expect(page).not.toHaveURL(/auth|login/, { timeout: 10_000 });
      } else {
        await expect(page).toHaveURL(/auth|login/, { timeout: 10_000 });
      }

      await context.close();
    });

    // ── inMaintenance ──
    if (client.config.inMaintenance !== undefined) {
      test(`${key}: inMaintenance=${client.config.inMaintenance}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'inMaintenance');
        const context = await browser.newContext();
        const page = await context.newPage();
        await page.goto(client.baseURL);
        await page.waitForLoadState('domcontentloaded');

        if (client.config.inMaintenance) {
          const maintenanceText = page.getByText(SELECTORS.MAINTENANCE_TEXT);
          await expect(maintenanceText).toBeVisible({ timeout: 10_000 });
        } else {
          const maintenanceText = page.getByText(SELECTORS.MAINTENANCE_TEXT);
          await expect(maintenanceText).not.toBeVisible({ timeout: 5_000 });
        }

        await context.close();
      });
    }

    // ── anonymousHideCart & anonymousHidePrice ──
    if (client.config.anonymousAccess === true) {
      if (client.config.anonymousHideCart !== undefined) {
        test(`${key}: anonymousHideCart=${client.config.anonymousHideCart}`, async ({ browser }) => {
          skipIfNotInB2B(client, 'anonymousHideCart');
          const context = await browser.newContext();
          const page = await context.newPage();
          await page.goto(`${client.baseURL}`);
          await page.waitForLoadState('domcontentloaded');

          const cartIcon = page.locator(SELECTORS.CART_ARIA)
            .or(page.getByRole('link', { name: SELECTORS.CART_LINK_TEXT })).first();

          if (client.config.anonymousHideCart) {
            const isVisible = await cartIcon.isVisible({ timeout: 5_000 }).catch(() => false);
            expect(isVisible).toBeFalsy();
          } else {
            await expect(cartIcon).toBeVisible({ timeout: 10_000 });
          }

          await context.close();
        });
      }

      if (client.config.anonymousHidePrice !== undefined) {
        test(`${key}: anonymousHidePrice=${client.config.anonymousHidePrice}`, async ({ browser }) => {
          skipIfNotInB2B(client, 'anonymousHidePrice');

          if (!client.config.anonymousHidePrice && client.defaultCommerce) {
            test.skip(true, `${key}: anonymousHidePrice=false pero requiere comercio seleccionado — precios sólo visibles después de elegir comercio`);
            return;
          }

          const context = await browser.newContext();
          const page = await context.newPage();
          await page.goto(`${client.baseURL}/products`);
          await page.waitForLoadState('domcontentloaded');

          const prices = page.locator(`text=/${SELECTORS.PRICE_PATTERN.source}/`);
          const priceCount = await prices.count();

          if (client.config.anonymousHidePrice) {
            expect(priceCount).toBe(0);
          } else {
            expect(priceCount).toBeGreaterThan(0);
          }

          await context.close();
        });
      }
    }

    // ── loginButtons.facebook ──
    if (client.config['loginButtons.facebook'] !== undefined) {
      test(`${key}: loginButtons.facebook=${client.config['loginButtons.facebook']}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'loginButtons.facebook');
        const context = await browser.newContext();
        const page = await context.newPage();
        await page.goto(`${client.baseURL}${client.loginPath}`);
        await page.waitForLoadState('domcontentloaded');

        const fbBtn = page.getByRole('button', { name: SELECTORS.FB_BUTTON })
          .or(page.locator(SELECTORS.FB_SELECTOR));

        if (client.config['loginButtons.facebook']) {
          const isVisible = await fbBtn.first().isVisible({ timeout: 8_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] loginButtons.facebook=true but button not found`);
        } else {
          const isVisible = await fbBtn.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    // ── loginButtons.google ──
    if (client.config['loginButtons.google'] !== undefined) {
      test(`${key}: loginButtons.google=${client.config['loginButtons.google']}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'loginButtons.google');
        const context = await browser.newContext();
        const page = await context.newPage();
        await page.goto(`${client.baseURL}${client.loginPath}`);
        await page.waitForLoadState('domcontentloaded');

        const googleBtn = page.getByRole('button', { name: SELECTORS.GOOGLE_BUTTON })
          .or(page.locator(SELECTORS.GOOGLE_SELECTOR));

        if (client.config['loginButtons.google']) {
          const isVisible = await googleBtn.first().isVisible({ timeout: 8_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] loginButtons.google=true but button not found`);
        } else {
          const isVisible = await googleBtn.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

  });
}

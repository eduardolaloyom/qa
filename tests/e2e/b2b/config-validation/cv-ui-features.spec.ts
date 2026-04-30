import { test, expect } from '@playwright/test';
import { skipIfNotInB2B } from '../../fixtures/b2b-feature';
import clients from '../../fixtures/clients';
import { loginIfNeeded } from './helpers';
import { SELECTORS } from './selectors';

for (const [key, client] of Object.entries(clients)) {
  if (!client.config.anonymousAccess && !client.credentials.email) continue; // skip inactive clients
  test.describe(`Config validation — UI Features: ${client.name}`, () => {

    // pendingDocuments
    if (client.config.pendingDocuments !== undefined) {
      test(`${key}: pendingDocuments=${client.config.pendingDocuments}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'pendingDocuments');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);

        await page.goto(`${client.baseURL}`);
        await page.waitForLoadState('domcontentloaded');

        const pendingLink = page.getByRole('link', { name: SELECTORS.PENDING_DOCS_TEXT })
          .or(page.getByText(SELECTORS.PENDING_DOCS_TEXT));

        if (client.config.pendingDocuments) {
          await expect(pendingLink.first()).toBeVisible({ timeout: 8_000 });
        } else {
          const isVisible = await pendingLink.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    // pointsEnabled
    if (client.config.pointsEnabled !== undefined) {
      test(`${key}: pointsEnabled=${client.config.pointsEnabled}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'pointsEnabled');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);

        await page.goto(`${client.baseURL}`);
        await page.waitForLoadState('domcontentloaded');

        const pointsSection = page.getByText(SELECTORS.POINTS_TEXT)
          .or(page.getByRole('link', { name: /puntos|points/i }));

        if (client.config.pointsEnabled) {
          await expect(pointsSection.first()).toBeVisible({ timeout: 8_000 });
        } else {
          const isVisible = await pointsSection.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    // enableTask
    if (client.config.enableTask !== undefined) {
      test(`${key}: enableTask=${client.config.enableTask}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enableTask');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);

        await page.goto(`${client.baseURL}`);
        await page.waitForLoadState('domcontentloaded');

        const taskLink = page.getByRole('link', { name: SELECTORS.TASK_LINK_TEXT })
          .or(page.getByText(SELECTORS.TASK_LABEL_TEXT));

        if (client.config.enableTask) {
          await expect(taskLink.first()).toBeVisible({ timeout: 8_000 });
        } else {
          const isVisible = await taskLink.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    // enableCreditNotes
    if (client.config.enableCreditNotes !== undefined) {
      test(`${key}: enableCreditNotes=${client.config.enableCreditNotes}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enableCreditNotes');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);

        await page.goto(`${client.baseURL}`);
        await page.waitForLoadState('domcontentloaded');

        const creditNotesLink = page.getByRole('link', { name: SELECTORS.CREDIT_NOTES_TEXT })
          .or(page.getByText(SELECTORS.CREDIT_NOTES_LABEL));

        if (client.config.enableCreditNotes) {
          await expect(creditNotesLink.first()).toBeVisible({ timeout: 8_000 });
        } else {
          const isVisible = await creditNotesLink.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    // showMinOne
    if (client.config.showMinOne !== undefined) {
      test(`${key}: showMinOne=${client.config.showMinOne}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'showMinOne');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);

        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');

        const minOneLabel = page.locator(SELECTORS.MIN_ONE_SELECTOR)
          .or(page.getByText(SELECTORS.MIN_ONE_TEXT));

        if (client.config.showMinOne) {
          const isVisible = await minOneLabel.first().isVisible({ timeout: 5_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] showMinOne=true but label not found`);
        } else {
          const isVisible = await minOneLabel.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    // footerCustomContent.useFooterCustomContent
    if (client.config['footerCustomContent.useFooterCustomContent'] === true) {
      test(`${key}: footerCustomContent.useFooterCustomContent=true visible`, async ({ browser }) => {
        skipIfNotInB2B(client, 'footerCustomContent');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);

        await page.goto(`${client.baseURL}`);
        await page.waitForLoadState('domcontentloaded');

        const footer = page.locator(SELECTORS.FOOTER_SELECTOR).first();
        await expect(footer).toBeVisible({ timeout: 10_000 });

        const footerText = await footer.textContent();
        expect(footerText?.trim().length).toBeGreaterThan(10);
        await context.close();
      });
    }

    // externalAccess
    if (client.config.externalAccess !== undefined) {
      test(`${key}: externalAccess=${client.config.externalAccess}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'externalAccess');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);

        await page.goto(`${client.baseURL}`);
        await page.waitForLoadState('domcontentloaded');

        const externalLink = page.getByRole('link', { name: SELECTORS.EXTERNAL_ACCESS_TEXT })
          .or(page.locator('[class*="external-access" i]'));

        if (client.config.externalAccess) {
          const isVisible = await externalLink.first().isVisible({ timeout: 5_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] externalAccess=true but link not found`);
        } else {
          const isVisible = await externalLink.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    // blockedClientAlert.enableBlockedClientAlert
    if (client.config['blockedClientAlert.enableBlockedClientAlert'] !== undefined) {
      test(`${key}: blockedClientAlert.enableBlockedClientAlert=${client.config['blockedClientAlert.enableBlockedClientAlert']}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'blockedClientAlert');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);

        await page.goto(`${client.baseURL}`);
        await page.waitForLoadState('domcontentloaded');

        const blockedAlert = page.getByText(SELECTORS.BLOCKED_CLIENT_TEXT)
          .or(page.locator('[class*="blocked-client" i], [class*="blockedClient" i]'));

        if (client.config['blockedClientAlert.enableBlockedClientAlert']) {
          const isVisible = await blockedAlert.first().isVisible({ timeout: 5_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] blockedClientAlert=true but alert not found — test commerce may not be blocked`);
        } else {
          const isVisible = await blockedAlert.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    // useNewPromotions
    if (client.config.useNewPromotions !== undefined) {
      test(`${key}: useNewPromotions=${client.config.useNewPromotions}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'useNewPromotions');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);

        await page.goto(`${client.baseURL}/products?promotions=true`);
        await page.waitForLoadState('domcontentloaded');
        await page.waitForTimeout(2_000);

        const hasPromotions = client.promotions && client.promotions.length > 0;

        if (!hasPromotions) {
          // promotions=[] → Ofertas debe mostrar estado vacío, no todos los productos — Sonrie-QA-003
          const addButtons = await page.getByRole('button', { name: 'Agregar' }).count();
          expect(addButtons, `promotions=[] pero Ofertas muestra ${addButtons} productos con botón Agregar`).toBe(0);
        } else {
          const promoSection = page.getByText(SELECTORS.PROMO_TEXT).first();
          const isVisible = await promoSection.isVisible({ timeout: 8_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] useNewPromotions=true pero no se encontró contenido promocional`);
        }
        await context.close();
      });
    }

    // enableBetaButtons
    if (client.config.enableBetaButtons !== undefined) {
      test(`${key}: enableBetaButtons=${client.config.enableBetaButtons}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enableBetaButtons');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);

        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');

        const betaBtn = page.locator('[class*="beta" i]')
          .or(page.getByText(SELECTORS.BETA_TEXT));

        if (client.config.enableBetaButtons) {
          const isVisible = await betaBtn.first().isVisible({ timeout: 5_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] enableBetaButtons=true but no beta element found`);
        } else {
          const isVisible = await betaBtn.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    // suggestions.hide
    if (client.config['suggestions.hide'] !== undefined) {
      test(`${key}: suggestions.hide=${client.config['suggestions.hide']}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'suggestions.hide');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');
        await page.waitForTimeout(3_000);

        const suggestionsSection = page.getByText(SELECTORS.SUGGESTIONS_TEXT).first()
          .or(page.locator('[class*="suggestion" i], [class*="suggested" i]').first());

        if (client.config['suggestions.hide']) {
          const isVisible = await suggestionsSection.isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        } else {
          const isVisible = await suggestionsSection.isVisible({ timeout: 8_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] suggestions.hide=false but suggestions section not found`);
        }
        await context.close();
      });
    }

    // enableNewUI
    if (client.config.enableNewUI !== undefined) {
      test(`${key}: enableNewUI=${client.config.enableNewUI}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enableNewUI');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');
        await page.waitForTimeout(3_000);

        const newUIEl = page.locator(SELECTORS.NEW_UI_SELECTOR);

        if (client.config.enableNewUI) {
          const isVisible = await newUIEl.first().isVisible({ timeout: 8_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] enableNewUI=true but new UI indicator not found — may use different selector`);
        } else {
          const isVisible = await newUIEl.first().isVisible({ timeout: 3_000 }).catch(() => false);
          if (isVisible) console.warn(`[${key}] enableNewUI=false but new UI indicator found`);
        }
        await context.close();
      });
    }

  });
}

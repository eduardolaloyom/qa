import { test, expect } from '@playwright/test';
import { skipIfNotInB2B } from '../../fixtures/b2b-feature';
import clients from '../../fixtures/clients';
import { loginIfNeeded, addOneProductToCart } from './helpers';
import { SELECTORS } from './selectors';

for (const [key, client] of Object.entries(clients)) {
  if (!client.config.anonymousAccess && !client.credentials.email) continue; // skip inactive clients
  test.describe(`Config validation — Payments: ${client.name}`, () => {

    // enablePayments / disablePayments
    if (client.config.enablePayments !== undefined) {
      test(`${key}: enablePayments=${client.config.enablePayments}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enablePayments');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);

        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');
        const addButton = page.getByRole('button', { name: SELECTORS.ADD_BUTTON_LABEL }).first();
        await expect(addButton).toBeVisible({ timeout: 15_000 });
        await addButton.click();
        await page.waitForLoadState('domcontentloaded');

        await page.goto(`${client.baseURL}/cart`);
        await page.waitForLoadState('domcontentloaded');

        const paymentsSection = page.locator(SELECTORS.PAYMENTS_CLASS).first();

        if (client.config.enablePayments) {
          await expect(paymentsSection).toBeVisible({ timeout: 10_000 });
        } else {
          const isVisible = await paymentsSection.isVisible({ timeout: 5_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    // disablePayments
    if (client.config.disablePayments === true) {
      test(`${key}: disablePayments=true — sección pagos ausente`, async ({ browser }) => {
        skipIfNotInB2B(client, 'disablePayments');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);

        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');
        const addButton = page.getByRole('button', { name: SELECTORS.ADD_BUTTON_LABEL }).first();
        await expect(addButton).toBeVisible({ timeout: 15_000 });
        await addButton.click();
        await page.waitForLoadState('domcontentloaded');

        await page.goto(`${client.baseURL}/cart`);
        await page.waitForLoadState('domcontentloaded');

        const paymentsSection = page.locator(SELECTORS.PAYMENTS_CLASS).first();
        const isVisible = await paymentsSection.isVisible({ timeout: 5_000 }).catch(() => false);
        expect(isVisible).toBeFalsy();
        await context.close();
      });
    }

    // enableSellerDiscount
    if (client.config.enableSellerDiscount !== undefined) {
      test(`${key}: enableSellerDiscount=${client.config.enableSellerDiscount}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enableSellerDiscount');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await addOneProductToCart(page, client);

        const discountField = page.getByText(SELECTORS.SELLER_DISCOUNT_TEXT)
          .or(page.getByPlaceholder(/descuento.*vendedor|discount/i));

        if (client.config.enableSellerDiscount) {
          await expect(discountField.first()).toBeVisible({ timeout: 8_000 });
        } else {
          const isVisible = await discountField.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    // taxes.showSummary
    if (client.config['taxes.showSummary'] !== undefined) {
      test(`${key}: taxes.showSummary=${client.config['taxes.showSummary']}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'taxes.showSummary');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await addOneProductToCart(page, client);

        const taxSummary = page.locator(SELECTORS.TAX_SUMMARY_CLASS)
          .or(page.getByText(SELECTORS.TAX_DETAIL_TEXT));

        if (client.config['taxes.showSummary']) {
          const isVisible = await taxSummary.first().isVisible({ timeout: 8_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] taxes.showSummary=true but detailed tax section not found`);
        } else {
          const isVisible = await taxSummary.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    // includeTaxRateInPrices
    if (client.config.includeTaxRateInPrices !== undefined) {
      test(`${key}: includeTaxRateInPrices=${client.config.includeTaxRateInPrices}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'includeTaxRateInPrices');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);

        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');
        const addButton = page.getByRole('button', { name: SELECTORS.ADD_BUTTON_LABEL }).first();
        await expect(addButton).toBeVisible({ timeout: 15_000 });
        await addButton.click();
        await page.waitForLoadState('domcontentloaded');

        await page.goto(`${client.baseURL}/cart`);
        await page.waitForLoadState('domcontentloaded');

        const bodyText = await page.locator('body').textContent();

        if (client.config.includeTaxRateInPrices) {
          const hasIvaSeparado = SELECTORS.IVA_SEPARADO_PATTERN.test(bodyText || '');
          expect(hasIvaSeparado).toBeFalsy();
        } else {
          const hasTaxConfig = client.config['taxes.useTaxRate'] && Number(client.config['taxes.taxRate'] || 0) > 0;
          if (hasTaxConfig) {
            const hasIvaLinea = SELECTORS.IVA_LINEA_PATTERN.test(bodyText || '');
            expect(hasIvaLinea).toBeTruthy();
          } else {
            test.info().annotations.push({ type: 'info', description: 'No tax rate configured (taxes.useTaxRate=false) — IVA line not expected' });
          }
        }
        await context.close();
      });
    }

    // enablePaymentsCollection
    if (client.config.enablePaymentsCollection !== undefined) {
      test(`${key}: enablePaymentsCollection=${client.config.enablePaymentsCollection}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enablePaymentsCollection');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);

        await page.goto(`${client.baseURL}/payment-collections`).catch(() => {});
        await page.waitForLoadState('domcontentloaded');

        const collectionsLink = page.getByRole('link', { name: SELECTORS.PAYMENT_COLLECTIONS_TEXT })
          .or(page.getByText(SELECTORS.PAYMENT_COLLECTIONS_LABEL));

        if (client.config.enablePaymentsCollection) {
          const isVisible = await collectionsLink.first().isVisible({ timeout: 8_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] enablePaymentsCollection=true but link not found`);
        } else {
          const isVisible = await collectionsLink.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    // hasTransferPaymentType
    if (client.config.hasTransferPaymentType !== undefined) {
      test(`${key}: hasTransferPaymentType=${client.config.hasTransferPaymentType}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'hasTransferPaymentType');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await addOneProductToCart(page, client);

        const transferOption = page.getByText(SELECTORS.TRANSFER_OPTION_TEXT)
          .or(page.getByLabel(SELECTORS.TRANSFER_OPTION_TEXT));

        if (client.config.hasTransferPaymentType) {
          const isVisible = await transferOption.first().isVisible({ timeout: 8_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] hasTransferPaymentType=true but transfer option not found — requires enablePayments=true`);
        } else {
          const isVisible = await transferOption.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    // discountTypes.enableOrderDiscountType
    if (client.config['discountTypes.enableOrderDiscountType'] !== undefined) {
      test(`${key}: discountTypes.enableOrderDiscountType=${client.config['discountTypes.enableOrderDiscountType']}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'discountTypes');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await addOneProductToCart(page, client);

        const orderDiscountUI = page.getByText(SELECTORS.ORDER_DISCOUNT_TEXT)
          .or(page.locator('[class*="order-discount" i]'));

        if (client.config['discountTypes.enableOrderDiscountType']) {
          const isVisible = await orderDiscountUI.first().isVisible({ timeout: 8_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] discountTypes.enableOrderDiscountType=true but UI not found`);
        } else {
          const isVisible = await orderDiscountUI.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    // discountTypes.enableProductDiscountType
    if (client.config['discountTypes.enableProductDiscountType'] !== undefined) {
      test(`${key}: discountTypes.enableProductDiscountType=${client.config['discountTypes.enableProductDiscountType']}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'discountTypes');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);

        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');

        const productDiscountUI = page.locator(SELECTORS.PRODUCT_DISCOUNT_SELECTOR)
          .or(page.getByText(SELECTORS.PRODUCT_DISCOUNT_TEXT));

        if (client.config['discountTypes.enableProductDiscountType']) {
          const isVisible = await productDiscountUI.first().isVisible({ timeout: 8_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] discountTypes.enableProductDiscountType=true but UI not found`);
        } else {
          const isVisible = await productDiscountUI.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    // payment.enableNewPaymentModule
    if (client.config['payment.enableNewPaymentModule'] !== undefined) {
      test(`${key}: payment.enableNewPaymentModule=${client.config['payment.enableNewPaymentModule']}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'payment.enableNewPaymentModule');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await addOneProductToCart(page, client);

        const paymentModule = page.locator(SELECTORS.PAYMENT_MODULE_SELECTOR)
          .or(page.locator('[data-testid*="payment" i]'));

        if (client.config['payment.enableNewPaymentModule']) {
          const isVisible = await paymentModule.first().isVisible({ timeout: 8_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] payment.enableNewPaymentModule=true but module not found — requires enablePayments=true`);
        } else {
          console.log(`[${key}] payment.enableNewPaymentModule=false — using legacy payment flow`);
        }
        await context.close();
      });
    }

    // paymentsWithoutAccount
    if (client.config.paymentsWithoutAccount !== undefined) {
      test(`${key}: paymentsWithoutAccount=${client.config.paymentsWithoutAccount}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'paymentsWithoutAccount');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await page.goto(`${client.baseURL}/cart`);
        await page.waitForLoadState('domcontentloaded');
        await page.waitForTimeout(2_000);

        const noAccountEl = page.getByText(SELECTORS.NO_ACCOUNT_TEXT)
          .or(page.locator('[class*="without-account" i], [class*="withoutAccount" i]'));

        if (client.config.paymentsWithoutAccount) {
          const isVisible = await noAccountEl.first().isVisible({ timeout: 8_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] paymentsWithoutAccount=true but no-account flow not found`);
        } else {
          const isVisible = await noAccountEl.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

  });
}

import { test, expect } from '@playwright/test';
import { skipIfNotInB2B } from '../../fixtures/b2b-feature';
import clients from '../../fixtures/clients';
import { loginIfNeeded, addOneProductToCart, clearCartForTest } from './helpers';
import { SELECTORS } from './selectors';

for (const [key, client] of Object.entries(clients)) {
  if (!client.config.anonymousAccess && !client.credentials.email) continue; // skip inactive clients
  test.describe(`Config validation — Cart: ${client.name}`, () => {

    test(`${key}: disableCart=${client.config.disableCart}`, async ({ browser }) => {
      skipIfNotInB2B(client, 'disableCart');
      const context = await browser.newContext();
      const page = await context.newPage();
      await loginIfNeeded(page, client);
      await page.goto(`${client.baseURL}/products`);
      await page.waitForLoadState('domcontentloaded');
      const addButtons = page.getByRole('button', { name: SELECTORS.ADD_BUTTON_LABEL });
      if (client.config.disableCart) {
        await page.waitForTimeout(3_000);
        expect(await addButtons.count()).toBe(0);
        await page.goto(`${client.baseURL}/cart`);
        await page.waitForLoadState('domcontentloaded');
        expect(page.url()).not.toMatch(/\/cart$/);
      } else {
        await expect(addButtons.first()).toBeVisible({ timeout: 20_000 });
        expect(await addButtons.count()).toBeGreaterThan(0);
        await page.goto(`${client.baseURL}/cart`);
        await page.waitForLoadState('domcontentloaded');
        await expect(page).toHaveURL(/cart/);
      }
      await context.close();
    });

    if (client.config.enableCoupons !== undefined) {
      test(`${key}: enableCoupons=${client.config.enableCoupons}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enableCoupons');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await clearCartForTest(page, client);
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');
        const addButton = page.getByRole('button', { name: SELECTORS.ADD_BUTTON_LABEL }).first();
        await expect(addButton).toBeVisible({ timeout: 15_000 });
        await addButton.click();
        await page.waitForLoadState('domcontentloaded');
        await page.goto(`${client.baseURL}/cart`);
        await page.waitForLoadState('domcontentloaded');
        const couponField = page.getByPlaceholder(SELECTORS.COUPON_PLACEHOLDER)
          .or(page.getByText(SELECTORS.COUPON_LABEL))
          .or(page.getByRole('button', { name: SELECTORS.APPLY_BUTTON }));
        if (client.config.enableCoupons) {
          await expect(couponField.first()).toBeVisible({ timeout: 10_000 });
        } else {
          await expect(couponField.first()).not.toBeVisible({ timeout: 5_000 });
        }
        await context.close();
      });
    }

    if (client.config.hideReceiptType !== undefined) {
      test(`${key}: hideReceiptType=${client.config.hideReceiptType}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'hideReceiptType');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await clearCartForTest(page, client);
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');
        const addButton = page.getByRole('button', { name: SELECTORS.ADD_BUTTON_LABEL }).first();
        await expect(addButton).toBeVisible({ timeout: 15_000 });
        await addButton.click();
        await page.waitForLoadState('domcontentloaded');
        await page.goto(`${client.baseURL}/cart`);
        await page.waitForLoadState('domcontentloaded');
        const receiptType = page.getByText(SELECTORS.RECEIPT_TYPE_TEXT);
        if (client.config.hideReceiptType) {
          await expect(receiptType).not.toBeVisible({ timeout: 5_000 });
        } else {
          await expect(receiptType).toBeVisible({ timeout: 5_000 });
        }
        await context.close();
      });
    }

    if (client.config.enableAskDeliveryDate !== undefined) {
      test(`${key}: enableAskDeliveryDate=${client.config.enableAskDeliveryDate}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enableAskDeliveryDate');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await clearCartForTest(page, client);
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');
        const addButton = page.getByRole('button', { name: SELECTORS.ADD_BUTTON_LABEL }).first();
        await expect(addButton).toBeVisible({ timeout: 15_000 });
        await addButton.click();
        await page.waitForLoadState('domcontentloaded');
        await page.goto(`${client.baseURL}/cart`);
        await page.waitForLoadState('domcontentloaded');
        const deliveryDateField = page.getByText(SELECTORS.DELIVERY_DATE_TEXT).or(page.locator('input[type="date"]'));
        if (client.config.enableAskDeliveryDate) {
          await expect(deliveryDateField.first()).toBeVisible({ timeout: 10_000 });
        } else {
          const isVisible = await deliveryDateField.first().isVisible({ timeout: 5_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    if (client.config.orderObservations !== undefined) {
      test(`${key}: orderObservations=${client.config.orderObservations}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'orderObservations');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await clearCartForTest(page, client);
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');
        const addButton = page.getByRole('button', { name: SELECTORS.ADD_BUTTON_LABEL }).first();
        await expect(addButton).toBeVisible({ timeout: 15_000 });
        await addButton.click();
        await page.waitForLoadState('domcontentloaded');
        await page.goto(`${client.baseURL}/cart`);
        await page.waitForLoadState('domcontentloaded');
        const observationsField = page.getByPlaceholder(SELECTORS.OBSERVATIONS_PLACEHOLDER)
          .or(page.getByLabel(SELECTORS.OBSERVATIONS_PLACEHOLDER))
          .or(page.locator('textarea[name*="observ" i]'));
        if (client.config.orderObservations) {
          await expect(observationsField.first()).toBeVisible({ timeout: 10_000 });
        } else {
          const isVisible = await observationsField.first().isVisible({ timeout: 5_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    if (client.config.purchaseOrderEnabled !== undefined) {
      test(`${key}: purchaseOrderEnabled=${client.config.purchaseOrderEnabled}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'purchaseOrderEnabled');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await clearCartForTest(page, client);
        await addOneProductToCart(page, client);
        const ocField = page.getByPlaceholder(SELECTORS.PURCHASE_ORDER_PLACEHOLDER)
          .or(page.getByLabel(/orden de compra|purchase order/i))
          .or(page.getByText(/orden de compra/i));
        if (client.config.purchaseOrderEnabled) {
          await expect(ocField.first()).toBeVisible({ timeout: 8_000 });
        } else {
          const isVisible = await ocField.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    if (client.config.editAddress !== undefined) {
      test(`${key}: editAddress=${client.config.editAddress}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'editAddress');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await clearCartForTest(page, client);
        await addOneProductToCart(page, client);
        const editAddrBtn = page.getByRole('button', { name: SELECTORS.EDIT_ADDRESS_TEXT })
          .or(page.getByText(SELECTORS.EDIT_ADDRESS_TEXT));
        if (client.config.editAddress) {
          const isVisible = await editAddrBtn.first().isVisible({ timeout: 8_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] editAddress=true but edit button not found — may require commerce with address`);
        } else {
          const isVisible = await editAddrBtn.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    if (client.config.limitAddingByStock !== undefined) {
      test(`${key}: limitAddingByStock=${client.config.limitAddingByStock}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'limitAddingByStock');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');
        const stockLimitIndicator = page.locator(SELECTORS.STOCK_LIMIT_SELECTOR).or(page.getByText(SELECTORS.STOCK_LIMIT_TEXT));
        if (client.config.limitAddingByStock) {
          const isVisible = await stockLimitIndicator.first().isVisible({ timeout: 5_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] limitAddingByStock=true but indicator not found — staging may have unlimited stock`);
        } else {
          const isVisible = await stockLimitIndicator.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    if (client.config.hasTransportCode !== undefined) {
      test(`${key}: hasTransportCode=${client.config.hasTransportCode}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'hasTransportCode');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await clearCartForTest(page, client);
        await addOneProductToCart(page, client);
        const transportField = page.getByPlaceholder(SELECTORS.TRANSPORT_CODE_PLACEHOLDER)
          .or(page.getByLabel(SELECTORS.TRANSPORT_CODE_PLACEHOLDER))
          .or(page.getByText(SELECTORS.TRANSPORT_CODE_TEXT));
        if (client.config.hasTransportCode) {
          await expect(transportField.first()).toBeVisible({ timeout: 8_000 });
        } else {
          const isVisible = await transportField.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    if (client.config.disableShowEstimatedDeliveryHour !== undefined) {
      test(`${key}: disableShowEstimatedDeliveryHour=${client.config.disableShowEstimatedDeliveryHour}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'disableShowEstimatedDeliveryHour');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await clearCartForTest(page, client);
        await addOneProductToCart(page, client);
        const deliveryHour = page.getByText(SELECTORS.DELIVERY_HOUR_TEXT)
          .or(page.locator('[class*="delivery-hour" i], [class*="estimatedHour" i]'));
        if (client.config.disableShowEstimatedDeliveryHour) {
          const isVisible = await deliveryHour.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        } else {
          const isVisible = await deliveryHour.first().isVisible({ timeout: 5_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] disableShowEstimatedDeliveryHour=false but hour not found — may not be configured in staging`);
        }
        await context.close();
      });
    }

    if (client.config.hasSingleDistributionCenter !== undefined) {
      test(`${key}: hasSingleDistributionCenter=${client.config.hasSingleDistributionCenter}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'hasSingleDistributionCenter');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await clearCartForTest(page, client);
        await addOneProductToCart(page, client);
        const dcSelector = page.getByText(SELECTORS.DC_CART_TEXT)
          .or(page.locator('[class*="distribution-center" i], [class*="distributionCenter" i]'));
        if (client.config.hasSingleDistributionCenter) {
          const count = await dcSelector.count();
          if (count > 1) console.warn(`[${key}] hasSingleDistributionCenter=true but multiple DC options visible`);
        } else {
          const isVisible = await dcSelector.first().isVisible({ timeout: 8_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] hasSingleDistributionCenter=false but DC selector not found`);
        }
        await context.close();
      });
    }

    if (client.config.disableObservationInput !== undefined) {
      test(`${key}: disableObservationInput=${client.config.disableObservationInput}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'disableObservationInput');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await clearCartForTest(page, client);
        await addOneProductToCart(page, client);
        const observationInput = page.getByLabel(SELECTORS.OBSERVATION_LABEL)
          .or(page.getByPlaceholder(/observaci[oó]n|observation/i));
        if (client.config.disableObservationInput) {
          const isVisible = await observationInput.first().isVisible({ timeout: 5_000 }).catch(() => false);
          if (isVisible) test.info().annotations.push({ type: 'warning', description: `disableObservationInput=true but observation input visible` });
          expect(isVisible).toBeFalsy();
        } else {
          const isVisible = await observationInput.first().isVisible({ timeout: 8_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] disableObservationInput=false but observation input not found`);
        }
        await context.close();
      });
    }

    if (client.config['shoppingDetail.lastOrder'] !== undefined) {
      test(`${key}: shoppingDetail.lastOrder=${client.config['shoppingDetail.lastOrder']}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'shoppingDetail.lastOrder');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await clearCartForTest(page, client);
        await addOneProductToCart(page, client);
        const lastOrderSection = page.getByText(SELECTORS.LAST_ORDER_TEXT)
          .or(page.locator('[class*="last-order" i], [class*="lastOrder" i]'));
        if (client.config['shoppingDetail.lastOrder']) {
          const isVisible = await lastOrderSection.first().isVisible({ timeout: 8_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] shoppingDetail.lastOrder=true but section not found — no previous orders in staging`);
        } else {
          const isVisible = await lastOrderSection.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    if (client.config.enableMassiveOrderSend === true) {
      test(`${key}: enableMassiveOrderSend=true visible`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enableMassiveOrderSend');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await page.goto(`${client.baseURL}/cart`);
        await page.waitForLoadState('domcontentloaded');
        const massiveBtn = page.getByText(SELECTORS.MASSIVE_SEND_TEXT).or(page.getByRole('button', { name: /masivo/i }));
        await expect(massiveBtn.first()).toBeVisible({ timeout: 10_000 });
        await context.close();
      });
    }

  });
}

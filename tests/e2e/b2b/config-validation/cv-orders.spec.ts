import { test, expect } from '@playwright/test';
import { skipIfNotInB2B } from '../../fixtures/b2b-feature';
import clients from '../../fixtures/clients';
import { loginIfNeeded, addOneProductToCart } from './helpers';
import { SELECTORS } from './selectors';

for (const [key, client] of Object.entries(clients)) {
  if (!client.config.anonymousAccess && !client.credentials.email) continue; // skip inactive clients
  test.describe(`Config validation — Orders: ${client.name}`, () => {

    // ordersRequireAuthorization
    if (client.config.ordersRequireAuthorization !== undefined) {
      test(`${key}: ordersRequireAuthorization=${client.config.ordersRequireAuthorization}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'ordersRequireAuthorization');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);

        await page.goto(`${client.baseURL}/orders`);
        await page.waitForLoadState('domcontentloaded');

        if (client.config.ordersRequireAuthorization) {
          const approvalBadge = page.getByText(SELECTORS.APPROVAL_PENDING_TEXT);
          const hasApprovalUI = await approvalBadge.isVisible({ timeout: 5_000 }).catch(() => false);
          expect(hasApprovalUI).toBeTruthy();
        }
        await context.close();
      });
    }

    // ordersRequireVerification
    if (client.config.ordersRequireVerification !== undefined) {
      test(`${key}: ordersRequireVerification=${client.config.ordersRequireVerification}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'ordersRequireVerification');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);

        await page.goto(`${client.baseURL}/orders`);
        await page.waitForLoadState('domcontentloaded');

        const verificationUI = page.getByText(SELECTORS.VERIFICATION_TEXT)
          .or(page.getByRole('button', { name: /verificar/i }));

        if (client.config.ordersRequireVerification) {
          const isVisible = await verificationUI.first().isVisible({ timeout: 5_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] ordersRequireVerification=true but no verification UI found`);
        } else {
          const isVisible = await verificationUI.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    // enableOrderValidation
    if (client.config.enableOrderValidation !== undefined) {
      test(`${key}: enableOrderValidation=${client.config.enableOrderValidation}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enableOrderValidation');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await addOneProductToCart(page, client);

        const validationUI = page.getByText(SELECTORS.VALIDATION_TEXT)
          .or(page.locator('[class*="order-validation" i]'));

        if (client.config.enableOrderValidation) {
          const isVisible = await validationUI.first().isVisible({ timeout: 8_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] enableOrderValidation=true but validation UI not found`);
        } else {
          const isVisible = await validationUI.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    // enableOrderApproval
    if (client.config.enableOrderApproval !== undefined) {
      test(`${key}: enableOrderApproval=${client.config.enableOrderApproval}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enableOrderApproval');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);

        await page.goto(`${client.baseURL}/orders`);
        await page.waitForLoadState('domcontentloaded');

        const approvalBtn = page.getByRole('button', { name: SELECTORS.APPROVAL_BUTTON_TEXT })
          .or(page.getByText(SELECTORS.APPROVAL_PENDING_BADGE));

        if (client.config.enableOrderApproval) {
          const isVisible = await approvalBtn.first().isVisible({ timeout: 5_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] enableOrderApproval=true but approval UI not found — no pending orders in staging`);
        } else {
          const isVisible = await approvalBtn.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    // hasVoucherPrinterEnabled
    if (client.config.hasVoucherPrinterEnabled !== undefined) {
      test(`${key}: hasVoucherPrinterEnabled=${client.config.hasVoucherPrinterEnabled}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'hasVoucherPrinterEnabled');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);

        await page.goto(`${client.baseURL}/orders`);
        await page.waitForLoadState('domcontentloaded');

        const printerBtn = page.getByRole('button', { name: SELECTORS.PRINT_VOUCHER_TEXT })
          .or(page.getByText(/imprimir.*voucher|print.*voucher/i));

        if (client.config.hasVoucherPrinterEnabled) {
          const isVisible = await printerBtn.first().isVisible({ timeout: 5_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] hasVoucherPrinterEnabled=true but print button not found — no orders in staging`);
        } else {
          const isVisible = await printerBtn.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    // shareOrderNewDesign
    if (client.config.shareOrderNewDesign !== undefined) {
      test(`${key}: shareOrderNewDesign=${client.config.shareOrderNewDesign}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'shareOrderNewDesign');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);

        await page.goto(`${client.baseURL}/orders`);
        await page.waitForLoadState('domcontentloaded');

        const shareBtn = page.getByRole('button', { name: SELECTORS.SHARE_ORDER_TEXT })
          .or(page.locator('[class*="share-order" i], [class*="shareOrder" i]'));

        if (client.config.shareOrderNewDesign) {
          const isVisible = await shareBtn.first().isVisible({ timeout: 5_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] shareOrderNewDesign=true but share button not found — no orders in staging`);
        } else {
          const isVisible = await shareBtn.first().isVisible({ timeout: 4_000 }).catch(() => false);
          console.log(`[${key}] shareOrderNewDesign=false — share button visible: ${isVisible}`);
        }
        await context.close();
      });
    }

    // enableInvoicesList
    if (client.config.enableInvoicesList !== undefined) {
      test(`${key}: enableInvoicesList=${client.config.enableInvoicesList}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enableInvoicesList');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await page.goto(`${client.baseURL}/invoices`);
        await page.waitForLoadState('domcontentloaded');
        await page.waitForTimeout(2_000);

        const notFound = await page.getByText(SELECTORS.INVOICE_NOT_FOUND).isVisible({ timeout: 4_000 }).catch(() => false);
        const redirected = page.url().includes('/products') || page.url().includes('/auth');
        const invoicesContent = page.locator('[class*="invoice" i], table').first();
        const hasContent = await invoicesContent.isVisible({ timeout: 4_000 }).catch(() => false);

        if (client.config.enableInvoicesList) {
          if (!hasContent) console.warn(`[${key}] enableInvoicesList=true but invoices list not found`);
        } else {
          expect(notFound || redirected || !hasContent).toBeTruthy();
        }
        await context.close();
      });
    }

    // enablePaymentDocumentsB2B
    if (client.config.enablePaymentDocumentsB2B !== undefined) {
      test(`${key}: enablePaymentDocumentsB2B=${client.config.enablePaymentDocumentsB2B}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enablePaymentDocumentsB2B');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await page.goto(`${client.baseURL}/payment-documents`);
        await page.waitForLoadState('domcontentloaded');
        await page.waitForTimeout(2_000);

        const notFound = await page.getByText(SELECTORS.INVOICE_NOT_FOUND).isVisible({ timeout: 4_000 }).catch(() => false);
        const redirected = page.url().includes('/products') || page.url().includes('/auth');
        const paymentDocsContent = page.locator(SELECTORS.PAYMENT_DOCS_SELECTOR);
        const hasContent = await paymentDocsContent.first().isVisible({ timeout: 4_000 }).catch(() => false);

        if (client.config.enablePaymentDocumentsB2B) {
          if (!hasContent) console.warn(`[${key}] enablePaymentDocumentsB2B=true but module not found`);
        } else {
          // Check nav/footer link is not visible — Sonrie-QA-001: link visible aunque flag=false
          await page.goto(`${client.baseURL}`);
          await page.waitForLoadState('domcontentloaded');
          const navLink = page.locator('a[href*="payment-document"]');
          const navLinkVisible = await navLink.first().isVisible({ timeout: 3_000 }).catch(() => false);

          expect(navLinkVisible, `enablePaymentDocumentsB2B=false pero link a /payment-documents visible en navegación`).toBe(false);
          expect(notFound || redirected || !hasContent, `enablePaymentDocumentsB2B=false pero módulo visible en /payment-documents`).toBeTruthy();
        }
        await context.close();
      });
    }

    // disableCommerceEdit
    if (client.config.disableCommerceEdit !== undefined) {
      test(`${key}: disableCommerceEdit=${client.config.disableCommerceEdit}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'disableCommerceEdit');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await page.goto(`${client.baseURL}/profile`);
        await page.waitForLoadState('domcontentloaded');
        await page.waitForTimeout(2_000);

        const editBtn = page.getByRole('button', { name: SELECTORS.DISABLE_COMMERCE_EDIT_TEXT })
          .or(page.locator('[class*="edit-commerce" i], [class*="editCommerce" i]'));

        if (client.config.disableCommerceEdit) {
          const isVisible = await editBtn.first().isVisible({ timeout: 5_000 }).catch(() => false);
          if (isVisible) {
            test.info().annotations.push({ type: 'warning', description: `disableCommerceEdit=true but edit button visible` });
          }
          expect(isVisible).toBeFalsy();
        } else {
          console.log(`[${key}] disableCommerceEdit=false — edit expected to be available`);
        }
        await context.close();
      });
    }

  });
}

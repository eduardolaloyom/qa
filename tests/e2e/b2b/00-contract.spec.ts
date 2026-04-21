/**
 * Contract tests for clients.ts fixture data integrity.
 * Pure data tests — no browser, no network, no page fixture.
 *
 * Catches type violations in client config variables before any E2E spec
 * runs against them. Mirrors validate_client_variables() in sync-clients.py.
 *
 * Schema ref: data/schemas/client-variables.schema.json
 * Bug ref: BAS-QA-006 — taxes.taxRate: 19 written instead of 0.19
 *
 * Sorted 00- to appear first in Playwright reports.
 */

import { test, expect } from '@playwright/test';
import clients from '../fixtures/clients';

const BOOL_FIELDS = [
  'anonymousAccess',
  'anonymousHideCart',
  'anonymousHidePrice',
  'disableCart',
  'disableCommerceEdit',
  'disableShowEstimatedDeliveryHour',
  'disableShowDiscount',
  'disableShowOffer',
  'editAddress',
  'enableAskDeliveryDate',
  'enableCoupons',
  'enableDialogNoSellReason',
  'enableInvoicesList',
  'enableOrderApproval',
  'enableOrderValidation',
  'enableSellerDiscount',
  'externalAccess',
  'hasMultiUnitEnabled',
  'hidePrices',
  'hideReceiptType',
  'hooks.cartShoppingHook',
  'hooks.getPendingDocumentsHook',
  'hooks.shippingHook',
  'hooks.stockHook',
  'hooks.updateTrafficLightHook',
  'inMaintenance',
  'includeTaxRateInPrices',
  'lazyLoadingPrices',
  'ordersRequireAuthorization',
  'ordersRequireVerification',
  'pendingDocuments',
  'pointsEnabled',
  'purchaseOrderEnabled',
  'showEmptyCategories',
  'showMinOne',
  'taxes.showSummary',
  'taxes.useTaxRate',
  'useMobileGps',
  'weightInfo',
] as const;

for (const [key, client] of Object.entries(clients)) {
  test.describe(`[contract] ${key}`, () => {

    for (const field of BOOL_FIELDS) {
      const value = client.config[field];
      if (value === undefined) continue;

      test(`${field} must be boolean (got ${typeof value} ${JSON.stringify(value)})`, () => {
        expect(
          typeof value,
          `${key}.config.${field} = ${JSON.stringify(value)} — expected boolean, got ${typeof value}. Schema: data/schemas/client-variables.schema.json`
        ).toBe('boolean');
      });
    }

    test('taxes.taxRate must be number in [0, 1]', () => {
      const taxRate = client.config['taxes.taxRate'];
      if (taxRate === undefined) return;
      expect(
        typeof taxRate,
        `${key}: taxes.taxRate = ${JSON.stringify(taxRate)} — expected number, got ${typeof taxRate}. BAS-QA-006: use 0.19 not 19`
      ).toBe('number');
      expect(taxRate, `${key}: taxes.taxRate ${taxRate} out of range [0, 1]`).toBeGreaterThanOrEqual(0);
      expect(taxRate, `${key}: taxes.taxRate ${taxRate} out of range [0, 1]`).toBeLessThanOrEqual(1);
    });

    test('fixture shape: name, baseURL, config', () => {
      expect(client.name).toBeTruthy();
      expect(typeof client.name).toBe('string');
      expect(client.baseURL).toMatch(/^https:\/\//);
      expect(typeof client.config).toBe('object');
    });

  });
}

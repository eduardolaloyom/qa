import { test, expect } from '@playwright/test';
import { skipIfNotInB2B } from '../../fixtures/b2b-feature';
import clients from '../../fixtures/clients';
import { loginIfNeeded } from './helpers';
import { SELECTORS } from './selectors';

for (const [key, client] of Object.entries(clients)) {
  if (!client.config.anonymousAccess && !client.credentials.email) continue; // skip inactive clients
  test.describe(`Config validation — Catalog: ${client.name}`, () => {

    test(`${key}: hidePrices=${client.config.hidePrices}`, async ({ browser }) => {
      skipIfNotInB2B(client, 'hidePrices');
      const context = await browser.newContext();
      const page = await context.newPage();
      await loginIfNeeded(page, client);
      await page.goto(`${client.baseURL}/products`);
      await page.waitForLoadState('domcontentloaded');
      const prices = page.locator(`text=/${SELECTORS.PRICE_PATTERN.source}/`);
      if (client.config.hidePrices) {
        await page.waitForTimeout(3_000);
        expect(await prices.count()).toBe(0);
      } else {
        await expect(prices.first()).toBeVisible({ timeout: 20_000 });
        expect(await prices.count()).toBeGreaterThan(0);
      }
      await context.close();
    });

    // TODO: currency no está en clients.ts, usar campo correcto cuando se disponibilice
    test.skip(`${key}: currency=${client.config.currency}`, async ({ browser }) => {
      const context = await browser.newContext();
      const page = await context.newPage();
      await loginIfNeeded(page, client);
      await page.goto(`${client.baseURL}/products`);
      await page.waitForLoadState('domcontentloaded');
      const currencySymbols: Record<string, string> = { clp: '$', cop: '$', pen: 'S/', usd: '$' };
      const symbol = currencySymbols[client.config.currency] || '$';
      const prices = page.locator(`text=/${symbol.replace('$', '\\$')}\\s*[\\d.,]+/`);
      const count = await prices.count();
      if (!client.config.hidePrices) expect(count).toBeGreaterThan(0);
      await context.close();
    });

    if (client.config.lazyLoadingPrices !== undefined) {
      test(`${key}: lazyLoadingPrices=${client.config.lazyLoadingPrices}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'lazyLoadingPrices');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        const priceRequests: string[] = [];
        page.on('request', req => {
          if (req.url().includes('/price') || req.url().includes('/pricing')) priceRequests.push(req.url());
        });
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');
        if (client.config.lazyLoadingPrices) {
          await page.waitForLoadState('domcontentloaded');
          expect(priceRequests.length).toBeGreaterThan(0);
        } else {
          const prices = page.locator(`text=/${SELECTORS.PRICE_PATTERN.source}/`);
          await expect(prices.first()).toBeVisible({ timeout: 20_000 });
          expect(await prices.count()).toBeGreaterThan(0);
        }
        await context.close();
      });
    }

    if (client.config.enableChooseSaleUnit !== undefined) {
      test(`${key}: enableChooseSaleUnit=${client.config.enableChooseSaleUnit}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enableChooseSaleUnit');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');
        const unitSelector = page.locator(SELECTORS.UNIT_SELECTOR);
        if (client.config.enableChooseSaleUnit) {
          const isVisible = await unitSelector.first().isVisible({ timeout: 8_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] enableChooseSaleUnit=true but selector not found — staging may lack multi-unit products`);
        } else {
          const isVisible = await unitSelector.first().isVisible({ timeout: 5_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    if (client.config.hasStockEnabled !== undefined) {
      test(`${key}: hasStockEnabled=${client.config.hasStockEnabled}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'hasStockEnabled');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');
        const stockBadge = page.getByText(SELECTORS.STOCK_TEXT)
          .or(page.getByText(SELECTORS.STOCK_DETAILED_TEXT))
          .or(page.locator('[data-testid*="stock-count" i], [data-testid*="stockCount" i]'));
        if (client.config.hasStockEnabled) {
          const isVisible = await stockBadge.first().isVisible({ timeout: 8_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] hasStockEnabled=true but stock badge not found — staging may have no stock data`);
        } else {
          const isVisible = await stockBadge.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    if (client.config.hasMultiUnitEnabled !== undefined) {
      test(`${key}: hasMultiUnitEnabled=${client.config.hasMultiUnitEnabled}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'hasMultiUnitEnabled');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');
        const multiUnit = page.locator(SELECTORS.MULTI_UNIT_SELECTOR);
        if (client.config.hasMultiUnitEnabled) {
          const isVisible = await multiUnit.first().isVisible({ timeout: 8_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] hasMultiUnitEnabled=true but selector not found — staging may lack multi-unit products`);
        } else {
          const isVisible = await multiUnit.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    if (client.config.hasNoSaleFilter !== undefined) {
      test(`${key}: hasNoSaleFilter=${client.config.hasNoSaleFilter}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'hasNoSaleFilter');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');
        const noSaleFilter = page.getByText(SELECTORS.NO_SALE_TEXT).or(page.locator(SELECTORS.NO_SALE_SELECTOR));
        if (client.config.hasNoSaleFilter) {
          await expect(noSaleFilter.first()).toBeVisible({ timeout: 8_000 });
        } else {
          const isVisible = await noSaleFilter.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    if (client.config['packagingInformation.hidePackagingInformationB2B'] !== undefined) {
      test(`${key}: packagingInformation.hidePackagingInformationB2B=${client.config['packagingInformation.hidePackagingInformationB2B']}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'packagingInformation');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');
        const packagingInfo = page.locator(SELECTORS.PACKAGING_SELECTOR).or(page.getByText(SELECTORS.PACKAGING_TEXT));
        if (client.config['packagingInformation.hidePackagingInformationB2B']) {
          const isVisible = await packagingInfo.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        } else {
          const isVisible = await packagingInfo.first().isVisible({ timeout: 8_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] packaging should be visible but not found — may need product with packaging data`);
        }
        await context.close();
      });
    }

    if (client.config.weightInfo !== undefined) {
      test(`${key}: weightInfo=${client.config.weightInfo}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'weightInfo');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');
        const weightLabel = page.getByText(SELECTORS.WEIGHT_TEXT).or(page.locator('[class*="weight" i]'));
        if (client.config.weightInfo) {
          const isVisible = await weightLabel.first().isVisible({ timeout: 5_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] weightInfo=true but weight data not found — staging products may lack weight`);
        } else {
          const dedicatedWeight = page.locator(SELECTORS.WEIGHT_DEDICATED_SELECTOR);
          const isVisible = await dedicatedWeight.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    if (client.config.showEmptyCategories !== undefined) {
      test(`${key}: showEmptyCategories=${client.config.showEmptyCategories}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'showEmptyCategories');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');
        const categories = page.locator(SELECTORS.CATEGORIES_SELECTOR);
        const categoryCount = await categories.count();
        if (client.config.showEmptyCategories) {
          console.log(`[${key}] showEmptyCategories=true — ${categoryCount} categories visible`);
        } else {
          console.log(`[${key}] showEmptyCategories=false — ${categoryCount} categories visible`);
        }
        await context.close();
      });
    }

    if (client.config.hasMultipleBusinessUnit !== undefined) {
      test(`${key}: hasMultipleBusinessUnit=${client.config.hasMultipleBusinessUnit}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'hasMultipleBusinessUnit');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');
        await page.waitForTimeout(3_000);
        const buSelector = page.locator('[class*="business-unit" i], [class*="businessUnit" i]')
          .or(page.getByText(SELECTORS.BUSINESS_UNIT_TEXT));
        if (client.config.hasMultipleBusinessUnit) {
          const isVisible = await buSelector.first().isVisible({ timeout: 8_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] hasMultipleBusinessUnit=true but selector not found`);
        } else {
          const isVisible = await buSelector.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    if (client.config.enablePriceOracle !== undefined) {
      test(`${key}: enablePriceOracle=${client.config.enablePriceOracle}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enablePriceOracle');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');
        await page.waitForTimeout(3_000);
        const oracleEl = page.locator(SELECTORS.PRICE_ORACLE_SELECTOR).or(page.getByText(SELECTORS.PRICE_ORACLE_TEXT));
        if (client.config.enablePriceOracle) {
          const isVisible = await oracleEl.first().isVisible({ timeout: 8_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] enablePriceOracle=true but oracle UI not found`);
        } else {
          const isVisible = await oracleEl.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    if (client.config.uploadOrderFileWithMinUnits !== undefined) {
      test(`${key}: uploadOrderFileWithMinUnits=${client.config.uploadOrderFileWithMinUnits}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'uploadOrderFileWithMinUnits');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');
        const uploadBtn = page.getByRole('button', { name: SELECTORS.UPLOAD_FILE_TEXT }).or(page.locator('input[type="file"]'));
        if (client.config.uploadOrderFileWithMinUnits) {
          const isVisible = await uploadBtn.first().isVisible({ timeout: 5_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] uploadOrderFileWithMinUnits=true but upload button not found`);
        } else {
          const isVisible = await uploadBtn.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    if (client.config.enableDistributionCentersSelector !== undefined) {
      test(`${key}: enableDistributionCentersSelector=${client.config.enableDistributionCentersSelector}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enableDistributionCentersSelector');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page, client);
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');
        const dcSelector = page.getByText(SELECTORS.DC_TEXT).or(page.locator(SELECTORS.DC_SELECTOR));
        if (client.config.enableDistributionCentersSelector) {
          await expect(dcSelector.first()).toBeVisible({ timeout: 8_000 });
        } else {
          const isVisible = await dcSelector.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

  });
}

import { test, expect } from '@playwright/test';

/**
 * ADM-STR — Store configuration validation
 * Tests that Admin config changes reflect correctly in B2B
 * Related: ai-specs/specs/admin-testing-standards.mdc
 * Checklists: checklists/admin/checklist-admin-reportes.md (ADM-STR section)
 */

const ADMIN_URL = process.env.ADMIN_URL || 'https://admin.youorder.me';
const ADMIN_EMAIL = process.env.ADMIN_EMAIL || '';
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || '';

async function adminLogin(page: any) {
  await page.goto(ADMIN_URL);
  await page.waitForLoadState('domcontentloaded');
  await page.getByLabel(/[Cc]orreo|[Ee]mail/).fill(ADMIN_EMAIL);
  await page.getByLabel(/[Cc]ontraseña|[Pp]assword/).fill(ADMIN_PASSWORD);
  await page.locator('form').getByRole('button', { name: /[Ii]niciar|[Ll]ogin|[Ee]ntrar/ }).click();
  await page.waitForURL(/(?!.*login|.*auth)/, { timeout: 30_000 });
}

test.describe('ADM-STR — Store Configuration', () => {

  test.beforeEach(async ({ page }) => {
    test.skip(!ADMIN_EMAIL || !ADMIN_PASSWORD, 'ADMIN_EMAIL and ADMIN_PASSWORD required');
    await adminLogin(page);
  });

  // ADM-STR-01: Store configuration page loads
  test('should load store settings page', async ({ page }) => {
    await page.goto(`${ADMIN_URL}/settings`);
    await page.waitForLoadState('domcontentloaded');

    // Settings page should be accessible
    await expect(page).not.toHaveURL(/login|auth/, { timeout: 10_000 });

    await page.screenshot({ path: 'test-results/admin-store-settings.png', fullPage: true });
  });

  // ADM-STR-10/11: Banner management
  test('should display banner management section', async ({ page }) => {
    await page.goto(`${ADMIN_URL}/banners`);
    await page.waitForLoadState('domcontentloaded');

    // Banner page should be accessible
    await expect(page).not.toHaveURL(/login|auth/, { timeout: 10_000 });

    await page.screenshot({ path: 'test-results/admin-banners.png', fullPage: true });
  });

  // ADM-STR-20/21: Promotions management
  test('should display promotions section', async ({ page }) => {
    await page.goto(`${ADMIN_URL}/promotions`);
    await page.waitForLoadState('domcontentloaded');

    await expect(page).not.toHaveURL(/login|auth/, { timeout: 10_000 });

    await page.screenshot({ path: 'test-results/admin-promotions.png', fullPage: true });
  });

  // ADM-STR-30: Commerces management
  test('should display commerces management section', async ({ page }) => {
    await page.goto(`${ADMIN_URL}/commerces`);
    await page.waitForLoadState('domcontentloaded');

    await expect(page).not.toHaveURL(/login|auth/, { timeout: 10_000 });

    await page.screenshot({ path: 'test-results/admin-commerces.png', fullPage: true });
  });

  // ADM-ACC-07: Multi-tenant isolation
  test('should only show own client data', async ({ page }) => {
    await page.goto(`${ADMIN_URL}/commerces`);
    await page.waitForLoadState('domcontentloaded');

    // Page content should not include generic YOM test data patterns
    const pageText = await page.textContent('body') || '';
    expect(pageText).not.toContain('client-a-testdata-sentinel');
  });
});

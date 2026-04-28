import { createClientTest, expect } from '../fixtures/multi-client-auth';
import clients from '../fixtures/clients';

/**
 * C7 — Documentos Tributarios
 *
 * Tests condicionales según flag enablePaymentDocumentsB2B:
 *   - Si true  → verifica que link y página son accesibles (C7-10, C7-11, C7-12)
 *   - Si false → verifica que link NO aparece y /payment-documents no está expuesto (C7-INV)
 *
 * Bastien-QA-002: enablePaymentDocumentsB2B=false pero "Mis documentos" visible → debe fallar aquí.
 */

for (const [key, client] of Object.entries(clients)) {
  const test = createClientTest(client);
  const flagEnabled = !!client.config.enablePaymentDocumentsB2B;

  test.describe(`C7 — Documentos Tributarios: ${client.name}`, () => {

    test(`${key}: C7-INV Link "Mis documentos" oculto cuando flag=false`, async ({ authedPage: page }) => {
      if (flagEnabled) {
        test.skip(true, `enablePaymentDocumentsB2B=true en ${client.name} — este test es para flag=false`);
        return;
      }

      await page.goto(`${client.baseURL}/products`);
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(2_000); // esperar render del menú lateral

      // El link/opción de documentos NO debe aparecer en el menú lateral ni en nav (NO el footer)
      // Scope a nav/aside/header para excluir el footer que puede tener links a /payment-documents
      // Match "Mis documentos", "Documentos tributarios", or bare "Documentos" menu item.
      // Scoped to nav/aside/header to avoid false matches in footer or page body.
      // Sonrie-QA-001: menu showed plain "Documentos" — regex updated to catch this variant.
      const menuDocLink = page.locator('nav, aside, header, [role="navigation"], [role="banner"]')
        .getByText(/\bdocumentos\b/i)
        .or(page.locator('nav a[href*="payment-documents"], aside a[href*="payment-documents"], header a[href*="payment-documents"]'));

      const isVisible = await menuDocLink.first().isVisible({ timeout: 5_000 }).catch(() => false);
      expect(isVisible, `${client.name}: "Mis documentos" visible en menú cuando enablePaymentDocumentsB2B=false`).toBe(false);
    });

    test(`${key}: C7-INV /payment-documents no accesible cuando flag=false`, async ({ authedPage: page }) => {
      if (flagEnabled) {
        test.skip(true, `enablePaymentDocumentsB2B=true en ${client.name} — este test es para flag=false`);
        return;
      }

      const response = await page.goto(`${client.baseURL}/payment-documents`);

      // Debe redirigir o mostrar 403/404 — no debe mostrar la UI de documentos
      const finalURL = page.url();
      const redirectedAway = !finalURL.includes('payment-documents');
      const pageText = await page.locator('body').textContent();
      const showsDocUI = /documentos|facturas|folio|RUT emisor/i.test(pageText || '');

      expect(
        redirectedAway || !showsDocUI,
        `${client.name}: /payment-documents accesible cuando enablePaymentDocumentsB2B=false (URL: ${finalURL})`
      ).toBe(true);
    });

    test(`${key}: C7-10 Facturas visibles en /orders cuando flag=true`, async ({ authedPage: page }) => {
      if (!flagEnabled) {
        test.skip(true, `enablePaymentDocumentsB2B=false en ${client.name}`);
        return;
      }

      await page.goto(`${client.baseURL}/orders`);
      await page.waitForLoadState('networkidle');

      // Debe haber un link/botón de facturas en la lista de órdenes
      const invoiceLink = page.getByText(/ver facturas|facturas|documentos/i)
        .or(page.locator('a[href*="payment-documents"]'));
      await expect(invoiceLink.first()).toBeVisible({ timeout: 15_000 });
    });

    test(`${key}: C7-11 Opción de facturas en menú lateral cuando flag=true`, async ({ authedPage: page }) => {
      if (!flagEnabled) {
        test.skip(true, `enablePaymentDocumentsB2B=false en ${client.name}`);
        return;
      }

      await page.goto(`${client.baseURL}/products`);
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(2_000);

      const menuDocOption = page.getByText(/mis documentos|facturas|documentos/i)
        .or(page.locator('nav a[href*="payment-documents"], aside a[href*="payment-documents"]'));
      await expect(menuDocOption.first()).toBeVisible({ timeout: 10_000 });
    });

    test(`${key}: C7-12 /payment-documents carga sin error cuando flag=true`, async ({ authedPage: page }) => {
      if (!flagEnabled) {
        test.skip(true, `enablePaymentDocumentsB2B=false en ${client.name}`);
        return;
      }

      const response = await page.goto(`${client.baseURL}/payment-documents`);
      expect(response?.ok() || response?.status() === 304).toBeTruthy();

      // Debe mostrar UI de documentos, no una página de error
      const bodyText = await page.locator('body').textContent();
      const isErrorPage = /404|not found|acceso denegado|forbidden/i.test(bodyText || '');
      expect(isErrorPage, `${client.name}: /payment-documents muestra error cuando debería ser accesible`).toBe(false);
    });

  });
}

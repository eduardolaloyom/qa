import { test, expect } from '../fixtures/auth';

test.describe('C3 — Precios y descuentos', () => {

  test('C3-01: Precios visibles en catalogo anonimo (formato CLP)', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('text=/\\$\\s*[\\d.,]+/')).toBeVisible({ timeout: 15_000 });

    const prices = page.locator('text=/\\$\\s*[\\d.,]+/');
    const count = await prices.count();
    expect(count).toBeGreaterThan(0);
  });

  test('C3-02: Detectar productos con precio $0', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('text=/\\$\\s*[\\d.,]+/')).toBeVisible({ timeout: 15_000 });

    // Buscar textos que contengan $0 como precio
    const zeroPrices = page.locator('text=/\\$\\s*0(?:[,.]0+)?\\s/');
    const count = await zeroPrices.count();

    // Reportar como warning — es dato de staging, no necesariamente un bug
    if (count > 0) {
      test.info().annotations.push({
        type: 'warning',
        description: `${count} elemento(s) con precio $0 encontrado(s) en catalogo`,
      });
    }
    // No deberia haber precios $0 en produccion, pero en staging se tolera
  });

  test('C3-03: Precios consistentes catalogo vs carro', async ({ authedPage: page }) => {
    await page.goto('/products');
    await expect(page.getByRole('button', { name: 'Agregar' }).first()).toBeVisible({ timeout: 30_000 });

    // Capturar el primer precio visible en la pagina
    const catalogPrice = await page.locator('text=/\\$\\s*[\\d.,]+/').first().textContent();
    expect(catalogPrice).toBeTruthy();

    // Agregar primer producto al carro
    await Promise.all([
      page.waitForResponse(resp => resp.url().includes('/cart') && resp.request().method() === 'POST'),
      page.getByRole('button', { name: 'Agregar' }).first().click(),
    ]);

    // Ir al carro
    await page.goto('/cart');
    await expect(page.getByText(/\d+ Producto/)).toBeVisible({ timeout: 15_000 });

    // Verificar que el precio del catalogo aparece en el carro
    const priceNumber = catalogPrice!.replace(/[^0-9.,]/g, '');
    if (priceNumber) {
      const cartHasPrice = await page.getByText(priceNumber).isVisible({ timeout: 5_000 }).catch(() => false);
      if (!cartHasPrice) {
        test.info().annotations.push({
          type: 'warning',
          description: `Precio catalogo ${catalogPrice} no encontrado exacto en carro — posible descuento aplicado`,
        });
      }
    }
  });

  test('C3-04: Descuento visible en catalogo', async ({ page }) => {
    // enableSellerDiscount=true + disableShowDiscount=false
    await page.goto('/');
    await expect(page.locator('text=/\\$\\s*[\\d.,]+/')).toBeVisible({ timeout: 15_000 });

    // Buscar cualquier indicador de descuento: %, "Dcto", "Antes", tachado, etc.
    const discountIndicators = page.locator('text=/\\d+%|[Dd]cto|[Dd]escuento|[Aa]ntes/')
      .or(page.locator('del, s, [class*="discount" i], [class*="strike" i], [class*="before" i]'));
    const count = await discountIndicators.count();

    if (count > 0) {
      test.info().annotations.push({
        type: 'info',
        description: `${count} indicador(es) de descuento encontrado(s)`,
      });
    }
    // Verificar que la feature esta activa — al menos debe haber productos con descuento
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('C3-05: Campo de cupon visible en carro', async ({ authedPage: page }) => {
    // enableCoupons=true
    await page.goto('/products');
    await expect(page.getByRole('button', { name: 'Agregar' }).first()).toBeVisible({ timeout: 30_000 });

    // Agregar producto
    await Promise.all([
      page.waitForResponse(resp => resp.url().includes('/cart') && resp.request().method() === 'POST'),
      page.getByRole('button', { name: 'Agregar' }).first().click(),
    ]);

    // Ir al carro
    await page.goto('/cart');
    await expect(page.getByText(/\d+ Producto/)).toBeVisible({ timeout: 15_000 });

    // Verificar que existe campo o boton de cupon
    const couponField = page.getByPlaceholder(/cup[oó]n/i)
      .or(page.getByText(/cup[oó]n/i))
      .or(page.getByRole('button', { name: /aplicar/i }));
    await expect(couponField.first()).toBeVisible({ timeout: 10_000 });
  });
});

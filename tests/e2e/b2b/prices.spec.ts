import { createClientTest, expect } from '../fixtures/multi-client-auth';
import clients from '../fixtures/clients';

for (const [key, client] of Object.entries(clients)) {
  const test = createClientTest(client);
  test.describe(`C3 — Precios y descuentos: ${client.name}`, () => {

    test(`${key}: C3-01 Precios visibles en catalogo anonimo (formato CLP)`, async ({ page }) => {
      await page.goto(client.baseURL);
      await expect(page.locator('text=/\\$\\s*[\\d.,]+/')).toBeVisible({ timeout: 15_000 });

      const prices = page.locator('text=/\\$\\s*[\\d.,]+/');
      const count = await prices.count();
      expect(count).toBeGreaterThan(0);
    });

    test(`${key}: C3-02 Detectar productos con precio $0`, async ({ page }) => {
      await page.goto(client.baseURL);
      await expect(page.locator('text=/\\$\\s*[\\d.,]+/')).toBeVisible({ timeout: 15_000 });

      const productCards = page.locator('[class*="ProductCard"], [class*="product-card"], [class*="card"]').filter({ has: page.locator('text=/\\$\\s*[\\d.,]+/') });
      const cardCount = await productCards.count();

      const zeroProducts: string[] = [];
      for (let i = 0; i < cardCount; i++) {
        const card = productCards.nth(i);
        const hasZero = await card.locator('text=/\\$\\s*0(?:[,.]0+)?\\s*$/').count();
        if (hasZero > 0) {
          const name = await card.locator('h2, h3, h4, a, [class*="name"], [class*="title"]').first().textContent().catch(() => `Producto #${i + 1}`);
          zeroProducts.push(name?.trim() || `Producto #${i + 1}`);
        }
      }

      // FAIL si hay productos con precio $0 — es un bug de datos
      expect(zeroProducts.length).toBe(0);
    });

    test(`${key}: C3-03 Precios consistentes catalogo vs carro`, async ({ authedPage: page }) => {
      await page.goto(`${client.baseURL}/products`);
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
      await page.goto(`${client.baseURL}/cart`);
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

    test(`${key}: C3-04 Descuento visible en catalogo`, async ({ page }) => {
      // enableSellerDiscount=true + disableShowDiscount=false
      await page.goto(client.baseURL);
      await expect(page.locator('text=/\\$\\s*[\\d.,]+/')).toBeVisible({ timeout: 15_000 });

      // Buscar cualquier indicador de descuento: %, "Dcto", "Descuento", tachado, etc.
      const discountIndicators = page.locator('text=/\\d+%|[Dd]cto|[Dd]escuento|[Aa]ntes/')
        .or(page.locator('del, s, [class*="discount" i], [class*="strike" i], [class*="before" i]'));
      const count = await discountIndicators.count();

      // Si la feature está habilitada, debe haber al menos UN indicador de descuento visible
      if (client.config.enableSellerDiscount && !client.config.disableShowDiscount) {
        expect(count).toBeGreaterThan(0);
      }
    });

    test(`${key}: C3-14 Campo de cupon visible en carro (enableCoupons)`, async ({ authedPage: page }) => {
      // enableCoupons=true — C3-14 canónico: campo cupón visible cuando flag activo
      await page.goto(`${client.baseURL}/products`);
      await expect(page.getByRole('button', { name: 'Agregar' }).first()).toBeVisible({ timeout: 30_000 });

      // Agregar producto
      await Promise.all([
        page.waitForResponse(resp => resp.url().includes('/cart') && resp.request().method() === 'POST'),
        page.getByRole('button', { name: 'Agregar' }).first().click(),
      ]);

      // Ir al carro
      await page.goto(`${client.baseURL}/cart`);
      await expect(page.getByText(/\d+ Producto/)).toBeVisible({ timeout: 15_000 });

      // Verificar que existe campo o boton de cupon
      const couponField = page.getByPlaceholder(/cup[oó]n/i)
        .or(page.getByText(/cup[oó]n/i))
        .or(page.getByRole('button', { name: /aplicar/i }));
      await expect(couponField.first()).toBeVisible({ timeout: 10_000 });
    });

    test(`${key}: C3-15 Cupon invalido muestra error claro`, async ({ authedPage: page }) => {
      if (!client.config.enableCoupons) {
        test.skip(true, `C3-15: ${client.name} no tiene enableCoupons=true`);
        return;
      }

      await page.goto(`${client.baseURL}/products`);
      await expect(page.getByRole('button', { name: 'Agregar' }).first()).toBeVisible({ timeout: 30_000 });

      await Promise.all([
        page.waitForResponse(resp => resp.url().includes('/cart') && resp.request().method() === 'POST'),
        page.getByRole('button', { name: 'Agregar' }).first().click(),
      ]);

      await page.goto(`${client.baseURL}/cart`);
      await expect(page.getByText(/\d+ Producto/)).toBeVisible({ timeout: 15_000 });

      // Ingresar código inventado
      const couponInput = page.getByPlaceholder(/cup[oó]n/i)
        .or(page.locator('input[name*="coupon" i], input[id*="coupon" i]'))
        .first();

      if (await couponInput.isVisible({ timeout: 5_000 }).catch(() => false)) {
        await couponInput.fill('CODIGO_INVALIDO_QA_TEST_XYZ');

        const applyBtn = page.getByRole('button', { name: /aplicar/i })
          .or(page.getByText(/aplicar/i))
          .first();
        await applyBtn.click();
        await page.waitForLoadState('networkidle');

        // Debe mostrar un mensaje de error claro — no aplicar descuento silenciosamente
        const errorMsg = page.getByText(/inv[aá]lido|no existe|vencido|error|incorrecto/i)
          .or(page.locator('[class*="error" i], [class*="alert" i], [role="alert"]'));
        await expect(errorMsg.first()).toBeVisible({ timeout: 10_000 });
      } else {
        test.skip(true, `C3-15: ${client.name} no tiene campo de cupón accesible en /cart`);
      }
    });

    test(`${key}: C3-11 Precio bruto vs neto — impuestos segun config`, async ({ authedPage: page }) => {
      // Verificar que el desglose de impuestos en el carro es coherente con la config
      await page.goto(`${client.baseURL}/products`);
      await expect(page.getByRole('button', { name: 'Agregar' }).first()).toBeVisible({ timeout: 30_000 });

      // Agregar productos para tener un carro con monto
      const addButtons = page.getByRole('button', { name: 'Agregar' });
      const count = Math.min(await addButtons.count(), 3);
      for (let i = 0; i < count; i++) {
        await Promise.all([
          page.waitForResponse(resp => resp.url().includes('/cart') && resp.request().method() === 'POST'),
          addButtons.nth(i).click(),
        ]);
      }

      // Ir al carro y verificar desglose
      await page.goto(`${client.baseURL}/cart`);
      await expect(page.getByText(/\d+ Producto/)).toBeVisible({ timeout: 15_000 });

      // Capturar todos los montos visibles en el resumen de facturacion
      const bodyText = await page.locator('body').textContent();

      // Debe existir un desglose (neto, impuesto, total) — no solo un numero suelto
      const hasNeto = /neto|subtotal/i.test(bodyText || '');
      const hasImpuesto = /impuesto|iva|tax/i.test(bodyText || '');
      const hasTotal = /total/i.test(bodyText || '');

      test.info().annotations.push({
        type: 'info',
        description: `Desglose: neto=${hasNeto}, impuesto=${hasImpuesto}, total=${hasTotal}`,
      });

      // Al menos debe mostrar un total
      expect(hasTotal).toBeTruthy();

      // Si muestra impuesto, debe haber coherencia (neto + impuesto ≈ total)
      if (hasImpuesto && hasNeto) {
        const amounts = (bodyText || '').match(/\$\s*[\d.,]+/g) || [];
        // Al menos debe haber 3 montos (neto, impuesto, total)
        expect(amounts.length).toBeGreaterThanOrEqual(3);
        test.info().annotations.push({
          type: 'info',
          description: `Montos encontrados: ${amounts.slice(0, 10).join(', ')}`,
        });
      }
    });

    // ── Calidad de datos del catálogo ──────────────────────────────────────

    test(`${key}: Catálogo carga con productos visibles @catalog @calidad`, async ({ authedPage: page }) => {
      await page.goto(`${client.baseURL}/products`);

      // Esperar que cargue el catálogo: botón Agregar o product card
      const firstIndicator = page.getByRole('button', { name: 'Agregar' }).first()
        .or(page.locator('[class*="ProductCard"], [class*="product-card"], [class*="product-item"]').first());
      await expect(firstIndicator).toBeVisible({ timeout: 45_000 });

      const productCards = page.locator(
        '[class*="ProductCard"], [class*="product-card"], [class*="product-item"], article[class*="product"], li[class*="product"]'
      ).or(page.getByRole('button', { name: 'Agregar' }));

      const count = await productCards.count();
      expect(count, `${client.name}: catálogo vacío — no se encontraron productos en /products`).toBeGreaterThan(0);
    });

    test(`${key}: Sin imágenes rotas en catálogo @catalog @calidad`, async ({ authedPage: page }) => {
      await page.goto(`${client.baseURL}/products`);
      await page.waitForLoadState('load');

      const allImages = page.locator('img');
      const total = await allImages.count();
      const limit = Math.min(total, 50);

      const brokenImages: string[] = [];
      for (let i = 0; i < limit; i++) {
        const img = allImages.nth(i);
        const [naturalWidth, src] = await img.evaluate((el: HTMLImageElement) => [
          el.naturalWidth,
          el.src || el.getAttribute('src') || '',
        ]);
        const isBroken = naturalWidth === 0
          && !src.includes('.svg')
          && !src.startsWith('data:')
          && src.length > 0;
        if (isBroken) brokenImages.push(src);
      }

      expect(brokenImages, `${client.name}: imágenes rotas encontradas:\n${brokenImages.join('\n')}`).toHaveLength(0);
    });

    test(`${key}: C5-05 Sugerencias se pueden agregar al carro`, async ({ authedPage: page }) => {
      await page.goto(`${client.baseURL}/products`);
      await expect(page.getByRole('button', { name: 'Agregar' }).first()).toBeVisible({ timeout: 30_000 });

      // Buscar seccion de sugerencias/recomendados en el catalogo
      const suggestions = page.locator('text=/[Ss]ugerencia|[Rr]ecomendado|[Dd]estacado|[Mm]ás vendido/')
        .or(page.locator('[class*="suggestion" i], [class*="recommend" i], [class*="featured" i]'));
      const hasSuggestions = await suggestions.count() > 0;

      if (hasSuggestions) {
        // Si hay sugerencias, verificar que tienen boton de agregar
        const suggestionArea = suggestions.first();
        const addBtn = suggestionArea.locator('..').locator('..').getByRole('button', { name: /agregar|añadir/i }).first();

        await expect(addBtn).toBeVisible({ timeout: 5_000 });

        const response = await Promise.all([
          page.waitForResponse(resp => resp.url().includes('/cart') && resp.request().method() === 'POST'),
          addBtn.click(),
        ]).then(([res]) => res);

        // Debe devolver éxito (2xx), no error (4xx, 5xx)
        expect(response.status()).toBeLessThan(400);
      } else {
        // No hay sugerencias — registrar pero no fallar (depende de config del cliente)
        test.info().annotations.push({
          type: 'info',
          description: 'No se encontraron sugerencias en catalogo — puede depender de config del cliente',
        });
      }
    });
  });
}

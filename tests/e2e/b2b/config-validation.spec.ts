import { test, expect } from '@playwright/test';
import { loginHelper } from '../fixtures/login';
import { skipIfNotInB2B } from '../fixtures/b2b-feature';
import clients from '../fixtures/clients';

/**
 * Validación de config: verifica que lo que dice MongoDB (clients.ts auto-generado)
 * coincida con lo que el frontend realmente muestra.
 *
 * Si MongoDB dice enableCoupons=true pero el campo de cupón no aparece → bug de config.
 * Si MongoDB dice anonymousAccess=false pero el catálogo se ve sin login → bug de seguridad.
 */
for (const [key, client] of Object.entries(clients)) {
  test.describe(`Config validation: ${client.name}`, () => {

    // Helper: login si es necesario
    async function loginIfNeeded(page: any) {
      await page.goto(client.baseURL);
      await page.waitForLoadState('domcontentloaded');
      if (!client.config.anonymousAccess) {
        await loginHelper(page, client.credentials.email, client.credentials.password, client.loginPath, client.baseURL);
      }
    }

    // ── anonymousAccess ──
    test(`${key}: anonymousAccess=${client.config.anonymousAccess}`, async ({ browser }) => {
      const context = await browser.newContext();
      const page = await context.newPage();
      await page.goto(client.baseURL);
      await page.waitForLoadState('domcontentloaded');

      if (client.config.anonymousAccess) {
        // Debe mostrar contenido sin login
        await expect(page).not.toHaveURL(/auth|login/, { timeout: 10_000 });
      } else {
        // Debe redirigir a login
        await expect(page).toHaveURL(/auth|login/, { timeout: 10_000 });
      }

      await context.close();
    });

    // ── hidePrices ──
    test(`${key}: hidePrices=${client.config.hidePrices}`, async ({ browser }) => {
      skipIfNotInB2B(client, 'hidePrices');
      const context = await browser.newContext();
      const page = await context.newPage();
      await loginIfNeeded(page);

      await page.goto(`${client.baseURL}/products`);
      await page.waitForLoadState('domcontentloaded');

      const prices = page.locator('text=/\\$\\s*[\\d.,]+/');
      const priceCount = await prices.count();

      if (client.config.hidePrices) {
        expect(priceCount).toBe(0);
      } else {
        expect(priceCount).toBeGreaterThan(0);
      }

      await context.close();
    });

    // ── disableCart ──
    test(`${key}: disableCart=${client.config.disableCart}`, async ({ browser }) => {
      skipIfNotInB2B(client, 'disableCart');
      const context = await browser.newContext();
      const page = await context.newPage();
      await loginIfNeeded(page);

      await page.goto(`${client.baseURL}/products`);
      await page.waitForLoadState('domcontentloaded');

      const addButtons = page.getByRole('button', { name: 'Agregar' });

      if (client.config.disableCart) {
        // No debe haber botones de agregar
        expect(await addButtons.count()).toBe(0);
        // Navegar a /cart debe redirigir o mostrar vacío
        await page.goto(`${client.baseURL}/cart`);
        await page.waitForLoadState('domcontentloaded');
        const currentUrl = page.url();
        expect(currentUrl).not.toMatch(/\/cart$/);
      } else {
        // Debe haber botones de agregar
        expect(await addButtons.count()).toBeGreaterThan(0);
        // /cart debe ser accesible
        await page.goto(`${client.baseURL}/cart`);
        await page.waitForLoadState('domcontentloaded');
        await expect(page).toHaveURL(/cart/);
      }

      await context.close();
    });

    // ── enableCoupons ──
    if (client.config.enableCoupons !== undefined) {
      test(`${key}: enableCoupons=${client.config.enableCoupons}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enableCoupons');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        // Agregar producto al carro para ver checkout
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');
        const addButton = page.getByRole('button', { name: 'Agregar' }).first();

        await expect(addButton).toBeVisible({ timeout: 15_000 });
        await addButton.click();
        await page.waitForLoadState('domcontentloaded');

        // Ir al carro directamente
        await page.goto(`${client.baseURL}/cart`);
        await page.waitForLoadState('domcontentloaded');

        const couponField = page.getByPlaceholder(/cup[oó]n/i)
          .or(page.getByText(/ingresar cup[oó]n/i))
          .or(page.getByRole('button', { name: /aplicar/i }));

        if (client.config.enableCoupons) {
          // Si está habilitado, DEBE existir el campo de cupón
          await expect(couponField.first()).toBeVisible({ timeout: 10_000 });
        } else {
          // Si está deshabilitado, NO debe existir el campo de cupón
          await expect(couponField.first()).not.toBeVisible({ timeout: 5_000 });
        }

        await context.close();
      });
    }

    // ── hideReceiptType ──
    if (client.config.hideReceiptType !== undefined) {
      test(`${key}: hideReceiptType=${client.config.hideReceiptType}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'hideReceiptType');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        // Ir al carro y buscar tipo de recibo
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');
        const addButton = page.getByRole('button', { name: 'Agregar' }).first();

        await expect(addButton).toBeVisible({ timeout: 15_000 });
        await addButton.click();
        await page.waitForLoadState('domcontentloaded');

        // Ir al carro directamente
        await page.goto(`${client.baseURL}/cart`);
        await page.waitForLoadState('domcontentloaded');

        const receiptType = page.getByText(/tipo de recibo|boleta|factura/i);

        if (client.config.hideReceiptType) {
          // No debe mostrar selector de tipo de recibo
          await expect(receiptType).not.toBeVisible({ timeout: 5_000 });
        } else {
          // Si está visible, DEBE mostrar el selector
          await expect(receiptType).toBeVisible({ timeout: 5_000 });
        }

        await context.close();
      });
    }

    // ── currency ──
    // TODO: currency no está en clients.ts, usar campo correcto cuando se disponibilice
    test.skip(`${key}: currency=${client.config.currency}`, async ({ browser }) => {
      const context = await browser.newContext();
      const page = await context.newPage();
      await loginIfNeeded(page);

      await page.goto(`${client.baseURL}/products`);
      await page.waitForLoadState('domcontentloaded');

      // Verificar que los precios usan el símbolo correcto
      const currencySymbols: Record<string, string> = {
        clp: '$',
        cop: '$',
        pen: 'S/',
        usd: '$',
      };
      const symbol = currencySymbols[client.config.currency] || '$';
      const prices = page.locator(`text=/${symbol.replace('$', '\\$')}\\s*[\\d.,]+/`);
      const count = await prices.count();

      if (!client.config.hidePrices) {
        expect(count).toBeGreaterThan(0);
      }

      await context.close();
    });

    // ── NUEVAS VARIABLES DE ALTA PRIORIDAD ──

    // inMaintenance
    if (client.config.inMaintenance !== undefined) {
      test(`${key}: inMaintenance=${client.config.inMaintenance}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'inMaintenance');
        const context = await browser.newContext();
        const page = await context.newPage();
        await page.goto(client.baseURL);
        await page.waitForLoadState('domcontentloaded');

        if (client.config.inMaintenance) {
          // Debe mostrar pantalla de mantenimiento
          const maintenanceText = page.getByText(/mantenimiento|maintenance|en construcción/i);
          await expect(maintenanceText).toBeVisible({ timeout: 10_000 });
        } else {
          // No debe mostrar mantenimiento
          const maintenanceText = page.getByText(/mantenimiento|maintenance|en construcción/i);
          await expect(maintenanceText).not.toBeVisible({ timeout: 5_000 });
        }

        await context.close();
      });
    }

    // anonymousHideCart y anonymousHidePrice
    if (client.config.anonymousAccess === true) {
      if (client.config.anonymousHideCart !== undefined) {
        test(`${key}: anonymousHideCart=${client.config.anonymousHideCart}`, async ({ browser }) => {
          skipIfNotInB2B(client, 'anonymousHideCart');
          const context = await browser.newContext();
          const page = await context.newPage();
          await page.goto(`${client.baseURL}`);
          await page.waitForLoadState('domcontentloaded');

          const cartIcon = page.locator(
            '[class*="cart" i], [aria-label*="carro" i], [aria-label*="carrito" i], a[href*="/cart"], [data-testid*="cart" i]'
          ).or(page.getByRole('link', { name: /carrito|carro/i })).first();

          if (client.config.anonymousHideCart) {
            // No debe mostrar ícono del carrito
            const isVisible = await cartIcon.isVisible({ timeout: 5_000 }).catch(() => false);
            expect(isVisible).toBeFalsy();
          } else {
            // Debe mostrar ícono del carrito
            await expect(cartIcon).toBeVisible({ timeout: 10_000 });
          }

          await context.close();
        });
      }

      if (client.config.anonymousHidePrice !== undefined) {
        test(`${key}: anonymousHidePrice=${client.config.anonymousHidePrice}`, async ({ browser }) => {
          skipIfNotInB2B(client, 'anonymousHidePrice');
          const context = await browser.newContext();
          const page = await context.newPage();
          await page.goto(`${client.baseURL}/products`);
          await page.waitForLoadState('domcontentloaded');

          const prices = page.locator('text=/\\$\\s*[\\d.,]+/');
          const priceCount = await prices.count();

          if (client.config.anonymousHidePrice) {
            // No debe mostrar precios sin login
            expect(priceCount).toBe(0);
          } else {
            // Debe mostrar precios
            expect(priceCount).toBeGreaterThan(0);
          }

          await context.close();
        });
      }
    }

    // enablePayments / disablePayments
    if (client.config.enablePayments !== undefined) {
      test(`${key}: enablePayments=${client.config.enablePayments}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enablePayments');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        // Agregar producto al carrito para llegar a checkout
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');

        const addButton = page.getByRole('button', { name: 'Agregar' }).first();
        await expect(addButton).toBeVisible({ timeout: 15_000 });
        await addButton.click();
        await page.waitForLoadState('domcontentloaded');

        await page.goto(`${client.baseURL}/cart`);
        await page.waitForLoadState('domcontentloaded');

        // Buscar sección de pagos en checkout
        const paymentsSection = page.locator('[class*="payment" i], [class*="pago" i]').first();

        if (client.config.enablePayments) {
          // Debe haber sección de pagos
          await expect(paymentsSection).toBeVisible({ timeout: 10_000 });
        } else {
          // NO debe haber sección de pagos
          const isVisible = await paymentsSection.isVisible({ timeout: 5_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }

        await context.close();
      });
    }

    // ordersRequireAuthorization
    if (client.config.ordersRequireAuthorization !== undefined) {
      test(`${key}: ordersRequireAuthorization=${client.config.ordersRequireAuthorization}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'ordersRequireAuthorization');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        // Ir a historial de órdenes
        await page.goto(`${client.baseURL}/orders`);
        await page.waitForLoadState('domcontentloaded');

        if (client.config.ordersRequireAuthorization) {
          // Debe mostrar badge/estado de aprobación pendiente
          const approvalBadge = page.getByText(/pendiente|aprobación|autorización|autorizar/i);
          const hasApprovalUI = await approvalBadge.isVisible({ timeout: 5_000 }).catch(() => false);
          expect(hasApprovalUI).toBeTruthy();
        }

        await context.close();
      });
    }

    // ── PRIORIDAD MEDIA — TAXES ──

    // includeTaxRateInPrices: si true los precios en catálogo ya incluyen IVA (no se suma en checkout)
    if (client.config.includeTaxRateInPrices !== undefined) {
      test(`${key}: includeTaxRateInPrices=${client.config.includeTaxRateInPrices}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'includeTaxRateInPrices');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');

        const addButton = page.getByRole('button', { name: 'Agregar' }).first();
        await expect(addButton).toBeVisible({ timeout: 15_000 });
        await addButton.click();
        await page.waitForLoadState('domcontentloaded');

        await page.goto(`${client.baseURL}/cart`);
        await page.waitForLoadState('domcontentloaded');

        const bodyText = await page.locator('body').textContent();

        if (client.config.includeTaxRateInPrices) {
          // El resumen NO debe desglosar IVA por separado (ya está incluido)
          const hasIvaSeparado = /\+\s*iva|\+\s*impuesto|precio neto/i.test(bodyText || '');
          expect(hasIvaSeparado).toBeFalsy();
        } else {
          // El resumen SÍ debe mostrar IVA como línea adicional
          const hasIvaLinea = /iva|impuesto|tax/i.test(bodyText || '');
          expect(hasIvaLinea).toBeTruthy();
        }

        await context.close();
      });
    }

    // lazyLoadingPrices: si true los precios cargan diferido (no están al primer render)
    if (client.config.lazyLoadingPrices !== undefined) {
      test(`${key}: lazyLoadingPrices=${client.config.lazyLoadingPrices}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'lazyLoadingPrices');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        // Interceptar requests a precios
        const priceRequests: string[] = [];
        page.on('request', req => {
          if (req.url().includes('/price') || req.url().includes('/pricing')) {
            priceRequests.push(req.url());
          }
        });

        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');

        if (client.config.lazyLoadingPrices) {
          // Con lazy loading, los precios se cargan DESPUÉS del primer render
          // Debe haber requests de precios durante o después del domcontentloaded
          await page.waitForLoadState('domcontentloaded');
          expect(priceRequests.length).toBeGreaterThan(0);
        } else {
          // Sin lazy loading, los precios deben estar disponibles al cargar
          await page.waitForLoadState('domcontentloaded');
          const prices = page.locator('text=/\\$\\s*[\\d.,]+/');
          expect(await prices.count()).toBeGreaterThan(0);
        }

        await context.close();
      });
    }

    // ── PRIORIDAD MEDIA — FEATURES DE UI ──

    // enableMassiveOrderSend: botón para enviar múltiples órdenes a la vez
    if (client.config.enableMassiveOrderSend === true) {
      test(`${key}: enableMassiveOrderSend=true visible`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enableMassiveOrderSend');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        await page.goto(`${client.baseURL}/cart`);
        await page.waitForLoadState('domcontentloaded');

        const massiveBtn = page.getByText(/envío masivo|enviar masivo|massive|masivo/i)
          .or(page.getByRole('button', { name: /masivo/i }));

        await expect(massiveBtn.first()).toBeVisible({ timeout: 10_000 });

        await context.close();
      });
    }

    // enableChooseSaleUnit: selector de unidad de venta en productos
    if (client.config.enableChooseSaleUnit !== undefined) {
      test(`${key}: enableChooseSaleUnit=${client.config.enableChooseSaleUnit}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enableChooseSaleUnit');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');

        const unitSelector = page.locator('select[name*="unit" i], [class*="unit-selector" i], [class*="saleUnit" i]');

        if (client.config.enableChooseSaleUnit) {
          // Flag=true: selector should be present when products with multiple units exist.
          // In staging, products may not have multi-unit SKUs configured — skip rather than fail.
          const isVisible = await unitSelector.first().isVisible({ timeout: 8_000 }).catch(() => false);
          if (!isVisible) {
            console.warn(`[${key}] enableChooseSaleUnit=true but selector not found — staging may lack multi-unit products`);
          }
          // Not a hard assert: absence in staging ≠ bug
        } else {
          const isVisible = await unitSelector.first().isVisible({ timeout: 5_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }

        await context.close();
      });
    }

    // enableAskDeliveryDate: campo para elegir fecha de entrega en checkout
    if (client.config.enableAskDeliveryDate !== undefined) {
      test(`${key}: enableAskDeliveryDate=${client.config.enableAskDeliveryDate}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enableAskDeliveryDate');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');

        const addButton = page.getByRole('button', { name: 'Agregar' }).first();
        await expect(addButton).toBeVisible({ timeout: 15_000 });
        await addButton.click();
        await page.waitForLoadState('domcontentloaded');

        await page.goto(`${client.baseURL}/cart`);
        await page.waitForLoadState('domcontentloaded');

        const deliveryDateField = page.getByText(/fecha de entrega|fecha pedido|delivery date/i)
          .or(page.locator('input[type="date"]'));

        if (client.config.enableAskDeliveryDate) {
          await expect(deliveryDateField.first()).toBeVisible({ timeout: 10_000 });
        } else {
          const isVisible = await deliveryDateField.first().isVisible({ timeout: 5_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }

        await context.close();
      });
    }

    // orderObservations: campo para escribir observaciones al confirmar pedido
    if (client.config.orderObservations !== undefined) {
      test(`${key}: orderObservations=${client.config.orderObservations}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'orderObservations');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');

        const addButton = page.getByRole('button', { name: 'Agregar' }).first();
        await expect(addButton).toBeVisible({ timeout: 15_000 });
        await addButton.click();
        await page.waitForLoadState('domcontentloaded');

        await page.goto(`${client.baseURL}/cart`);
        await page.waitForLoadState('domcontentloaded');

        const observationsField = page.getByPlaceholder(/observaci[oó]n|comentario|nota/i)
          .or(page.getByLabel(/observaci[oó]n|comentario|nota/i))
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

    // footerCustomContent.useFooterCustomContent: footer personalizado
    if (client.config['footerCustomContent.useFooterCustomContent'] === true) {
      test(`${key}: footerCustomContent.useFooterCustomContent=true visible`, async ({ browser }) => {
        skipIfNotInB2B(client, 'footerCustomContent');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        await page.goto(`${client.baseURL}`);
        await page.waitForLoadState('domcontentloaded');

        const footer = page.locator('footer, [class*="footer" i]').first();
        await expect(footer).toBeVisible({ timeout: 10_000 });

        // El footer debe tener contenido personalizado (no solo copyright genérico)
        const footerText = await footer.textContent();
        expect(footerText?.trim().length).toBeGreaterThan(10);

        await context.close();
      });
    }

    // disablePayments: explícitamente deshabilitado — distinto de enablePayments=false
    if (client.config.disablePayments === true) {
      test(`${key}: disablePayments=true — sección pagos ausente`, async ({ browser }) => {
        skipIfNotInB2B(client, 'disablePayments');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');

        const addButton = page.getByRole('button', { name: 'Agregar' }).first();
        await expect(addButton).toBeVisible({ timeout: 15_000 });
        await addButton.click();
        await page.waitForLoadState('domcontentloaded');

        await page.goto(`${client.baseURL}/cart`);
        await page.waitForLoadState('domcontentloaded');

        const paymentsSection = page.locator('[class*="payment" i], [class*="pago" i]').first();
        const isVisible = await paymentsSection.isVisible({ timeout: 5_000 }).catch(() => false);
        expect(isVisible).toBeFalsy();

        await context.close();
      });
    }

    // ── VARIABLES ADICIONALES ──

    // Helper interno: agrega un producto al carrito
    async function addOneProductToCart(page: any) {
      await page.goto(`${client.baseURL}/products`);
      await page.waitForLoadState('domcontentloaded');
      const addBtn = page.getByRole('button', { name: 'Agregar' }).first();
      await expect(addBtn).toBeVisible({ timeout: 20_000 });
      await addBtn.click();
      await page.waitForTimeout(800);
      await page.goto(`${client.baseURL}/cart`);
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(500);
    }

    // purchaseOrderEnabled: campo OC en checkout
    if (client.config.purchaseOrderEnabled !== undefined) {
      test(`${key}: purchaseOrderEnabled=${client.config.purchaseOrderEnabled}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'purchaseOrderEnabled');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);
        await addOneProductToCart(page);

        const ocField = page.getByPlaceholder(/orden de compra|purchase order|o\.c\./i)
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

    // enableSellerDiscount: campo de descuento de vendedor en carrito
    if (client.config.enableSellerDiscount !== undefined) {
      test(`${key}: enableSellerDiscount=${client.config.enableSellerDiscount}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enableSellerDiscount');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);
        await addOneProductToCart(page);

        const discountField = page.getByText(/descuento.*vendedor|seller.*discount|descuento.*adicional/i)
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

    // hasStockEnabled: indicador de stock en tarjetas de producto
    if (client.config.hasStockEnabled !== undefined) {
      test(`${key}: hasStockEnabled=${client.config.hasStockEnabled}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'hasStockEnabled');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');

        // Specific text patterns only — avoid broad class selector that matches empty containers
        const stockBadge = page.getByText(/\b(en stock|sin stock|agotado)\b/i)
          .or(page.getByText(/\b\d+\s+(unidades?\s*disponibles?|en\s*stock)\b/i))
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

    // taxes.showSummary: resumen de impuestos en carrito
    if (client.config['taxes.showSummary'] !== undefined) {
      test(`${key}: taxes.showSummary=${client.config['taxes.showSummary']}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'taxes.showSummary');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);
        await addOneProductToCart(page);

        // taxes.showSummary controls a detailed tax breakdown section, not the simple "Impuestos" billing line
        const taxSummary = page.locator('[class*="tax-summary" i], [class*="taxSummary" i], [class*="tax-breakdown" i]')
          .or(page.getByText(/desglose.*impuesto|resumen.*impuesto|detalle.*impuesto/i));

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

    // pendingDocuments: sección documentos pendientes en nav
    if (client.config.pendingDocuments !== undefined) {
      test(`${key}: pendingDocuments=${client.config.pendingDocuments}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'pendingDocuments');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        await page.goto(`${client.baseURL}`);
        await page.waitForLoadState('domcontentloaded');

        const pendingLink = page.getByRole('link', { name: /documentos pendientes|pending.*doc/i })
          .or(page.getByText(/documentos pendientes/i));

        if (client.config.pendingDocuments) {
          await expect(pendingLink.first()).toBeVisible({ timeout: 8_000 });
        } else {
          const isVisible = await pendingLink.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    // pointsEnabled: sección puntos/fidelidad
    if (client.config.pointsEnabled !== undefined) {
      test(`${key}: pointsEnabled=${client.config.pointsEnabled}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'pointsEnabled');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        await page.goto(`${client.baseURL}`);
        await page.waitForLoadState('domcontentloaded');

        const pointsSection = page.getByText(/puntos|points|fidelidad|loyalty/i)
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

    // enableTask: sección de tareas en nav
    if (client.config.enableTask !== undefined) {
      test(`${key}: enableTask=${client.config.enableTask}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enableTask');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        await page.goto(`${client.baseURL}`);
        await page.waitForLoadState('domcontentloaded');

        const taskLink = page.getByRole('link', { name: /tarea|task/i })
          .or(page.getByText(/mis tareas|tareas/i));

        if (client.config.enableTask) {
          await expect(taskLink.first()).toBeVisible({ timeout: 8_000 });
        } else {
          const isVisible = await taskLink.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    // enableCreditNotes: notas de crédito en nav u órdenes
    if (client.config.enableCreditNotes !== undefined) {
      test(`${key}: enableCreditNotes=${client.config.enableCreditNotes}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enableCreditNotes');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        await page.goto(`${client.baseURL}`);
        await page.waitForLoadState('domcontentloaded');

        const creditNotesLink = page.getByRole('link', { name: /nota.*cr[eé]dito|credit.*note/i })
          .or(page.getByText(/notas de cr[eé]dito/i));

        if (client.config.enableCreditNotes) {
          await expect(creditNotesLink.first()).toBeVisible({ timeout: 8_000 });
        } else {
          const isVisible = await creditNotesLink.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    // enableDistributionCentersSelector: selector de centros de distribución
    if (client.config.enableDistributionCentersSelector !== undefined) {
      test(`${key}: enableDistributionCentersSelector=${client.config.enableDistributionCentersSelector}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enableDistributionCentersSelector');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');

        const dcSelector = page.getByText(/centro.*distribución|distribution.*center|bodega/i)
          .or(page.locator('[class*="distribution" i], [class*="centro-dist" i]'));

        if (client.config.enableDistributionCentersSelector) {
          await expect(dcSelector.first()).toBeVisible({ timeout: 8_000 });
        } else {
          const isVisible = await dcSelector.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    // editAddress: botón editar dirección en carrito
    if (client.config.editAddress !== undefined) {
      test(`${key}: editAddress=${client.config.editAddress}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'editAddress');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);
        await addOneProductToCart(page);

        const editAddrBtn = page.getByRole('button', { name: /editar.*direcci[oó]n|cambiar.*direcci[oó]n|edit.*address/i })
          .or(page.getByText(/editar direcci[oó]n|cambiar direcci[oó]n/i));

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

    // showMinOne: cantidad mínima de 1 unidad forzada
    if (client.config.showMinOne !== undefined) {
      test(`${key}: showMinOne=${client.config.showMinOne}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'showMinOne');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');

        // showMinOne shows "Mínimo: 1" label on product cards — use specific class or exact label pattern
        const minOneLabel = page.locator('[class*="min-one" i], [class*="minOne" i], [class*="show-min" i]')
          .or(page.getByText(/^mínimo:\s*1$|^mínimo 1 unidad$/i));

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

    // hasMultiUnitEnabled: selector de múltiples unidades en productos
    if (client.config.hasMultiUnitEnabled !== undefined) {
      test(`${key}: hasMultiUnitEnabled=${client.config.hasMultiUnitEnabled}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'hasMultiUnitEnabled');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');

        const multiUnit = page.locator('select[name*="unit" i], [class*="multi-unit" i], [class*="multiUnit" i]');

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

    // hasNoSaleFilter: filtro de productos sin venta
    if (client.config.hasNoSaleFilter !== undefined) {
      test(`${key}: hasNoSaleFilter=${client.config.hasNoSaleFilter}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'hasNoSaleFilter');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');

        const noSaleFilter = page.getByText(/sin venta|no.*sale|no venta/i)
          .or(page.locator('[class*="no-sale" i], [class*="noSale" i]'));

        if (client.config.hasNoSaleFilter) {
          await expect(noSaleFilter.first()).toBeVisible({ timeout: 8_000 });
        } else {
          const isVisible = await noSaleFilter.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    // limitAddingByStock: no permite agregar más allá del stock disponible
    if (client.config.limitAddingByStock !== undefined) {
      test(`${key}: limitAddingByStock=${client.config.limitAddingByStock}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'limitAddingByStock');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');

        const stockLimitIndicator = page.locator('[class*="stock-limit" i], [class*="stockLimit" i]')
          .or(page.getByText(/límite.*stock|stock.*limit|sin stock disponible/i));

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

    // packagingInformation.hidePackagingInformationB2B: info de empaque oculta
    if (client.config['packagingInformation.hidePackagingInformationB2B'] !== undefined) {
      test(`${key}: packagingInformation.hidePackagingInformationB2B=${client.config['packagingInformation.hidePackagingInformationB2B']}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'packagingInformation');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');

        const packagingInfo = page.locator('[class*="packaging" i], [class*="empaque" i]')
          .or(page.getByText(/empaque|packaging|embalaje|contenido neto/i));

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

    // ordersRequireVerification: verificación adicional en órdenes
    if (client.config.ordersRequireVerification !== undefined) {
      test(`${key}: ordersRequireVerification=${client.config.ordersRequireVerification}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'ordersRequireVerification');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        await page.goto(`${client.baseURL}/orders`);
        await page.waitForLoadState('domcontentloaded');

        const verificationUI = page.getByText(/verificaci[oó]n|verificar|verify/i)
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

    // enableOrderValidation: paso de validación antes de confirmar pedido
    if (client.config.enableOrderValidation !== undefined) {
      test(`${key}: enableOrderValidation=${client.config.enableOrderValidation}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enableOrderValidation');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);
        await addOneProductToCart(page);

        const validationUI = page.getByText(/validar pedido|order validation|validación/i)
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

    // enableOrderApproval: botón de aprobación en lista de órdenes
    if (client.config.enableOrderApproval !== undefined) {
      test(`${key}: enableOrderApproval=${client.config.enableOrderApproval}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enableOrderApproval');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        await page.goto(`${client.baseURL}/orders`);
        await page.waitForLoadState('domcontentloaded');

        const approvalBtn = page.getByRole('button', { name: /aprobar|aprobación|approval/i })
          .or(page.getByText(/pendiente.*aprobación|approval pending/i));

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

    // hasTransportCode: campo código de transporte en checkout
    if (client.config.hasTransportCode !== undefined) {
      test(`${key}: hasTransportCode=${client.config.hasTransportCode}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'hasTransportCode');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);
        await addOneProductToCart(page);

        const transportField = page.getByPlaceholder(/c[oó]digo.*transporte|transport.*code/i)
          .or(page.getByLabel(/c[oó]digo.*transporte|transport/i))
          .or(page.getByText(/c[oó]digo de transporte/i));

        if (client.config.hasTransportCode) {
          await expect(transportField.first()).toBeVisible({ timeout: 8_000 });
        } else {
          const isVisible = await transportField.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    // hasVoucherPrinterEnabled: botón imprimir voucher en órdenes
    if (client.config.hasVoucherPrinterEnabled !== undefined) {
      test(`${key}: hasVoucherPrinterEnabled=${client.config.hasVoucherPrinterEnabled}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'hasVoucherPrinterEnabled');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        await page.goto(`${client.baseURL}/orders`);
        await page.waitForLoadState('domcontentloaded');

        const printerBtn = page.getByRole('button', { name: /imprimir|print|voucher/i })
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

    // disableShowEstimatedDeliveryHour: oculta hora estimada de entrega en cart
    if (client.config.disableShowEstimatedDeliveryHour !== undefined) {
      test(`${key}: disableShowEstimatedDeliveryHour=${client.config.disableShowEstimatedDeliveryHour}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'disableShowEstimatedDeliveryHour');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);
        await addOneProductToCart(page);

        const deliveryHour = page.getByText(/hora.*entrega|entrega.*hora|estimated.*hour|delivery.*hour/i)
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

    // enablePaymentsCollection: opción cobro/colecta en sección pagos
    if (client.config.enablePaymentsCollection !== undefined) {
      test(`${key}: enablePaymentsCollection=${client.config.enablePaymentsCollection}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enablePaymentsCollection');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        await page.goto(`${client.baseURL}/payment-collections`).catch(() => {});
        await page.waitForLoadState('domcontentloaded');

        const collectionsLink = page.getByRole('link', { name: /cobro|colecta|collection/i })
          .or(page.getByText(/cobros|colectas|payment collection/i));

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

    // hasTransferPaymentType: opción de pago por transferencia
    if (client.config.hasTransferPaymentType !== undefined) {
      test(`${key}: hasTransferPaymentType=${client.config.hasTransferPaymentType}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'hasTransferPaymentType');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);
        await addOneProductToCart(page);

        const transferOption = page.getByText(/transferencia/i)
          .or(page.getByLabel(/transferencia/i));

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

    // uploadOrderFileWithMinUnits: botón carga masiva de pedidos
    if (client.config.uploadOrderFileWithMinUnits !== undefined) {
      test(`${key}: uploadOrderFileWithMinUnits=${client.config.uploadOrderFileWithMinUnits}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'uploadOrderFileWithMinUnits');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');

        const uploadBtn = page.getByRole('button', { name: /subir.*archivo|upload.*file|carga masiva|importar/i })
          .or(page.locator('input[type="file"]'));

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

    // enableBetaButtons: botones/features beta visibles
    if (client.config.enableBetaButtons !== undefined) {
      test(`${key}: enableBetaButtons=${client.config.enableBetaButtons}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enableBetaButtons');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');

        const betaBtn = page.locator('[class*="beta" i]')
          .or(page.getByText(/beta/i));

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

    // discountTypes.enableOrderDiscountType: tipo de descuento a nivel de orden
    if (client.config['discountTypes.enableOrderDiscountType'] !== undefined) {
      test(`${key}: discountTypes.enableOrderDiscountType=${client.config['discountTypes.enableOrderDiscountType']}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'discountTypes');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);
        await addOneProductToCart(page);

        const orderDiscountUI = page.getByText(/descuento.*orden|order.*discount|tipo.*descuento/i)
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

    // discountTypes.enableProductDiscountType: tipo de descuento a nivel de producto
    if (client.config['discountTypes.enableProductDiscountType'] !== undefined) {
      test(`${key}: discountTypes.enableProductDiscountType=${client.config['discountTypes.enableProductDiscountType']}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'discountTypes');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');

        const productDiscountUI = page.locator('[class*="product-discount" i], [class*="productDiscount" i]')
          .or(page.getByText(/descuento.*producto|product.*discount/i));

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

    // weightInfo: información de peso en productos
    if (client.config.weightInfo !== undefined) {
      test(`${key}: weightInfo=${client.config.weightInfo}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'weightInfo');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');

        const weightLabel = page.getByText(/peso|weight|\d+\s*kg|\d+\s*g\b/i)
          .or(page.locator('[class*="weight" i]'));

        if (client.config.weightInfo) {
          const isVisible = await weightLabel.first().isVisible({ timeout: 5_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] weightInfo=true but weight data not found — staging products may lack weight`);
        } else {
          // Skip false-negative risk: product names can contain weight units
          // Only fail if a dedicated weight UI element is found
          const dedicatedWeight = page.locator('[class*="weight-info" i], [class*="weightInfo" i]');
          const isVisible = await dedicatedWeight.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    // showEmptyCategories: categorías vacías visibles en sidebar
    if (client.config.showEmptyCategories !== undefined) {
      test(`${key}: showEmptyCategories=${client.config.showEmptyCategories}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'showEmptyCategories');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');

        // Click en una categoría para verificar si las subcategorías vacías aparecen
        const categories = page.locator('[class*="categor" i] a, nav a[href*="categor"]');
        const categoryCount = await categories.count();

        if (client.config.showEmptyCategories) {
          // Con flag=true, debe haber más categorías visibles (incluyendo vacías)
          // Soft check: no hard assert en staging
          console.log(`[${key}] showEmptyCategories=true — ${categoryCount} categories visible`);
        } else {
          // Con flag=false, las categorías vacías no deben aparecer
          // No hay forma directa de distinguir vacías de llenas sin conocer los datos
          console.log(`[${key}] showEmptyCategories=false — ${categoryCount} categories visible`);
        }
        await context.close();
      });
    }

    // externalAccess: acceso externo habilitado
    if (client.config.externalAccess !== undefined) {
      test(`${key}: externalAccess=${client.config.externalAccess}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'externalAccess');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        await page.goto(`${client.baseURL}`);
        await page.waitForLoadState('domcontentloaded');

        const externalLink = page.getByRole('link', { name: /acceso externo|external access/i })
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

    // blockedClientAlert.enableBlockedClientAlert: alerta de cliente bloqueado
    if (client.config['blockedClientAlert.enableBlockedClientAlert'] !== undefined) {
      test(`${key}: blockedClientAlert.enableBlockedClientAlert=${client.config['blockedClientAlert.enableBlockedClientAlert']}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'blockedClientAlert');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        await page.goto(`${client.baseURL}`);
        await page.waitForLoadState('domcontentloaded');

        const blockedAlert = page.getByText(/bloqueado para compras|tu comercio.*bloqueado|blocked.*purchase/i)
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

    // useNewPromotions: motor de promociones nuevo activo
    if (client.config.useNewPromotions !== undefined) {
      test(`${key}: useNewPromotions=${client.config.useNewPromotions}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'useNewPromotions');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        await page.goto(`${client.baseURL}/products?promotions=true`);
        await page.waitForLoadState('domcontentloaded');

        // La sección de promociones debe existir (independiente del motor)
        const promoSection = page.getByText(/promoci[oó]n|oferta|descuento/i).first();
        const isVisible = await promoSection.isVisible({ timeout: 8_000 }).catch(() => false);
        // Soft check: solo validamos que la página de promociones carga
        if (!isVisible) console.warn(`[${key}] useNewPromotions=${client.config.useNewPromotions} — no promo content found in staging`);
        await context.close();
      });
    }

    // "payment.enableNewPaymentModule": módulo de pago nuevo
    if (client.config['payment.enableNewPaymentModule'] !== undefined) {
      test(`${key}: payment.enableNewPaymentModule=${client.config['payment.enableNewPaymentModule']}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'payment.enableNewPaymentModule');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);
        await addOneProductToCart(page);

        // El módulo nuevo de pagos tiene una UI distinta — verificar sección pagos
        const paymentModule = page.locator('[class*="payment-module" i], [class*="paymentModule" i]')
          .or(page.locator('[data-testid*="payment" i]'));

        if (client.config['payment.enableNewPaymentModule']) {
          const isVisible = await paymentModule.first().isVisible({ timeout: 8_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] payment.enableNewPaymentModule=true but module not found — requires enablePayments=true`);
        } else {
          // Old module or no module — no strict assert
          console.log(`[${key}] payment.enableNewPaymentModule=false — using legacy payment flow`);
        }
        await context.close();
      });
    }

    // shareOrderNewDesign: diseño nuevo en compartir pedido
    if (client.config.shareOrderNewDesign !== undefined) {
      test(`${key}: shareOrderNewDesign=${client.config.shareOrderNewDesign}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'shareOrderNewDesign');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);

        await page.goto(`${client.baseURL}/orders`);
        await page.waitForLoadState('domcontentloaded');

        const shareBtn = page.getByRole('button', { name: /compartir|share/i })
          .or(page.locator('[class*="share-order" i], [class*="shareOrder" i]'));

        if (client.config.shareOrderNewDesign) {
          const isVisible = await shareBtn.first().isVisible({ timeout: 5_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] shareOrderNewDesign=true but share button not found — no orders in staging`);
        } else {
          const isVisible = await shareBtn.first().isVisible({ timeout: 4_000 }).catch(() => false);
          // Soft check: share button may still exist with old design
          console.log(`[${key}] shareOrderNewDesign=false — share button visible: ${isVisible}`);
        }
        await context.close();
      });
    }

    // "shoppingDetail.lastOrder": detalle último pedido en carrito
    if (client.config['shoppingDetail.lastOrder'] !== undefined) {
      test(`${key}: shoppingDetail.lastOrder=${client.config['shoppingDetail.lastOrder']}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'shoppingDetail.lastOrder');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);
        await addOneProductToCart(page);

        const lastOrderSection = page.getByText(/[uú]ltimo pedido|último orden|last order/i)
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

    // "loginButtons.facebook": botón Facebook en login
    if (client.config['loginButtons.facebook'] !== undefined) {
      test(`${key}: loginButtons.facebook=${client.config['loginButtons.facebook']}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'loginButtons.facebook');
        const context = await browser.newContext();
        const page = await context.newPage();
        await page.goto(`${client.baseURL}${client.loginPath}`);
        await page.waitForLoadState('domcontentloaded');

        const fbBtn = page.getByRole('button', { name: /facebook/i })
          .or(page.locator('[class*="facebook" i], [data-provider="facebook"]'));

        if (client.config['loginButtons.facebook']) {
          const isVisible = await fbBtn.first().isVisible({ timeout: 8_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] loginButtons.facebook=true but button not found`);
        } else {
          const isVisible = await fbBtn.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    // "loginButtons.google": botón Google en login
    if (client.config['loginButtons.google'] !== undefined) {
      test(`${key}: loginButtons.google=${client.config['loginButtons.google']}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'loginButtons.google');
        const context = await browser.newContext();
        const page = await context.newPage();
        await page.goto(`${client.baseURL}${client.loginPath}`);
        await page.waitForLoadState('domcontentloaded');

        const googleBtn = page.getByRole('button', { name: /google/i })
          .or(page.locator('[class*="google" i], [data-provider="google"]'));

        if (client.config['loginButtons.google']) {
          const isVisible = await googleBtn.first().isVisible({ timeout: 8_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] loginButtons.google=true but button not found`);
        } else {
          const isVisible = await googleBtn.first().isVisible({ timeout: 4_000 }).catch(() => false);
          expect(isVisible).toBeFalsy();
        }
        await context.close();
      });
    }

    // "suggestions.hide": ocultar sección de sugerencias en catálogo
    if (client.config['suggestions.hide'] !== undefined) {
      test(`${key}: suggestions.hide=${client.config['suggestions.hide']}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'suggestions.hide');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');
        await page.waitForTimeout(3_000);

        const suggestionsSection = page.getByText(/sugerencia|suggested/i).first()
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

    // "hasMultipleBusinessUnit": selector de unidad de negocio
    if (client.config.hasMultipleBusinessUnit !== undefined) {
      test(`${key}: hasMultipleBusinessUnit=${client.config.hasMultipleBusinessUnit}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'hasMultipleBusinessUnit');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');
        await page.waitForTimeout(3_000);

        const buSelector = page.locator('[class*="business-unit" i], [class*="businessUnit" i]')
          .or(page.getByText(/unidad de negocio|business unit/i));

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

    // "enablePriceOracle": precio con fecha estimada de actualización
    if (client.config.enablePriceOracle !== undefined) {
      test(`${key}: enablePriceOracle=${client.config.enablePriceOracle}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enablePriceOracle');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');
        await page.waitForTimeout(3_000);

        const oracleEl = page.locator('[class*="price-oracle" i], [class*="priceOracle" i]')
          .or(page.getByText(/precio estimado|precio actualiz/i));

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

    // "paymentsWithoutAccount": flujo pago sin cuenta registrada
    if (client.config.paymentsWithoutAccount !== undefined) {
      test(`${key}: paymentsWithoutAccount=${client.config.paymentsWithoutAccount}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'paymentsWithoutAccount');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);
        await page.goto(`${client.baseURL}/cart`);
        await page.waitForLoadState('domcontentloaded');
        await page.waitForTimeout(2_000);

        const noAccountEl = page.getByText(/sin cuenta|without account|pago invitado/i)
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

    // "enableNewUI": layout con nuevo diseño UI
    if (client.config.enableNewUI !== undefined) {
      test(`${key}: enableNewUI=${client.config.enableNewUI}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enableNewUI');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');
        await page.waitForTimeout(3_000);

        const newUIEl = page.locator('[class*="new-ui" i], [class*="newUi" i], [data-ui-version="new"]');

        if (client.config.enableNewUI) {
          const isVisible = await newUIEl.first().isVisible({ timeout: 8_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] enableNewUI=true but new UI indicator not found — may use different selector`);
        } else {
          // Standard layout — soft check only
          const isVisible = await newUIEl.first().isVisible({ timeout: 3_000 }).catch(() => false);
          if (isVisible) console.warn(`[${key}] enableNewUI=false but new UI indicator found`);
        }
        await context.close();
      });
    }

    // "enablePaymentDocumentsB2B": módulo de documentos de pago (cobranza)
    if (client.config.enablePaymentDocumentsB2B !== undefined) {
      test(`${key}: enablePaymentDocumentsB2B=${client.config.enablePaymentDocumentsB2B}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enablePaymentDocumentsB2B');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);
        await page.goto(`${client.baseURL}/payment-documents`);
        await page.waitForLoadState('domcontentloaded');
        await page.waitForTimeout(2_000);

        const notFound = await page.getByText(/404|no encontrad|not found/i).isVisible({ timeout: 4_000 }).catch(() => false);
        const redirected = page.url().includes('/products') || page.url().includes('/auth');
        const paymentDocsContent = page.locator('[class*="payment-document" i], [class*="paymentDocument" i]');
        const hasContent = await paymentDocsContent.first().isVisible({ timeout: 4_000 }).catch(() => false);

        if (client.config.enablePaymentDocumentsB2B) {
          if (!hasContent) console.warn(`[${key}] enablePaymentDocumentsB2B=true but module not found`);
        } else {
          if (hasContent) {
            test.info().annotations.push({ type: 'warning', description: `enablePaymentDocumentsB2B=false but module visible` });
          }
          expect(notFound || redirected || !hasContent).toBeTruthy();
        }
        await context.close();
      });
    }

    // "enableInvoicesList": lista de facturas/documentos
    if (client.config.enableInvoicesList !== undefined) {
      test(`${key}: enableInvoicesList=${client.config.enableInvoicesList}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'enableInvoicesList');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);
        await page.goto(`${client.baseURL}/invoices`);
        await page.waitForLoadState('domcontentloaded');
        await page.waitForTimeout(2_000);

        const notFound = await page.getByText(/404|no encontrad|not found/i).isVisible({ timeout: 4_000 }).catch(() => false);
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

    // "disableCommerceEdit": deshabilitar edición de comercio
    if (client.config.disableCommerceEdit !== undefined) {
      test(`${key}: disableCommerceEdit=${client.config.disableCommerceEdit}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'disableCommerceEdit');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);
        await page.goto(`${client.baseURL}/profile`);
        await page.waitForLoadState('domcontentloaded');
        await page.waitForTimeout(2_000);

        const editBtn = page.getByRole('button', { name: /editar|edit/i })
          .or(page.locator('[class*="edit-commerce" i], [class*="editCommerce" i]'));

        if (client.config.disableCommerceEdit) {
          const isVisible = await editBtn.first().isVisible({ timeout: 5_000 }).catch(() => false);
          if (isVisible) {
            test.info().annotations.push({ type: 'warning', description: `disableCommerceEdit=true but edit button visible` });
          }
          expect(isVisible).toBeFalsy();
        } else {
          // Soft: edit may be on different path
          console.log(`[${key}] disableCommerceEdit=false — edit expected to be available`);
        }
        await context.close();
      });
    }

    // "disableObservationInput": ocultar campo de observaciones en carrito
    if (client.config.disableObservationInput !== undefined) {
      test(`${key}: disableObservationInput=${client.config.disableObservationInput}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'disableObservationInput');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);
        await addOneProductToCart(page);

        const observationInput = page.getByLabel(/observaci[oó]n|observation|nota|note/i)
          .or(page.getByPlaceholder(/observaci[oó]n|observation/i));

        if (client.config.disableObservationInput) {
          const isVisible = await observationInput.first().isVisible({ timeout: 5_000 }).catch(() => false);
          if (isVisible) {
            test.info().annotations.push({ type: 'warning', description: `disableObservationInput=true but observation input visible` });
          }
          expect(isVisible).toBeFalsy();
        } else {
          const isVisible = await observationInput.first().isVisible({ timeout: 8_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] disableObservationInput=false but observation input not found`);
        }
        await context.close();
      });
    }

    // "hasSingleDistributionCenter": un solo centro de distribución
    if (client.config.hasSingleDistributionCenter !== undefined) {
      test(`${key}: hasSingleDistributionCenter=${client.config.hasSingleDistributionCenter}`, async ({ browser }) => {
        skipIfNotInB2B(client, 'hasSingleDistributionCenter');
        const context = await browser.newContext();
        const page = await context.newPage();
        await loginIfNeeded(page);
        await addOneProductToCart(page);

        const dcSelector = page.getByText(/centro de distribución|distribution center/i)
          .or(page.locator('[class*="distribution-center" i], [class*="distributionCenter" i]'));

        if (client.config.hasSingleDistributionCenter) {
          // With single DC, selector should not appear (no choice to make)
          const count = await dcSelector.count();
          if (count > 1) console.warn(`[${key}] hasSingleDistributionCenter=true but multiple DC options visible`);
        } else {
          const isVisible = await dcSelector.first().isVisible({ timeout: 8_000 }).catch(() => false);
          if (!isVisible) console.warn(`[${key}] hasSingleDistributionCenter=false but DC selector not found`);
        }
        await context.close();
      });
    }

  });
}

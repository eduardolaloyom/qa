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
      await page.waitForLoadState('networkidle');

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
      await page.waitForLoadState('networkidle');

      const addButtons = page.getByRole('button', { name: 'Agregar' });
      const cartLink = page.locator('a[href*="cart"]');

      if (client.config.disableCart) {
        // No debe haber botones de agregar NI link al carro
        expect(await addButtons.count()).toBe(0);
        expect(await cartLink.count()).toBe(0);
      } else {
        // Debe haber botones de agregar Y link al carro
        expect(await addButtons.count()).toBeGreaterThan(0);
        expect(await cartLink.count()).toBeGreaterThan(0);
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
        await page.waitForLoadState('networkidle');
        const addButton = page.getByRole('button', { name: 'Agregar' }).first();

        await expect(addButton).toBeVisible({ timeout: 15_000 });
        await addButton.click();
        await page.waitForLoadState('networkidle');

        // Ir al carro
        await page.locator('a[href*="cart"]').first().click();
        await page.waitForLoadState('networkidle');

        const couponField = page.getByPlaceholder(/cup[oó]n/i)
          .or(page.getByText(/cup[oó]n/i))
          .or(page.getByRole('button', { name: /aplicar.*cup/i }));

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
        await page.waitForLoadState('networkidle');
        const addButton = page.getByRole('button', { name: 'Agregar' }).first();

        await expect(addButton).toBeVisible({ timeout: 15_000 });
        await addButton.click();
        await page.waitForLoadState('networkidle');

        await page.locator('a[href*="cart"]').first().click();
        await page.waitForLoadState('networkidle');

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
      await page.waitForLoadState('networkidle');

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
        await page.waitForLoadState('networkidle');

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
          await page.waitForLoadState('networkidle');

          const cartIcon = page.locator('[class*="cart" i], [aria-label*="carro" i], [aria-label*="carrito" i]').first();

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
          await page.waitForLoadState('networkidle');

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
        await page.waitForLoadState('networkidle');

        const addButton = page.getByRole('button', { name: 'Agregar' }).first();
        await expect(addButton).toBeVisible({ timeout: 15_000 });
        await addButton.click();
        await page.waitForLoadState('networkidle');

        await page.goto(`${client.baseURL}/cart`);
        await page.waitForLoadState('networkidle');

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
        await page.waitForLoadState('networkidle');

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
        await page.waitForLoadState('networkidle');

        const addButton = page.getByRole('button', { name: 'Agregar' }).first();
        await expect(addButton).toBeVisible({ timeout: 15_000 });
        await addButton.click();
        await page.waitForLoadState('networkidle');

        await page.goto(`${client.baseURL}/cart`);
        await page.waitForLoadState('networkidle');

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
          await page.waitForLoadState('networkidle');
          expect(priceRequests.length).toBeGreaterThan(0);
        } else {
          // Sin lazy loading, los precios deben estar disponibles al cargar
          await page.waitForLoadState('networkidle');
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
        await page.waitForLoadState('networkidle');

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
        await page.waitForLoadState('networkidle');

        const unitSelector = page.locator('select[name*="unit" i], [class*="unit-selector" i], [class*="saleUnit" i]')
          .or(page.getByText(/unidad|caja|kg|litro/i).first());

        if (client.config.enableChooseSaleUnit) {
          await expect(unitSelector.first()).toBeVisible({ timeout: 10_000 });
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
        await page.waitForLoadState('networkidle');

        const addButton = page.getByRole('button', { name: 'Agregar' }).first();
        await expect(addButton).toBeVisible({ timeout: 15_000 });
        await addButton.click();
        await page.waitForLoadState('networkidle');

        await page.goto(`${client.baseURL}/cart`);
        await page.waitForLoadState('networkidle');

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
        await page.waitForLoadState('networkidle');

        const addButton = page.getByRole('button', { name: 'Agregar' }).first();
        await expect(addButton).toBeVisible({ timeout: 15_000 });
        await addButton.click();
        await page.waitForLoadState('networkidle');

        await page.goto(`${client.baseURL}/cart`);
        await page.waitForLoadState('networkidle');

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
        await page.waitForLoadState('networkidle');

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
        await page.waitForLoadState('networkidle');

        const addButton = page.getByRole('button', { name: 'Agregar' }).first();
        await expect(addButton).toBeVisible({ timeout: 15_000 });
        await addButton.click();
        await page.waitForLoadState('networkidle');

        await page.goto(`${client.baseURL}/cart`);
        await page.waitForLoadState('networkidle');

        const paymentsSection = page.locator('[class*="payment" i], [class*="pago" i]').first();
        const isVisible = await paymentsSection.isVisible({ timeout: 5_000 }).catch(() => false);
        expect(isVisible).toBeFalsy();

        await context.close();
      });
    }
  });
}

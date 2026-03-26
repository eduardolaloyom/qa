import { test, expect } from '@playwright/test';
import clients from '../fixtures/clients.json';

// Correr los flujos críticos contra cada cliente
for (const [key, client] of Object.entries(clients)) {
  test.describe(`${client.name} (${client.baseURL})`, () => {

    // ── LOGIN ──
    test(`${key}: Login exitoso`, async ({ browser }) => {
      const context = await browser.newContext();
      const page = await context.newPage();

      await page.goto(client.baseURL);
      await page.waitForLoadState('domcontentloaded');

      // Si anonymousAccess=true, ir directo al login path
      // Si anonymousAccess=false, ya debería redirigir a login
      if (client.config.anonymousAccess) {
        await page.goto(`${client.baseURL}${client.loginPath}`);
        await page.waitForLoadState('domcontentloaded');
      } else {
        await page.waitForLoadState('domcontentloaded');
      }

      // Soportar B2B nuevo (MUI labels) y antiguo (placeholders)
      const emailField = page.getByLabel('Correo')
        .or(page.getByPlaceholder('Email'))
        .or(page.locator('input[type="email"]'));
      const passField = page.getByLabel('Contraseña')
        .or(page.getByPlaceholder('Contraseña'))
        .or(page.locator('input[type="password"]'));
      const submitBtn = page.locator('form').getByRole('button', { name: /iniciar sesión|entrar/i })
        .or(page.getByRole('button', { name: /entrar/i }));

      await emailField.fill(client.credentials.email);
      await passField.fill(client.credentials.password);
      await submitBtn.click();

      // Debe salir de la página de login
      await expect(page).not.toHaveURL(/auth\/jwt\/login|\/login$/, { timeout: 30_000 });

      await context.close();
    });

    // ── ACCESO ANÓNIMO ──
    if (client.config.anonymousAccess) {
      test(`${key}: Acceso anónimo muestra catálogo`, async ({ browser }) => {
        const context = await browser.newContext();
        const page = await context.newPage();
        await page.goto(client.baseURL);
        await expect(page).not.toHaveURL(/auth|login/);
        await expect(page.locator('text=/\\$\\s*[\\d.,]+/')).toBeVisible({ timeout: 15_000 });
        await context.close();
      });
    } else {
      test(`${key}: Sin acceso anónimo redirige a login`, async ({ browser }) => {
        const context = await browser.newContext();
        const page = await context.newPage();
        await page.goto(client.baseURL);
        // Debe redirigir a login
        await expect(page).toHaveURL(/auth|login/, { timeout: 15_000 });
        await context.close();
      });
    }

    // ── CATÁLOGO ──
    test(`${key}: Catálogo muestra productos con precios`, async ({ browser }) => {
      const context = await browser.newContext();
      const page = await context.newPage();
      await page.goto(client.baseURL);
      await page.waitForLoadState('domcontentloaded');

      // Login si es necesario
      if (!client.config.anonymousAccess) {
        const emailF = page.getByLabel('Correo').or(page.getByPlaceholder('Email')).or(page.locator('input[type="email"]'));
        const passF = page.getByLabel('Contraseña').or(page.getByPlaceholder('Contraseña')).or(page.locator('input[type="password"]'));
        const submitF = page.locator('form').getByRole('button', { name: /iniciar sesión|entrar/i }).or(page.getByRole('button', { name: /entrar/i }));
        await emailF.fill(client.credentials.email);
        await passF.fill(client.credentials.password);
        await submitF.click();
        await expect(page).not.toHaveURL(/auth\/jwt\/login|\/login$/, { timeout: 30_000 });
      }

      // Verificar precios visibles
      if (!client.config.hidePrices) {
        await expect(page.locator('text=/\\$\\s*[\\d.,]+/')).toBeVisible({ timeout: 30_000 });
      }

      await context.close();
    });

    // ── CARRITO ──
    if (!client.config.disableCart) {
      test(`${key}: Agregar producto al carro`, async ({ browser }) => {
        const context = await browser.newContext();
        const page = await context.newPage();
        await page.goto(client.baseURL);
        await page.waitForLoadState('domcontentloaded');

        // Login
        if (!client.config.anonymousAccess) {
          await page.getByLabel('Correo').fill(client.credentials.email);
          await page.getByLabel('Contraseña').fill(client.credentials.password);
          await page.locator('form').getByRole('button', { name: /iniciar sesión/i }).click();
          await expect(page).not.toHaveURL(/auth\/jwt\/login|\/login$/, { timeout: 30_000 });
        }

        // Ir a productos
        await page.goto(`${client.baseURL}/products`);
        await page.waitForLoadState('domcontentloaded');

        // Agregar producto
        const addButton = page.getByRole('button', { name: 'Agregar' }).first();
        await addButton.waitFor({ timeout: 30_000 });

        const [response] = await Promise.all([
          page.waitForResponse(resp => resp.url().includes('/cart') && resp.request().method() === 'POST'),
          addButton.click(),
        ]);

        expect(response.ok()).toBeTruthy();

        await context.close();
      });
    }

    // ── PRECIOS $0 ──
    test(`${key}: No hay productos con precio $0`, async ({ browser }) => {
      const context = await browser.newContext();
      const page = await context.newPage();
      await page.goto(client.baseURL);
      await page.waitForLoadState('domcontentloaded');

      // Login si necesario
      if (!client.config.anonymousAccess) {
        const emailF = page.getByLabel('Correo').or(page.getByPlaceholder('Email')).or(page.locator('input[type="email"]'));
        const passF = page.getByLabel('Contraseña').or(page.getByPlaceholder('Contraseña')).or(page.locator('input[type="password"]'));
        const submitF = page.locator('form').getByRole('button', { name: /iniciar sesión|entrar/i }).or(page.getByRole('button', { name: /entrar/i }));
        await emailF.fill(client.credentials.email);
        await passF.fill(client.credentials.password);
        await submitF.click();
        await expect(page).not.toHaveURL(/auth\/jwt\/login|\/login$/, { timeout: 30_000 });
      }

      // Ir a catálogo de productos
      await page.goto(`${client.baseURL}/products`);
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(5000);

      const zeroPrices = page.locator('text=/\\$\\s*0(?:[,.]0+)?\\s*$/');
      const count = await zeroPrices.count();
      expect(count).toBe(0);

      await context.close();
    });
  });
}

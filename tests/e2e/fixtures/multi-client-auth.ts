import { test as base, expect } from '@playwright/test';
import { loginHelper } from './login';
import clients from './clients';

/**
 * Custom fixture for multi-client authenticated tests.
 * Iterates over all clients in clients.ts and provides an authenticated page per client.
 * Replaces the old auth.ts fixture which was hardcoded to tienda.youorder.me.
 */
export const test = base.extend<{ authedPage: ReturnType<typeof base['page']>; client: typeof clients[keyof typeof clients] }>({
  client: async ({ }, use) => {
    // This will be overridden by test parameterization in actual specs
    const firstClient = Object.values(clients)[0];
    await use(firstClient);
  },

  authedPage: async ({ browser, client }, use) => {
    const context = await browser.newContext({ baseURL: client.baseURL });
    const page = await context.newPage();

    // Login using the client's credentials
    await loginHelper(page, client.credentials.email, client.credentials.password, client.loginPath, client.baseURL);

    await use(page);
    await context.close();
  },
});

export { expect };

import { defineConfig, devices } from '@playwright/test';
import dotenv from 'dotenv';
import path from 'path';

dotenv.config({ path: path.resolve(__dirname, '.env') });

export default defineConfig({
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 1,
  workers: 4,
  reporter: [
    ['html', { open: 'never' }],
    ['json', { outputFile: 'playwright-report/results.json' }],
    ['list'],
  ],
  use: {
    baseURL: process.env.BASE_URL || 'https://tienda.youorder.me',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
    // Timeouts largos para resolver el problema de lentitud que rompio Cypress
    actionTimeout: 30_000,
    navigationTimeout: 60_000,
  },
  timeout: 120_000,
  expect: {
    timeout: 15_000,
  },
  projects: [
    {
      name: 'b2b',
      testDir: './b2b',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'admin',
      testDir: './admin',
      use: {
        ...devices['Desktop Chrome'],
        baseURL: process.env.ADMIN_URL || 'https://admin.youorder.me',
      },
    },
  ],
});

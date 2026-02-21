import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { defineConfig } from '@playwright/test';

const frontendDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)));
const repoRoot = path.resolve(frontendDir, '../..');
const adminBaseURL = process.env.ADMIN_E2E_BASE_URL ?? 'http://127.0.0.1:18000';

export default defineConfig({
  testDir: './e2e',
  testMatch: 'admin-smoke.spec.ts',
  timeout: 120_000,
  expect: {
    timeout: 10_000,
  },
  retries: process.env.CI ? 1 : 0,
  reporter: [['list']],
  use: {
    baseURL: adminBaseURL,
    headless: true,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  webServer: {
    command: 'uv run uvicorn web_app:app --host 127.0.0.1 --port 18000',
    cwd: path.join(repoRoot, 'backend', 'src'),
    url: `${adminBaseURL}/healthz`,
    timeout: 120_000,
    reuseExistingServer: !process.env.CI,
  },
});

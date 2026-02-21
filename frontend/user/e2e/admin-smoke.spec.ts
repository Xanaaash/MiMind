import { expect, test, type APIRequestContext } from '@playwright/test';

const ADMIN_BASE_URL = process.env.ADMIN_E2E_BASE_URL ?? 'http://127.0.0.1:18000';
const ADMIN_E2E_ENABLED = process.env.PLAYWRIGHT_ADMIN_E2E === '1';

async function createSeedUser(request: APIRequestContext): Promise<{ userId: string; email: string }> {
  const email = `admin-smoke-${Date.now()}-${Math.floor(Math.random() * 100000)}@example.com`;
  const response = await request.post(`${ADMIN_BASE_URL}/api/register`, {
    data: {
      email,
      locale: 'zh-CN',
      policy_version: '2026.02',
    },
  });

  expect(response.ok()).toBeTruthy();
  const payload = (await response.json()) as { user_id: string };
  expect(payload.user_id).toBeTruthy();

  return { userId: payload.user_id, email };
}

test('admin smoke flow: login -> panels -> triage -> compliance erase', async ({ page, request }) => {
  test.skip(!ADMIN_E2E_ENABLED, 'Run with PLAYWRIGHT_ADMIN_E2E=1 and playwright.admin.config.ts');

  const adminPassword = process.env.ADMIN_PASSWORD ?? 'admin';
  const { userId, email } = await createSeedUser(request);

  await page.goto(`${ADMIN_BASE_URL}/admin/`);
  await expect(page.getByRole('heading', { name: '登录管理台' })).toBeVisible();

  await page.locator('#loginPassword').fill(adminPassword);
  await page.locator('#loginForm button[type="submit"]').click();
  await expect(page.locator('#adminApp')).toBeVisible();

  await page.locator('button[data-module="observability"]').click();
  await page.locator('#loadObservabilityBtn').click();
  await expect(page.locator('#obsTotalInvocations')).toHaveText(/\d+/);

  await page.locator('button[data-module="prompt_registry"]').click();
  await page.locator('#loadPromptRegistryBtn').click();
  await expect(page.locator('#promptPackList .prompt-card').first()).toBeVisible();

  await page.locator('button[data-module="user_management"]').click();
  await page.locator('#loadAdminUsersBtn').click();

  const targetRow = page.locator('#adminUsersRows tr').filter({ hasText: email }).first();
  await expect(targetRow).toBeVisible();
  await targetRow.getByRole('button', { name: '选择' }).click();
  await expect(page.locator('#adminTriageUserId')).toHaveValue(userId);

  await page.locator('#adminTriageChannel').selectOption('yellow');
  await page.locator('#adminTriageReason').fill('playwright-smoke');
  await page.locator('#adminTriageHalt').check();
  await page.locator('#adminTriageHotline').check();
  await page.locator('#adminTriageForm button[type="submit"]').click();
  await expect(page.locator('#adminTriageResult')).toContainText(userId);
  await expect(page.locator('#adminTriageResult')).toContainText('"channel": "yellow"');

  await page.locator('button[data-module="compliance_ops"]').click();
  await page.locator('#complianceUseSelectedBtn').click();
  await expect(page.locator('#complianceUserId')).toHaveValue(userId);

  await page.locator('#complianceExportBtn').click();
  await expect(page.locator('#complianceResult')).toContainText(userId);
  await expect(page.locator('#complianceResult')).toContainText('"generated_at"');

  await page.locator('#complianceEraseConfirm').check();
  await page.locator('#complianceEraseBtn').click();
  await expect(page.locator('#complianceResult')).toContainText('"existed_before": true');
  await expect(page.locator('#complianceResult')).toContainText('"total_deleted"');
});

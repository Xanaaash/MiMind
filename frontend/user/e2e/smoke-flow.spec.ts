import { expect, test, type Page } from '@playwright/test';

async function completeOnboarding(page: Page) {
  for (let step = 0; step < 50; step += 1) {
    if (/\/home$/.test(page.url())) {
      break;
    }

    const options = page.locator('div.bg-paper button[type="button"]');
    await expect(options.first()).toBeVisible();
    await options.first().click();

    const actionButton = page.locator('div.flex.justify-between.mt-6 button').last();
    const actionLabel = (await actionButton.innerText()).trim().toLowerCase();
    await actionButton.click();

    if (actionLabel.includes('finish') || actionLabel.includes('完成')) {
      await page.waitForURL('**/home', { timeout: 30_000 });
      break;
    }
  }
}

async function completePhq9Scale(page: Page) {
  for (let step = 0; step < 9; step += 1) {
    const options = page.locator('div.bg-panel button[type="button"]');
    await expect(options.first()).toBeVisible();
    await options.first().click();

    const actionButton = page.locator('div.flex.justify-between.mt-6 button').last();
    await actionButton.click();
  }
}

test('smoke flow: register -> assessment -> result -> coach', async ({ page }) => {
  await page.goto('/auth');
  await page.locator('input[type="text"]').fill('admin');
  await page.locator('input[type="password"]').fill('admin');
  await page.getByRole('button', { name: /登录|log in/i }).click();
  await expect(page).toHaveURL(/\/home$/);

  await page.goto('/onboarding');
  await completeOnboarding(page);
  await expect(page).toHaveURL(/\/home$/);

  await page.goto('/scales/phq9');
  await completePhq9Scale(page);
  await expect(page).toHaveURL(/\/scales\/phq9\/result$/);

  await page.goto('/coach');
  const styleButtons = page.locator('button.w-full.text-left');
  await expect(styleButtons.first()).toBeVisible();
  await styleButtons.first().click();

  const chatInput = page.locator('input[enterkeyhint="send"]');
  await expect(chatInput).toBeVisible();
  const userMessage = 'I am stressed and want a small plan for tomorrow.';
  await chatInput.fill(userMessage);
  await page.locator('form button[type="submit"]').click();

  await expect(page.getByText(userMessage)).toBeVisible();
  await expect.poll(async () => page.locator('p.whitespace-pre-wrap').count()).toBeGreaterThan(1);
});

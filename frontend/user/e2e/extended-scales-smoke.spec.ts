import { expect, test, type Page } from '@playwright/test';

async function completeWho5Scale(page: Page) {
  for (let step = 0; step < 5; step += 1) {
    const options = page.locator('button[aria-pressed]');
    await expect(options.first()).toBeVisible();
    await options.first().click();

    const actionButton = page.locator('div.flex.justify-between.mt-6 button').last();
    await actionButton.click();
  }
}

test('extended scales smoke: WHO-5 submit flow reaches result', async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem('mc_user_id', 'extended-scale-e2e-user');
    localStorage.setItem('mc_email', 'extended-scale-e2e@example.com');
    localStorage.setItem('mc_locale', 'en-US');
  });

  await page.goto('/scales');
  await expect(page).toHaveURL(/\/scales$/);
  await page.getByText(/WHO-5/i).first().click();
  await expect(page).toHaveURL(/\/scales\/who5$/);

  await completeWho5Scale(page);

  await expect(page).toHaveURL(/\/scales\/who5\/result$/);
  await expect(page.getByText(/results|测评结果/i)).toBeVisible();
});

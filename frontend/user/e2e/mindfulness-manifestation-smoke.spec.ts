import { expect, test } from '@playwright/test';

test('mindfulness manifestation smoke: entry -> quick -> deep complete flow', async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem('mc_user_id', 'mindfulness-e2e-user');
    localStorage.setItem('mc_email', 'mindfulness-e2e@example.com');
    localStorage.setItem('mc_locale', 'en-US');
  });

  await page.goto('/mindfulness');
  await expect(page).toHaveURL(/\/mindfulness$/);

  await page.getByTestId('mindfulness-entry-manifestation-quick').click();
  await expect(page).toHaveURL(/\/mindfulness\/manifestation\?mode=quick$/);

  await page.getByTestId('manifestation-quick-generate').click();
  await expect(page.getByText(/returning to steadiness|回到稳定/)).toBeVisible();

  await page.getByTestId('manifestation-mode-deep').click();
  await expect(page.getByTestId('manifestation-affirmation-input')).toBeVisible();

  await page.getByTestId('manifestation-affirmation-input').fill('I can complete one intentional step today.');
  await page.getByTestId('manifestation-add-affirmation').click();
  await expect(page.getByText('I can complete one intentional step today.')).toBeVisible();

  await page.getByTestId('manifestation-vision-title').fill('Focused Day');
  await page.getByTestId('manifestation-vision-note').fill('I finish one meaningful task with calm attention.');
  await page.getByTestId('manifestation-save-vision').click();
  await expect(page.getByText('Focused Day')).toBeVisible();
});

import { expect, test } from '@playwright/test';

test('tools rearchitecture smoke: toolbar persistence -> relief quick start -> mindfulness routes', async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem('mc_user_id', 'tools-e2e-user');
    localStorage.setItem('mc_email', 'tools-e2e@example.com');
    localStorage.setItem('mc_locale', 'en-US');
  });
  await page.goto('/home');
  await expect(page).toHaveURL(/\/home$/);

  await page.getByRole('button', { name: /疗愈工具|healing tools/i }).click();
  await expect(page.locator('aside[aria-hidden="false"]')).toBeVisible();
  await page.getByRole('button', { name: /白噪音|white noise/i }).click();
  await page.getByRole('button', { name: /雨声|rain/i }).click();
  await expect(page.getByRole('slider', { name: /雨声|rain/i })).toBeVisible();

  await page.getByRole('link', { name: /教练|coach/i }).first().click();
  await expect(page).toHaveURL(/\/coach$/);
  await expect(page.locator('aside[aria-hidden="false"]')).toBeVisible();
  await page.getByRole('button', { name: /白噪音|white noise/i }).first().click();
  await expect(page.getByRole('slider', { name: /雨声|rain/i })).toBeVisible();

  await page.getByRole('link', { name: /急救舱|relief/i }).first().click();
  await expect(page).toHaveURL(/\/relief$/);
  await page.getByRole('button', { name: /粉红噪音|pink noise/i }).first().click();
  await expect(page).toHaveURL(/\/relief\/sensory$/);
  await expect(page.locator('aside[aria-hidden="false"]')).toBeVisible();
  await page.getByRole('button', { name: /白噪音|white noise/i }).first().click();
  await expect(page.getByRole('slider', { name: /雨声|rain/i })).toBeVisible();

  await page.getByRole('link', { name: /心灵空间|mindfulness/i }).first().click();
  await expect(page).toHaveURL(/\/mindfulness$/);
  await page.getByText(/冥想引导|guided meditation/i).first().click();
  await expect(page).toHaveURL(/\/mindfulness\/meditation$/);
  await expect(page.getByText(/正在播放|now playing/i)).not.toBeVisible();

  await page.getByRole('button', { name: /开始|start/i }).first().click();
  const nowPlayingCard = page.locator('div.rounded-2xl').filter({ hasText: /正在播放|now playing/i }).first();
  await expect(nowPlayingCard).toBeVisible();
  const firstNowPlayingText = await nowPlayingCard.innerText();

  await page.getByRole('button', { name: /开始|start/i }).first().click();
  await expect.poll(async () => nowPlayingCard.innerText()).not.toBe(firstNowPlayingText);
});

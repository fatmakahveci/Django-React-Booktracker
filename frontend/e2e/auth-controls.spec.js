import { test, expect } from '@playwright/test';

const limited = (route) => route.fulfill({
  status: 429, headers: { 'Retry-After': '60' },
  contentType: 'application/json', body: JSON.stringify({ detail: 'Request was throttled.' }),
});

test('login and registration display the retry interval', async ({ page }) => {
  await page.route('**/api/token/', limited);
  await page.goto('/login/');
  await page.locator('[name="email"]').fill('limited@example.com');
  await page.locator('[name="password"]').fill('BookReader42!');
  await page.getByRole('button', { name: 'Submit' }).click();
  await expect(page.getByRole('alert')).toContainText('Try again in 60 seconds.');
  await page.route('**/api/register/', limited);
  await page.goto('/register/');
  await page.locator('[name="user_name"]').fill('limited_reader');
  await page.locator('[name="email"]').fill('limited@example.com');
  await page.locator('[name="password"]').fill('BookReader42!');
  await page.locator('[name="match_password"]').fill('BookReader42!');
  await page.getByRole('button', { name: 'Submit' }).click();
  await expect(page.getByRole('alert')).toContainText('Try again in 60 seconds.');
});

test('failed server logout still clears local credentials and reports uncertainty', async ({ page, request }) => {
  const suffix = Date.now();
  const email = `logout${suffix}@example.com`;
  const password = 'BookReader42!';
  const registration = await request.post('http://127.0.0.1:8191/register/', {
    data: { email, user_name: `logout${suffix}`, password },
  });
  expect(registration.status()).toBe(201);
  await page.goto('/login/');
  await page.locator('[name="email"]').fill(email);
  await page.locator('[name="password"]').fill(password);
  await page.getByRole('button', { name: 'Submit' }).click();
  await expect(page).toHaveURL(/\/books\/$/);
  await page.route('**/api/logout/', (route) => route.abort());
  await page.getByRole('link', { name: 'Logout' }).click();
  await expect(page).toHaveURL(/\/login\/\?logout=unconfirmed$/);
  await expect(page.getByRole('alert')).toContainText('Server logout could not be confirmed');
  expect(await page.evaluate(() => localStorage.getItem('authTokens'))).toBeNull();
});

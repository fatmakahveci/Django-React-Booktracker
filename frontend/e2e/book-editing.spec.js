import { test, expect } from "@playwright/test";

async function registerReader(page) {
  const suffix = `${Date.now()}`;
  await page.goto('/register/');
  await page.locator('[name="user_name"]').fill(`reader${suffix}`);
  await page.locator('[name="email"]').fill(`reader${suffix}@example.com`);
  await page.locator('[name="password"]').fill('BookReader42!');
  await page.locator('[name="match_password"]').fill('BookReader42!');
  await page.getByRole('button', { name: 'Submit' }).click();
  await expect(page).toHaveURL(/\/login\/$/);
  await page.locator('[name="email"]').fill(`reader${suffix}@example.com`);
  await page.locator('[name="password"]').fill('BookReader42!');
  await page.getByRole('button', { name: 'Submit' }).click();
  await expect(page).toHaveURL(/\/books\/$/);
  await expect(page.getByRole('button', { name: 'Save', exact: true })).toBeEnabled();
}

async function fillNewBook(page) {
  const form = page.getByRole('form', { name: 'Add book' });
  await form.getByLabel('Title', { exact: true }).fill('Original title');
  await form.getByLabel('Author', { exact: true }).fill('Original author');
  await form.getByLabel('Year', { exact: true }).fill('1969');
}

const fail = (route) => route.fulfill({ status: 400, contentType: 'application/json', body: JSON.stringify({ detail: 'Please retry this operation.' }) });

test('edit all details, cancel changes, and preserve finished status after reload', async ({ page }) => {
  await registerReader(page);
  await fillNewBook(page);
  await page.getByRole('button', { name: 'Save', exact: true }).click();
  await page.getByRole('button', { name: 'Edit', exact: true }).click();
  const dialog = page.getByRole('dialog', { name: 'Edit book' });
  await dialog.getByLabel('Title', { exact: true }).fill('Discard this');
  await dialog.getByRole('button', { name: 'Cancel' }).click();
  await expect(page.getByText('Original title', { exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Edit', exact: true }).click();
  await expect(dialog.getByLabel('Title', { exact: true })).toHaveValue('Original title');
  await dialog.getByLabel('Title', { exact: true }).fill('Revised title');
  await dialog.getByLabel('Author', { exact: true }).fill('Revised author');
  await dialog.getByLabel('Year', { exact: true }).fill('1974');
  await page.route('**/api/books/*/', fail);
  await dialog.getByRole('button', { name: 'Save changes' }).click();
  await expect(dialog.getByRole('alert')).toContainText('Could not save your changes.');
  await expect(dialog.getByLabel('Title', { exact: true })).toHaveValue('Revised title');
  await page.unroute('**/api/books/*/', fail);
  await dialog.getByRole('button', { name: 'Save changes' }).click();
  await expect(dialog).not.toBeVisible();
  await expect(page.getByText('Revised author', { exact: true })).toBeVisible();
  await expect(page.getByText('1974', { exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Finish', exact: true }).click();
  await expect(page.getByRole('button', { name: 'Unfinish', exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Edit', exact: true }).click();
  await dialog.getByLabel('Title', { exact: true }).fill('Finished title');
  await dialog.getByRole('button', { name: 'Save changes' }).click();
  await expect(dialog).not.toBeVisible();
  await page.reload();
  await expect(page.getByText('Finished title', { exact: true })).toBeVisible();
  await expect(page.getByText('Revised author', { exact: true })).toBeVisible();
  await expect(page.getByText('1974', { exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Unfinish', exact: true })).toBeVisible();
});

test('failed creation preserves input; failed status and delete preserve the shelf', async ({ page }) => {
  await registerReader(page);
  await fillNewBook(page);
  await page.route('**/api/books/', fail);
  await page.getByRole('button', { name: 'Save', exact: true }).click();
  await expect(page.getByRole('alert')).toContainText('Could not add the book.');
  await expect(page.getByLabel('Title', { exact: true })).toHaveValue('Original title');
  await page.unroute('**/api/books/', fail);
  await page.getByRole('button', { name: 'Save', exact: true }).click();
  await expect(page.getByText('Original title', { exact: true })).toBeVisible();
  await expect(page.getByLabel('Title', { exact: true })).toHaveValue('');
  await page.route('**/api/books/*/', fail);
  await page.getByRole('button', { name: 'Finish', exact: true }).click();
  await expect(page.getByRole('alert')).toContainText('Could not change the reading status.');
  await expect(page.getByRole('button', { name: 'Finish', exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Unfinish', exact: true })).toHaveCount(0);
  await page.getByRole('button', { name: 'Delete', exact: true }).click();
  await expect(page.getByRole('alert')).toContainText('Could not delete the book.');
  await expect(page.getByText('Original title', { exact: true })).toBeVisible();
  await page.unroute('**/api/books/*/', fail);
  await page.getByRole('button', { name: 'Delete', exact: true }).click();
  await expect(page.getByText('Original title', { exact: true })).toHaveCount(0);
});

test('failed loading can be retried', async ({ page }) => {
  await registerReader(page);
  await page.route('**/api/books/', fail);
  await page.reload();
  await expect(page.getByRole('alert')).toContainText('Could not load your books.');
  await expect(page.getByRole('button', { name: 'Save', exact: true })).toBeDisabled();
  await page.unroute('**/api/books/', fail);
  await page.getByRole('button', { name: 'Retry loading books' }).click();
  await expect(page.getByRole('button', { name: 'Save', exact: true })).toBeEnabled();
  await expect(page.getByRole('alert')).toHaveCount(0);
});

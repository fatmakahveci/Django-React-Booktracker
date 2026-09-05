import { test, expect } from "@playwright/test";

test("register, login, create a book, rotate tokens, reload and logout", async ({ page, request }) => {
  const suffix = `${Date.now()}`;
  const email = `reader${suffix}@example.com`;
  const password = "BookReader42!";
  await page.goto("/register/");
  await page.locator('[name="user_name"]').fill(`reader${suffix}`);
  await page.locator('[name="email"]').fill(email);
  await page.locator('[name="password"]').fill(password);
  await page.locator('[name="match_password"]').fill(password);
  await page.getByRole("button", { name: "Submit" }).click();
  await expect(page).toHaveURL(/\/login\/$/);
  await page.locator('[name="email"]').fill(email);
  await page.locator('[name="password"]').fill(password);
  await page.getByRole("button", { name: "Submit" }).click();
  await expect(page).toHaveURL(/\/books\/$/);
  await page.locator('[name="title"]').fill("The Left Hand of Darkness");
  await page.locator('[name="author"]').fill("Ursula K. Le Guin");
  await page.locator('[name="year"]').fill("1969");
  await page.getByRole("button", { name: "Save", exact: true }).click();
  await expect(page.getByText("The Left Hand of Darkness", { exact: true })).toBeVisible();

  const oldRefresh = await page.evaluate(() => {
    const tokens = JSON.parse(localStorage.getItem("authTokens"));
    const refresh = tokens.refresh;
    // Keep the decodable identity but invalidate the signature, forcing a real
    // Django 401 and the client's refresh path without waiting for expiry.
    tokens.access = tokens.access.split(".").slice(0, 2).join(".") + ".invalid";
    localStorage.setItem("authTokens", JSON.stringify(tokens));
    return refresh;
  });
  const refreshResponse = page.waitForResponse((r) => r.url().endsWith("/token/refresh/") && r.status() === 200);
  await page.reload();
  await refreshResponse;
  await expect(page.getByText("The Left Hand of Darkness", { exact: true })).toBeVisible();
  const newRefresh = await page.evaluate(() => JSON.parse(localStorage.getItem("authTokens")).refresh);
  expect(newRefresh).not.toBe(oldRefresh);
  const rejected = await request.post("http://127.0.0.1:8191/token/refresh/", { data: { refresh: oldRefresh } });
  expect(rejected.status()).toBe(401);
  await page.getByRole("link", { name: "Logout" }).click();
  await expect(page).toHaveURL("http://127.0.0.1:5191/");
  expect(await page.evaluate(() => localStorage.getItem("authTokens"))).toBeNull();
  await page.goto("/books/");
  await expect(page.locator('[name="title"]')).toHaveCount(0);
});

test("malformed persisted credentials do not crash the login page", async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem("authTokens", "invalid-json"));
  await page.goto("/login/");
  await expect(page.getByRole("heading", { name: "Login" })).toBeVisible();
});

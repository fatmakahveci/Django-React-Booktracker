import { beforeEach, expect, test, vi } from "vitest";

let api, publicApi, logoutSession;
const tokens = { access: "old-access", refresh: "old-refresh" };
const response = (config, data = {}) => ({ config, data, status: 200, statusText: "OK", headers: {} });

beforeEach(async () => {
  vi.resetModules();
  ({ default: api, publicApi, logoutSession } = await import("../api"));
  localStorage.clear();
  localStorage.setItem("authTokens", JSON.stringify(tokens));
});

test("logout revokes the stored refresh and clears local credentials", async () => {
  publicApi.defaults.adapter = vi.fn(async (config) => response(config));
  await logoutSession();
  const config = publicApi.defaults.adapter.mock.calls[0][0];
  expect(config.url).toBe("/logout/");
  expect(JSON.parse(config.data)).toEqual({ refresh: tokens.refresh });
  expect(localStorage.getItem("authTokens")).toBeNull();
});

test("a network failure is reported but local credentials are still cleared", async () => {
  publicApi.defaults.adapter = async () => { throw new Error("Offline"); };
  await expect(logoutSession()).rejects.toThrow("Offline");
  expect(localStorage.getItem("authTokens")).toBeNull();
});

test("already invalid refresh tokens do not make logout fail", async () => {
  publicApi.defaults.adapter = async () => { throw { response: { status: 401 } }; };
  await expect(logoutSession()).resolves.toBeUndefined();
  expect(localStorage.getItem("authTokens")).toBeNull();
});

test("logout waits for a pending refresh and revokes the rotated token", async () => {
  let completeRefresh;
  const rotated = { access: "new-access", refresh: "new-refresh" };
  api.defaults.adapter = async (config) => { throw { config, response: { status: 401 } }; };
  publicApi.defaults.adapter = vi.fn((config) => {
    if (config.url === "/token/refresh/") {
      return new Promise((resolve) => { completeRefresh = () => resolve(response(config, rotated)); });
    }
    return Promise.resolve(response(config));
  });
  const bookRequest = api.get("/books/").catch((error) => error);
  await vi.waitFor(() => expect(completeRefresh).toBeTypeOf("function"));
  const logout = logoutSession();
  completeRefresh();
  await logout;
  await bookRequest;
  const calls = publicApi.defaults.adapter.mock.calls.map(([config]) => config);
  expect(JSON.parse(calls.find((config) => config.url === "/logout/").data)).toEqual({ refresh: "new-refresh" });
  expect(localStorage.getItem("authTokens")).toBeNull();
});

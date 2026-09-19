import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
beforeEach(() => vi.resetModules());
afterEach(() => vi.unstubAllGlobals());
describe("cookie API client", () => {
  it("coalesces concurrent renewal and retries protected requests", async () => {
    let renewed = false;
    let refreshes = 0;
    const fetcher = vi.fn(async (input: string) => {
      if (input.endsWith("auth/csrf/"))
        return new Response(JSON.stringify({ csrfToken: "csrf" }));
      if (input.endsWith("auth/refresh/")) {
        refreshes++;
        await Promise.resolve();
        renewed = true;
        return new Response("{}");
      }
      return new Response(
        JSON.stringify(renewed ? { ok: true } : { detail: "Expired" }),
        { status: renewed ? 200 : 401 },
      );
    });
    vi.stubGlobal("fetch", fetcher);
    const { api } = await import("./client");
    await Promise.all([api("books/"), api("auth/me/")]);
    expect(refreshes).toBe(1);
    expect(
      fetcher.mock.calls.some(([path]) => path.endsWith("auth/refresh/")),
    ).toBe(true);
  });
  it("does not refresh login failures or retry failed writes blindly", async () => {
    const fetcher = vi.fn(
      async () =>
        new Response(JSON.stringify({ detail: "Rejected" }), { status: 401 }),
    );
    vi.stubGlobal("fetch", fetcher);
    const { api } = await import("./client");
    await expect(api("auth/login/")).rejects.toThrow("Rejected");
    expect(fetcher).toHaveBeenCalledTimes(1);
  });
  it("shows Retry-After and preserves validation details", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(
        async () =>
          new Response("{}", { status: 429, headers: { "Retry-After": "17" } }),
      ),
    );
    const { api } = await import("./client");
    await expect(api("books/")).rejects.toThrow("17 seconds");
  });
});

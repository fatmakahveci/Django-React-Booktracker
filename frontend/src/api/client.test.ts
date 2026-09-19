import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
beforeEach(() => vi.resetModules());
afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});
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
  it("does not refresh login failures", async () => {
    const fetcher = vi.fn(
      async () =>
        new Response(JSON.stringify({ detail: "Rejected" }), { status: 401 }),
    );
    vi.stubGlobal("fetch", fetcher);
    const { api } = await import("./client");
    await expect(api("auth/login/")).rejects.toThrow("Rejected");
    expect(fetcher).toHaveBeenCalledTimes(1);
  });
  it("shows Retry-After", async () => {
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

  it("does not retry a write after a server failure", async () => {
    const fetcher = vi.fn(async (path: string) =>
      path.endsWith("auth/csrf/")
        ? new Response(JSON.stringify({ csrfToken: "csrf" }))
        : new Response(JSON.stringify({ detail: "Unavailable" }), {
            status: 503,
          }),
    );
    vi.stubGlobal("fetch", fetcher);
    const { api } = await import("./client");
    await expect(api("books/", "POST", { title: "Draft" })).rejects.toThrow(
      "Unavailable",
    );
    expect(fetcher.mock.calls.map(([path]) => path)).toEqual([
      "/api/auth/csrf/",
      "/api/books/",
    ]);
  });

  it("expires a session when the retried request is still unauthorized", async () => {
    const dispatch = vi.spyOn(window, "dispatchEvent");
    vi.stubGlobal(
      "fetch",
      vi.fn(async (path: string) => {
        if (path.endsWith("auth/csrf/"))
          return new Response(JSON.stringify({ csrfToken: "csrf" }));
        if (path.endsWith("auth/refresh/")) return new Response("{}");
        return new Response(JSON.stringify({ detail: "Revoked" }), {
          status: 401,
        });
      }),
    );
    const { api } = await import("./client");
    await expect(api("books/")).rejects.toThrow("Revoked");
    expect(dispatch).toHaveBeenCalledTimes(1);
    expect(dispatch.mock.calls[0][0].type).toBe("session-expired");
  });

  it("waits for refresh before logout and does not replay a pending write", async () => {
    let completeRefresh!: (response: Response) => void;
    let refreshStarted!: () => void;
    const started = new Promise<void>((resolve) => {
      refreshStarted = resolve;
    });
    const fetcher = vi.fn(async (path: string) => {
      if (path.endsWith("auth/csrf/"))
        return new Response(JSON.stringify({ csrfToken: "csrf" }));
      if (path.endsWith("auth/refresh/")) {
        refreshStarted();
        return new Promise<Response>((resolve) => {
          completeRefresh = resolve;
        });
      }
      if (path.endsWith("auth/logout/"))
        return new Response(null, { status: 204 });
      return new Response(JSON.stringify({ detail: "Expired" }), {
        status: 401,
      });
    });
    vi.stubGlobal("fetch", fetcher);
    const { api, logout } = await import("./client");
    const write = expect(
      api("books/1/", "PATCH", { finished: true }),
    ).rejects.toThrow("Expired");
    await started;
    const ending = logout();
    expect(
      fetcher.mock.calls.some(([path]) => path.endsWith("auth/logout/")),
    ).toBe(false);
    completeRefresh(new Response("{}"));
    await Promise.all([write, ending]);
    expect(
      fetcher.mock.calls.filter(([path]) => path.endsWith("books/1/")),
    ).toHaveLength(1);
    expect(fetcher.mock.calls.at(-1)?.[0]).toBe("/api/auth/logout/");
  });

  it("keeps logout failures visible and allows a retry", async () => {
    let attempts = 0;
    vi.stubGlobal(
      "fetch",
      vi.fn(async (path: string) => {
        if (path.endsWith("auth/csrf/"))
          return new Response(JSON.stringify({ csrfToken: "csrf" }));
        attempts++;
        return attempts === 1
          ? new Response(JSON.stringify({ detail: "Unavailable" }), {
              status: 503,
            })
          : new Response(null, { status: 204 });
      }),
    );
    const { logout } = await import("./client");
    await expect(logout()).rejects.toThrow("Unavailable");
    await expect(logout()).resolves.toBeUndefined();
    expect(attempts).toBe(2);
  });
});

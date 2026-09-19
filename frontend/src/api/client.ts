const base = import.meta.env.VITE_API_URL || "/api/";
let csrf = "";
let csrfPending: Promise<string> | null = null;
let refreshPending: Promise<void> | null = null;
let endingSession = false;
export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public fields: Record<string, unknown> = {},
  ) {
    super(message);
  }
}
export async function csrfToken(): Promise<string> {
  if (csrf) return csrf;
  if (!csrfPending)
    csrfPending = fetch(`${base}auth/csrf/`, { credentials: "include" })
      .then(async (response) => {
        if (!response.ok)
          throw new ApiError(
            response.status,
            "Could not connect. Please try again.",
          );
        const data = await response.json();
        csrf = data.csrfToken;
        return csrf;
      })
      .finally(() => {
        csrfPending = null;
      });
  return csrfPending;
}
async function send<T>(
  path: string,
  method: string,
  body?: unknown,
): Promise<T> {
  const headers: Record<string, string> = { Accept: "application/json" };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (!["GET", "HEAD"].includes(method))
    headers["X-CSRFToken"] = await csrfToken();
  const response = await fetch(`${base}${path}`, {
    method,
    credentials: "include",
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const wait = response.headers.get("Retry-After");
    throw new ApiError(
      response.status,
      response.status === 429
        ? `Too many attempts. Try again in ${wait || "a few"} seconds.`
        : data.error?.message ||
            data.detail ||
            "Something went wrong. Please try again.",
      data.error?.fields || {},
    );
  }
  return response.status === 204 ? (undefined as T) : response.json();
}
export async function api<T>(
  path: string,
  method = "GET",
  body?: unknown,
  retry = true,
): Promise<T> {
  try {
    return await send<T>(path, method, body);
  } catch (error) {
    if (
      error instanceof ApiError &&
      error.status === 401 &&
      retry &&
      !endingSession &&
      !/auth\/(login|register|refresh|logout|csrf|password\/reset|email)/.test(
        path,
      )
    ) {
      if (!refreshPending)
        refreshPending = send<void>("auth/refresh/", "POST").finally(() => {
          refreshPending = null;
        });
      try {
        await refreshPending;
      } catch (refreshError) {
        if (
          refreshError instanceof ApiError &&
          [400, 401, 403].includes(refreshError.status)
        )
          window.dispatchEvent(new Event("session-expired"));
        throw refreshError;
      }
      if (endingSession) throw error;
      try {
        return await send<T>(path, method, body);
      } catch (retryError) {
        // A revoked session can fail even if refresh completed just beforehand.
        if (retryError instanceof ApiError && retryError.status === 401)
          window.dispatchEvent(new Event("session-expired"));
        throw retryError;
      }
    }
    throw error;
  }
}
export async function logout(): Promise<void> {
  endingSession = true;
  try {
    if (refreshPending) await refreshPending.catch(() => undefined);
    await send("auth/logout/", "POST");
  } finally {
    endingSession = false;
  }
}
export function errorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    const fields = Object.entries(error.fields)
      .filter(([key]) => key !== "detail")
      .map(
        ([key, value]) =>
          `${key.replaceAll("_", " ")}: ${Array.isArray(value) ? value.join(" ") : String(value)}`,
      );
    return fields.length ? fields.join(" ") : error.message;
  }
  return "Could not connect. Your changes have not been saved. Please try again.";
}

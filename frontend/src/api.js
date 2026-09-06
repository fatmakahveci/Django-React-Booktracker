import axios from "axios";

export function readTokens() {
  try {
    const tokens = JSON.parse(localStorage.getItem("authTokens"));
    return typeof tokens?.access === "string" && typeof tokens?.refresh === "string"
      ? tokens : null;
  } catch {
    return null;
  }
}

export function clearTokens() {
  localStorage.removeItem("authTokens");
  localStorage.removeItem("user");
}

const baseURL = import.meta.env.VITE_API_URL || "http://localhost:8000/";
export const publicApi = axios.create({ baseURL, timeout: 15000 });
const api = axios.create({ baseURL, timeout: 15000 });
let refreshing;

api.interceptors.request.use((config) => {
  const tokens = readTokens();
  if (tokens) config.headers.Authorization = `Bearer ${tokens.access}`;
  return config;
});

api.interceptors.response.use((response) => response, async (error) => {
  const original = error.config;
  const tokens = readTokens();
  if (error.response?.status !== 401 || !original || original._retried || !tokens) {
    return Promise.reject(error);
  }
  original._retried = true;
  try {
    // Parallel book requests share one refresh, so rotation cannot invalidate
    // a second simultaneous refresh request.
    if (!refreshing) {
      refreshing = publicApi.post("/token/refresh/", { refresh: tokens.refresh })
        .then(({ data }) => {
          if (readTokens()?.refresh !== tokens.refresh) throw new Error("Session changed");
          if (typeof data.access !== "string") throw new Error("Invalid token response");
          const updated = { access: data.access, refresh: data.refresh || tokens.refresh };
          localStorage.setItem("authTokens", JSON.stringify(updated));
          return updated;
        }).finally(() => { refreshing = undefined; });
    }
    const updated = await refreshing;
    original.headers.Authorization = `Bearer ${updated.access}`;
    return api(original);
  } catch (refreshError) {
    // Never erase a newer login or resurrect a session after logout.
    if (readTokens()?.refresh === tokens.refresh) {
      clearTokens();
      window.location.assign("/login/");
    }
    return Promise.reject(refreshError);
  }
});

export default api;

// One fetch wrapper for every screen: adds the sign-in token, normalises errors,
// and signs the user out when the server says the session is no longer valid.
const API_BASE = import.meta.env?.VITE_API_BASE ?? "";
const TOKEN_KEY = "autocare.token";

export function getToken() {
  try { return localStorage.getItem(TOKEN_KEY); } catch { return null; }
}
export function setToken(t) {
  try { t ? localStorage.setItem(TOKEN_KEY, t) : localStorage.removeItem(TOKEN_KEY); } catch { /* private mode */ }
}

export class ApiError extends Error {
  constructor(status, body) {
    const b = body?.detail && typeof body.detail === "object" ? body.detail : body;
    const validation = Array.isArray(body?.detail) ? "Check the highlighted fields and try again." : null;
    super(b?.message ?? validation ?? `Request failed (${status})`);
    this.status = status;
    this.code = b?.error ?? "unknown_error";
    this.language = b?.language ?? "en";
  }
}

export async function api(path, { method = "GET", body, signal } = {}) {
  const headers = { Accept: "application/json" };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, { method, headers, signal, body: body === undefined ? undefined : JSON.stringify(body) });
  } catch (e) {
    if (e.name === "AbortError") throw e;
    throw new ApiError(0, { message: "The AutoCare server didn't respond. Check that it is running." });
  }
  if (res.status === 204) return null;
  let data = null;
  try { data = await res.json(); } catch { /* empty body */ }
  if (!res.ok) {
    const err = new ApiError(res.status, data);
    if (res.status === 401 && token) window.dispatchEvent(new Event("autocare:signed-out"));
    throw err;
  }
  return data;
}

// Endpoints used by the screens. All go through api() so the sign-in token is attached.
import { api, ApiError } from "./client";

export { ApiError as DiagnoseApiError };

export const askDiagnosticQuestion = ({ userVehicleId, query, codeSource = "typed", signal }) =>
  api("/api/v1/diagnose/query", { method: "POST", body: { user_vehicle_id: userVehicleId ?? null, query, code_source: codeSource }, signal });

// Story 3: read fault codes from a scanner photo (data URL). The server doesn't keep the photo.
export const readCodeFromPhoto = (image, language = "en") =>
  api("/api/v1/diagnose/read-code", { method: "POST", body: { image, language } });

// Story 12: severity + body area of visible damage. Photos are not stored by the server.
export const assessDamage = ({ userVehicleId, images, note, language = "en" }) =>
  api("/api/v1/damage/assess", { method: "POST", body: { user_vehicle_id: userVehicleId, images, note, language } });

export const auth = {
  login: (email, password) => api("/api/v1/auth/login", { method: "POST", body: { email, password } }),
  register: (full_name, email, password) => api("/api/v1/auth/register", { method: "POST", body: { full_name, email, password } }),
  me: () => api("/api/v1/auth/me"),
};

export const owner = {
  catalog: () => api("/api/v1/catalog/vehicles"),
  vehicles: () => api("/api/v1/me/vehicles"),
  addVehicle: (body) => api("/api/v1/me/vehicles", { method: "POST", body }),
  updateVehicle: (id, body) => api(`/api/v1/me/vehicles/${id}`, { method: "PATCH", body }),
  cases: () => api("/api/v1/me/cases"),
};

export const mechanic = {
  submit: (note) => api("/api/v1/mechanic/notes", { method: "POST", body: note }),
  notes: () => api("/api/v1/mechanic/notes"),
};

export const admin = {
  stats: () => api("/api/v1/admin/stats"),
  documents: () => api("/api/v1/admin/documents"),
  notes: (status) => api(`/api/v1/admin/notes${status ? `?status=${status}` : ""}`),
  approve: (id) => api(`/api/v1/admin/notes/${id}/approve`, { method: "POST" }),
  reject: (id) => api(`/api/v1/admin/notes/${id}/reject`, { method: "POST" }),
  users: () => api("/api/v1/admin/users"),
  setRole: (id, role) => api(`/api/v1/admin/users/${id}`, { method: "PATCH", body: { role } }),
};

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

// Story 7 / M5: Repair recommendation verification
export const verifyRepair = ({ userVehicleId, proposedRepair, symptoms, code, damageLocation }) =>
  api("/api/v1/diagnose/verify-repair", {
    method: "POST",
    body: { user_vehicle_id: userVehicleId, proposed_repair: proposedRepair, symptoms, code: code || null, damage_location: damageLocation || null }
  });

// Story 8 / M6: Knowledge graph root-cause chains
export const fetchRootCauses = (symptom, maxDepth = 3) =>
  api("/api/v1/diagnose/root-cause", { method: "POST", body: { symptom, max_depth: maxDepth } });

// Story 9 / M8: Similar cases bank
export const fetchSimilarCases = ({ userVehicleId, symptom, code, topK = 3 }) =>
  api("/api/v1/diagnose/similar-cases", {
    method: "POST",
    body: { user_vehicle_id: userVehicleId, symptom, code: code || null, top_k: topK }
  });

// Story 10 & 11 / M7: Vehicle Health & Maintenance Prediction
export const fetchVehicleHealth = (userVehicleId) =>
  api(`/api/v1/vehicle/${userVehicleId}/health`);

export const fetchMaintenancePrediction = (userVehicleId) =>
  api(`/api/v1/vehicle/${userVehicleId}/maintenance-prediction`);

// Story 13 / M9: Download PDF Report
export const downloadReportPdf = async ({ userVehicleId, query, diagnosis }) => {
  const token = localStorage.getItem("autocare.token");
  const res = await fetch("/api/v1/diagnose/report/pdf", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    },
    body: JSON.stringify({ user_vehicle_id: userVehicleId, query, diagnosis })
  });
  if (!res.ok) throw new Error("PDF generation failed");
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `autocare-report-${diagnosis.case_id || "export"}.pdf`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
};


export const auth = {
  login: (email, password) => api("/api/v1/auth/login", { method: "POST", body: { email, password } }),
  register: (full_name, email, password) => api("/api/v1/auth/register", { method: "POST", body: { full_name, email, password } }),
  googleAuth: ({ credential, email, full_name, google_id }) => api("/api/v1/auth/google", { method: "POST", body: { credential, email, full_name, google_id } }),
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

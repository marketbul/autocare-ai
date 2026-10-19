import { useState, useEffect } from "react";
import { Alert } from "./ui";

export function SettingsScreen({ user, theme, onToggleTheme, go }) {
  const [lang, setLang] = useState(() => {
    try { return localStorage.getItem("autocare_lang") || "en"; } catch { return "en"; }
  });
  const [units, setUnits] = useState(() => {
    try { return localStorage.getItem("autocare_units") || "km"; } catch { return "km"; }
  });
  const [notifications, setNotifications] = useState(true);
  const [safetyAlerts, setSafetyAlerts] = useState(true);
  const [savedMsg, setSavedMsg] = useState(false);

  function handleSave() {
    try {
      localStorage.setItem("autocare_lang", lang);
      localStorage.setItem("autocare_units", units);
      setSavedMsg(true);
      setTimeout(() => setSavedMsg(false), 3000);
    } catch {}
  }

  return (
    <div className="page" style={{ maxWidth: "800px" }}>
      <div className="page-head">
        <div>
          <h1>Settings & Preferences</h1>
          <p>Manage your interface theme, vehicle diagnostic units, language, and account security.</p>
        </div>
        {savedMsg && (
          <span style={{
            padding: "6px 12px",
            background: "var(--success-dim)",
            border: "1px solid var(--success-border)",
            color: "var(--success)",
            borderRadius: "8px",
            fontSize: "13px",
            fontWeight: "600"
          }}>
            ✓ Preferences saved
          </span>
        )}
      </div>

      {/* 1. Appearance & Theme */}
      <div className="panel">
        <h2 style={{ marginBottom: "14px", display: "flex", alignItems: "center", gap: "8px" }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="5"/>
            <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
          </svg>
          Appearance
        </h2>

        <div style={{ display: "grid", gap: "16px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <b style={{ display: "block", fontSize: "14px", color: "var(--text-primary)" }}>Theme Mode</b>
              <small style={{ color: "var(--text-muted)", fontSize: "12.5px" }}>Choose between clean light mode or dark slate mode.</small>
            </div>

            <div style={{ display: "flex", gap: "6px", background: "var(--surface-2)", padding: "4px", borderRadius: "8px", border: "1px solid var(--border)" }}>
              <button
                type="button"
                onClick={() => theme !== "light" && onToggleTheme && onToggleTheme()}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                  padding: "6px 12px",
                  borderRadius: "6px",
                  border: "none",
                  background: theme === "light" ? "var(--surface-1)" : "transparent",
                  color: theme === "light" ? "var(--primary)" : "var(--text-secondary)",
                  fontWeight: theme === "light" ? "700" : "500",
                  fontSize: "13px",
                  cursor: "pointer",
                  boxShadow: theme === "light" ? "var(--shadow-sm)" : "none"
                }}
              >
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/>
                </svg>
                Light
              </button>

              <button
                type="button"
                onClick={() => theme !== "dark" && onToggleTheme && onToggleTheme()}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                  padding: "6px 12px",
                  borderRadius: "6px",
                  border: "none",
                  background: theme === "dark" ? "var(--surface-1)" : "transparent",
                  color: theme === "dark" ? "var(--primary)" : "var(--text-secondary)",
                  fontWeight: theme === "dark" ? "700" : "500",
                  fontSize: "13px",
                  cursor: "pointer",
                  boxShadow: theme === "dark" ? "var(--shadow-sm)" : "none"
                }}
              >
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
                </svg>
                Dark
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 2. Diagnostic & Language Preferences */}
      <div className="panel">
        <h2 style={{ marginBottom: "14px", display: "flex", alignItems: "center", gap: "8px" }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" y1="22" x2="4" y2="15"/>
          </svg>
          Diagnostic Preferences
        </h2>

        <div style={{ display: "grid", gap: "16px" }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "14px" }}>
            <div>
              <label style={{ display: "block", fontSize: "13px", fontWeight: "600", marginBottom: "6px", color: "var(--text-primary)" }}>
                Preferred Diagnostic Language
              </label>
              <select value={lang} onChange={(e) => { setLang(e.target.value); handleSave(); }}>
                <option value="en">English (Official Workshop Manuals)</option>
                <option value="roman_ur">Roman Urdu (gaari garam ho rahi hai)</option>
                <option value="ur">اردو (قومی زبان)</option>
              </select>
            </div>

            <div>
              <label style={{ display: "block", fontSize: "13px", fontWeight: "600", marginBottom: "6px", color: "var(--text-primary)" }}>
                Distance Units
              </label>
              <select value={units} onChange={(e) => { setUnits(e.target.value); handleSave(); }}>
                <option value="km">Kilometers (km) - Pakistan Standard</option>
                <option value="mi">Miles (mi)</option>
              </select>
            </div>
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", paddingTop: "8px", borderTop: "1px solid var(--border)" }}>
            <div>
              <b style={{ display: "block", fontSize: "13.5px", color: "var(--text-primary)" }}>10× Safety Priority Triage</b>
              <small style={{ color: "var(--text-muted)", fontSize: "12px" }}>Automatically flags brake, steering, and coolant boil hazards as Critical Stop alerts.</small>
            </div>
            <input
              type="checkbox"
              checked={safetyAlerts}
              onChange={(e) => setSafetyAlerts(e.target.checked)}
              style={{ width: "20px", height: "20px", accentColor: "var(--primary)" }}
            />
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", paddingTop: "8px", borderTop: "1px solid var(--border)" }}>
            <div>
              <b style={{ display: "block", fontSize: "13.5px", color: "var(--text-primary)" }}>Service Maintenance Reminders</b>
              <small style={{ color: "var(--text-muted)", fontSize: "12px" }}>Proactive notifications when oil or brake pads approach service intervals.</small>
            </div>
            <input
              type="checkbox"
              checked={notifications}
              onChange={(e) => setNotifications(e.target.checked)}
              style={{ width: "20px", height: "20px", accentColor: "var(--primary)" }}
            />
          </div>
        </div>
      </div>

      {/* 3. Account & Authentication Info */}
      <div className="panel">
        <h2 style={{ marginBottom: "14px", display: "flex", alignItems: "center", gap: "8px" }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
          </svg>
          Account Profile
        </h2>

        <div style={{ display: "grid", gap: "12px", fontSize: "13.5px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
            <span style={{ color: "var(--text-secondary)" }}>Full Name</span>
            <b style={{ color: "var(--text-primary)" }}>{user?.full_name || "Muhammad Abdullah"}</b>
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
            <span style={{ color: "var(--text-secondary)" }}>Email Address</span>
            <b style={{ color: "var(--text-primary)" }}>{user?.email || "abdullah262686@gmail.com"}</b>
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
            <span style={{ color: "var(--text-secondary)" }}>Account Role</span>
            <span className="pill pill-ok" style={{ textTransform: "capitalize" }}>{user?.role || "owner"}</span>
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0" }}>
            <span style={{ color: "var(--text-secondary)" }}>Google Authentication</span>
            <span style={{ color: "var(--success)", fontWeight: "600", display: "inline-flex", alignItems: "center", gap: "4px" }}>
              ✓ Verified Active
            </span>
          </div>
        </div>
      </div>

      {/* 4. Project & System Information */}
      <div className="panel" style={{ background: "var(--surface-2)" }}>
        <h2 style={{ marginBottom: "10px", fontSize: "14px", color: "var(--text-secondary)" }}>
          System & Build Information
        </h2>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", fontSize: "12.5px", color: "var(--text-muted)" }}>
          <div>Project: <b>AutoCare AI (FYP-1)</b></div>
          <div>Institution: <b>PUCIT / Dept of Computer Science</b></div>
          <div>Version: <b>2.4.0 (Production Release)</b></div>
          <div>Engine API: <b>FastAPI + SQLite + NetworkX</b></div>
        </div>
      </div>
    </div>
  );
}

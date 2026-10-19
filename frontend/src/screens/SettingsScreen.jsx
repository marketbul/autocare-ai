import { useState } from "react";
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
    <div className="page" style={{ maxWidth: "860px" }}>
      <div className="page-head">
        <div>
          <h1>Settings & Workspace</h1>
          <p>Customize your diagnostic copilot, telemetry display, language, and theme preferences.</p>
        </div>
        {savedMsg && (
          <span style={{
            padding: "6px 14px",
            background: "var(--success-dim)",
            border: "1px solid var(--success-border)",
            color: "var(--success)",
            borderRadius: "8px",
            fontSize: "13px",
            fontWeight: "600"
          }}>
            ✓ Settings saved
          </span>
        )}
      </div>

      {/* 1. Appearance & Theme Selection with Visual Cards */}
      <div className="panel">
        <h2 style={{ marginBottom: "16px", display: "flex", alignItems: "center", gap: "8px", fontSize: "16px" }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="5"/>
            <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
          </svg>
          Interface Appearance
        </h2>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "14px" }}>
          {/* Dark Mode Card */}
          <div
            onClick={() => theme !== "dark" && onToggleTheme && onToggleTheme()}
            style={{
              padding: "16px",
              borderRadius: "12px",
              border: `2px solid ${theme === "dark" ? "var(--primary)" : "var(--border)"}`,
              background: theme === "dark" ? "var(--surface-2)" : "var(--surface-1)",
              cursor: "pointer",
              transition: "all 0.2s ease"
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
              <b style={{ color: "var(--text-primary)", fontSize: "14px" }}>🌙 Dark Zinc Mode</b>
              {theme === "dark" && <span style={{ color: "var(--primary)", fontWeight: "700", fontSize: "12px" }}>Active</span>}
            </div>
            <p style={{ margin: 0, fontSize: "12.5px", color: "var(--text-muted)" }}>
              High-contrast carbon canvas designed for workshop bay screens and low-light inspection environments.
            </p>
          </div>

          {/* Light Mode Card */}
          <div
            onClick={() => theme !== "light" && onToggleTheme && onToggleTheme()}
            style={{
              padding: "16px",
              borderRadius: "12px",
              border: `2px solid ${theme === "light" ? "var(--primary)" : "var(--border)"}`,
              background: theme === "light" ? "var(--surface-2)" : "var(--surface-1)",
              cursor: "pointer",
              transition: "all 0.2s ease"
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
              <b style={{ color: "var(--text-primary)", fontSize: "14px" }}>☀️ Crisp Light Mode</b>
              {theme === "light" && <span style={{ color: "var(--primary)", fontWeight: "700", fontSize: "12px" }}>Active</span>}
            </div>
            <p style={{ margin: 0, fontSize: "12.5px", color: "var(--text-muted)" }}>
              Clean, daylight-readable corporate white surface matching Apple and Linear design guidelines.
            </p>
          </div>
        </div>
      </div>

      {/* 2. Diagnostic & Language Preferences */}
      <div className="panel">
        <h2 style={{ marginBottom: "16px", display: "flex", alignItems: "center", gap: "8px", fontSize: "16px" }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" y1="22" x2="4" y2="15"/>
          </svg>
          Diagnostic Engine & Localization
        </h2>

        <div style={{ display: "grid", gap: "16px" }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "14px" }}>
            <div>
              <label style={{ display: "block", fontSize: "13px", fontWeight: "600", marginBottom: "6px", color: "var(--text-primary)" }}>
                Diagnostic Language Engine
              </label>
              <select value={lang} onChange={(e) => { setLang(e.target.value); handleSave(); }}>
                <option value="en">English (Official OEM Service Manuals)</option>
                <option value="roman_ur">Roman Urdu (Desi Mechanic Terminology)</option>
                <option value="ur">اردو (قومی زبان و تکنیکی لغات)</option>
              </select>
            </div>

            <div>
              <label style={{ display: "block", fontSize: "13px", fontWeight: "600", marginBottom: "6px", color: "var(--text-primary)" }}>
                Telemetry Units
              </label>
              <select value={units} onChange={(e) => { setUnits(e.target.value); handleSave(); }}>
                <option value="km">Kilometers (km) &bull; Celsius (°C) &bull; PKR (₨)</option>
                <option value="mi">Miles (mi) &bull; Fahrenheit (°F) &bull; USD ($)</option>
              </select>
            </div>
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", paddingTop: "10px", borderTop: "1px solid var(--border)" }}>
            <div>
              <b style={{ display: "block", fontSize: "13.5px", color: "var(--text-primary)" }}>High-Urgency Mechanical Safety Intercept</b>
              <small style={{ color: "var(--text-muted)", fontSize: "12px" }}>Immediately triggers critical warnings when brake hydraulic drop or coolant boil is identified.</small>
            </div>
            <input
              type="checkbox"
              checked={safetyAlerts}
              onChange={(e) => setSafetyAlerts(e.target.checked)}
              style={{ width: "20px", height: "20px", accentColor: "var(--primary)" }}
            />
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", paddingTop: "10px", borderTop: "1px solid var(--border)" }}>
            <div>
              <b style={{ display: "block", fontSize: "13.5px", color: "var(--text-primary)" }}>Predictive Wear & Maintenance Notifications</b>
              <small style={{ color: "var(--text-muted)", fontSize: "12px" }}>Alerts before engine oil degradation or brake pad wear reaches safety thresholds.</small>
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

      {/* 3. Account Profile Information */}
      <div className="panel">
        <h2 style={{ marginBottom: "16px", display: "flex", alignItems: "center", gap: "8px", fontSize: "16px" }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
          </svg>
          Account & Project Team Profile
        </h2>

        <div style={{ display: "grid", gap: "12px", fontSize: "13.5px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
            <span style={{ color: "var(--text-secondary)" }}>Student Name</span>
            <b style={{ color: "var(--text-primary)" }}>{user?.full_name || "Abdullah"}</b>
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
            <span style={{ color: "var(--text-secondary)" }}>PUCIT Roll Number</span>
            <b style={{ color: "var(--primary)" }}>BSDSF23A035 (35)</b>
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
            <span style={{ color: "var(--text-secondary)" }}>Email Address</span>
            <b style={{ color: "var(--text-primary)" }}>{user?.email || "abdullah262686@gmail.com"}</b>
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
            <span style={{ color: "var(--text-secondary)" }}>Current Workspace Role</span>
            <span className="pill pill-ok" style={{ textTransform: "capitalize" }}>{user?.role || "owner"}</span>
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0" }}>
            <span style={{ color: "var(--text-secondary)" }}>Authentication Status</span>
            <span style={{ color: "var(--success)", fontWeight: "600", display: "inline-flex", alignItems: "center", gap: "4px" }}>
              ✓ Google Verified &bull; Active
            </span>
          </div>
        </div>
      </div>

      {/* 4. Academic & FYP Meta */}
      <div className="panel" style={{ background: "var(--surface-2)" }}>
        <h2 style={{ marginBottom: "10px", fontSize: "14px", color: "var(--text-secondary)" }}>
          Academic Project Specification
        </h2>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", fontSize: "12.5px", color: "var(--text-muted)" }}>
          <div>Project: <b>AutoCare AI (FYP Venture)</b></div>
          <div>Institution: <b>PUCIT, University of the Punjab</b></div>
          <div>Course: <b>Entrepreneurship for Computing Students</b></div>
          <div>Instructor: <b>Dr. Sadeeqa R. Khan</b></div>
        </div>
      </div>
    </div>
  );
}

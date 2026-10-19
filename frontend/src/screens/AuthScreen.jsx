import { useState } from "react";
import { auth } from "../api/diagnose";
import { Alert, Field } from "./ui";

const BASE = import.meta.env?.BASE_URL ?? "/app/";

const DEMO_CREDENTIALS = {
  owner: {
    email: "abdullah262686@gmail.com",
    name: "Abdullah",
    password: "password123",
    label: "Car Owner (Abdullah)"
  },
  mechanic: {
    email: "mechanic@autocare.pk",
    name: "Certified Workshop Mechanic",
    password: "password123",
    label: "Mechanic"
  },
  admin: {
    email: "admin@autocare.pk",
    name: "System Admin",
    password: "password123",
    label: "Administrator"
  }
};

export default function AuthScreen({ onSignedIn, theme, onToggleTheme }) {
  const [mode, setMode] = useState("signin");
  const [role, setRole] = useState("owner");
  const [form, setForm] = useState({ full_name: "", email: "", password: "" });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [showGoogleModal, setShowGoogleModal] = useState(false);
  const [googleEmail, setGoogleEmail] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  function pickRole(r) {
    setRole(r);
    const currentDemo = Object.values(DEMO_CREDENTIALS).find(c => c.email === form.email);
    if (!form.email || currentDemo) {
      setForm((f) => ({
        ...f,
        email: DEMO_CREDENTIALS[r].email,
        password: DEMO_CREDENTIALS[r].password,
        full_name: DEMO_CREDENTIALS[r].name
      }));
    }
  }

  async function directLoginRole(r) {
    const cred = DEMO_CREDENTIALS[r];
    setRole(r);
    setForm({ email: cred.email, password: cred.password, full_name: cred.name });
    setBusy(true);
    setError(null);
    try {
      const session = await auth.login(cred.email, cred.password);
      onSignedIn(session);
    } catch {
      // If login fails, attempt register for demo
      try {
        const session = await auth.register(cred.name, cred.email, cred.password);
        onSignedIn(session);
      } catch (err) {
        setError(err.message || "Failed to sign in demo user.");
      }
    } finally {
      setBusy(false);
    }
  }

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const session = mode === "signin"
        ? await auth.login(form.email, form.password)
        : await auth.register(form.full_name, form.email, form.password);
      onSignedIn(session);
    } catch (err) {
      setError(err.message || "Failed to sign in. Please verify your credentials.");
    } finally {
      setBusy(false);
    }
  }

  async function handleGoogleAuth(emailToUse, nameToUse) {
    const targetEmail = (emailToUse || "abdullah262686@gmail.com").trim();
    const targetName = (nameToUse || "Abdullah").trim();
    setBusy(true);
    setError(null);
    try {
      const session = await auth.googleAuth({
        email: targetEmail,
        full_name: targetName
      });
      setShowGoogleModal(false);
      onSignedIn(session);
    } catch (err) {
      setError(err.message || "Google Account authentication failed.");
    } finally {
      setBusy(false);
    }
  }

  const signin = mode === "signin";

  return (
    <div className="auth-wrapper">
      {/* Background Ambient Glow */}
      <div className="auth-bg-glow" />

      {/* Top Header Floating Bar */}
      <div className="auth-top-bar">
        <div className="auth-top-brand">
          <img src={`${BASE}emblem-256.jpg`} alt="AutoCare AI" width="24" height="24" />
          <span>AutoCare <b>AI</b></span>
          <span className="auth-version-badge">v2.4 Enterprise</span>
        </div>

        {onToggleTheme && (
          <button
            type="button"
            className="icon-btn"
            onClick={onToggleTheme}
            title={`Switch to ${theme === "dark" ? "Light" : "Dark"} mode`}
            style={{ width: "36px", height: "36px", borderRadius: "10px" }}
          >
            {theme === "dark" ? (
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="5"/>
                <line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
                <line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
              </svg>
            ) : (
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
              </svg>
            )}
          </button>
        )}
      </div>

      <div className="auth-card">
        {/* Brand Header */}
        <div className="auth-header">
          <div className="auth-logo-frame">
            <img src={`${BASE}emblem-256.jpg`} alt="AutoCare AI" />
          </div>
          <h1>{signin ? "Welcome back" : "Get started with AutoCare AI"}</h1>
          <p>Autonomous vehicle diagnostics, telemetry & repair transparency</p>
        </div>

        {/* Primary Action: Modern Google Auth Button */}
        <button
          type="button"
          className="google-auth-btn"
          onClick={() => setShowGoogleModal(true)}
          disabled={busy}
        >
          <svg width="18" height="18" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.17z"/>
            <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.34 24 12 24z"/>
            <path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.98 0 12s.45 3.82 1.25 5.42l4.03-3.15z"/>
            <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.34 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"/>
          </svg>
          <span>{signin ? "Continue with Google" : "Sign up with Google"}</span>
        </button>

        {/* Divider */}
        <div className="auth-divider">
          <div className="auth-divider-line" />
          <span>or continue with email</span>
          <div className="auth-divider-line" />
        </div>

        {/* Role Selector Tabs */}
        <div>
          <label className="auth-label">Select Account Role</label>
          <div className="auth-role-tabs">
            {[
              { id: "owner", label: "Car Owner", icon: "🚗" },
              { id: "mechanic", label: "Mechanic", icon: "🔧" },
              { id: "admin", label: "Admin", icon: "🛡️" }
            ].map((r) => (
              <button
                key={r.id}
                type="button"
                onClick={() => pickRole(r.id)}
                className={`auth-role-tab ${role === r.id ? "is-selected" : ""}`}
              >
                <span style={{ marginRight: "4px" }}>{r.icon}</span>
                {r.label}
              </button>
            ))}
          </div>
        </div>

        {/* Form Inputs */}
        <form className="form" onSubmit={submit}>
          {!signin && (
            <Field label="Full Name">
              <input
                type="text"
                placeholder="e.g. Abdullah"
                value={form.full_name}
                onChange={set("full_name")}
                required
              />
            </Field>
          )}

          <Field label="Email Address">
            <input
              type="email"
              placeholder="name@example.com"
              value={form.email}
              onChange={set("email")}
              autoComplete="username"
              required
            />
          </Field>

          <Field label="Password">
            <div style={{ position: "relative" }}>
              <input
                type={showPassword ? "text" : "password"}
                placeholder="••••••••••••"
                value={form.password}
                onChange={set("password")}
                autoComplete={signin ? "current-password" : "new-password"}
                style={{ paddingRight: "40px" }}
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                tabIndex={-1}
                style={{
                  position: "absolute",
                  right: "10px",
                  top: "50%",
                  transform: "translateY(-50%)",
                  background: "transparent",
                  border: 0,
                  color: "var(--text-muted)",
                  cursor: "pointer",
                  padding: "4px"
                }}
              >
                {showPassword ? (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                ) : (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                )}
              </button>
            </div>
          </Field>

          {error && <Alert tone="warn">{error}</Alert>}

          <button
            type="submit"
            className="btn primary"
            disabled={busy}
            style={{ width: "100%", padding: "11px 0", marginTop: "6px", fontWeight: "600", fontSize: "14px" }}
          >
            {busy ? "Authenticating..." : (signin ? `Sign in as ${role === 'owner' ? 'Car Owner' : role === 'mechanic' ? 'Mechanic' : 'System Admin'}` : "Create Account")}
          </button>
        </form>

        {/* Quick Demo One-Click Logins */}
        <div className="auth-quick-demo">
          <span className="auth-quick-label">⚡ 1-Click Instant Demo Login:</span>
          <div className="auth-quick-chips">
            <button
              type="button"
              className="auth-chip"
              onClick={() => directLoginRole("owner")}
              title="Sign in as Abdullah (Car Owner)"
            >
              🚗 Abdullah (Owner)
            </button>
            <button
              type="button"
              className="auth-chip"
              onClick={() => directLoginRole("mechanic")}
              title="Sign in as Certified Mechanic"
            >
              🔧 Mechanic
            </button>
            <button
              type="button"
              className="auth-chip"
              onClick={() => directLoginRole("admin")}
              title="Sign in as Administrator"
            >
              🛡️ Admin
            </button>
          </div>
        </div>

        {/* Bottom Switch */}
        <div className="auth-footer-switch">
          {signin ? (
            <>New to AutoCare AI? <button type="button" className="link" onClick={() => setMode("signup")}>Create account</button></>
          ) : (
            <>Already have an account? <button type="button" className="link" onClick={() => setMode("signin")}>Sign in</button></>
          )}
        </div>
      </div>

      {/* Professional Google Account Chooser Modal */}
      {showGoogleModal && (
        <div className="google-modal-backdrop" onClick={() => setShowGoogleModal(false)}>
          <div className="google-modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="google-modal-head">
              <svg width="22" height="22" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.17z"/>
                <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.34 24 12 24z"/>
                <path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.98 0 12s.45 3.82 1.25 5.42l4.03-3.15z"/>
                <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.34 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"/>
              </svg>
              <div>
                <h3>Choose an account</h3>
                <p>to continue to <b>AutoCare AI</b></p>
              </div>
              <button
                type="button"
                className="google-close-btn"
                onClick={() => setShowGoogleModal(false)}
              >
                ✕
              </button>
            </div>

            {/* Selected Google Account Row: Abdullah */}
            <div
              className="google-account-item"
              onClick={() => handleGoogleAuth("abdullah262686@gmail.com", "Abdullah")}
            >
              <div className="google-avatar">
                <span>A</span>
              </div>
              <div className="google-account-info">
                <b>Abdullah</b>
                <span>abdullah262686@gmail.com</span>
                <small className="google-badge">PUCIT &bull; Roll #35 &bull; Signed In</small>
              </div>
              <div className="google-check-arrow">&rarr;</div>
            </div>

            {/* Custom Google Email Option */}
            <div style={{ marginTop: "12px", borderTop: "1px solid var(--border)", paddingTop: "12px" }}>
              <span style={{ fontSize: "12px", color: "var(--text-muted)", display: "block", marginBottom: "6px" }}>
                Or use another Google email:
              </span>
              <div style={{ display: "flex", gap: "8px" }}>
                <input
                  type="email"
                  placeholder="your.email@gmail.com"
                  value={googleEmail}
                  onChange={(e) => setGoogleEmail(e.target.value)}
                  style={{ fontSize: "13px", padding: "7px 10px" }}
                />
                <button
                  type="button"
                  className="btn primary"
                  onClick={() => handleGoogleAuth(googleEmail, googleEmail.split("@")[0])}
                  disabled={!googleEmail.trim() || busy}
                  style={{ padding: "0 14px", fontSize: "12.5px" }}
                >
                  Continue
                </button>
              </div>
            </div>

            <div className="google-privacy-footer">
              To continue, Google will share your name, email address, and language preference with AutoCare AI.
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

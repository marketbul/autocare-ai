import { useState } from "react";
import { auth } from "../api/diagnose";
import { Alert, Field } from "./ui";

const BASE = import.meta.env?.BASE_URL ?? "/app/";

const DEMO_CREDENTIALS = {
  owner: {
    email: "abdullah262686@gmail.com",
    name: "Muhammad Abdullah",
    password: "password123",
    label: "Car Owner (Muhammad Abdullah)"
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
  const [googleName, setGoogleName] = useState("");

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  function pickRole(r) {
    setRole(r);
    // Optionally prefill email if empty or currently matching another demo
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

  function applyDemo(r) {
    const cred = DEMO_CREDENTIALS[r];
    setRole(r);
    setForm({
      email: cred.email,
      password: cred.password,
      full_name: cred.name
    });
    setError(null);
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
    const targetEmail = (emailToUse || googleEmail || "").trim();
    if (!targetEmail) {
      setError("Please provide a valid Google account email.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const session = await auth.googleAuth({
        email: targetEmail,
        full_name: (nameToUse || googleName || targetEmail.split("@")[0]).trim()
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
      {/* Top Bar Theme Toggle */}
      <div style={{
        position: "absolute",
        top: "20px",
        right: "24px",
        display: "flex",
        alignItems: "center",
        gap: "10px"
      }}>
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
        {/* Simple Brand Header */}
        <div className="auth-header">
          <img src={`${BASE}emblem-256.jpg`} alt="AutoCare AI" />
          <h1>{signin ? "Sign in to AutoCare AI" : "Create your account"}</h1>
          <p>Autonomous vehicle diagnostic & telemetry platform</p>
        </div>

        {/* Option 1: Continue with Google */}
        <button
          type="button"
          onClick={() => setShowGoogleModal(true)}
          disabled={busy}
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "10px",
            padding: "10px 16px",
            background: "var(--surface-2)",
            color: "var(--text-primary)",
            border: "1px solid var(--border)",
            borderRadius: "8px",
            fontWeight: "600",
            fontSize: "14px",
            cursor: "pointer",
            boxShadow: "var(--shadow-sm)"
          }}
        >
          <svg width="18" height="18" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.17z"/>
            <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.34 24 12 24z"/>
            <path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.98 0 12s.45 3.82 1.25 5.42l4.03-3.15z"/>
            <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.34 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"/>
          </svg>
          <span>{signin ? "Sign in with Google" : "Create account with Google"}</span>
        </button>

        {/* Google Quick Modal */}
        {showGoogleModal && (
          <div style={{
            padding: "14px",
            background: "var(--surface-2)",
            border: "1px solid var(--border)",
            borderRadius: "10px",
            display: "grid",
            gap: "10px"
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <b style={{ fontSize: "13px", color: "var(--text-primary)" }}>Google One-Click Sign In</b>
              <button
                type="button"
                onClick={() => setShowGoogleModal(false)}
                style={{ background: "none", border: 0, color: "var(--text-muted)", cursor: "pointer", fontSize: "15px" }}
              >
                ✕
              </button>
            </div>
            <input
              type="email"
              placeholder="Enter your google email (e.g. user@gmail.com)"
              value={googleEmail}
              onChange={(e) => setGoogleEmail(e.target.value)}
              style={{ fontSize: "13px" }}
            />
            <div style={{ display: "flex", gap: "8px" }}>
              <button
                type="button"
                className="btn primary"
                onClick={() => handleGoogleAuth()}
                disabled={busy}
                style={{ flex: 1, padding: "7px 0" }}
              >
                {busy ? "Verifying..." : "Verify & Continue"}
              </button>
              <button
                type="button"
                className="btn"
                onClick={() => handleGoogleAuth("abdullah262686@gmail.com", "Muhammad Abdullah")}
                disabled={busy}
                style={{ fontSize: "12px" }}
              >
                Use Abdullah's Google Account
              </button>
            </div>
          </div>
        )}

        {/* Divider */}
        <div style={{ display: "flex", alignItems: "center", gap: "10px", margin: "2px 0" }}>
          <div style={{ flex: 1, height: "1px", background: "var(--border)" }} />
          <span style={{ fontSize: "12px", color: "var(--text-muted)", textTransform: "uppercase" }}>or with email</span>
          <div style={{ flex: 1, height: "1px", background: "var(--border)" }} />
        </div>

        {/* Role Selector Tabs (Car Owner, Mechanic, Admin) */}
        <div>
          <label style={{ display: "block", fontSize: "12.5px", fontWeight: "600", color: "var(--text-secondary)", marginBottom: "6px" }}>
            Account Role
          </label>
          <div style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr 1fr",
            gap: "6px",
            background: "var(--surface-2)",
            padding: "4px",
            borderRadius: "8px",
            border: "1px solid var(--border)"
          }}>
            {[
              { id: "owner", label: "Car Owner" },
              { id: "mechanic", label: "Mechanic" },
              { id: "admin", label: "Admin" }
            ].map((r) => (
              <button
                key={r.id}
                type="button"
                onClick={() => pickRole(r.id)}
                style={{
                  padding: "6px 0",
                  borderRadius: "6px",
                  border: "none",
                  background: role === r.id ? "var(--surface-1)" : "transparent",
                  color: role === r.id ? "var(--primary)" : "var(--text-secondary)",
                  fontWeight: role === r.id ? "700" : "500",
                  fontSize: "12.5px",
                  cursor: "pointer",
                  boxShadow: role === r.id ? "var(--shadow-sm)" : "none",
                  transition: "all 0.15s ease"
                }}
              >
                {r.label}
              </button>
            ))}
          </div>
        </div>

        {/* Standard Form */}
        <form className="form" onSubmit={submit}>
          {!signin && (
            <Field label="Full Name">
              <input
                type="text"
                placeholder="e.g. Muhammad Abdullah"
                value={form.full_name}
                onChange={set("full_name")}
                required
              />
            </Field>
          )}

          <Field label="Email Address">
            <input
              type="email"
              placeholder="your@email.com"
              value={form.email}
              onChange={set("email")}
              autoComplete="username"
              required
            />
          </Field>

          <Field label="Password">
            <input
              type="password"
              placeholder="••••••••••••"
              value={form.password}
              onChange={set("password")}
              autoComplete={signin ? "current-password" : "new-password"}
              required
            />
          </Field>

          {error && <Alert>{error}</Alert>}

          <button className="btn primary" disabled={busy} style={{ width: "100%", padding: "10px 0", marginTop: "4px" }}>
            {busy ? "Signing in..." : (signin ? `Sign in as ${role === 'owner' ? 'Car Owner' : role === 'mechanic' ? 'Mechanic' : 'Admin'}` : "Create Account")}
          </button>
        </form>

        {/* Quick Demo Fill Helper */}
        <div style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: "8px",
          fontSize: "12px",
          color: "var(--text-muted)",
          paddingTop: "4px"
        }}>
          <span>Quick Demo Fill:</span>
          <button type="button" className="link" onClick={() => applyDemo("owner")}>Owner</button>
          <span>•</span>
          <button type="button" className="link" onClick={() => applyDemo("mechanic")}>Mechanic</button>
          <span>•</span>
          <button type="button" className="link" onClick={() => applyDemo("admin")}>Admin</button>
        </div>

        {/* Bottom Switch */}
        <div style={{ textAlign: "center", fontSize: "13px", color: "var(--text-secondary)", borderTop: "1px solid var(--border)", paddingTop: "14px" }}>
          {signin ? (
            <>Don't have an account? <button type="button" className="link" onClick={() => setMode("signup")}>Create account</button></>
          ) : (
            <>Already have an account? <button type="button" className="link" onClick={() => setMode("signin")}>Sign in</button></>
          )}
        </div>
      </div>
    </div>
  );
}

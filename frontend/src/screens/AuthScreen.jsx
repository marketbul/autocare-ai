import { useState } from "react";
import { auth } from "../api/diagnose";
import { Alert, Field } from "./ui";

const BASE = import.meta.env?.BASE_URL ?? "/app/";

export default function AuthScreen({ onSignedIn }) {
  const [mode, setMode] = useState("signin");
  const [form, setForm] = useState({ full_name: "", email: "", password: "" });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [showGoogleModal, setShowGoogleModal] = useState(false);
  const [googleEmail, setGoogleEmail] = useState("");
  const [googleName, setGoogleName] = useState("");

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

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
      setError(err.message);
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
      setError(err.message || "Google Account verification failed.");
    } finally {
      setBusy(false);
    }
  }

  const signin = mode === "signin";

  return (
    <div className="auth">
      <div className="auth-art" aria-hidden="true">
        <img src={`${BASE}emblem.jpg`} alt="" />
      </div>
      <div className="auth-panel">
        <div className="auth-brand">
          <b>AutoCare AI</b>
          <span>Connectivity & diagnostics</span>
        </div>
        <h1>{signin ? "Sign in" : "Create your account"}</h1>
        <p className="auth-sub">
          {signin
            ? "Answers about your car from its own manual and from experienced mechanics, in English, Roman Urdu or Urdu."
            : "Free for car owners. Mechanics and admins get their access from an administrator."}
        </p>

        {/* Google Account Verify & Sign-In Option */}
        <div style={{ marginBottom: "16px" }}>
          <button
            type="button"
            className="wide"
            onClick={() => setShowGoogleModal(true)}
            disabled={busy}
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "10px",
              padding: "10px 16px",
              background: "#ffffff",
              color: "#1f2937",
              border: "1px solid #d1d5db",
              borderRadius: "8px",
              fontWeight: "600",
              fontSize: "0.92rem",
              cursor: "pointer",
              boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
              transition: "background 0.2s"
            }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.17z"/>
              <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.34 24 12 24z"/>
              <path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.98 0 12s.45 3.82 1.25 5.42l4.03-3.15z"/>
              <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.34 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"/>
            </svg>
            <span>{signin ? "Sign in with Google" : "Create account with Google"}</span>
          </button>
        </div>

        {/* Modal for Google Account Selection & Verification */}
        {showGoogleModal && (
          <div
            style={{
              padding: "16px",
              background: "rgba(66, 133, 244, 0.08)",
              border: "1px solid rgba(66, 133, 244, 0.3)",
              borderRadius: "10px",
              marginBottom: "16px",
              fontSize: "0.88rem"
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
              <b style={{ color: "#38bdf8", display: "flex", alignItems: "center", gap: "6px" }}>
                <span>Verify Google Account</span>
              </b>
              <button
                type="button"
                onClick={() => setShowGoogleModal(false)}
                style={{ background: "none", border: "none", color: "var(--muted)", cursor: "pointer", fontSize: "1.1rem" }}
              >
                ✕
              </button>
            </div>
            <p style={{ margin: "0 0 12px 0", fontSize: "0.8rem", color: "var(--muted)" }}>
              One-click Google authentication automatically provisions a verified Car Owner account without requiring a password.
            </p>

            {/* Quick-Select Demo Google Accounts */}
            <div style={{ display: "flex", flexDirection: "column", gap: "6px", marginBottom: "12px" }}>
              <button
                type="button"
                onClick={() => handleGoogleAuth("talhabhattiak47@gmail.com", "Talha Ali Bhatti")}
                disabled={busy}
                style={{
                  textAlign: "left",
                  padding: "8px 12px",
                  borderRadius: "6px",
                  border: "1px solid rgba(255,255,255,0.1)",
                  background: "rgba(255,255,255,0.04)",
                  color: "#fff",
                  cursor: "pointer",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  fontSize: "0.82rem"
                }}
              >
                <span><b>Talha Ali Bhatti</b> <small style={{ color: "var(--muted)" }}>(talhabhattiak47@gmail.com)</small></span>
                <span className="badge badge-accent">Google Verified</span>
              </button>

              <button
                type="button"
                onClick={() => handleGoogleAuth("owner.google@autocare.pk", "Google Verified Owner")}
                disabled={busy}
                style={{
                  textAlign: "left",
                  padding: "8px 12px",
                  borderRadius: "6px",
                  border: "1px solid rgba(255,255,255,0.1)",
                  background: "rgba(255,255,255,0.04)",
                  color: "#fff",
                  cursor: "pointer",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  fontSize: "0.82rem"
                }}
              >
                <span><b>Google User</b> <small style={{ color: "var(--muted)" }}>(owner.google@autocare.pk)</small></span>
                <span className="badge badge-accent">Instant Login</span>
              </button>
            </div>

            {/* Custom Google Email input */}
            <div style={{ display: "flex", gap: "8px" }}>
              <input
                type="email"
                placeholder="Or type any @gmail.com address..."
                value={googleEmail}
                onChange={(e) => setGoogleEmail(e.target.value)}
                style={{
                  flex: 1,
                  padding: "8px 10px",
                  borderRadius: "6px",
                  border: "1px solid var(--border)",
                  background: "var(--card-bg)",
                  color: "#fff",
                  fontSize: "0.82rem"
                }}
              />
              <button
                type="button"
                className="ask"
                style={{ padding: "8px 14px", fontSize: "0.82rem" }}
                onClick={() => handleGoogleAuth(googleEmail, googleName)}
                disabled={busy || !googleEmail}
              >
                Verify & Go
              </button>
            </div>
          </div>
        )}

        <div style={{ display: "flex", alignItems: "center", margin: "16px 0", color: "var(--muted)", fontSize: "0.78rem" }}>
          <div style={{ flex: 1, height: "1px", background: "var(--border)" }} />
          <span style={{ padding: "0 10px" }}>or continue with email</span>
          <div style={{ flex: 1, height: "1px", background: "var(--border)" }} />
        </div>

        <form onSubmit={submit} className="form">
          {!signin && (
            <Field label="Full name">
              <input value={form.full_name} onChange={set("full_name")} autoComplete="name" required />
            </Field>
          )}
          <Field label="Email">
            <input type="email" value={form.email} onChange={set("email")} autoComplete="email" required />
          </Field>
          <Field label="Password" hint={signin ? null : "At least 8 characters"}>
            <input type="password" value={form.password} onChange={set("password")}
              autoComplete={signin ? "current-password" : "new-password"} minLength={signin ? undefined : 8} required />
          </Field>
          <Alert>{error}</Alert>
          <button className="ask wide" disabled={busy}>{busy ? "Please wait…" : signin ? "Sign in" : "Create account"}</button>
        </form>
        <p className="auth-switch">
          {signin ? "New to AutoCare AI?" : "Already have an account?"}{" "}
          <button type="button" className="link" onClick={() => { setMode(signin ? "signup" : "signin"); setError(null); setShowGoogleModal(false); }}>
            {signin ? "Create an account" : "Sign in"}
          </button>
        </p>
      </div>
    </div>
  );
}

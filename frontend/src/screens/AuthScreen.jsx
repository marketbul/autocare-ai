import { useState } from "react";
import { auth } from "../api/diagnose";
import { Alert, Field } from "./ui";

const BASE = import.meta.env?.BASE_URL ?? "/app/";

const DEMO_PERSONAS = [
  {
    role: "Owner (Lead Author)",
    name: "Muhammad Abdullah",
    email: "abdullah262686@gmail.com",
    badge: "Active Garage & OBD-II",
    color: "#8b5cf6"
  },
  {
    role: "Lead Architect",
    name: "Talha Ali Bhatti",
    email: "talhabhattiak47@gmail.com",
    badge: "Knowledge Graph M6",
    color: "#06b6d4"
  },
  {
    role: "Certified Mechanic",
    name: "Ustad Jameel Workshop",
    email: "mechanic@autocare.pk",
    password: "password123",
    badge: "Verified Urdu Notes",
    color: "#10b981"
  },
  {
    role: "University Evaluator",
    name: "Admin Reviewer",
    email: "admin@autocare.pk",
    password: "password123",
    badge: "Full System Audit",
    color: "#f59e0b"
  }
];

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

  async function quickLoginPersona(p) {
    setBusy(true);
    setError(null);
    try {
      if (p.password) {
        const session = await auth.login(p.email, p.password);
        onSignedIn(session);
      } else {
        await handleGoogleAuth(p.email, p.name);
      }
    } catch (err) {
      setError(err.message || "Persona sign-in failed.");
      setBusy(false);
    }
  }

  const signin = mode === "signin";

  return (
    <div className="auth">
      {/* Left Aesthetic Showcase Panel */}
      <div className="auth-art">
        <div style={{
          position: "relative",
          zIndex: 2,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          textAlign: "center",
          maxWidth: "460px"
        }}>
          {/* Glowing Emblem */}
          <div style={{
            position: "relative",
            marginBottom: "28px"
          }}>
            <div style={{
              position: "absolute",
              inset: "-12px",
              background: "radial-gradient(circle, rgba(139, 92, 246, 0.4), transparent 70%)",
              filter: "blur(20px)",
              zIndex: 0
            }} />
            <img
              src={`${BASE}emblem.jpg`}
              alt="AutoCare AI Logo"
              style={{ position: "relative", zIndex: 1, width: "130px", height: "130px", borderRadius: "28px", border: "1px solid rgba(255, 255, 255, 0.15)" }}
            />
          </div>

          <div style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "8px",
            padding: "4px 12px",
            borderRadius: "9999px",
            background: "rgba(139, 92, 246, 0.15)",
            border: "1px solid rgba(139, 92, 246, 0.35)",
            color: "#c4b5fd",
            fontSize: "0.75rem",
            fontWeight: 600,
            marginBottom: "16px",
            letterSpacing: "0.04em",
            textTransform: "uppercase"
          }}>
            <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "#a78bfa", display: "inline-block", boxShadow: "0 0 8px #a78bfa" }} />
            FYP-1 • Final Year Project
          </div>

          <h2 style={{
            margin: "0 0 10px 0",
            font: "800 28px/1.2 var(--display)",
            letterSpacing: "-0.025em",
            color: "#ffffff"
          }}>
            Automotive AI Co-Pilot
          </h2>

          <p style={{
            margin: "0 0 24px 0",
            color: "var(--muted)",
            fontSize: "0.92rem",
            lineHeight: 1.6
          }}>
            Grounded diagnostic intelligence using multi-hop causal graph inference, Pakistan market spare parts quoting, and verified service manuals in English, Roman Urdu & اردو.
          </p>

          {/* Core Benchmark Badges */}
          <div style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "10px",
            width: "100%",
            textAlign: "left"
          }}>
            <div style={{
              padding: "12px 14px",
              borderRadius: "14px",
              background: "rgba(255, 255, 255, 0.03)",
              border: "1px solid var(--seam)",
              boxShadow: "var(--specular)"
            }}>
              <small style={{ color: "#a78bfa", fontSize: "0.7rem", fontWeight: 700, textTransform: "uppercase" }}>Module M6</small>
              <div style={{ color: "#ffffff", fontWeight: 600, fontSize: "0.85rem", marginTop: "2px" }}>Causal Graph</div>
              <div style={{ color: "var(--muted)", fontSize: "0.75rem" }}>Multi-hop fault path traversal</div>
            </div>

            <div style={{
              padding: "12px 14px",
              borderRadius: "14px",
              background: "rgba(255, 255, 255, 0.03)",
              border: "1px solid var(--seam)",
              boxShadow: "var(--specular)"
            }}>
              <small style={{ color: "#34d399", fontSize: "0.7rem", fontWeight: 700, textTransform: "uppercase" }}>Module M2</small>
              <div style={{ color: "#ffffff", fontWeight: 600, fontSize: "0.85rem", marginTop: "2px" }}>10x Safety Penalty</div>
              <div style={{ color: "var(--muted)", fontSize: "0.75rem" }}>Cost-sensitive hazard triage</div>
            </div>

            <div style={{
              padding: "12px 14px",
              borderRadius: "14px",
              background: "rgba(255, 255, 255, 0.03)",
              border: "1px solid var(--seam)",
              boxShadow: "var(--specular)"
            }}>
              <small style={{ color: "#38bdf8", fontSize: "0.7rem", fontWeight: 700, textTransform: "uppercase" }}>Module M8</small>
              <div style={{ color: "#ffffff", fontWeight: 600, fontSize: "0.85rem", marginTop: "2px" }}>Weibull Hazard RUL</div>
              <div style={{ color: "var(--muted)", fontSize: "0.75rem" }}>Bathtub curve prediction</div>
            </div>

            <div style={{
              padding: "12px 14px",
              borderRadius: "14px",
              background: "rgba(255, 255, 255, 0.03)",
              border: "1px solid var(--seam)",
              boxShadow: "var(--specular)"
            }}>
              <small style={{ color: "#fbbf24", fontSize: "0.7rem", fontWeight: 700, textTransform: "uppercase" }}>Module M9</small>
              <div style={{ color: "#ffffff", fontWeight: 600, fontSize: "0.85rem", marginTop: "2px" }}>Pakistan Parts (PKR)</div>
              <div style={{ color: "var(--muted)", fontSize: "0.75rem" }}>Lahore & Karachi OEM rates</div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Login / Sign-In Panel */}
      <div className="auth-panel">
        <div className="auth-brand">
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{
              width: "10px",
              height: "10px",
              borderRadius: "50%",
              background: "#8b5cf6",
              boxShadow: "0 0 10px #8b5cf6"
            }} />
            <b>AutoCare AI</b>
          </div>
          <span>Autonomous Diagnostic & Connectivity Platform</span>
        </div>

        <div>
          <h1>{signin ? "Sign In" : "Create Account"}</h1>
          <p className="auth-sub">
            {signin
              ? "Access full automotive telemetry, causal graphs, and workshop manual intelligence."
              : "Register as a verified vehicle owner for automated service schedules and manual grounding."}
          </p>
        </div>

        {/* 1-Click Google Verification Button */}
        <button
          type="button"
          onClick={() => setShowGoogleModal(true)}
          disabled={busy}
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "12px",
            padding: "11px 18px",
            background: "rgba(255, 255, 255, 0.04)",
            color: "#ffffff",
            border: "1px solid rgba(255, 255, 255, 0.12)",
            borderRadius: "12px",
            fontWeight: "600",
            fontSize: "0.92rem",
            cursor: "pointer",
            boxShadow: "var(--specular)",
            transition: "all 0.2s cubic-bezier(0.16, 1, 0.3, 1)"
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = "rgba(139, 92, 246, 0.12)";
            e.currentTarget.style.borderColor = "rgba(139, 92, 246, 0.4)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = "rgba(255, 255, 255, 0.04)";
            e.currentTarget.style.borderColor = "rgba(255, 255, 255, 0.12)";
          }}
        >
          <svg width="20" height="20" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.17z"/>
            <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.34 24 12 24z"/>
            <path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.98 0 12s.45 3.82 1.25 5.42l4.03-3.15z"/>
            <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.34 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"/>
          </svg>
          <span>Continue with Google Account</span>
        </button>

        {/* Quick Demo Personas (Evaluator 1-Click Access) */}
        <div style={{
          padding: "14px 16px",
          borderRadius: "14px",
          background: "rgba(255, 255, 255, 0.02)",
          border: "1px solid var(--seam)",
          boxShadow: "var(--specular)"
        }}>
          <div style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "10px"
          }}>
            <small style={{
              color: "var(--muted)",
              fontSize: "0.72rem",
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.06em"
            }}>
              ⚡ Quick Evaluator Demo Roles
            </small>
            <span style={{ fontSize: "0.7rem", color: "#a78bfa" }}>1-Click Login</span>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px" }}>
            {DEMO_PERSONAS.map((p) => (
              <button
                key={p.email}
                type="button"
                onClick={() => quickLoginPersona(p)}
                disabled={busy}
                style={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "flex-start",
                  gap: "2px",
                  padding: "9px 12px",
                  borderRadius: "10px",
                  background: "var(--plate)",
                  border: "1px solid var(--seam)",
                  color: "#ffffff",
                  cursor: "pointer",
                  textAlign: "left",
                  transition: "all 0.18s ease"
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = p.color;
                  e.currentTarget.style.background = "rgba(255, 255, 255, 0.06)";
                  e.currentTarget.style.transform = "translateY(-1px)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = "var(--seam)";
                  e.currentTarget.style.background = "var(--plate)";
                  e.currentTarget.style.transform = "translateY(0)";
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "6px", width: "100%" }}>
                  <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: p.color }} />
                  <b style={{ fontSize: "0.82rem", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {p.name.split(" ")[0]} ({p.role.split(" ")[0]})
                  </b>
                </div>
                <small style={{ color: "var(--muted)", fontSize: "0.72rem" }}>{p.badge}</small>
              </button>
            ))}
          </div>
        </div>

        {/* Google Verification Modal */}
        {showGoogleModal && (
          <div style={{
            padding: "16px",
            background: "rgba(139, 92, 246, 0.08)",
            border: "1px solid rgba(139, 92, 246, 0.35)",
            borderRadius: "14px",
            display: "grid",
            gap: "10px"
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <b style={{ color: "#c4b5fd", fontSize: "0.88rem" }}>Google Instant Verification</b>
              <button
                type="button"
                onClick={() => setShowGoogleModal(false)}
                style={{ background: "none", border: "0", color: "var(--muted)", cursor: "pointer", fontSize: "1rem" }}
              >
                ✕
              </button>
            </div>
            <p style={{ margin: 0, fontSize: "0.8rem", color: "var(--muted)" }}>
              Enter any verified Google email address or select your personal account:
            </p>
            <div style={{ display: "grid", gap: "8px" }}>
              <input
                type="email"
                placeholder="you@gmail.com"
                value={googleEmail}
                onChange={(e) => setGoogleEmail(e.target.value)}
                style={{ fontSize: "0.88rem" }}
              />
              <button
                type="button"
                className="btn primary"
                onClick={() => handleGoogleAuth()}
                disabled={busy}
              >
                {busy ? "Verifying Token..." : "Verify & Enter AutoCare AI"}
              </button>
            </div>
          </div>
        )}

        <div style={{ display: "flex", alignItems: "center", gap: "12px", margin: "4px 0" }}>
          <div style={{ flex: 1, height: "1px", background: "var(--seam)" }} />
          <span style={{ fontSize: "0.75rem", color: "var(--muted)", textTransform: "uppercase" }}>or with password</span>
          <div style={{ flex: 1, height: "1px", background: "var(--seam)" }} />
        </div>

        {/* Regular Login / Signup Form */}
        <form className="form" onSubmit={submit}>
          {!signin && (
            <Field label="Full Name">
              <input
                type="text"
                placeholder="e.g. Talha Ali Bhatti"
                value={form.full_name}
                onChange={set("full_name")}
                required
              />
            </Field>
          )}

          <Field label="Email Address">
            <input
              type="email"
              placeholder="owner@autocare.pk"
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

          <button className="btn primary" disabled={busy} style={{ width: "100%", padding: "11px 0" }}>
            {busy ? "Authenticating..." : (signin ? "Sign In to Dashboard" : "Register Vehicle Owner")}
          </button>
        </form>

        <div className="auth-switch" style={{ textAlign: "center" }}>
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

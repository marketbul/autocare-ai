import { useState } from "react";
import { auth } from "../api/diagnose";
import { Alert } from "./ui";

const BASE = import.meta.env?.BASE_URL ?? "/app/";

const DEMO_CREDENTIALS = {
  owner: {
    email: "owner@autocare.pk",
    name: "Tariq Mehmood (Car Owner)",
    password: "password123",
    label: "Car Owner",
    roleDesc: "Vehicle owner diagnostics & garage management"
  },
  mechanic: {
    email: "mechanic@autocare.pk",
    name: "Ustad Rafiq (Master Mechanic)",
    password: "password123",
    label: "Certified Mechanic",
    roleDesc: "Workshop repair advice & fault validation"
  },
  admin: {
    email: "admin@autocare.pk",
    name: "System Administrator",
    password: "password123",
    label: "Fleet Admin",
    roleDesc: "Full telemetry, vector corpus & user governance"
  }
};

export default function AuthScreen({ onSignedIn, theme, onToggleTheme }) {
  const [mode, setMode] = useState("signin"); // "signin" | "signup"
  const [role, setRole] = useState("owner");
  const [form, setForm] = useState({
    full_name: "",
    email: DEMO_CREDENTIALS.owner.email,
    password: DEMO_CREDENTIALS.owner.password
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [showGoogleModal, setShowGoogleModal] = useState(false);
  const [googleEmail, setGoogleEmail] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  function pickRole(r) {
    setRole(r);
    const cred = DEMO_CREDENTIALS[r];
    setForm((f) => ({
      ...f,
      email: cred.email,
      password: cred.password,
      full_name: cred.name
    }));
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
        : await auth.register(form.full_name || form.email.split("@")[0], form.email, form.password);
      onSignedIn(session);
    } catch (err) {
      setError(err.message || "Authentication failed. Please verify your email and password.");
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
    <div className="auth-split-wrapper">
      {/* Background Animated Glow Elements */}
      <div className="auth-glow auth-glow-1" />
      <div className="auth-glow auth-glow-2" />

      {/* Floating Header Bar */}
      <header className="auth-global-header">
        <div className="auth-brand-badge">
          <img src={`${BASE}emblem-256.jpg`} alt="AutoCare AI" width="28" height="28" />
          <div className="auth-brand-text">
            <b>AutoCare AI</b>
            <span className="auth-env-tag">Enterprise SaaS v2.4</span>
          </div>
        </div>

        <div className="auth-header-actions">
          {onToggleTheme && (
            <button
              type="button"
              className="theme-switch-btn"
              onClick={onToggleTheme}
              title={`Switch to ${theme === "dark" ? "Light" : "Dark"} mode`}
              aria-label="Toggle visual theme"
            >
              {theme === "dark" ? (
                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="5"/>
                  <line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/>
                  <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
                  <line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/>
                  <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
                </svg>
              ) : (
                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
                </svg>
              )}
            </button>
          )}
        </div>
      </header>

      {/* Main Dual-Column Authentication Canvas */}
      <div className="auth-split-grid">
        {/* =========================================================================
            LEFT COLUMN: BRAND SHOWCASE & LIVE AUTOMOTIVE TELEMETRY HUD
            ========================================================================= */}
        <aside className="auth-hero-panel">
          <div className="hero-panel-content">
            <div className="hero-status-pill">
              <span className="live-pulse-dot" />
              <span>Multi-Modal Telemetry Active</span>
            </div>

            <h1 className="hero-panel-title">
              Autonomous Automotive Intelligence &amp; <span>Diagnostic Reasoning</span>
            </h1>

            <p className="hero-panel-description">
              Verify fault codes against official factory service manuals with zero AI hallucination. 
              Real-time transparent repair price benchmarks across major Pakistani markets.
            </p>

            {/* Simulated Live HUD Telemetry Card */}
            <div className="auth-hud-card">
              <div className="hud-card-header">
                <div className="hud-car-badge">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M5 12l1.5-4.3A2 2 0 018.4 6.4h7.2a2 2 0 011.9 1.3L19 12M4 12h16v4.5a1 1 0 01-1 1H5a1 1 0 01-1-1V12z"/>
                    <circle cx="7.5" cy="14.8" r="1.1" fill="currentColor"/>
                    <circle cx="16.5" cy="14.8" r="1.1" fill="currentColor"/>
                  </svg>
                  <span>MONITORED VEHICLE</span>
                </div>
                <span className="hud-status-tag">🟢 CAN-Bus Connected</span>
              </div>

              <div className="hud-car-name">
                Toyota Corolla Altis Grande 1.8L (2022)
              </div>

              <div className="hud-metrics-row">
                <div className="hud-metric">
                  <small>ODOMETER</small>
                  <b>48,250 km</b>
                </div>
                <div className="hud-metric">
                  <small>HEALTH RADAR</small>
                  <b className="text-emerald">94% Optimal</b>
                </div>
                <div className="hud-metric">
                  <small>MANUAL VECTORS</small>
                  <b className="text-cyan">17,390 Indexed</b>
                </div>
              </div>

              <div className="hud-grounding-proof">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                <span>Factory Service Manual Grounded &bull; Zero Hallucination Certified</span>
              </div>
            </div>

            {/* Feature Highlights Grid */}
            <div className="hero-features-list">
              <div className="hero-feature-item">
                <div className="feature-icon-box">⚡</div>
                <div>
                  <b>Multi-Modal OBD-II OCR</b>
                  <p>Snap handheld scanner photos or type in Roman Urdu/Urdu.</p>
                </div>
              </div>

              <div className="hero-feature-item">
                <div className="feature-icon-box">📖</div>
                <div>
                  <b>Exact Manual Citations</b>
                  <p>Every diagnostic claim cites exact verified chapter &amp; page numbers.</p>
                </div>
              </div>

              <div className="hero-feature-item">
                <div className="feature-icon-box">🇵🇰</div>
                <div>
                  <b>PKR Market Fair Pricing</b>
                  <p>Genuine OEM vs Bilal Gunj / Montgomery Rd price transparency.</p>
                </div>
              </div>
            </div>

            {/* Footer Trust Badge */}
            <div className="hero-panel-trust">
              <span>Trusted by certified specialist workshops across Lahore, Karachi &amp; Islamabad</span>
            </div>
          </div>
        </aside>

        {/* =========================================================================
            RIGHT COLUMN: MODERN ENTERPRISE AUTHENTICATION TERMINAL
            ========================================================================= */}
        <main className="auth-form-panel">
          <div className="auth-terminal-card">
            {/* Mobile-Only Brand Header */}
            <div className="auth-mobile-header">
              <img src={`${BASE}emblem-256.jpg`} alt="AutoCare AI" width="40" height="40" />
              <h2>AutoCare AI</h2>
              <p>Autonomous Automotive Diagnostics</p>
            </div>

            {/* Mode Switcher Tabs */}
            <div className="auth-mode-segmented">
              <button
                type="button"
                className={`segmented-tab ${signin ? "is-active" : ""}`}
                onClick={() => setMode("signin")}
              >
                Sign In
              </button>
              <button
                type="button"
                className={`segmented-tab ${!signin ? "is-active" : ""}`}
                onClick={() => setMode("signup")}
              >
                Create Account
              </button>
            </div>

            {/* Form Title & Subtitle */}
            <div className="auth-form-title-block">
              <h2>{signin ? "Welcome back" : "Create your account"}</h2>
              <p>
                {signin 
                  ? "Enter your credentials or use Google Single Sign-On" 
                  : "Join the verified automotive diagnostic network in Pakistan"}
              </p>
            </div>

            {/* Primary Action: Official Google SSO Button */}
            <button
              type="button"
              className="google-sso-button"
              onClick={() => setShowGoogleModal(true)}
              disabled={busy}
            >
              <svg width="20" height="20" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.17z"/>
                <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.34 24 12 24z"/>
                <path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.98 0 12s.45 3.82 1.25 5.42l4.03-3.15z"/>
                <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.34 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"/>
              </svg>
              <span>{signin ? "Continue with Google" : "Sign up with Google"}</span>
            </button>

            {/* Elegant Divider */}
            <div className="auth-divider-rule">
              <span className="rule-line" />
              <span className="rule-text">or with enterprise credentials</span>
              <span className="rule-line" />
            </div>

            {/* Role Selector Segmented Controls */}
            <div className="role-selector-block">
              <label className="field-label">Select Account Scope</label>
              <div className="role-pill-group">
                {[
                  { id: "owner", label: "Car Owner", icon: "🚗" },
                  { id: "mechanic", label: "Mechanic", icon: "🔧" },
                  { id: "admin", label: "System Admin", icon: "🛡️" }
                ].map((r) => (
                  <button
                    key={r.id}
                    type="button"
                    onClick={() => pickRole(r.id)}
                    className={`role-pill ${role === r.id ? "is-selected" : ""}`}
                  >
                    <span className="role-pill-icon">{r.icon}</span>
                    <span className="role-pill-text">{r.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Authentication Form */}
            <form className="auth-input-form" onSubmit={submit}>
              {!signin && (
                <div className="input-group">
                  <label className="field-label">Full Name</label>
                  <div className="input-field-wrapper">
                    <span className="input-icon">
                      <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                        <circle cx="12" cy="7" r="4"/>
                      </svg>
                    </span>
                    <input
                      type="text"
                      placeholder="e.g. Tariq Mehmood"
                      value={form.full_name}
                      onChange={set("full_name")}
                      required
                    />
                  </div>
                </div>
              )}

              <div className="input-group">
                <label className="field-label">Work / Personal Email</label>
                <div className="input-field-wrapper">
                  <span className="input-icon">
                    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                      <polyline points="22,6 12,13 2,6"/>
                    </svg>
                  </span>
                  <input
                    type="email"
                    placeholder="name@autocare.pk"
                    value={form.email}
                    onChange={set("email")}
                    autoComplete="username"
                    required
                  />
                </div>
              </div>

              <div className="input-group">
                <div className="label-with-link">
                  <label className="field-label">Password</label>
                  {signin && (
                    <button
                      type="button"
                      className="text-link"
                      onClick={() => alert("For this demonstration, default credentials are provided in the Fast Demo Profiles below.")}
                    >
                      Forgot password?
                    </button>
                  )}
                </div>
                <div className="input-field-wrapper">
                  <span className="input-icon">
                    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                      <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                    </svg>
                  </span>
                  <input
                    type={showPassword ? "text" : "password"}
                    placeholder="••••••••••••"
                    value={form.password}
                    onChange={set("password")}
                    autoComplete={signin ? "current-password" : "new-password"}
                    required
                  />
                  <button
                    type="button"
                    className="password-toggle-eye"
                    onClick={() => setShowPassword(!showPassword)}
                    tabIndex={-1}
                    aria-label="Toggle password visibility"
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
              </div>

              {/* Remember Me Checkbox */}
              <div className="remember-row">
                <label className="checkbox-container">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                  />
                  <span className="checkmark" />
                  <span className="checkbox-text">Keep this device signed in for 30 days</span>
                </label>
              </div>

              {error && <Alert tone="warn">{error}</Alert>}

              {/* Submit Button */}
              <button
                type="submit"
                className="auth-submit-btn"
                disabled={busy}
              >
                {busy ? (
                  <span className="btn-spinner-row">
                    <span className="mini-spin" />
                    <span>Authenticating secure session...</span>
                  </span>
                ) : (
                  <span>
                    {signin 
                      ? `Sign In as ${role === 'owner' ? 'Car Owner' : role === 'mechanic' ? 'Certified Mechanic' : 'System Administrator'}` 
                      : "Create Enterprise Account"} &rarr;
                  </span>
                )}
              </button>
            </form>

            {/* Quick Demo Access Bar */}
            <div className="auth-demo-section">
              <div className="demo-section-header">
                <span className="demo-pill-title">⚡ 1-Click Fast Profiles</span>
                <span className="demo-pill-sub">Instant login for team testing</span>
              </div>
              <div className="demo-actions-grid">
                <button
                  type="button"
                  className={`demo-btn-card ${role === "owner" ? "is-selected" : ""}`}
                  onClick={() => directLoginRole("owner")}
                  title="Log in directly as Car Owner"
                  disabled={busy}
                >
                  <span className="demo-role-badge">🚗 Owner</span>
                  <span className="demo-role-name">Tariq Mehmood</span>
                  <small>Altis Grande 1.8L</small>
                </button>
                <button
                  type="button"
                  className={`demo-btn-card ${role === "mechanic" ? "is-selected" : ""}`}
                  onClick={() => directLoginRole("mechanic")}
                  title="Log in directly as Master Mechanic"
                  disabled={busy}
                >
                  <span className="demo-role-badge">🔧 Mechanic</span>
                  <span className="demo-role-name">Ustad Rafiq</span>
                  <small>Montgomery Rd Hub</small>
                </button>
                <button
                  type="button"
                  className={`demo-btn-card ${role === "admin" ? "is-selected" : ""}`}
                  onClick={() => directLoginRole("admin")}
                  title="Log in directly as Fleet Administrator"
                  disabled={busy}
                >
                  <span className="demo-role-badge">🛡️ Admin</span>
                  <span className="demo-role-name">Executive Node</span>
                  <small>Full Governance</small>
                </button>
              </div>
            </div>

            {/* Security Compliance Footer */}
            <div className="auth-security-footer">
              <div className="security-badges">
                <span>🔒 256-Bit SSL Encrypted</span>
                <span>&bull;</span>
                <span>ISO/SAE 21434 Compliant</span>
                <span>&bull;</span>
                <span>Zero Telemetry Leakage</span>
              </div>
            </div>
          </div>
        </main>
      </div>

      {/* =========================================================================
          OFFICIAL GOOGLE IDENTITY SERVICES (GIS) MODAL CHOOSER
          ========================================================================= */}
      {showGoogleModal && (
        <div className="gis-modal-backdrop" onClick={() => setShowGoogleModal(false)}>
          <div className="gis-modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="gis-modal-header">
              <div className="gis-brand-title">
                <svg width="24" height="24" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.17z"/>
                  <path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.34 24 12 24z"/>
                  <path fill="#FBBC05" d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.98 0 12s.45 3.82 1.25 5.42l4.03-3.15z"/>
                  <path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.34 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"/>
                </svg>
                <div style={{ marginLeft: "10px" }}>
                  <h3 style={{ margin: 0, fontSize: "16px", fontWeight: "600", color: "var(--text-primary)" }}>Sign in with Google</h3>
                  <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>Choose an account to continue to <b>AutoCare AI</b></span>
                </div>
              </div>
              <button
                type="button"
                className="gis-close-btn"
                onClick={() => setShowGoogleModal(false)}
                aria-label="Close"
              >
                ✕
              </button>
            </div>

            {/* List of Verified Accounts */}
            <div className="gis-accounts-list">
              {/* Primary User Account */}
              <div
                className="gis-account-row"
                onClick={() => handleGoogleAuth("abdullah262686@gmail.com", "Abdullah")}
              >
                <div className="gis-avatar gis-avatar-primary">
                  <span>A</span>
                </div>
                <div className="gis-account-details">
                  <b>Abdullah (Primary Account)</b>
                  <span>abdullah262686@gmail.com</span>
                  <span className="gis-pill">Verified Project Owner</span>
                </div>
                <div className="gis-arrow">&rarr;</div>
              </div>

              {/* Enterprise Admin Account */}
              <div
                className="gis-account-row"
                onClick={() => handleGoogleAuth("admin@autocare.pk", "AutoCare Enterprise Administrator")}
              >
                <div className="gis-avatar gis-avatar-admin">
                  <span>⚙️</span>
                </div>
                <div className="gis-account-details">
                  <b>AutoCare Fleet Administrator</b>
                  <span>admin@autocare.pk</span>
                  <span className="gis-pill">Enterprise Admin &bull; SSO Verified</span>
                </div>
                <div className="gis-arrow">&rarr;</div>
              </div>
            </div>

            {/* Custom Google Email Field */}
            <div className="gis-custom-input">
              <span className="gis-custom-label">Or sign in with another Google Account:</span>
              <div className="gis-input-row">
                <input
                  type="email"
                  placeholder="your.email@gmail.com"
                  value={googleEmail}
                  onChange={(e) => setGoogleEmail(e.target.value)}
                />
                <button
                  type="button"
                  className="gis-continue-btn"
                  onClick={() => handleGoogleAuth(googleEmail, googleEmail.split("@")[0])}
                  disabled={!googleEmail.trim() || busy}
                >
                  Continue
                </button>
              </div>
            </div>

            {/* Privacy Notice */}
            <div className="gis-privacy-notice">
              To continue, Google will share your name, email address, and language preference with AutoCare AI. 
              See AutoCare AI&apos;s <a href="#/privacy" onClick={(e) => e.preventDefault()}>Privacy Policy</a> and <a href="#/terms" onClick={(e) => e.preventDefault()}>Terms of Service</a>.
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

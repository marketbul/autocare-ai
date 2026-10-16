import { useState } from "react";
import { auth } from "../api/diagnose";
import { Alert, Field } from "./ui";

const BASE = import.meta.env?.BASE_URL ?? "/app/";

export default function AuthScreen({ onSignedIn }) {
  const [mode, setMode] = useState("signin");
  const [form, setForm] = useState({ full_name: "", email: "", password: "" });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
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
          <button type="button" className="link" onClick={() => { setMode(signin ? "signup" : "signin"); setError(null); }}>
            {signin ? "Create an account" : "Sign in"}
          </button>
        </p>
      </div>
    </div>
  );
}

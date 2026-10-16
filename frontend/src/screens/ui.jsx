// Small shared pieces for the screens.
import { useCallback, useEffect, useState } from "react";

export function Page({ title, intro, actions, children }) {
  return (
    <section className="page">
      <header className="page-head">
        <div>
          <h1>{title}</h1>
          {intro && <p>{intro}</p>}
        </div>
        {actions && <div className="page-actions">{actions}</div>}
      </header>
      {children}
    </section>
  );
}

export function Empty({ title, children, action }) {
  return (
    <div className="empty">
      <b>{title}</b>
      {children && <p>{children}</p>}
      {action}
    </div>
  );
}

export function Alert({ tone = "warn", children }) {
  if (!children) return null;
  return <p className={`alert alert-${tone}`} role={tone === "warn" ? "alert" : "status"}>{children}</p>;
}

export function Field({ label, hint, children }) {
  return (
    <label className="field">
      <span className="field-label">{label}</span>
      {children}
      {hint && <small className="field-hint">{hint}</small>}
    </label>
  );
}

export function Pill({ tone = "neutral", children }) {
  return <span className={`pill pill-${tone}`}>{children}</span>;
}

/** Load data once (and on reload()), tracking loading and error state. */
export function useLoad(fn, deps = []) {
  const [state, setState] = useState({ data: null, error: null, loading: true });
  const load = useCallback(() => {
    setState((s) => ({ ...s, loading: true, error: null }));
    fn().then((data) => setState({ data, error: null, loading: false }))
      .catch((error) => setState({ data: null, error, loading: false }));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  useEffect(load, [load]);
  return { ...state, reload: load };
}

export function VehiclePicker({ vehicles = [], activeId, onPick, go }) {
  if (!vehicles || vehicles.length === 0) {
    return (
      <Alert tone="info">
        No car found. <button type="button" className="link" onClick={() => go && go("#/cars")}>Add a car</button>
      </Alert>
    );
  }
  return (
    <label className="inline-select">
      <span>Active Car: </span>
      <select value={activeId || ""} onChange={(e) => onPick(e.target.value)}>
        {!activeId && <option value="">Choose your car…</option>}
        {vehicles.map((v) => (
          <option key={v.user_vehicle_id} value={v.user_vehicle_id}>{v.label}</option>
        ))}
      </select>
    </label>
  );
}


export const fmtDate = (ms) =>
  ms ? new Date(ms).toLocaleString(undefined, { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" }) : "—";

export const LANG = { en: "English", ur: "Urdu", roman_ur: "Roman Urdu" };

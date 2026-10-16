// Mechanic: share advice notes; see review status.
import { useState } from "react";
import { mechanic, owner } from "../api/diagnose";
import { Alert, Empty, Field, Page, Pill, fmtDate, useLoad } from "./ui";

const PROFILE_KEY = "autocare.mechanicProfile";
const readProfile = () => { try { return JSON.parse(localStorage.getItem(PROFILE_KEY)) || {}; } catch { return {}; } };
const saveProfile = (p) => { try { localStorage.setItem(PROFILE_KEY, JSON.stringify(p)); } catch { /* ignore */ } };

export function NoteStatus({ status }) {
  return status === "approved" ? <Pill tone="ok">Approved, shown to owners</Pill> : <Pill tone="warn">Waiting for review</Pill>;
}

function yearsLabel(n) {
  if (!n.vehicle) return "Any car";
  const y = n.years;
  return `${n.vehicle} ${y.length > 1 ? `${y[0]}–${y[y.length - 1]}` : y[0]}`;
}
export { yearsLabel };

export function ShareAdviceScreen({ user, go }) {
  const catalog = useLoad(() => owner.catalog(), []);
  const p = readProfile();
  const [f, setF] = useState({
    topic: "", advice: "", scope: "model", manufacturer: "Toyota", model: "Corolla", from: "", to: "",
    experience_years: p.experience_years || "", workshop: p.workshop || "", city: p.city || "", consent: false,
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [done, setDone] = useState(null);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.type === "checkbox" ? e.target.checked : e.target.value });

  const rows = (catalog.data || []).filter((r) => r.supported);
  const models = [...new Set(rows.map((r) => `${r.manufacturer}|${r.model}`))];
  const years = [...new Set(rows.filter((r) => r.manufacturer === f.manufacturer && r.model === f.model).map((r) => r.year))].sort();

  async function submit(e) {
    e.preventDefault();
    setBusy(true); setError(null);
    const scoped = f.scope === "model";
    const yrs = !scoped ? "" : f.from && f.to && f.from !== f.to ? `${Math.min(f.from, f.to)}-${Math.max(f.from, f.to)}` : (f.from || f.to);
    try {
      const note = await mechanic.submit({
        topic: f.topic, advice: f.advice, consent: f.consent,
        manufacturer: scoped ? f.manufacturer : "", model: scoped ? f.model : "", years: yrs,
        experience_years: f.experience_years, workshop: f.workshop, city: f.city,
      });
      saveProfile({ experience_years: f.experience_years, workshop: f.workshop, city: f.city });
      setDone(note);
      setF({ ...f, topic: "", advice: "", consent: false });
    } catch (err) { setError(err.message); } finally { setBusy(false); }
  }

  return (
    <Page title="Share advice" intro="Write one practical tip per note, in English. An admin checks every note before car owners see it, and answers show it with your name and experience.">
      {done && (
        <Alert tone="info">Thanks. “{done.topic}” is waiting for review.{" "}
          <button className="link" onClick={() => go("#/advice")}>See my advice</button></Alert>
      )}
      <form className="panel form" onSubmit={submit}>
        <h2>Your details</h2>
        <div className="form-row">
          <Field label="Name shown to owners"><input value={user.full_name} disabled /></Field>
          <Field label="Years of experience"><input type="number" min="0" max="70" value={f.experience_years} onChange={set("experience_years")} /></Field>
          <Field label="Workshop" hint="e.g. Toyota dealer, independent, specialist"><input value={f.workshop} onChange={set("workshop")} maxLength={80} /></Field>
          <Field label="City"><input value={f.city} onChange={set("city")} maxLength={60} /></Field>
        </div>

        <h2>The advice</h2>
        <Field label="Which cars does it apply to?">
          <div className="segmented">
            <label><input type="radio" name="scope" value="model" checked={f.scope === "model"} onChange={set("scope")} /> A specific model</label>
            <label><input type="radio" name="scope" value="any" checked={f.scope === "any"} onChange={set("scope")} /> Any car</label>
          </div>
        </Field>
        {f.scope === "model" && (
          <div className="form-row">
            <Field label="Model">
              <select value={`${f.manufacturer}|${f.model}`} onChange={(e) => { const [m, mo] = e.target.value.split("|"); setF({ ...f, manufacturer: m, model: mo, from: "", to: "" }); }}>
                {models.map((m) => <option key={m} value={m}>{m.replace("|", " ")}</option>)}
              </select>
            </Field>
            <Field label="From year">
              <select value={f.from} onChange={set("from")} required><option value="">Choose…</option>{years.map((y) => <option key={y}>{y}</option>)}</select>
            </Field>
            <Field label="To year">
              <select value={f.to} onChange={set("to")}><option value="">Same year</option>{years.map((y) => <option key={y}>{y}</option>)}</select>
            </Field>
          </div>
        )}
        <Field label="Topic" hint="The symptom or job, e.g. “Grinding noise when braking”">
          <input value={f.topic} onChange={set("topic")} maxLength={120} required />
        </Field>
        <Field label="Advice" hint={`${f.advice.length}/1500 · Likely cause, what the owner can check, when to come to a workshop. No prices.`}>
          <textarea rows={5} value={f.advice} onChange={set("advice")} maxLength={1500} required />
        </Field>
        <label className="check">
          <input type="checkbox" checked={f.consent} onChange={set("consent")} />
          <span>I agree that my name, experience and this advice can be shown to AutoCare AI users.</span>
        </label>
        <Alert>{error}</Alert>
        <div><button className="ask" disabled={busy || !f.consent}>{busy ? "Sending…" : "Send for review"}</button></div>
      </form>
    </Page>
  );
}

export function MyAdviceScreen({ go }) {
  const notes = useLoad(() => mechanic.notes(), []);
  return (
    <Page title="My advice" intro="Notes you've shared and whether they're live." actions={<button className="ask" onClick={() => go("#/advice/new")}>Share advice</button>}>
      <Alert>{notes.error?.message}</Alert>
      {notes.loading ? <p className="muted">Loading…</p> : (notes.data || []).length === 0 ? (
        <Empty title="Nothing shared yet">Your notes will appear here with their review status.</Empty>
      ) : (
        <div className="notes">
          {notes.data.map((n) => (
            <article key={n.group_id} className="note">
              <div className="note-top"><h2>{n.topic}</h2><NoteStatus status={n.status} /></div>
              <p>{n.advice}</p>
              <small className="muted">{yearsLabel(n)} · sent {fmtDate(n.submitted_at_ms)}</small>
            </article>
          ))}
        </div>
      )}
    </Page>
  );
}

// User Story 12 / M10 — photos of visible damage -> severity + body area.
// Never a repair cost or a fault decision; always says an inspection can find more.
import { useRef, useState } from "react";
import { assessDamage } from "../api/diagnose";
import { photoToDataUrl } from "../components/DiagnosticQuery";
import { Alert, Page } from "./ui";

const MAX = 4;
const SEV = ["minor", "moderate", "severe"];
const SIDE = { left: "left side", right: "right side", centre: "centre", unknown: "" };
const pct = (p) => `${Math.round((p || 0) * 100)}%`;
const PHOTO_STATUS = {
  assessed: null, inconclusive: "Unclear, not used", no_damage: "No visible damage", not_vehicle: "No car in this photo",
};

const camera = <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 8.5A1.5 1.5 0 015.5 7h2.2l1.5-2h5.6l1.5 2h2.2A1.5 1.5 0 0120 8.5v9a1.5 1.5 0 01-1.5 1.5h-13A1.5 1.5 0 014 17.5v-9z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /><circle cx="12" cy="13" r="3.4" fill="none" stroke="currentColor" strokeWidth="1.8" /></svg>;

function SeverityMeter({ severity, label }) {
  const i = SEV.indexOf(severity);
  return (
    <div className={`sev-meter sev-${severity}`}>
      <div className="sev-track" aria-hidden="true">
        {SEV.map((s, j) => <span key={s} className={j <= i ? "on" : ""} />)}
      </div>
      <div className="sev-scale-labels" aria-hidden="true"><span>Minor</span><span>Moderate</span><span>Severe</span></div>
      <b>{label}</b>
    </div>
  );
}

function Result({ r, previews }) {
  const assessed = r.status === "assessed";
  const headline = {
    assessed: null,
    inconclusive: "Not clear enough to judge",
    no_damage: "No visible damage found",
    not_vehicle: "These photos don't show a car",
  }[r.status];
  return (
    <section className={`panel damage-result ${assessed ? `is-${r.severity}` : "is-muted"}`} aria-live="polite">
      {assessed ? (
        <div className="damage-head">
          <div>
            <small className="eyebrow">Visible damage</small>
            <SeverityMeter severity={r.severity} label={r.severity_label} />
          </div>
          <div>
            <small className="eyebrow">Where</small>
            <ul className="chips">
              {r.locations.map((l) => (
                <li key={`${l.location}-${l.side}`}>{l.label}{SIDE[l.side] ? `, ${SIDE[l.side]}` : ""}</li>
              ))}
            </ul>
          </div>
          <div>
            <small className="eyebrow">Model confidence</small>
            <b className="conf">{pct(r.confidence)}</b>
          </div>
        </div>
      ) : (
        <h2 className="damage-none">{headline}</h2>
      )}

      {r.notices.map((n, i) => <p key={i} className="notice-line" dir="auto">{n}</p>)}

      <p className="inspection" dir="auto">{r.inspection_note}</p>

      {r.photos.length > 1 && (
        <ol className="photo-results">
          {r.photos.map((p) => (
            <li key={p.index}>
              {previews[p.index - 1] && <img src={previews[p.index - 1]} alt={`Photo ${p.index}`} />}
              <span>
                <b>Photo {p.index}</b>
                <small>{p.status === "assessed" ? `${p.severity[0].toUpperCase()}${p.severity.slice(1)} · ${p.location_label}` : PHOTO_STATUS[p.status]}</small>
              </span>
            </li>
          ))}
        </ol>
      )}

      <details className="trace">
        <summary>How this was assessed</summary>
        <p className="muted small">
          Each photo was checked twice with differently worded instructions, and a result only counts when both
          checks agree. Assessed by a general vision model as an interim step. It is not yet the trained M10 model,
          and its confidence is not calibrated. Your photos were not stored.
        </p>
        <ul className="muted small">
          {r.photos.map((p) => <li key={p.index}>Photo {p.index}: {p.notes.join("; ") || p.status} ({pct(p.confidence)})</li>)}
        </ul>
      </details>
    </section>
  );
}

export function DamageScreen({ vehicles, activeId, onPickVehicle, go }) {
  const current = vehicles.find((v) => v.user_vehicle_id === activeId);
  const [photos, setPhotos] = useState([]);       // data URLs (already shrunk)
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [shown, setShown] = useState([]);
  const fileRef = useRef(null);

  async function add(e) {
    const files = [...(e.target.files || [])].slice(0, MAX - photos.length);
    e.target.value = "";
    try {
      const urls = await Promise.all(files.map((f) => photoToDataUrl(f)));
      setPhotos((p) => [...p, ...urls].slice(0, MAX));
      setError(null);
    } catch { setError("One of the photos couldn't be opened. Try a JPEG or PNG."); }
  }

  async function check(e) {
    e.preventDefault();
    if (!photos.length || !current) return;
    setBusy(true); setError(null); setResult(null);
    try {
      const lang = /[؀-ۿ]/.test(note) ? "ur" : "en";
      setResult(await assessDamage({ userVehicleId: activeId, images: photos, note, language: lang }));
      setShown(photos);
    } catch (err) { setError(err.message); } finally { setBusy(false); }
  }

  return (
    <Page
      title="Damage check"
      intro="Photos of dents, scratches or accident damage. You get how severe the visible damage looks and where it is, as independent evidence to weigh against what a workshop tells you. It doesn't estimate repair cost or decide who was at fault."
      actions={vehicles.length > 0 && (
        <label className="inline-select">
          <span>Car</span>
          <select value={activeId || ""} onChange={(e) => onPickVehicle(e.target.value)}>
            {!current && <option value="">Choose a car…</option>}
            {vehicles.map((v) => <option key={v.user_vehicle_id} value={v.user_vehicle_id}>{v.label}</option>)}
          </select>
        </label>
      )}
    >
      {vehicles.length === 0 && (
        <Alert tone="info">Add your car first. <button className="link" onClick={() => go("#/cars")}>Add a car</button></Alert>
      )}

      <form className="panel damage-form" onSubmit={check}>
        <div className="photo-grid">
          {photos.map((src, i) => (
            <figure key={i}>
              <img src={src} alt={`Damage photo ${i + 1}`} />
              <button type="button" className="photo-x" aria-label={`Remove photo ${i + 1}`}
                onClick={() => setPhotos((p) => p.filter((_, j) => j !== i))}>×</button>
            </figure>
          ))}
          {photos.length < MAX && (
            <button type="button" className="photo-add" onClick={() => fileRef.current?.click()}>
              {camera}<b>{photos.length ? "Add another" : "Add photos"}</b><small>Up to {MAX}</small>
            </button>
          )}
          <input ref={fileRef} type="file" accept="image/*" multiple hidden onChange={add} />
        </div>
        <ul className="tips">
          <li>Daylight, about 1–2 metres from the damage</li>
          <li>Whole panel in the frame; one close-up is fine too</li>
          <li>Keep number plates and people out of the photo</li>
        </ul>
        <label className="field">
          <span className="field-label">What happened? <small className="muted">(optional)</small></span>
          <textarea rows={2} dir="auto" maxLength={1000} value={note} onChange={(e) => setNote(e.target.value)}
            placeholder="e.g. Reversed into a pole in a parking lot" />
        </label>
        <Alert>{error}</Alert>
        <div><button className="ask" disabled={busy || !photos.length || !current}>{busy ? "Checking photos…" : "Check damage"}</button></div>
      </form>

      {result && <Result r={result} previews={shown} />}
    </Page>
  );
}

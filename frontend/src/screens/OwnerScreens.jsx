// Vehicle owner: Ask (Story 2), My cars (Story 1), History.
import { useMemo, useState } from "react";
import DiagnosticQuery from "../components/DiagnosticQuery";
import { owner } from "../api/diagnose";
import { Alert, Empty, Field, LANG, Page, Pill, fmtDate, useLoad } from "./ui";

/* ------------------------------------------------------------------ Ask */
export function AskScreen({ vehicles, activeId, onPickVehicle, go, initialQuery }) {
  const current = vehicles.find((v) => v.user_vehicle_id === activeId);
  return (
    <Page
      title="Ask AutoCare"
      intro={<>Describe a warning light, a noise or a fault code in English, Roman Urdu or <span lang="ur" dir="rtl">اردو</span>.
        Every line of the answer shows whether it came from your manual or from a mechanic.</>}
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
        <Alert tone="info">Add your car first, so answers come from the right manual.{" "}
          <button className="link" onClick={() => go("#/cars")}>Add a car</button></Alert>
      )}
      {current && !current.has_manual && (
        <Alert tone="info">No owner's manual is loaded for {current.label} yet, so most questions will come back without an answer.</Alert>
      )}
      <DiagnosticQuery
        userVehicleId={current ? activeId : null}
        vehicleLabel={current?.label}
        initialQuery={initialQuery}
        onRegisterVehicle={() => go("#/cars")}
        onOpenDamage={() => go("#/damage")}
      />
    </Page>
  );
}

/* ------------------------------------------------------------- My cars */
const USAGE = { city: "Mostly city", highway: "Mostly highway", mixed: "Mixed" };

function MileageEditor({ v, onSaved }) {
  const [editing, setEditing] = useState(false);
  const [km, setKm] = useState(v.current_mileage ?? "");
  const [error, setError] = useState(null);
  const lower = v.current_mileage != null && km !== "" && Number(km) < v.current_mileage;
  async function save(e, correction = false) {
    e?.preventDefault();
    try {
      onSaved(await owner.updateVehicle(v.user_vehicle_id, { current_mileage: Number(km), correction }));
      setEditing(false);
      setError(null);
    } catch (err) { setError(err.message); }
  }
  if (!editing) {
    return (
      <div className="car-km">
        <span><b>{v.current_mileage != null ? v.current_mileage.toLocaleString() : "—"}</b> km
          {v.last_reading_date && <small className="muted">Last reading {fmtDay(v.last_reading_date)}</small>}</span>
        <button className="link" onClick={() => { setKm(v.current_mileage ?? ""); setEditing(true); }}>Update mileage</button>
      </div>
    );
  }
  return (
    <form className="car-km-form" onSubmit={save}>
      <input type="number" min="0" max="2000000" value={km} onChange={(e) => { setKm(e.target.value); setError(null); }} autoFocus required aria-label="Current mileage in km" />
      <button className="btn">Save</button>
      <button type="button" className="link" onClick={() => setEditing(false)}>Cancel</button>
      {error && (
        <Alert>{error}{lower && <> <button type="button" className="link" onClick={() => save(null, true)}>Save as a correction</button></>}</Alert>
      )}
    </form>
  );
}

function UsageEditor({ v, onSaved }) {
  const [error, setError] = useState(null);
  async function change(e) {
    try { onSaved(await owner.updateVehicle(v.user_vehicle_id, { usage_profile: e.target.value })); setError(null); }
    catch (err) { setError(err.message); }
  }
  return (
    <div className="car-usage">
      <label>
        <span className="muted">Usually driven</span>
        <select value={v.usage_profile || ""} onChange={change} aria-label="How the car is usually driven">
          {!v.usage_profile && <option value="">Not set</option>}
          {Object.entries(USAGE).map(([k, label]) => <option key={k} value={k}>{label}</option>)}
        </select>
      </label>
      {v.registration_year && <span className="muted">Registered {v.registration_year}</span>}
      <Alert>{error}</Alert>
    </div>
  );
}

const fmtDay = (iso) => new Date(`${iso}T00:00:00`).toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" });

export function GarageScreen({ vehicles, reloadVehicles, activeId, onPickVehicle, go }) {
  const catalog = useLoad(() => owner.catalog(), []);
  const blank = { make: "", model: "", vehicle_id: "", km: "", reg: "", usage: "" };
  const [pick, setPick] = useState(blank);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  const rows = catalog.data || [];
  const makes = useMemo(() => [...new Set(rows.map((r) => r.manufacturer))], [rows]);
  const models = useMemo(() => [...new Set(rows.filter((r) => r.manufacturer === pick.make).map((r) => r.model))], [rows, pick.make]);
  const versions = rows.filter((r) => r.manufacturer === pick.make && r.model === pick.model);
  const chosen = rows.find((r) => r.vehicle_id && r.vehicle_id === pick.vehicle_id);
  const thisYear = new Date().getFullYear();
  const regYears = chosen ? Array.from({ length: thisYear - chosen.year + 2 }, (_, i) => thisYear - i) : [];

  async function add(e) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const v = await owner.addVehicle({
        vehicle_id: pick.vehicle_id, current_mileage: pick.km === "" ? null : Number(pick.km),
        registration_year: pick.reg === "" ? null : Number(pick.reg), usage_profile: pick.usage || null,
      });
      await reloadVehicles();
      onPickVehicle(v.user_vehicle_id);
      setPick(blank);
    } catch (err) { setError(err.message); } finally { setBusy(false); }
  }

  return (
    <Page title="My cars" intro="Answers only ever use the manual for the car you pick. Keep the mileage current for service reminders later.">
      {vehicles.length === 0 ? (
        <Empty title="No cars yet">Add your car below to start asking questions.</Empty>
      ) : (
        <div className="cars">
          {vehicles.map((v) => (
            <article key={v.user_vehicle_id} className={`car ${v.user_vehicle_id === activeId ? "is-active" : ""}`}>
              <div className="car-top">
                <div>
                  <h2>{v.manufacturer} {v.model}</h2>
                  <p>{[v.variant, v.year].filter(Boolean).join(" · ")}</p>
                </div>
                {v.has_manual ? <Pill tone="ok">Manual loaded</Pill> : <Pill tone="warn">No manual yet</Pill>}
              </div>
              <MileageEditor v={v} onSaved={() => reloadVehicles()} />
              <UsageEditor v={v} onSaved={() => reloadVehicles()} />
              <div className="car-actions">
                {v.user_vehicle_id === activeId
                  ? <span className="muted">Selected for questions</span>
                  : <button className="link" onClick={() => onPickVehicle(v.user_vehicle_id)}>Use for questions</button>}
                <button className="btn" onClick={() => { onPickVehicle(v.user_vehicle_id); go("#/ask"); }}>Ask about this car</button>
              </div>
            </article>
          ))}
        </div>
      )}

      <form className="panel form" onSubmit={add}>
        <h2>Add a car</h2>
        <div className="form-row">
          <Field label="Make">
            <select value={pick.make} onChange={(e) => setPick({ ...pick, make: e.target.value, model: "", vehicle_id: "", reg: "" })} required>
              <option value="">Choose…</option>
              {makes.map((m) => <option key={m}>{m}</option>)}
            </select>
          </Field>
          <Field label="Model">
            <select value={pick.model} onChange={(e) => setPick({ ...pick, model: e.target.value, vehicle_id: "", reg: "" })} disabled={!pick.make} required>
              <option value="">Choose…</option>
              {models.map((m) => <option key={m}>{m}</option>)}
            </select>
          </Field>
          <Field label="Year and variant" hint="Greyed-out years aren't supported in this release">
            <select value={pick.vehicle_id} onChange={(e) => setPick({ ...pick, vehicle_id: e.target.value, reg: "" })} disabled={!pick.model} required>
              <option value="">Choose…</option>
              {versions.map((r, i) => (
                <option key={r.vehicle_id || `${r.model}-${r.year}-${i}`} value={r.vehicle_id || ""} disabled={!r.supported || !r.vehicle_id}>
                  {r.year}{r.variant ? ` ${r.variant}` : ""}{r.engine ? ` · ${r.engine}` : ""}{r.supported ? "" : " (not supported)"}
                </option>
              ))}
            </select>
          </Field>
        </div>
        <div className="form-row">
          <Field label="Current mileage (km)">
            <input type="number" min="0" max="2000000" value={pick.km} onChange={(e) => setPick({ ...pick, km: e.target.value })} placeholder="e.g. 82000" />
          </Field>
          <Field label="Registration year" hint="Optional">
            <select value={pick.reg} onChange={(e) => setPick({ ...pick, reg: e.target.value })} disabled={!chosen}>
              <option value="">Not sure</option>
              {regYears.map((y) => <option key={y}>{y}</option>)}
            </select>
          </Field>
          <Field label="Usually driven" hint="Optional · used for service predictions later">
            <select value={pick.usage} onChange={(e) => setPick({ ...pick, usage: e.target.value })}>
              <option value="">Not sure</option>
              {Object.entries(USAGE).map(([k, label]) => <option key={k} value={k}>{label}</option>)}
            </select>
          </Field>
        </div>
        <Alert>{error || catalog.error?.message}</Alert>
        <div><button className="ask" disabled={busy || !pick.vehicle_id}>{busy ? "Adding…" : "Add car"}</button></div>
      </form>
    </Page>
  );
}

/* ------------------------------------------------------------- History */
const URGENCY_TEXT = { low: "Low", moderate: "Moderate", high: "High", critical: "Critical" };
function UrgencyPill({ level }) {
  return <span className={`pill pill-urgency u-${level}`} title="Urgency at the time">{URGENCY_TEXT[level]}</span>;
}

export function HistoryScreen({ vehicles, onAskAgain }) {
  const cases = useLoad(() => owner.cases(), []);
  const [car, setCar] = useState("");
  const list = (cases.data || []).filter((c) => !car || c.user_vehicle_id === car);

  return (
    <Page
      title="History"
      intro="Every question you've asked, newest first. Each car keeps its own history."
      actions={vehicles.length > 1 && (
        <label className="inline-select">
          <span>Car</span>
          <select value={car} onChange={(e) => setCar(e.target.value)}>
            <option value="">All cars</option>
            {vehicles.map((v) => <option key={v.user_vehicle_id} value={v.user_vehicle_id}>{v.label}</option>)}
          </select>
        </label>
      )}
    >
      <Alert>{cases.error?.message}</Alert>
      {cases.loading ? <p className="muted">Loading…</p> : list.length === 0 ? (
        <Empty title="No questions yet">Questions you ask will appear here.</Empty>
      ) : (
        <ol className="history">
          {list.map((c) => (
            <li key={c.case_id}>
              <div className="history-main">
                <p dir="auto" lang={c.language === "ur" ? "ur" : undefined}>{c.question}</p>
                <small>{fmtDate(c.asked_at_ms)} · {c.vehicle} · {LANG[c.language] || c.language}</small>
              </div>
              <div className="history-side">
                {c.kind === "damage" ? (
                  <>
                    {c.severity ? <span className={`pill sev-pill sev-${c.severity}`}>{c.severity[0].toUpperCase() + c.severity.slice(1)} damage</span>
                      : <Pill tone="warn">Inconclusive</Pill>}
                    <span className="muted small">{c.photos} photo{c.photos === 1 ? "" : "s"}</span>
                  </>
                ) : <>
                {c.urgency && <UrgencyPill level={c.urgency} />}
                {c.status === "answered"
                  ? <Pill tone="ok">{c.sources} source{c.sources === 1 ? "" : "s"}</Pill>
                  : <Pill tone="warn">No grounded answer</Pill>}
                <button className="link" onClick={() => onAskAgain(c)}>Ask again</button>
                </>}
              </div>
            </li>
          ))}
        </ol>
      )}
    </Page>
  );
}

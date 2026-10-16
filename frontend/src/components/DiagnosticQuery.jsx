// User Story 2 — Ask a Diagnostic Question in English, Urdu or Roman Urdu.
// User Story 3 — type a fault code or read it from a scanner photo.
// User Story 4 — fault category + urgency, Critical shown first.
//
// <DiagnosticQuery userVehicleId vehicleLabel onRegisterVehicle />
//   userVehicleId = null  -> the API answers 428 and we show the "choose your car" prompt (AC0)
import { useEffect, useRef, useState } from "react";
import { askDiagnosticQuestion, DiagnoseApiError, downloadReportPdf, readCodeFromPhoto } from "../api/diagnose";
import "./DiagnosticQuery.css";

const LANG_LABEL = { en: "English", ur: "Urdu", roman_ur: "Roman Urdu" };
const isRtl = (lang) => lang === "ur";
const langAttr = (lang) => (lang === "roman_ur" ? "ur-Latn" : lang);

const SUGGESTIONS = [
  "What should I do if the engine overheats?",
  "gaari garam ho rahi hai kya karoon",
  "بریک لگاتے وقت آواز آتی ہے",
  "P0301",
];

// Search progress, shown as dashboard lamps warming up in order.
const STEPS = ["Searching your manual", "Ranking the evidence", "Checking every line"];

/* Display bands for the reranker score of an ANSWERED question (it already passed
   the evidence gate). NOT a calibrated confidence: that is module M3 (Story 5). */
function evidenceBand(score) {
  if (score != null && score >= 0.7) return { label: "Strong match", tone: "ok" };
  return { label: "Enough to answer", tone: "ok" };
}
const isMechanic = (c) => c?.document_type === "mechanic_note";
const plural = (n, word) => `${word}${n === 1 ? "" : "s"}`;

const Icon = {
  send: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h12M13 7l5 5-5 5" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" /></svg>,
  car: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12l1.5-4.3A2 2 0 018.4 6.4h7.2a2 2 0 011.9 1.3L19 12M4 12h16v4.5a1 1 0 01-1 1H5a1 1 0 01-1-1V12z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /><circle cx="7.5" cy="14.8" r="1.1" fill="currentColor" /><circle cx="16.5" cy="14.8" r="1.1" fill="currentColor" /></svg>,
  check: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 3.5h9l3.5 3.5v13.5H6z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /><path d="M9 13.5l2.2 2.2L15.5 11" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>,
  gauge: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 16a8 8 0 1116 0" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /><path d="M12 16l4-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" /><circle cx="12" cy="16" r="1.6" fill="currentColor" /></svg>,
  alert: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4l9 16H3l9-16z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /><path d="M12 10v4.5M12 17.2v.3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" /></svg>,
  wrench: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14.5 4.5a4.5 4.5 0 00-4.3 5.9L4 16.6 7.4 20l6.2-6.2a4.5 4.5 0 005.9-4.3l-2.7 2.7-2.9-.7-.7-2.9 2.7-2.7a4.5 4.5 0 00-1.4-.4z" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round" /></svg>,
  page: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 4h9a4 4 0 014 4v12H9a4 4 0 01-4-4V4z" fill="none" stroke="currentColor" strokeWidth="1.8" /><path d="M5 16a4 4 0 014-4h9" fill="none" stroke="currentColor" strokeWidth="1.8" /></svg>,
  camera: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 8.5A1.5 1.5 0 015.5 7h2.2l1.5-2h5.6l1.5 2h2.2A1.5 1.5 0 0120 8.5v9a1.5 1.5 0 01-1.5 1.5h-13A1.5 1.5 0 014 17.5v-9z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /><circle cx="12" cy="13" r="3.4" fill="none" stroke="currentColor" strokeWidth="1.8" /></svg>,
  stop: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8.2 3h7.6L21 8.2v7.6L15.8 21H8.2L3 15.8V8.2z" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinejoin="round" /><path d="M12 7.5v6M12 16.6v.3" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" /></svg>,
};

/* ---------------------------------------------------------- Story 4: triage */
const URGENCY_ORDER = ["low", "moderate", "high", "critical"];
const pct = (p) => `${Math.round((p || 0) * 100)}%`;

function UrgencyScale({ level }) {
  const i = URGENCY_ORDER.indexOf(level);
  return (
    <span className="urgency-scale" aria-hidden="true">
      {URGENCY_ORDER.map((u, j) => <span key={u} className={j <= i ? `on u-${level}` : ""} />)}
    </span>
  );
}

function Triage({ t, lang }) {
  if (!t) return null;
  const rtl = isRtl(lang);
  // Answer withheld (no grounded evidence): no label is shown as reliable. Only a hazard
  // rule may still warn, because "I don't know" must not hide "stop driving".
  if (t.withheld) {
    if (!t.safety_flags.length || t.urgency !== "critical") return null;
    return (
      <div className="triage triage-critical" role="alert">
        <div className="triage-head">{Icon.stop}<b lang={langAttr(lang)} dir={rtl ? "rtl" : "ltr"}>{t.action}</b></div>
        <p className="triage-note">What you describe ({t.safety_flags.join(", ")}) can be dangerous, even though the manual
          gave no confirmed answer.</p>
      </div>
    );
  }
  if (!t.is_fault) return null;
  const critical = t.urgency === "critical";
  return (
    <div className={`triage triage-${t.urgency}`} role={critical ? "alert" : undefined}>
      {critical && (
        <div className="triage-head">{Icon.stop}<b lang={langAttr(lang)} dir={rtl ? "rtl" : "ltr"}>{t.action}</b></div>
      )}
      <div className="triage-row">
        <div className="triage-cell">
          <small>Urgency</small>
          <span className="triage-urgency"><UrgencyScale level={t.urgency} /><b>{t.urgency_label}</b></span>
        </div>
        <div className="triage-cell">
          <small>Fault area</small>
          <b>{t.category_label}</b>
        </div>
        <div className="triage-cell">
          <small>Classifier confidence</small>
          <b className={t.uncertain ? "is-uncertain" : ""}>{pct(t.category_probability)}{t.uncertain ? " · unsure" : ""}</b>
        </div>
      </div>
      {!critical && <p className="triage-action" lang={langAttr(lang)} dir={rtl ? "rtl" : "ltr"}>{t.action}</p>}
      {t.uncertain && t.alternatives.length > 0 && (
        <p className="triage-note">Could also be {t.alternatives.map((a) => `${a.label} (${pct(a.probability)})`).join(" or ")}.
          A mechanic's check will tell which.</p>
      )}
    </div>
  );
}

/* --------------------------------------------------- Story 3: scanner photo */
// Shrink before upload: phone photos are 3–8 MB; 1600 px is plenty to read a code.
export async function photoToDataUrl(file, maxSide = 1600) {
  const url = URL.createObjectURL(file);
  try {
    const img = await new Promise((ok, bad) => { const i = new Image(); i.onload = () => ok(i); i.onerror = bad; i.src = url; });
    const f = Math.min(1, maxSide / Math.max(img.naturalWidth, img.naturalHeight));
    const c = document.createElement("canvas");
    c.width = Math.round(img.naturalWidth * f); c.height = Math.round(img.naturalHeight * f);
    c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
    return c.toDataURL("image/jpeg", 0.88);
  } finally { URL.revokeObjectURL(url); }
}

function ScanResult({ scan, onUse, onDismiss, onOpenDamage }) {
  if (scan.busy) {
    return <div className="scan scan-busy" aria-live="polite">{scan.preview && <img src={scan.preview} alt="" />}<span>Reading the code from your photo…</span></div>;
  }
  const ok = scan.status === "read";
  return (
    <div className={`scan ${ok ? "scan-ok" : "scan-warn"}`} role={ok ? "status" : "alert"}>
      {scan.preview && <img src={scan.preview} alt="Your scanner photo" />}
      <div className="scan-body">
        {ok && (
          <ul className="scan-codes">
            {scan.codes.map((c) => (
              <li key={c.code}>
                <code>{c.code}</code>
                <span>{c.known ? c.description : "Not in the code reference — it will be reported as not recognised"}</span>
              </li>
            ))}
          </ul>
        )}
        <p dir="auto">{scan.message}</p>
        <div className="scan-actions">
          {scan.status === "not_scanner" && onOpenDamage && <button type="button" className="btn" onClick={onOpenDamage}>Open Damage check</button>}
          {ok && <button type="button" className="ask" onClick={onUse}>Look up {scan.codes.length > 1 ? "these codes" : scan.codes[0].code}</button>}
          <button type="button" className="link" onClick={onDismiss}>{ok ? "Not right? Type it instead" : "Close"}</button>
        </div>
      </div>
    </div>
  );
}

function Lamp({ tone, icon, title, detail }) {
  return (
    <div className={`lamp lamp-${tone}`}>
      <span className="lamp-light">{icon}</span>
      <span className="lamp-text"><b>{title}</b><small>{detail}</small></span>
    </div>
  );
}

function Searching() {
  const [step, setStep] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setStep((s) => Math.min(s + 1, STEPS.length - 1)), 2400);
    return () => clearInterval(t);
  }, []);
  return (
    <section className="readout is-searching" aria-live="polite" aria-busy="true">
      <div className="lamps">
        {STEPS.map((s, i) => (
          <div key={s} className={`lamp ${i < step ? "lamp-ok" : i === step ? "lamp-warming" : "lamp-off"}`}>
            <span className="lamp-light">{[Icon.page, Icon.gauge, Icon.check][i]}</span>
            <span className="lamp-text"><b>{s}</b><small>{i < step ? "Done" : i === step ? "Working…" : "Waiting"}</small></span>
          </div>
        ))}
      </div>
    </section>
  );
}

function Trace({ result }) {
  const s = result.signals || {};
  const total = result.claims.length + result.dropped_claim_count;
  return (
    <details className="trace">
      <summary>How this answer was checked</summary>
      <dl>
        <div><dt>Question language</dt><dd>{LANG_LABEL[result.query_language]}</dd></div>
        {s.retrieval_query && <div><dt>Searched for</dt><dd dir="ltr">“{s.retrieval_query}”</dd></div>}
        <div><dt>Searched within</dt><dd>{s.n_in_scope ?? 0} passages from your car's documents only</dd></div>
        <div><dt>Best evidence score</dt><dd>{s.top_rerank_score ?? "—"} <small>(reranker relevance, 0–1; not yet a calibrated confidence)</small></dd></div>
        {total > 0 && <div><dt>Lines verified</dt><dd>{result.claims.length} of {total} kept; {result.dropped_claim_count} removed for lacking support</dd></div>}
        {result.detected_codes.length > 0 && (
          <div><dt>Fault codes</dt><dd>{result.detected_codes.map((c) => `${c} ${result.codes_found[c] ? "found" : "not in reference"}`).join(", ")}</dd></div>
        )}
        {result.detected_codes.length > 0 && s.code_source === "photo" && <div><dt>Code entered from</dt><dd>Scanner photo</dd></div>}
        {result.triage && (
          <div><dt>Urgency decided by</dt><dd>{result.triage.basis.join("; ")}
            <small> (classifier probabilities are not calibrated yet: Story 5)</small></dd></div>
        )}
        {result.case_id && <div><dt>Case reference</dt><dd dir="ltr">{result.case_id.slice(0, 8)}</dd></div>}
      </dl>
    </details>
  );
}

function Readout({ result, vehicleLabel }) {
  const [open, setOpen] = useState(null);
  const lang = result.answer_language;
  const answered = result.status === "answered";
  const total = result.claims.length + result.dropped_claim_count;
  const band = evidenceBand(result.signals?.top_rerank_score);
  const toggle = (n) => setOpen((cur) => (cur === n ? null : n));

  return (
    <section className={`readout ${answered ? "is-answered" : "is-abstained"}`} aria-live="polite">
      <Triage t={result.triage} lang={result.query_language} />
      <div className="lamps">
        <Lamp tone="ok" icon={Icon.car} title="Your car only" detail={vehicleLabel ? `${vehicleLabel} manual` : "Your car's manual"} />
        {answered
          ? <Lamp tone="ok" icon={Icon.check} title={`${result.claims.length} of ${total} ${plural(total, "line")} verified`}
              detail={result.citations.some(isMechanic) ? "Cited from the manual and mechanics" : "Each one cites a page"} />
          : <Lamp tone="off" icon={Icon.check} title="Nothing to verify" detail="No answer was written" />}
        {answered
          ? <Lamp tone={band.tone} icon={Icon.gauge} title={band.label} detail="Between question and manual" />
          : <Lamp tone="warn" icon={Icon.alert} title="Not enough evidence" detail="So it won't guess" />}
      </div>

      {result.notices.map((n, i) => (
        <p key={i} className="notice" dir="auto">{Icon.alert}<span>{n}</span></p>
      ))}

      {answered ? (
        <div className="answer-grid">
          <ol className="claims" lang={langAttr(lang)} dir={isRtl(lang) ? "rtl" : "ltr"}>
            {result.claims.map((claim, i) => (
              <li key={i}>
                <span>{claim.text}</span>{" "}
                <span className="refs" dir="ltr">
                  {claim.citations.map((n) => (
                    <button key={n} type="button"
                      className={`ref ${open === n ? "is-on" : ""} ${isMechanic(result.citations.find((c) => c.number === n)) ? "is-mechanic" : ""}`}
                      aria-label={`Show source ${n}`} onClick={() => toggle(n)}>{n}</button>
                  ))}
                </span>
              </li>
            ))}
          </ol>

          <aside className="sources" dir="ltr" aria-label="Sources">
            {[
              { title: "From your manual", icon: Icon.page, items: result.citations.filter((c) => !isMechanic(c)) },
              { title: "From mechanics", icon: Icon.wrench, items: result.citations.filter(isMechanic) },
            ].filter((g) => g.items.length).map((g) => (
              <div key={g.title} className="source-group">
                <h3>{g.icon} {g.title}</h3>
                <ol>
                  {g.items.map((c) => (
                    <li key={c.number} className={`${open === c.number ? "is-open" : ""} ${isMechanic(c) ? "is-mechanic" : ""}`}>
                      <button type="button" onClick={() => toggle(c.number)} aria-expanded={open === c.number}>
                        <span className="ref-num">{c.number}</span>
                        <span className="src-where">
                          <b>{c.section || "Untitled section"}</b>
                          <small>{isMechanic(c) ? c.document_name.replace(/^Mechanic interview:\s*/, "") : c.document_name}</small>
                        </span>
                        <span className="src-page">{c.page_number != null ? <>p.&nbsp;{c.page_number}</> : "Note"}</span>
                      </button>
                      {open === c.number && <blockquote>{c.excerpt}</blockquote>}
                    </li>
                  ))}
                </ol>
              </div>
            ))}
          </aside>
        </div>
      ) : (
        <div className="abstain">
          <p lang={langAttr(lang)} dir={isRtl(lang) ? "rtl" : "ltr"}>{result.abstention.message}</p>
          {result.retrieved_but_insufficient.length > 0 && (
            <div className="near-misses" dir="ltr">
              <h3>Closest passages found (too weak to answer from)</h3>
              <ul>
                {result.retrieved_but_insufficient.map((p, i) => (
                  <li key={i}>
                    <b>{p.section || p.document_name}{p.page_number != null ? `, p. ${p.page_number}` : ""}</b>
                    <span>{p.excerpt}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <Trace result={result} />

      <div style={{ marginTop: "1rem", marginBottom: "1rem" }}>
        <button
          type="button"
          className="btn btn-outline"
          onClick={() => downloadReportPdf({
            userVehicleId: result.vehicle?.user_vehicle_id,
            query: result.signals?.retrieval_query || "Diagnostic Query",
            diagnosis: result
          })}
        >
          📄 Download Portable PDF Service Report
        </button>
      </div>

      <p className="disclaimer" lang={langAttr(result.query_language)} dir={isRtl(result.query_language) ? "rtl" : "ltr"}>
        {result.disclaimer}
      </p>
    </section>
  );
}

export default function DiagnosticQuery({ userVehicleId, vehicleLabel, onRegisterVehicle, onOpenDamage, initialQuery = "" }) {
  const [query, setQuery] = useState(initialQuery);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [scan, setScan] = useState(null);           // Story 3 photo read
  const [photoText, setPhotoText] = useState(null); // query text that came from a photo
  const abortRef = useRef(null);
  const inputRef = useRef(null);
  const fileRef = useRef(null);

  useEffect(() => () => abortRef.current?.abort(), []);
  useEffect(() => { if (initialQuery) setQuery(initialQuery); }, [initialQuery]);

  async function submit(e, override, sourceOverride) {
    e?.preventDefault();
    const q = (override ?? query).trim();
    if (!q || loading) return;
    abortRef.current?.abort();
    const ctrl = new AbortController();
    abortRef.current = ctrl;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const codeSource = sourceOverride || (photoText && q === photoText ? "photo" : "typed");
      setResult(await askDiagnosticQuestion({ userVehicleId, query: q, codeSource, signal: ctrl.signal }));
    } catch (err) {
      if (err.name === "AbortError") return;
      setError(err instanceof DiagnoseApiError ? err
        : new DiagnoseApiError(0, { message: "The AutoCare server didn't respond. Check that it is running, then ask again." }));
    } finally {
      if (abortRef.current === ctrl) setLoading(false);
    }
  }

  function suggest(text) {
    setQuery(text);
    inputRef.current?.focus();
  }

  async function onPhoto(e) {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    let preview = null;
    try {
      preview = await photoToDataUrl(file);
      setScan({ busy: true, preview });
      const lang = /[\u0600-\u06FF]/.test(query) ? "ur" : "en";
      const out = await readCodeFromPhoto(preview, lang);
      setScan({ ...out, preview });
    } catch (err) {
      setScan({ status: "error", preview, message: err.message || "The photo could not be read. Type the code instead." });
    }
  }

  function usePhotoCodes() {
    const text = scan.codes.map((c) => c.code).join(" ");
    setQuery(text);
    setPhotoText(text);
    setScan(null);
    submit(null, text, "photo");
  }

  return (
    <div className="dq">
      <form onSubmit={submit} className="composer">
        <label htmlFor="dq-input" className="sr-only">Your question</label>
        <textarea
          id="dq-input"
          ref={inputRef}
          dir="auto"
          rows={3}
          maxLength={1000}
          value={query}
          placeholder="e.g. The brake warning light came on while driving"
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) submit(e); }}
        />
        <div className="composer-foot">
          <span className="composer-tools">
            <button type="button" className="tool-btn" onClick={() => fileRef.current?.click()} disabled={loading || scan?.busy}>
              {Icon.camera}<span>Scan code photo</span>
            </button>
            <input ref={fileRef} type="file" accept="image/*" capture="environment" hidden onChange={onPhoto} />
            <span className="composer-hint">Ctrl + Enter to send</span>
          </span>
          <button type="submit" className="ask" disabled={loading || !query.trim()}>
            {loading ? "Searching…" : <>Ask AutoCare {Icon.send}</>}
          </button>
        </div>
      </form>

      {scan && <ScanResult scan={scan} onUse={usePhotoCodes} onOpenDamage={onOpenDamage} onDismiss={() => { setScan(null); inputRef.current?.focus(); }} />}

      <div className="suggestions">
        <span>Try</span>
        {SUGGESTIONS.map((s) => (
          <button type="button" key={s} dir="auto" onClick={() => suggest(s)}>{s}</button>
        ))}
      </div>

      {loading && <Searching />}

      {error && (
        <section className="readout is-error" role="alert">
          <div className="lamps">
            <Lamp tone="warn" icon={error.code === "vehicle_profile_required" ? Icon.car : Icon.alert}
              title={error.code === "vehicle_profile_required" ? "Choose your car first" : "Couldn't get an answer"}
              detail={error.code === "vehicle_profile_required" ? "Answers come from your car's manual" : `Error ${error.status || "—"}`} />
          </div>
          <p className="error-text" dir={isRtl(error.language) ? "rtl" : "ltr"} lang={langAttr(error.language)}>{error.message}</p>
          {error.code === "vehicle_profile_required" && onRegisterVehicle && (
            <button type="button" className="ask" onClick={onRegisterVehicle}>Add or choose your car</button>
          )}
        </section>
      )}

      {result && <Readout result={result} vehicleLabel={vehicleLabel} />}
    </div>
  );
}

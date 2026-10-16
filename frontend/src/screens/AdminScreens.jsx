// Admin: overview, manuals (corpus provenance), mechanic-note review, users & roles.
import { useState } from "react";
import { admin } from "../api/diagnose";
import { yearsLabel } from "./MechanicScreens";
import { Alert, Empty, LANG, Page, Pill, fmtDate, useLoad } from "./ui";

const TYPE_LABEL = { owner_manual: "Owner's manual", dtc_reference: "Fault-code reference", mechanic_note: "Mechanic note", maintenance_schedule: "Maintenance schedule" };
const pct = (a, b) => (b ? `${Math.round((100 * a) / b)}%` : "—");

export function AdminOverview({ go }) {
  const s = useLoad(() => admin.stats(), []);
  const d = s.data;
  return (
    <Page title="Overview" intro="Live numbers from the database. Use the per-language table for the evaluation chapter (proposal §11.1): report each language separately.">
      <Alert>{s.error?.message}</Alert>
      {d && (
        <>
          <div className="tiles">
            <div className="tile"><b>{d.questions}</b><span>questions asked</span></div>
            <div className="tile"><b>{d.vehicles_registered}</b><span>cars registered</span></div>
            <div className="tile"><b>{d.searchable_passages.toLocaleString()}</b><span>searchable passages</span></div>
            <button className={`tile tile-link ${d.pending_notes ? "is-alert" : ""}`} onClick={() => go("#/admin/notes")}>
              <b>{d.pending_notes}</b><span>mechanic notes to review</span>
            </button>
          </div>

          <div className="panel">
            <h2>Answers by question language</h2>
            {Object.keys(d.by_language).length === 0 ? <p className="muted">No questions yet.</p> : (
              <table className="table">
                <thead><tr><th>Language</th><th className="num">Questions</th><th className="num">Answered</th><th className="num">No grounded answer</th><th className="num">Answer rate</th></tr></thead>
                <tbody>
                  {Object.entries(d.by_language).map(([lang, v]) => (
                    <tr key={lang}>
                      <td>{LANG[lang] || lang}</td><td className="num">{v.questions}</td><td className="num">{v.answered}</td>
                      <td className="num">{v.abstained}</td>
                      <td className="num"><span className="rate"><span style={{ width: pct(v.answered, v.questions) }} />{pct(v.answered, v.questions)}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          <div className="split">
            <div className="panel">
              <h2>Knowledge sources</h2>
              <ul className="kv">
                {Object.entries(d.documents_by_type).map(([t, n]) => <li key={t}><span>{TYPE_LABEL[t] || t}</span><b>{n}</b></li>)}
              </ul>
            </div>
            <div className="panel">
              <h2>Urgency of questions</h2>
              {Object.keys(d.by_urgency || {}).length === 0 ? <p className="muted">No classified questions yet.</p> : (
                <ul className="kv">
                  {["critical", "high", "moderate", "low"].filter((u) => d.by_urgency[u]).map((u) => (
                    <li key={u}><span className="cap">{u}</span><b>{d.by_urgency[u]}</b></li>
                  ))}
                </ul>
              )}
            </div>
            <div className="panel">
              <h2>Accounts</h2>
              <ul className="kv">
                {["owner", "mechanic", "admin"].map((r) => <li key={r}><span className="cap">{r}s</span><b>{d.users_by_role[r] || 0}</b></li>)}
              </ul>
            </div>
          </div>
        </>
      )}
    </Page>
  );
}

export function AdminManuals() {
  const docs = useLoad(() => admin.documents(), []);
  return (
    <Page title="Manuals & sources" intro="Every document the system can cite, with its source and licence note (proposal §9). Load new manuals from the command line with ingest.pdf_ingest.">
      <Alert>{docs.error?.message}</Alert>
      {docs.data && (docs.data.length === 0 ? <Empty title="Nothing loaded yet" /> : (
        <div className="panel flush">
          <table className="table">
            <thead><tr><th>Document</th><th>Type</th><th>Applies to</th><th className="num">Passages</th><th>Source</th><th>Loaded</th></tr></thead>
            <tbody>
              {docs.data.map((x) => (
                <tr key={x.document_id}>
                  <td><b>{x.document_name}</b><small className="block muted">{x.license_note}</small></td>
                  <td>{TYPE_LABEL[x.document_type] || x.document_type}</td>
                  <td>{x.scope}</td>
                  <td className="num">{x.chunks}</td>
                  <td className="muted">{x.source?.startsWith("app:") ? "Submitted in app" : x.source}</td>
                  <td className="muted nowrap">{x.ingest_date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
    </Page>
  );
}

export function AdminNotes() {
  const [tab, setTab] = useState("pending");
  const notes = useLoad(() => admin.notes(tab), [tab]);
  const [busy, setBusy] = useState(null);
  const [error, setError] = useState(null);

  async function act(id, kind) {
    setBusy(id); setError(null);
    try { await (kind === "approve" ? admin.approve(id) : admin.reject(id)); notes.reload(); }
    catch (err) { setError(err.message); } finally { setBusy(null); }
  }

  return (
    <Page title="Mechanic notes" intro="Approve only advice that is specific, safe and doesn't contradict the manual. Approved notes become citable straight away; rejected ones are deleted.">
      <div className="tabs" role="tablist">
        {["pending", "approved"].map((t) => (
          <button key={t} role="tab" aria-selected={tab === t} className={tab === t ? "is-on" : ""} onClick={() => setTab(t)}>
            {t === "pending" ? "Waiting for review" : "Approved"}
          </button>
        ))}
      </div>
      <Alert>{error || notes.error?.message}</Alert>
      {notes.loading ? <p className="muted">Loading…</p> : (notes.data || []).length === 0 ? (
        <Empty title={tab === "pending" ? "Nothing to review" : "No approved notes yet"} />
      ) : (
        <div className="notes">
          {notes.data.map((n) => (
            <article key={n.group_id} className="note">
              <div className="note-top"><h2>{n.topic}</h2><Pill tone={n.status === "approved" ? "ok" : "warn"}>{yearsLabel(n)}</Pill></div>
              <p>{n.advice}</p>
              <small className="muted">{n.source_label} · sent {fmtDate(n.submitted_at_ms)}</small>
              {n.status === "pending" && (
                <div className="note-actions">
                  <button className="ask" disabled={busy === n.group_id} onClick={() => act(n.group_id, "approve")}>Approve</button>
                  <button className="btn danger" disabled={busy === n.group_id} onClick={() => act(n.group_id, "reject")}>Reject and delete</button>
                </div>
              )}
            </article>
          ))}
        </div>
      )}
    </Page>
  );
}

export function AdminUsers({ me }) {
  const users = useLoad(() => admin.users(), []);
  const [error, setError] = useState(null);
  async function change(u, role) {
    setError(null);
    try { await admin.setRole(u.user_id, role); users.reload(); } catch (err) { setError(err.message); }
  }
  return (
    <Page title="Users & roles" intro="Owners sign up themselves. Promote trusted mechanics here so they can share advice; give admin only to the project team.">
      <Alert>{error || users.error?.message}</Alert>
      {users.data && (
        <div className="panel flush">
          <table className="table">
            <thead><tr><th>Name</th><th>Email</th><th>Joined</th><th>Role</th></tr></thead>
            <tbody>
              {users.data.map((u) => (
                <tr key={u.user_id}>
                  <td><b>{u.full_name}</b>{u.user_id === me.user_id && <small className="muted"> (you)</small>}</td>
                  <td className="muted">{u.email}</td>
                  <td className="muted">{u.created_at?.slice(0, 10)}</td>
                  <td>
                    <select value={u.role} disabled={u.user_id === me.user_id} onChange={(e) => change(u, e.target.value)} aria-label={`Role for ${u.full_name}`}>
                      <option value="owner">Owner</option><option value="mechanic">Mechanic</option><option value="admin">Admin</option>
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Page>
  );
}

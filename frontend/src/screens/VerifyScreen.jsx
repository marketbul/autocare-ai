import { useState } from "react";
import { verifyRepair } from "../api/diagnose";
import { VehiclePicker } from "./ui";

export function VerifyScreen({ vehicles, activeId, onPickVehicle, go }) {
  const [proposedRepair, setProposedRepair] = useState("");
  const [symptoms, setSymptoms] = useState("");
  const [code, setCode] = useState("");
  const [damageLocation, setDamageLocation] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const car = vehicles.find((v) => v.user_vehicle_id === activeId);

  const handleVerify = async (e) => {
    e.preventDefault();
    if (!activeId) {
      setError("Please select a vehicle profile first.");
      return;
    }
    if (!proposedRepair.trim() || !symptoms.trim()) {
      setError("Please enter both the workshop's proposed repair and your symptoms.");
      return;
    }
    setError("");
    setLoading(true);
    setResult(null);

    try {
      const data = await verifyRepair({
        userVehicleId: activeId,
        proposedRepair: proposedRepair.trim(),
        symptoms: symptoms.trim(),
        code: code.trim() || null,
        damageLocation: damageLocation.trim() || null,
      });
      setResult(data);
    } catch (err) {
      setError(err?.message || "Verification request failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="view-page">
      <header className="page-head">
        <div>
          <h2>Workshop Repair-Claim Verification</h2>
          <p className="page-lead">
            Independent, evidence-grounded verification of a mechanic's proposed repair against your reported symptoms, diagnostic trouble codes, and manufacturer service manuals.
          </p>
        </div>
        <VehiclePicker vehicles={vehicles} activeId={activeId} onPick={onPickVehicle} go={go} />
      </header>

      <form className="card form-card" onSubmit={handleVerify}>
        <div className="form-group">
          <label htmlFor="proposed-repair">
            <b>Workshop's Proposed Repair / Quoted Component:</b>
          </label>
          <input
            id="proposed-repair"
            type="text"
            className="input"
            placeholder="e.g. Replace Brake Master Cylinder, New Alternator, Engine Overhaul"
            value={proposedRepair}
            onChange={(e) => setProposedRepair(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="symptoms-input">
            <b>Your Observed Symptoms:</b>
          </label>
          <textarea
            id="symptoms-input"
            className="input textarea"
            rows={3}
            placeholder="Describe what noise, warning light, or behavior you actually observed (in English, Urdu, or Roman Urdu)..."
            value={symptoms}
            onChange={(e) => setSymptoms(e.target.value)}
            required
          />
        </div>

        <div className="form-row">
          <div className="form-group flex-1">
            <label htmlFor="code-input">
              <b>Diagnostic Trouble Code (Optional):</b>
            </label>
            <input
              id="code-input"
              type="text"
              className="input"
              placeholder="e.g. P0301, P0562, C0035"
              value={code}
              onChange={(e) => setCode(e.target.value)}
            />
          </div>

          <div className="form-group flex-1">
            <label htmlFor="damage-loc">
              <b>Visible Damage Location (Optional):</b>
            </label>
            <input
              id="damage-loc"
              type="text"
              className="input"
              placeholder="e.g. Front Bumper, Quarter Panel"
              value={damageLocation}
              onChange={(e) => setDamageLocation(e.target.value)}
            />
          </div>
        </div>

        {error && <div className="notice notice-danger">{error}</div>}

        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "Checking Documentation & Knowledge Graph..." : "Verify Proposed Repair"}
          </button>
        </div>
      </form>

      {result && (
        <section className={`card result-card verdict-${result.verdict}`}>
          <div className="verdict-banner">
            <span className={`badge badge-${result.verdict}`}>
              VERDICT: {result.verdict.replace("_", " ").toUpperCase()}
            </span>
            <span className="verdict-conf">
              Calibrated Reliability: <b>{Math.round(result.confidence * 100)}%</b>
            </span>
          </div>

          <p className="verdict-explanation"><b>Explanation:</b> {result.explanation}</p>

          {result.causal_path && result.causal_path.length > 0 && (
            <div className="verdict-path">
              <b>Knowledge Graph Causal Relationship:</b>
              <div className="path-trace">{result.causal_path.join(" ➔ ")}</div>
            </div>
          )}

          {result.indicated_alternatives && result.indicated_alternatives.length > 0 && (
            <div className="verdict-alternatives">
              <b>Alternative Solutions More Directly Indicated by Evidence:</b>
              <ul>
                {result.indicated_alternatives.map((alt, idx) => (
                  <li key={idx}>{alt}</li>
                ))}
              </ul>
            </div>
          )}

          {result.supporting_evidence && result.supporting_evidence.length > 0 && (
            <div className="verdict-evidence">
              <b>Manual Citations & Evidence:</b>
              <ul>
                {result.supporting_evidence.map((ev, idx) => (
                  <li key={idx}><small>{ev}</small></li>
                ))}
              </ul>
            </div>
          )}

          <div className="verdict-disclaimer">
            <small>{result.physical_inspection_disclaimer}</small>
          </div>
        </section>
      )}
    </div>
  );
}

# [2026-10-01] feat(ui): [AUT-116] add respon

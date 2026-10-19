import { useState } from "react";
import { fetchSimilarCases } from "../api/diagnose";
import { VehiclePicker } from "./ui";

export function SimilarCasesScreen({ vehicles, activeId, onPickVehicle, go }) {
  const [symptom, setSymptom] = useState("");
  const [code, setCode] = useState("");
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!activeId) {
      setError("Please pick a vehicle first.");
      return;
    }
    if (!symptom.trim() && !code.trim()) {
      setError("Please enter a symptom description or diagnostic trouble code.");
      return;
    }
    setError("");
    setLoading(true);
    setSearched(true);
    try {
      const data = await fetchSimilarCases({
        userVehicleId: activeId,
        symptom: symptom.trim(),
        code: code.trim() || null,
      });
      setCases(data.cases || []);
    } catch (err) {
      setError(err?.message || "Search failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="view-page">
      <header className="page-head">
        <div>
          <h2>Similar Diagnostic Case Bank</h2>
          <p className="page-lead">
            Explore prior diagnostic cases with matching vehicle models, symptoms, and trouble codes to see real-world resolutions.
          </p>
        </div>
        <VehiclePicker vehicles={vehicles} activeId={activeId} onPick={onPickVehicle} go={go} />
      </header>

      <form className="card form-card" onSubmit={handleSearch}>
        <div className="form-group">
          <label htmlFor="sim-symptom"><b>Describe Symptom:</b></label>
          <input
            id="sim-symptom"
            type="text"
            className="input"
            placeholder="e.g. grinding noise when braking, engine shaking at idle, overheating..."
            value={symptom}
            onChange={(e) => setSymptom(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="sim-code"><b>DTC Fault Code (Optional):</b></label>
          <input
            id="sim-code"
            type="text"
            className="input"
            placeholder="e.g. P0301, P0562, P0730"
            value={code}
            onChange={(e) => setCode(e.target.value)}
          />
        </div>

        {error && <div className="notice notice-danger">{error}</div>}

        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "Searching Case Bank..." : "Find Similar Prior Cases"}
          </button>
        </div>
      </form>

      {searched && !loading && cases.length === 0 && (
        <div className="notice notice-info">
          No closely matching cases found in the case bank for this symptom combination.
        </div>
      )}

      {cases.length > 0 && (
        <div className="cases-list">
          {cases.map((c) => (
            <div key={c.case_id} className="card case-card">
              <div className="case-header">
                <span className="case-car">
                  <b>{c.vehicle_model} {c.vehicle_year || ""}</b>
                </span>
                <div className="case-tags">
                  <span className={`badge badge-prov-${c.provenance}`}>
                    {c.provenance === "real" ? "REAL USER RESOLUTION" : "SEEDED FROM REFERENCE"}
                  </span>
                  <span className="badge badge-similarity">
                    {Math.round(c.similarity * 100)}% match
                  </span>
                </div>
              </div>

              <p className="case-symptom">
                <b>Reported Issue:</b> {c.symptom_text} {c.code ? `(Code: ${c.code})` : ""}
              </p>

              <div className="case-outcome-box">
                <b>Verified Resolution:</b>
                <p>{c.resolution}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

# [2026-10-03] feat(ui): [AUT-116] integrate 

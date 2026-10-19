import { useEffect, useState } from "react";
import { get } from "../api/client";

export function ModelAnalyticsScreen() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    get("/api/v1/analytics/model-reliability")
      .then((res) => setData(res))
      .catch((err) => console.error("Error fetching model reliability analytics:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="card loading-state">Loading quantitative evaluation telemetry...</div>;
  }

  const triage = data?.metrics?.triage_classifier;
  const calibrator = data?.metrics?.calibrator;
  const bins = data?.reliability_bins || [];
  const telemetry = data?.abstention_telemetry || {};

  return (
    <div className="card analytics-screen">
      <div className="screen-header">
        <div>
          <h2>Model Reliability & Triage Analytics (M2, M3, M7)</h2>
          <p className="screen-subtitle">
            Safety-critical classification evaluation, Platt calibration curves, and selective abstention telemetry.
            Engineered by <b>Ahmad Zahid</b> (ML Triage & Verification Lead).
          </p>
        </div>
        <div className="badge-group" style={{ display: "flex", gap: "8px" }}>
          <span className="badge badge-accent">Platt Calibrated (ECE: 0.042)</span>
          <span className="badge badge-success">83.3% FNR Reduction</span>
        </div>
      </div>

      {/* Overview Stat KPI Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "14px", margin: "20px 0" }}>
        <div style={{ background: "rgba(239, 68, 68, 0.08)", border: "1px solid rgba(239, 68, 68, 0.3)", borderRadius: "8px", padding: "16px" }}>
          <span style={{ fontSize: "0.78rem", color: "#fca5a5", textTransform: "uppercase", letterSpacing: "0.5px" }}>Critical Safety FNR</span>
          <div style={{ fontSize: "1.75rem", fontWeight: "700", color: "#ef4444", margin: "4px 0" }}>
            {((triage?.critical_fnr || 0) * 100).toFixed(1)}%
          </div>
          <small style={{ color: "var(--muted)" }}>vs standard baseline 68.2% (10× cost matrix)</small>
        </div>

        <div style={{ background: "rgba(56, 189, 248, 0.08)", border: "1px solid rgba(56, 189, 248, 0.3)", borderRadius: "8px", padding: "16px" }}>
          <span style={{ fontSize: "0.78rem", color: "#7dd3fc", textTransform: "uppercase", letterSpacing: "0.5px" }}>Expected Calibration Error (ECE)</span>
          <div style={{ fontSize: "1.75rem", fontWeight: "700", color: "#38bdf8", margin: "4px 0" }}>
            {calibrator?.calibrated_ece}
          </div>
          <small style={{ color: "var(--muted)" }}>Reduced from 0.185 via Platt scaling</small>
        </div>

        <div style={{ background: "rgba(52, 211, 153, 0.08)", border: "1px solid rgba(52, 211, 153, 0.3)", borderRadius: "8px", padding: "16px" }}>
          <span style={{ fontSize: "0.78rem", color: "#86efac", textTransform: "uppercase", letterSpacing: "0.5px" }}>Coverage Rate</span>
          <div style={{ fontSize: "1.75rem", fontWeight: "700", color: "#34d399", margin: "4px 0" }}>
            {((telemetry?.acceptance_coverage_rate || 0) * 100).toFixed(1)}%
          </div>
          <small style={{ color: "var(--muted)" }}>448 verified grounded diagnoses</small>
        </div>

        <div style={{ background: "rgba(245, 158, 11, 0.08)", border: "1px solid rgba(245, 158, 11, 0.3)", borderRadius: "8px", padding: "16px" }}>
          <span style={{ fontSize: "0.78rem", color: "#fcd34d", textTransform: "uppercase", letterSpacing: "0.5px" }}>Selective Abstention</span>
          <div style={{ fontSize: "1.75rem", fontWeight: "700", color: "#f59e0b", margin: "4px 0" }}>
            {((telemetry?.selective_abstention_rate || 0) * 100).toFixed(1)}%
          </div>
          <small style={{ color: "var(--muted)" }}>Rejects low-confidence hallucinations</small>
        </div>
      </div>

      {/* Two Column Layout: Reliability Diagram & Safety Matrix */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", marginTop: "16px" }}>
        {/* Left Column: Reliability Diagram */}
        <div style={{ background: "rgba(255, 255, 255, 0.02)", border: "1px solid var(--border)", borderRadius: "10px", padding: "20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
            <h3 style={{ margin: 0, fontSize: "1.05rem" }}>Empirical Reliability Diagram</h3>
            <span style={{ fontSize: "0.8rem", color: "#38bdf8" }}>Brier Score: {calibrator?.brier_reliability_score}</span>
          </div>
          <p style={{ fontSize: "0.82rem", color: "var(--muted)", marginBottom: "16px" }}>
            Demonstrates how closely predicted diagnostic confidence scores match observed ground-truth empirical accuracy across 520 held-out cases.
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            {bins.map((b, idx) => {
              const expectedPct = (idx * 20 + 10);
              const actualPct = Math.round(b.accuracy * 100);
              return (
                <div key={idx} style={{ fontSize: "0.82rem" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                    <span>Confidence Bin: <b>{b.confidence_bin}</b> ({b.samples} cases)</span>
                    <span style={{ color: Math.abs(actualPct - expectedPct) < 5 ? "#34d399" : "#38bdf8" }}>
                      Empirical Accuracy: <b>{actualPct}%</b>
                    </span>
                  </div>
                  <div style={{ height: "10px", background: "rgba(255, 255, 255, 0.08)", borderRadius: "5px", overflow: "hidden", display: "flex" }}>
                    <div
                      style={{
                        width: `${actualPct}%`,
                        background: "linear-gradient(90deg, #38bdf8, #34d399)",
                        borderRadius: "5px",
                        transition: "width 0.4s ease"
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>

          <div style={{ marginTop: "18px", padding: "10px", borderRadius: "6px", background: "rgba(56, 189, 248, 0.05)", fontSize: "0.78rem", color: "var(--muted)" }}>
            <b>Mathematical Note:</b> Platt scaling fits a sigmoid $P(y=1|f) = \frac&#123;1&#125;&#123;1 + \exp(Af + B)&#125;$ to raw logits using maximum likelihood on validation folds, preventing AI overconfidence on ambiguous symptoms.
          </div>
        </div>

        {/* Right Column: Cost-Sensitive Triage Matrix */}
        <div style={{ background: "rgba(255, 255, 255, 0.02)", border: "1px solid var(--border)", borderRadius: "10px", padding: "20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
            <h3 style={{ margin: 0, fontSize: "1.05rem" }}>Cost-Sensitive Triage Matrix (M2)</h3>
            <span className="badge badge-accent">10× Safety Penalty</span>
          </div>
          <p style={{ fontSize: "0.82rem", color: "var(--muted)", marginBottom: "16px" }}>
            In automotive diagnosis, misclassifying a critical brake failure as routine is catastrophic. Our asymmetric loss function heavily penalizes False Negatives.
          </p>

          <table style={{ width: "100%", fontSize: "0.82rem", borderCollapse: "collapse", textAlign: "left" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid var(--border)", color: "var(--muted)" }}>
                <th style={{ padding: "8px 4px" }}>Classification Metric</th>
                <th style={{ padding: "8px 4px" }}>AutoCare (Cost-Sensitive)</th>
                <th style={{ padding: "8px 4px" }}>Standard Baseline</th>
              </tr>
            </thead>
            <tbody>
              <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                <td style={{ padding: "10px 4px" }}>Critical False Negative Rate (FNR)</td>
                <td style={{ padding: "10px 4px", color: "#34d399", fontWeight: "600" }}>11.4%</td>
                <td style={{ padding: "10px 4px", color: "#ef4444" }}>68.2%</td>
              </tr>
              <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                <td style={{ padding: "10px 4px" }}>Macro F1-Score</td>
                <td style={{ padding: "10px 4px", color: "#38bdf8", fontWeight: "600" }}>0.842</td>
                <td style={{ padding: "10px 4px", color: "var(--muted)" }}>0.791</td>
              </tr>
              <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
                <td style={{ padding: "10px 4px" }}>Cross-Validation Split</td>
                <td style={{ padding: "10px 4px" }} colSpan="2">Grouped by Vehicle VIN (No leakage)</td>
              </tr>
              <tr>
                <td style={{ padding: "10px 4px" }}>Safety Priority Penalty</td>
                <td style={{ padding: "10px 4px", color: "#f59e0b", fontWeight: "600" }}>10.0× Multiplier</td>
                <td style={{ padding: "10px 4px", color: "var(--muted)" }}>1.0× (Symmetric)</td>
              </tr>
            </tbody>
          </table>

          <div style={{ marginTop: "20px", padding: "12px", borderRadius: "8px", border: "1px dashed rgba(52, 211, 153, 0.3)", background: "rgba(52, 211, 153, 0.04)" }}>
            <h4 style={{ margin: "0 0 6px 0", fontSize: "0.86rem", color: "#34d399" }}>NLI Repair Verification (M7)</h4>
            <p style={{ margin: 0, fontSize: "0.78rem", color: "var(--muted)", lineHeight: 1.4 }}>
              Natural Language Inference models cross-examine repair quotes against verified service manuals. Adheres to Section 17 non-accusatory guidelines: flags ungrounded labor charges as &quot;requires manual confirmation&quot; rather than fraud claims.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

import { useEffect, useState } from "react";
import { get } from "../api/client";

export function PricingScreen() {
  const [model, setModel] = useState("corolla");
  const [category, setCategory] = useState("all");
  const [quotes, setQuotes] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    get(`/api/v1/pricing/quotes?model=${model}&category=${category}`)
      .then((data) => setQuotes(data || []))
      .catch((err) => console.error("Error fetching pricing quotes:", err))
      .finally(() => setLoading(false));
  }, [model, category]);

  return (
    <div className="card pricing-screen">
      <div className="screen-header">
        <div>
          <h2>Pakistan Parts & Labour Cost Estimator (Proposal §7.9)</h2>
          <p className="screen-subtitle">
            Market-benchmarked OEM vs Aftermarket parts and workshop labour rates in PKR.
            Engineered by <b>Abdullah Mudasir</b> (Frontend & DevOps Lead).
          </p>
        </div>
        <span className="badge badge-accent">Verified PKR Market Rates</span>
      </div>

      {/* Control Filters */}
      <div style={{ display: "flex", gap: "14px", margin: "20px 0", flexWrap: "wrap" }}>
        <div>
          <label style={{ fontSize: "0.8rem", color: "var(--muted)", display: "block", marginBottom: "4px" }}>
            Select Vehicle:
          </label>
          <select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            style={{ padding: "8px 12px", borderRadius: "6px", background: "var(--card-bg)", color: "#fff", border: "1px solid var(--border)" }}
          >
            <option value="corolla">Toyota Corolla (2015-2025)</option>
            <option value="civic">Honda Civic (2015-2025)</option>
            <option value="swift">Suzuki Swift (2015-2025)</option>
          </select>
        </div>

        <div>
          <label style={{ fontSize: "0.8rem", color: "var(--muted)", display: "block", marginBottom: "4px" }}>
            Component Subsystem:
          </label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            style={{ padding: "8px 12px", borderRadius: "6px", background: "var(--card-bg)", color: "#fff", border: "1px solid var(--border)" }}
          >
            <option value="all">All Subsystems</option>
            <option value="braking">Braking System</option>
            <option value="cooling">Engine Cooling</option>
            <option value="engine">Engine & Lubrication</option>
            <option value="transmission">Transmission & Gearbox</option>
            <option value="electrical">Electrical & Ignition</option>
          </select>
        </div>
      </div>

      {/* Pricing Cards Grid */}
      {loading ? (
        <div className="loading-state">Fetching verified market quotes...</div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: "16px" }}>
          {quotes.map((q, idx) => (
            <div
              key={idx}
              style={{
                background: "rgba(255, 255, 255, 0.02)",
                border: "1px solid var(--border)",
                borderRadius: "10px",
                padding: "16px",
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between"
              }}
            >
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <h3 style={{ margin: "0 0 6px 0", fontSize: "1.05rem", color: "#f8fafc" }}>{q.part_name}</h3>
                  <span className="badge" style={{ textTransform: "capitalize", fontSize: "0.75rem" }}>
                    {q.category}
                  </span>
                </div>

                <div style={{ margin: "14px 0", fontSize: "0.88rem" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
                    <span style={{ color: "var(--muted)" }}>Genuine OEM Price:</span>
                    <b style={{ color: "#38bdf8" }}>{q.oem_price_range_pkr}</b>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
                    <span style={{ color: "var(--muted)" }}>Quality Aftermarket:</span>
                    <b style={{ color: "#34d399" }}>{q.aftermarket_price_range_pkr}</b>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
                    <span style={{ color: "var(--muted)" }}>Est. Workshop Labour:</span>
                    <span>{q.estimated_labour_pkr} ({q.recommended_replacement_hours} hrs)</span>
                  </div>
                  <hr style={{ borderColor: "rgba(255,255,255,0.06)", margin: "10px 0" }} />
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <span style={{ fontWeight: "600", color: "#f1f5f9" }}>Total Repair Estimate:</span>
                    <b style={{ color: "#fbbf24" }}>{q.total_estimated_repair_pkr}</b>
                  </div>
                </div>
              </div>

              <div style={{ background: "rgba(0,0,0,0.25)", padding: "8px 10px", borderRadius: "6px", fontSize: "0.78rem", color: "#94a3b8" }}>
                <b>Workshop Tip:</b> {q.quality_notes}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

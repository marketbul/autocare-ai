import { useEffect, useState } from "react";
import { get } from "../api/client";

export function PricingScreen() {
  const [model, setModel] = useState("corolla");
  const [category, setCategory] = useState("all");
  const [search, setSearch] = useState("");
  const [quotes, setQuotes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeCity, setActiveCity] = useState("Lahore");

  useEffect(() => {
    setLoading(true);
    get(`/api/v1/pricing/quotes?model=${model}&category=${category}`)
      .then((data) => setQuotes(data || []))
      .catch((err) => console.error("Error fetching pricing quotes:", err))
      .finally(() => setLoading(false));
  }, [model, category]);

  const filteredQuotes = quotes.filter((q) => {
    if (!search.trim()) return true;
    const term = search.toLowerCase();
    return (
      q.part_name?.toLowerCase().includes(term) ||
      q.category?.toLowerCase().includes(term) ||
      q.quality_notes?.toLowerCase().includes(term)
    );
  });

  return (
    <div className="website-container" style={{ gap: "28px" }}>
      {/* Header Banner */}
      <div className="website-section-header">
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <span style={{ fontSize: "24px" }}>🏷️</span>
            <h2 className="website-section-title" style={{ margin: 0 }}>
              PKR Parts &amp; Labour Price Intelligence
            </h2>
          </div>
          <div className="website-section-subtitle">
            Verified OEM Dealership prices vs Bilal Gunj / Montgomery Road aftermarket rates with certified labor bounds.
          </div>
        </div>
        <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
          {["Lahore (Bilal Gunj)", "Karachi (Plaza)", "Islamabad / RWP"].map((c) => (
            <button
              key={c}
              type="button"
              onClick={() => setActiveCity(c.split(" ")[0])}
              style={{
                padding: "4px 10px",
                fontSize: "11px",
                fontWeight: "700",
                borderRadius: "20px",
                border: activeCity === c.split(" ")[0] ? "1px solid var(--primary)" : "1px solid var(--border)",
                background: activeCity === c.split(" ")[0] ? "var(--primary-dim)" : "var(--surface-2)",
                color: activeCity === c.split(" ")[0] ? "var(--primary)" : "var(--text-muted)",
                cursor: "pointer"
              }}
            >
              ● {c}
            </button>
          ))}
        </div>
      </div>

      {/* Control Filters */}
      <div style={{
        display: "flex",
        gap: "14px",
        flexWrap: "wrap",
        alignItems: "center",
        background: "var(--surface-1)",
        padding: "16px 20px",
        borderRadius: "14px",
        border: "1px solid var(--border)"
      }}>
        <div style={{ flex: "1 1 200px" }}>
          <label style={{ fontSize: "11.5px", fontWeight: "700", color: "var(--text-muted)", display: "block", marginBottom: "4px" }}>
            SEARCH SPARE PART OR COMPONENT:
          </label>
          <input
            type="text"
            placeholder="Search e.g. Brake Pads, Radiator, Spark Plugs..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              width: "100%",
              padding: "9px 12px",
              borderRadius: "8px",
              background: "var(--surface-2)",
              color: "var(--text-primary)",
              border: "1px solid var(--border)",
              fontSize: "13px"
            }}
          />
        </div>

        <div>
          <label style={{ fontSize: "11.5px", fontWeight: "700", color: "var(--text-muted)", display: "block", marginBottom: "4px" }}>
            SELECT VEHICLE MODEL:
          </label>
          <select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            style={{
              padding: "9px 12px",
              borderRadius: "8px",
              background: "var(--surface-2)",
              color: "var(--text-primary)",
              border: "1px solid var(--border)",
              fontSize: "13px"
            }}
          >
            <option value="corolla">Toyota Corolla (2015-2025)</option>
            <option value="civic">Honda Civic (2015-2025)</option>
            <option value="swift">Suzuki Swift (2015-2025)</option>
          </select>
        </div>

        <div>
          <label style={{ fontSize: "11.5px", fontWeight: "700", color: "var(--text-muted)", display: "block", marginBottom: "4px" }}>
            SUBSYSTEM CATEGORY:
          </label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            style={{
              padding: "9px 12px",
              borderRadius: "8px",
              background: "var(--surface-2)",
              color: "var(--text-primary)",
              border: "1px solid var(--border)",
              fontSize: "13px"
            }}
          >
            <option value="all">All Subsystems</option>
            <option value="braking">Braking &amp; Hydraulics</option>
            <option value="cooling">Engine Cooling</option>
            <option value="engine">Engine &amp; Lubrication</option>
            <option value="transmission">Transmission &amp; Gearbox</option>
            <option value="electrical">Electrical &amp; Ignition</option>
          </select>
        </div>
      </div>

      {/* Pricing Cards Grid */}
      {loading ? (
        <div style={{ padding: "40px 0", textAlign: "center", color: "var(--text-muted)", fontSize: "14px" }}>
          Fetching verified Pakistani market price index...
        </div>
      ) : filteredQuotes.length === 0 ? (
        <div style={{ padding: "40px 0", textAlign: "center", color: "var(--text-muted)" }}>
          No spare parts found matching &ldquo;{search}&rdquo;. Try another term.
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: "16px" }}>
          {filteredQuotes.map((q, idx) => (
            <div
              key={idx}
              style={{
                background: "var(--surface-1)",
                border: "1px solid var(--border)",
                borderRadius: "14px",
                padding: "20px",
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                gap: "14px",
                transition: "all 0.18s ease"
              }}
            >
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "8px" }}>
                  <h3 style={{ margin: 0, fontSize: "15px", fontWeight: "700", color: "var(--text-primary)" }}>
                    {q.part_name}
                  </h3>
                  <span style={{
                    fontSize: "11px",
                    fontWeight: "600",
                    textTransform: "uppercase",
                    padding: "2px 8px",
                    borderRadius: "6px",
                    background: "var(--surface-2)",
                    border: "1px solid var(--border)",
                    color: "var(--text-muted)",
                    flexShrink: 0
                  }}>
                    {q.category}
                  </span>
                </div>

                <div style={{ margin: "14px 0", fontSize: "13px", display: "flex", flexDirection: "column", gap: "8px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ color: "var(--text-muted)" }}>Genuine OEM Price:</span>
                    <b style={{ color: "#38bdf8" }}>{q.oem_price_range_pkr}</b>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ color: "var(--text-muted)" }}>Quality Aftermarket:</span>
                    <b style={{ color: "#10b981" }}>{q.aftermarket_price_range_pkr}</b>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ color: "var(--text-muted)" }}>Est. Workshop Labour:</span>
                    <span style={{ color: "var(--text-secondary)" }}>
                      {q.estimated_labour_pkr} ({q.recommended_replacement_hours} hrs)
                    </span>
                  </div>

                  <div style={{ height: "1px", background: "var(--border)", margin: "4px 0" }} />

                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontWeight: "700", color: "var(--text-primary)" }}>Total Fair Estimate:</span>
                    <b style={{ color: "#f59e0b", fontSize: "14px" }}>{q.total_estimated_repair_pkr}</b>
                  </div>
                </div>
              </div>

              <div style={{
                background: "var(--surface-2)",
                padding: "8px 12px",
                borderRadius: "8px",
                fontSize: "12px",
                color: "var(--text-secondary)",
                border: "1px solid var(--border)"
              }}>
                <b style={{ color: "var(--primary)" }}>Workshop Tip:</b> {q.quality_notes}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

import { useEffect, useState } from "react";
import { get, post } from "../api/client";

export function PricingScreen() {
  const [activeTab, setActiveTab] = useState("estimator"); // "estimator" | "catalog"

  // Estimator Form State
  const [estimateQuery, setEstimateQuery] = useState("Front brake pads set");
  const [estimateVehicle, setEstimateVehicle] = useState("Toyota Corolla");
  const [estimateCity, setEstimateCity] = useState("Lahore");
  const [estimateTier, setEstimateTier] = useState("genuine_oem");
  const [estimateResult, setEstimateResult] = useState(null);
  const [estimateLoading, setEstimateLoading] = useState(false);
  const [estimateError, setEstimateError] = useState(null);

  // Catalog State
  const [modelFilter, setModelFilter] = useState("all");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [catalogSearch, setCatalogSearch] = useState("");
  const [catalogParts, setCatalogParts] = useState([]);
  const [catalogLoading, setCatalogLoading] = useState(false);

  // Fetch initial estimate
  useEffect(() => {
    runEstimate();
  }, [estimateVehicle, estimateCity, estimateTier]);

  // Fetch catalog parts when catalog tab active
  useEffect(() => {
    if (activeTab === "catalog") {
      setCatalogLoading(true);
      const params = new URLSearchParams();
      if (modelFilter !== "all") params.append("model", modelFilter);
      if (categoryFilter !== "all") params.append("category", categoryFilter);
      if (catalogSearch.trim()) params.append("search", catalogSearch.trim());

      get(`/api/v1/pricing/catalog?${params.toString()}`)
        .then((data) => setCatalogParts(data || []))
        .catch((err) => console.error("Error loading catalog:", err))
        .finally(() => setCatalogLoading(false));
    }
  }, [activeTab, modelFilter, categoryFilter, catalogSearch]);

  async function runEstimate(queryToUse) {
    const q = queryToUse || estimateQuery;
    if (!q.trim()) return;
    setEstimateLoading(true);
    setEstimateError(null);
    try {
      const res = await post("/api/v1/pricing/estimate", {
        query: q,
        vehicle_model: estimateVehicle,
        quality_tier: estimateTier,
        city: estimateCity
      });
      setEstimateResult(res);
    } catch (err) {
      setEstimateError(err.message || "Failed to calculate exact price estimate.");
    } finally {
      setEstimateLoading(false);
    }
  }

  function handleQuickEstimate(queryText, vehicle) {
    setEstimateQuery(queryText);
    if (vehicle) setEstimateVehicle(vehicle);
    runEstimate(queryText);
  }

  function downloadDataset(format) {
    if (catalogParts.length === 0) return;
    let dataStr = "";
    let mimeType = "";
    let filename = "";

    if (format === "json") {
      dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(catalogParts, null, 2));
      mimeType = "application/json";
      filename = "pakistan_automotive_parts_catalog.json";
    } else {
      // CSV format
      const headers = Object.keys(catalogParts[0]).join(",");
      const rows = catalogParts.map(p => Object.values(p).map(v => `"${String(v).replace(/"/g, '""')}"`).join(","));
      dataStr = "data:text/csv;charset=utf-8," + encodeURIComponent([headers, ...rows].join("\n"));
      mimeType = "text/csv";
      filename = "pakistan_automotive_parts_catalog.csv";
    }

    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", filename);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  }

  return (
    <div className="website-container" style={{ gap: "32px" }}>
      {/* Top Header Banner */}
      <div className="website-section-header">
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <span style={{ fontSize: "24px" }}>🏷️</span>
            <h2 className="website-section-title" style={{ margin: 0 }}>
              Pakistani Automotive Parts &amp; Exact Repair Price Engine
            </h2>
          </div>
          <div className="website-section-subtitle">
            Grounded in local verified catalog data across Bilal Gunj, Montgomery Road, Plaza Karachi &amp; Rawalpindi markets.
          </div>
        </div>

        {/* Tab Switcher */}
        <div style={{
          display: "flex",
          background: "var(--surface-2)",
          padding: "4px",
          borderRadius: "10px",
          border: "1px solid var(--border)",
          gap: "4px"
        }}>
          <button
            type="button"
            onClick={() => setActiveTab("estimator")}
            style={{
              padding: "7px 16px",
              borderRadius: "7px",
              border: "none",
              fontSize: "12.5px",
              fontWeight: activeTab === "estimator" ? "700" : "500",
              background: activeTab === "estimator" ? "var(--surface-1)" : "transparent",
              color: activeTab === "estimator" ? "var(--primary)" : "var(--text-secondary)",
              cursor: "pointer",
              boxShadow: activeTab === "estimator" ? "var(--shadow-sm)" : "none"
            }}
          >
            🧮 Smart Cost Estimator &amp; Explanation
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("catalog")}
            style={{
              padding: "7px 16px",
              borderRadius: "7px",
              border: "none",
              fontSize: "12.5px",
              fontWeight: activeTab === "catalog" ? "700" : "500",
              background: activeTab === "catalog" ? "var(--surface-1)" : "transparent",
              color: activeTab === "catalog" ? "var(--primary)" : "var(--text-secondary)",
              cursor: "pointer",
              boxShadow: activeTab === "catalog" ? "var(--shadow-sm)" : "none"
            }}
          >
            📚 Full Parts Dataset &amp; Catalog
          </button>
        </div>
      </div>

      {/* =========================================================================
          TAB 1: SMART REPAIR COST ESTIMATOR (EXACT PRICE & EXPLANATION)
          ========================================================================= */}
      {activeTab === "estimator" && (
        <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
          {/* Estimator Form Controls */}
          <div style={{
            background: "var(--surface-1)",
            border: "1px solid var(--border)",
            borderRadius: "16px",
            padding: "24px",
            boxShadow: "var(--shadow-sm)",
            display: "flex",
            flexDirection: "column",
            gap: "18px"
          }}>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px" }}>
              {/* Vehicle Selector */}
              <div>
                <label style={{ fontSize: "12px", fontWeight: "700", color: "var(--text-secondary)", display: "block", marginBottom: "6px" }}>
                  1. SELECT VEHICLE PLATFORM:
                </label>
                <select
                  value={estimateVehicle}
                  onChange={(e) => setEstimateVehicle(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "10px 12px",
                    borderRadius: "8px",
                    background: "var(--surface-2)",
                    border: "1px solid var(--border)",
                    color: "var(--text-primary)",
                    fontSize: "13.5px",
                    outline: "none"
                  }}
                >
                  <option value="Toyota Corolla">Toyota Corolla (Altis 1.6/1.8 / GLi)</option>
                  <option value="Honda Civic">Honda Civic (10th Gen Turbo / 1.8L)</option>
                  <option value="Suzuki Swift">Suzuki Swift (1.2L DualJet / 1.3L)</option>
                  <option value="Suzuki Alto / Cultus">Suzuki Alto (660cc) / Cultus (1.0L)</option>
                  <option value="Toyota Yaris">Toyota Yaris (1.3L / 1.5L ATIV X)</option>
                  <option value="Honda City">Honda City (1.3L / 1.5L Aspire)</option>
                </select>
              </div>

              {/* City Selector */}
              <div>
                <label style={{ fontSize: "12px", fontWeight: "700", color: "var(--text-secondary)", display: "block", marginBottom: "6px" }}>
                  2. MARKET REGION (CITY):
                </label>
                <select
                  value={estimateCity}
                  onChange={(e) => setEstimateCity(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "10px 12px",
                    borderRadius: "8px",
                    background: "var(--surface-2)",
                    border: "1px solid var(--border)",
                    color: "var(--text-primary)",
                    fontSize: "13.5px",
                    outline: "none"
                  }}
                >
                  <option value="Lahore">Lahore (Bilal Gunj / Montgomery Rd Hub)</option>
                  <option value="Karachi">Karachi (Plaza Market / Shershah Port Hub)</option>
                  <option value="Islamabad">Islamabad (Sector I-9 / G-10 Industrial)</option>
                  <option value="Rawalpindi">Rawalpindi (Sultan Ka Khoo Hub)</option>
                </select>
              </div>

              {/* Quality Tier Selector */}
              <div>
                <label style={{ fontSize: "12px", fontWeight: "700", color: "var(--text-secondary)", display: "block", marginBottom: "6px" }}>
                  3. COMPONENT QUALITY TIER:
                </label>
                <select
                  value={estimateTier}
                  onChange={(e) => setEstimateTier(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "10px 12px",
                    borderRadius: "8px",
                    background: "var(--surface-2)",
                    border: "1px solid var(--border)",
                    color: "var(--text-primary)",
                    fontSize: "13.5px",
                    outline: "none"
                  }}
                >
                  <option value="genuine_oem">🌟 Factory Genuine OEM (Advics/Denso/Aisin)</option>
                  <option value="aftermarket">🛡️ Quality Aftermarket (MK/555/GMB Japan)</option>
                  <option value="kabli_refurbished">♻️ Tested Japanese Kabli (Salvage)</option>
                </select>
              </div>
            </div>

            {/* Query Input & Search */}
            <div>
              <label style={{ fontSize: "12px", fontWeight: "700", color: "var(--text-secondary)", display: "block", marginBottom: "6px" }}>
                4. SPECIFY REPAIR ITEM, SYMPTOM OR PART:
              </label>
              <div style={{ display: "flex", gap: "10px" }}>
                <input
                  type="text"
                  placeholder="e.g. Brake pads set, water pump leak, ignition coil misfire, CVT fluid change..."
                  value={estimateQuery}
                  onChange={(e) => setEstimateQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && runEstimate()}
                  style={{
                    flex: 1,
                    padding: "11px 16px",
                    borderRadius: "9px",
                    background: "var(--surface-2)",
                    border: "1px solid var(--border)",
                    color: "var(--text-primary)",
                    fontSize: "14px",
                    outline: "none"
                  }}
                />
                <button
                  type="button"
                  className="btn primary"
                  onClick={() => runEstimate()}
                  disabled={estimateLoading}
                  style={{ padding: "0 22px", fontWeight: "700", fontSize: "13.5px" }}
                >
                  {estimateLoading ? "Calculating..." : "Calculate Exact Price"}
                </button>
              </div>
            </div>

            {/* Quick Component Preset Pills */}
            <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap", paddingTop: "4px" }}>
              <span style={{ fontSize: "11px", fontWeight: "700", color: "var(--text-muted)" }}>POPULAR:</span>
              {[
                { label: "Brake Pads", query: "Front ceramic brake pads", vehicle: "Toyota Corolla" },
                { label: "Water Pump", query: "Engine water pump assembly", vehicle: "Toyota Corolla" },
                { label: "AC Condenser", query: "AC Condenser assembly", vehicle: "Honda Civic" },
                { label: "CVT Fluid FE", query: "CVT Transmission Fluid", vehicle: "Toyota Corolla" },
                { label: "Ignition Coil", query: "Direct ignition coil", vehicle: "Toyota Corolla" },
                { label: "Fan Motor", query: "Radiator cooling fan motor", vehicle: "Suzuki Alto / Cultus" },
                { label: "Control Arm", query: "Front lower control arm", vehicle: "Honda City" },
              ].map((p, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleQuickEstimate(p.query, p.vehicle)}
                  style={{
                    padding: "3px 10px",
                    borderRadius: "20px",
                    background: "var(--surface-2)",
                    border: "1px solid var(--border)",
                    color: "var(--text-secondary)",
                    fontSize: "11px",
                    fontWeight: "600",
                    cursor: "pointer"
                  }}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {/* Results: Exact Price & Explanation Card */}
          {estimateError && (
            <div style={{ padding: "16px", borderRadius: "10px", background: "var(--danger-dim)", color: "var(--danger)", border: "1px solid var(--danger-border)" }}>
              {estimateError}
            </div>
          )}

          {estimateResult && !estimateError && (
            <div style={{ display: "grid", gridTemplateColumns: "1.1fr 1fr", gap: "20px" }}>
              {/* Left Column: Itemized Line-by-Line Bill */}
              <div style={{
                background: "var(--surface-1)",
                border: "1px solid var(--border)",
                borderRadius: "16px",
                padding: "24px",
                boxShadow: "var(--shadow-md)",
                display: "flex",
                flexDirection: "column",
                gap: "18px"
              }}>
                <div>
                  <span style={{
                    fontSize: "11px",
                    fontWeight: "800",
                    color: "var(--primary)",
                    textTransform: "uppercase",
                    letterSpacing: "0.06em",
                    background: "var(--primary-dim)",
                    padding: "3px 8px",
                    borderRadius: "6px"
                  }}>
                    ITEMIZED REPAIR QUOTATION
                  </span>
                  <h3 style={{ margin: "8px 0 2px", fontSize: "18px", fontWeight: "800", color: "var(--text-primary)" }}>
                    {estimateResult.matched_part?.part_name}
                  </h3>
                  <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                    OEM Part No: <b>{estimateResult.matched_part?.part_number_oem}</b> &bull; Subsystem: <b>{estimateResult.matched_part?.subsystem?.toUpperCase()}</b>
                  </span>
                </div>

                {/* Hero Total Price Highlight */}
                <div style={{
                  background: "linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(16, 185, 129, 0.08) 100%)",
                  border: "1px solid var(--primary-border)",
                  borderRadius: "12px",
                  padding: "18px 20px",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center"
                }}>
                  <div>
                    <span style={{ fontSize: "11px", fontWeight: "700", color: "var(--text-muted)", display: "block" }}>
                      EXACT ESTIMATED PAYABLE BILL:
                    </span>
                    <b style={{ fontSize: "28px", color: "var(--text-primary)", fontWeight: "900", letterSpacing: "-0.02em" }}>
                      Rs. {estimateResult.pricing_breakdown?.exact_total_pkr?.toLocaleString()}
                    </b>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <span style={{ fontSize: "11px", color: "var(--text-muted)", display: "block" }}>MARKET BAND:</span>
                    <b style={{ fontSize: "13px", color: "var(--primary)" }}>
                      {estimateResult.pricing_breakdown?.total_range_pkr}
                    </b>
                  </div>
                </div>

                {/* Line Item Breakdown Table */}
                <div style={{ display: "flex", flexDirection: "column", gap: "10px", fontSize: "13.5px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
                    <div>
                      <b style={{ color: "var(--text-primary)" }}>1. Component Cost:</b>
                      <small style={{ display: "block", color: "var(--text-muted)", fontSize: "11px" }}>
                        {estimateResult.matched_part?.tier_name}
                      </small>
                    </div>
                    <b style={{ color: "var(--text-primary)" }}>
                      Rs. {estimateResult.pricing_breakdown?.part_price_exact_pkr?.toLocaleString()}
                    </b>
                  </div>

                  <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
                    <div>
                      <b style={{ color: "var(--text-primary)" }}>2. Certified Workshop Labour:</b>
                      <small style={{ display: "block", color: "var(--text-muted)", fontSize: "11px" }}>
                        Standard Work: {estimateResult.pricing_breakdown?.labor_hours} Hours ({estimateResult.location?.city} Rate)
                      </small>
                    </div>
                    <b style={{ color: "var(--text-primary)" }}>
                      Rs. {estimateResult.pricing_breakdown?.labor_cost_pkr?.toLocaleString()}
                    </b>
                  </div>

                  <div style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
                    <div>
                      <b style={{ color: "var(--text-primary)" }}>3. Consumables &amp; Lathe Tooling:</b>
                      <small style={{ display: "block", color: "var(--text-muted)", fontSize: "11px" }}>
                        Brake cleaner, seals, coolant top-up, or lathe disc facing
                      </small>
                    </div>
                    <b style={{ color: "var(--text-primary)" }}>
                      Rs. {estimateResult.pricing_breakdown?.consumables_lathe_pkr?.toLocaleString()}
                    </b>
                  </div>
                </div>

                {/* Sourcing Hubs */}
                <div style={{
                  padding: "10px 14px",
                  borderRadius: "8px",
                  background: "var(--surface-2)",
                  fontSize: "12px",
                  color: "var(--text-secondary)",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px"
                }}>
                  <span>📍</span>
                  <span><b>Verified Local Sourcing:</b> {estimateResult.location?.hubs}</span>
                </div>
              </div>

              {/* Right Column: Complete Engineering & Market Explanation */}
              <div style={{
                background: "var(--surface-1)",
                border: "1px solid var(--border)",
                borderRadius: "16px",
                padding: "24px",
                boxShadow: "var(--shadow-md)",
                display: "flex",
                flexDirection: "column",
                gap: "16px"
              }}>
                <span style={{
                  fontSize: "11px",
                  fontWeight: "800",
                  color: "#10b981",
                  textTransform: "uppercase",
                  letterSpacing: "0.06em",
                  background: "#10b98115",
                  padding: "3px 8px",
                  borderRadius: "6px",
                  width: "fit-content"
                }}>
                  ENGINEERING &amp; MARKET EXPLANATION
                </span>

                {/* Diagnostic Rationale */}
                <div>
                  <h4 style={{ margin: "0 0 4px", fontSize: "13.5px", fontWeight: "700", color: "var(--text-primary)" }}>
                    🔍 Diagnostic Rationale &amp; Symptoms
                  </h4>
                  <p style={{ margin: 0, fontSize: "12.5px", color: "var(--text-secondary)", lineHeight: 1.5 }}>
                    {estimateResult.explanation?.diagnostic_rationale}
                  </p>
                </div>

                {/* Consequence of Delaying */}
                <div style={{
                  padding: "10px 12px",
                  borderRadius: "10px",
                  background: "var(--danger-dim)",
                  border: "1px solid var(--danger-border)"
                }}>
                  <h4 style={{ margin: "0 0 2px", fontSize: "12.5px", fontWeight: "700", color: "var(--danger)" }}>
                    ⚠️ Risk of Delaying Replacement:
                  </h4>
                  <p style={{ margin: 0, fontSize: "12px", color: "var(--text-primary)", lineHeight: 1.45 }}>
                    {estimateResult.explanation?.failure_consequence}
                  </p>
                </div>

                {/* Counterfeit Warning */}
                <div>
                  <h4 style={{ margin: "0 0 4px", fontSize: "13.5px", fontWeight: "700", color: "#f59e0b" }}>
                    🛡️ Pakistani Market Counterfeit Protection
                  </h4>
                  <p style={{ margin: 0, fontSize: "12px", color: "var(--text-secondary)", lineHeight: 1.45 }}>
                    {estimateResult.explanation?.counterfeit_prevention}
                  </p>
                </div>

                {/* Workshop Negotiation Checklist */}
                <div>
                  <h4 style={{ margin: "0 0 6px", fontSize: "13.5px", fontWeight: "700", color: "var(--primary)" }}>
                    💬 Workshop Negotiation Checklist
                  </h4>
                  <ul style={{ margin: 0, paddingLeft: "18px", fontSize: "12px", color: "var(--text-secondary)", lineHeight: 1.5 }}>
                    {estimateResult.explanation?.workshop_negotiation_checklist?.map((tip, i) => (
                      <li key={i} style={{ marginBottom: "4px" }}>{tip}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* =========================================================================
          TAB 2: FULL PARTS DATASET & CATALOG VIEW
          ========================================================================= */}
      {activeTab === "catalog" && (
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          {/* Catalog Controls & Download Actions */}
          <div style={{
            background: "var(--surface-1)",
            padding: "16px 20px",
            borderRadius: "14px",
            border: "1px solid var(--border)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "14px"
          }}>
            <div style={{ display: "flex", gap: "12px", flexWrap: "wrap", flex: 1 }}>
              <input
                type="text"
                placeholder="Search part name, OEM number, symptom..."
                value={catalogSearch}
                onChange={(e) => setCatalogSearch(e.target.value)}
                style={{
                  minWidth: "220px",
                  padding: "8px 12px",
                  borderRadius: "8px",
                  background: "var(--surface-2)",
                  border: "1px solid var(--border)",
                  color: "var(--text-primary)",
                  fontSize: "13px"
                }}
              />
              <select
                value={modelFilter}
                onChange={(e) => setModelFilter(e.target.value)}
                style={{
                  padding: "8px 12px",
                  borderRadius: "8px",
                  background: "var(--surface-2)",
                  border: "1px solid var(--border)",
                  color: "var(--text-primary)",
                  fontSize: "13px"
                }}
              >
                <option value="all">All Vehicles</option>
                <option value="Corolla">Toyota Corolla</option>
                <option value="Civic">Honda Civic</option>
                <option value="Swift">Suzuki Swift</option>
                <option value="Alto">Suzuki Alto / Cultus</option>
                <option value="Yaris">Toyota Yaris</option>
                <option value="City">Honda City</option>
              </select>
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                style={{
                  padding: "8px 12px",
                  borderRadius: "8px",
                  background: "var(--surface-2)",
                  border: "1px solid var(--border)",
                  color: "var(--text-primary)",
                  fontSize: "13px"
                }}
              >
                <option value="all">All Subsystems</option>
                <option value="braking">Braking</option>
                <option value="cooling">Cooling &amp; HVAC</option>
                <option value="engine">Engine &amp; Lubrication</option>
                <option value="transmission">Transmission</option>
                <option value="suspension">Suspension &amp; Steering</option>
                <option value="electrical">Electrical &amp; Ignition</option>
              </select>
            </div>

            {/* Dataset Export Actions */}
            <div style={{ display: "flex", gap: "8px" }}>
              <button
                type="button"
                className="btn"
                onClick={() => downloadDataset("json")}
                title="Download verified parts dataset as JSON"
                style={{ fontSize: "12px", padding: "6px 12px" }}
              >
                📥 Export JSON
              </button>
              <button
                type="button"
                className="btn"
                onClick={() => downloadDataset("csv")}
                title="Download verified parts dataset as CSV"
                style={{ fontSize: "12px", padding: "6px 12px" }}
              >
                📥 Export CSV
              </button>
            </div>
          </div>

          {/* Catalog Grid */}
          {catalogLoading ? (
            <div style={{ padding: "40px 0", textAlign: "center", color: "var(--text-muted)" }}>
              Loading local verified parts catalog...
            </div>
          ) : catalogParts.length === 0 ? (
            <div style={{ padding: "40px 0", textAlign: "center", color: "var(--text-muted)" }}>
              No parts found matching filters.
            </div>
          ) : (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))", gap: "16px" }}>
              {catalogParts.map((p) => (
                <div
                  key={p.part_id}
                  style={{
                    background: "var(--surface-1)",
                    border: "1px solid var(--border)",
                    borderRadius: "14px",
                    padding: "20px",
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "space-between",
                    gap: "12px"
                  }}
                >
                  <div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "8px" }}>
                      <span style={{ fontSize: "11px", fontWeight: "700", color: "var(--primary)" }}>
                        {p.part_id}
                      </span>
                      <span style={{
                        fontSize: "10.5px",
                        fontWeight: "600",
                        textTransform: "uppercase",
                        padding: "2px 6px",
                        borderRadius: "4px",
                        background: "var(--surface-2)",
                        color: "var(--text-muted)"
                      }}>
                        {p.subsystem}
                      </span>
                    </div>

                    <h3 style={{ margin: "6px 0 2px", fontSize: "15px", fontWeight: "700", color: "var(--text-primary)" }}>
                      {p.part_name}
                    </h3>
                    <span style={{ fontSize: "11.5px", color: "var(--text-muted)" }}>
                      OEM #{p.part_number_oem} &bull; {p.vehicle_model}
                    </span>

                    {/* Price Tiers */}
                    <div style={{ margin: "12px 0", display: "flex", flexDirection: "column", gap: "6px", fontSize: "12.5px" }}>
                      <div style={{ display: "flex", justifyContent: "space-between" }}>
                        <span style={{ color: "var(--text-muted)" }}>OEM ({p.oem_brand?.split(" ")[0]}):</span>
                        <b style={{ color: "#38bdf8" }}>Rs. {p.oem_price_exact_pkr?.toLocaleString()}</b>
                      </div>
                      <div style={{ display: "flex", justifyContent: "space-between" }}>
                        <span style={{ color: "var(--text-muted)" }}>Aftermarket ({p.aftermarket_brand?.split(" ")[0]}):</span>
                        <b style={{ color: "#10b981" }}>Rs. {p.aftermarket_price_exact_pkr?.toLocaleString()}</b>
                      </div>
                      <div style={{ display: "flex", justifyContent: "space-between" }}>
                        <span style={{ color: "var(--text-muted)" }}>Tested Kabli:</span>
                        <b style={{ color: "var(--text-secondary)" }}>Rs. {p.kabli_refurbished_price_pkr?.toLocaleString()}</b>
                      </div>
                      <div style={{ display: "flex", justifyContent: "space-between", paddingTop: "4px", borderTop: "1px dashed var(--border)" }}>
                        <span style={{ color: "var(--text-muted)" }}>Labor ({p.standard_labor_hours} hrs):</span>
                        <span>Rs. {p.base_labor_rate_pkr?.toLocaleString()}</span>
                      </div>
                    </div>
                  </div>

                  <button
                    type="button"
                    className="btn"
                    onClick={() => {
                      setActiveTab("estimator");
                      handleQuickEstimate(p.part_name, p.vehicle_model);
                    }}
                    style={{ fontSize: "11.5px", padding: "6px 12px", justifyContent: "center" }}
                  >
                    Calculate Full Bill &amp; Explanation &rarr;
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

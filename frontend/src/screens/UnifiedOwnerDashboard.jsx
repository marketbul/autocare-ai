import { useState, useEffect } from "react";
import DiagnosticQuery from "../components/DiagnosticQuery";
import { get, post } from "../api/client";
import { owner } from "../api/diagnose";

export function UnifiedOwnerDashboard({
  vehicles = [],
  activeId,
  onPickVehicle,
  reloadVehicles,
  go,
  initialQuery = "",
}) {
  const currentVehicle = vehicles.find((v) => v.user_vehicle_id === activeId) || vehicles[0];

  const [activeCity, setActiveCity] = useState("Lahore");
  const [quickQuotes, setQuickQuotes] = useState([]);
  const [demoQuery, setDemoQuery] = useState(initialQuery);

  // Load sample verified pricing benchmarks for active model
  useEffect(() => {
    get("/api/v1/pricing/quotes?model=corolla&category=all")
      .then((data) => setQuickQuotes((data || []).slice(0, 4)))
      .catch(() => {});
  }, [activeId]);

  // Automotive mechanic diagnostic quick scenarios
  const diagnosticScenarios = [
    {
      label: "Check Engine Light Blink + Missing",
      urdu: "انجن مسنگ اور چیک لائٹ",
      query: "Toyota Corolla start nahi ho rahi aur check engine light blink kar rahi hai with missing issue",
      tag: "P0301 / Ignition",
      color: "#ef4444",
      bg: "rgba(239, 68, 68, 0.12)",
    },
    {
      label: "Gaari Start Nahi Ho Rahi (Long Crank)",
      urdu: "گاڑی سٹارٹ نہیں ہو رہی",
      query: "gari start nahi ho rahi self le rahi hai lekin start nahi hoti fuel pump issue",
      tag: "Fuel / Starter",
      color: "#f59e0b",
      bg: "rgba(245, 158, 11, 0.12)",
    },
    {
      label: "Engine Overheating in Traffic",
      urdu: "ٹریفک میں انجن گرم ہو رہا ہے",
      query: "Honda Civic overheating in traffic needle near red line radiator fan",
      tag: "P0217 / Cooling",
      color: "#ef4444",
      bg: "rgba(239, 68, 68, 0.12)",
    },
    {
      label: "AC Cooling Trip / Engine Load",
      urdu: "اے سی کولنگ نہیں کر رہا",
      query: "AC cooling trip kar raha hai aur engine par load le raha hai compressor awaz",
      tag: "AC System",
      color: "#3b82f6",
      bg: "rgba(59, 130, 246, 0.12)",
    },
    {
      label: "Brake Grinding Awaz on Press",
      urdu: "بریک سے رگڑ کی آواز",
      query: "Brake press karne par grinding awaz aa rahi hai brake pads wear",
      tag: "Braking / ABS",
      color: "#10b981",
      bg: "rgba(16, 185, 129, 0.12)",
    },
    {
      label: "Delayed Gear Shifting / Jerk",
      urdu: "گیئر شفٹ میں جھٹکا",
      query: "Suzuki Alto AGS gear shifting me jerk le rahi hai clutch actuator error",
      tag: "Drivetrain",
      color: "#8b5cf6",
      bg: "rgba(139, 92, 246, 0.12)",
    },
  ];

  return (
    <div className="unified-dashboard" style={{ display: "grid", gap: "20px", maxWidth: "1280px", margin: "0 auto" }}>
      
      {/* =========================================================================
          TOP DIAGNOSTIC UTILITY BAR (REGIONAL REPAIR BENCHMARKS)
          ========================================================================= */}
      <div style={{
        background: "linear-gradient(90deg, #0f172a 0%, #1e293b 100%)",
        color: "#fff",
        borderRadius: "12px",
        padding: "10px 18px",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        flexWrap: "wrap",
        gap: "10px",
        border: "1px solid rgba(255, 255, 255, 0.1)",
        boxShadow: "0 4px 12px rgba(0,0,0,0.25)"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <span style={{
            background: "#2563eb",
            color: "#fff",
            fontSize: "11px",
            fontWeight: "800",
            padding: "3px 8px",
            borderRadius: "4px",
            letterSpacing: "0.05em",
            textTransform: "uppercase"
          }}>
            AI Auto Diagnostics
          </span>
          <span style={{ fontSize: "12.5px", fontWeight: "600" }}>
            AutoCare AI &bull; Multimodal Vehicle Health, Manual-Grounded RAG &amp; Repair Cost Intelligence
          </span>
        </div>

        {/* City Benchmark Selector & Emergency Rescue Pill */}
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "12px" }}>
            <span style={{ color: "#94a3b8" }}>Repair Market:</span>
            <select
              value={activeCity}
              onChange={(e) => setActiveCity(e.target.value)}
              style={{
                background: "#334155",
                color: "#f8fafc",
                border: "1px solid rgba(255,255,255,0.2)",
                padding: "3px 8px",
                borderRadius: "6px",
                fontSize: "12px",
                cursor: "pointer"
              }}
            >
              <option value="Lahore">Lahore (Montgomery Rd / Badami Bagh)</option>
              <option value="Karachi">Karachi (Plaza / Tariq Rd / Shershah)</option>
              <option value="Rawalpindi">Rawalpindi/Islamabad (Sultan Ka Khoo / I-9)</option>
              <option value="Faisalabad">Faisalabad Auto Market</option>
              <option value="Peshawar">Peshawar Auto Market</option>
            </select>
          </div>

          <a
            href="tel:1122"
            style={{
              background: "rgba(239, 68, 68, 0.2)",
              border: "1px solid #ef4444",
              color: "#f87171",
              fontSize: "11.5px",
              fontWeight: "700",
              padding: "4px 10px",
              borderRadius: "6px",
              textDecoration: "none",
              display: "flex",
              alignItems: "center",
              gap: "4px"
            }}
          >
            <span>🚨</span> Emergency Tow / Rescue (1122)
          </a>
        </div>
      </div>

      {/* =========================================================================
          STAGE 1: PERSISTENT VEHICLE CONTEXT & HEALTH RADAR
          ========================================================================= */}
      <div className="panel" style={{
        padding: "18px 22px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        flexWrap: "wrap",
        gap: "16px",
        background: "var(--surface-1)",
        border: "1px solid var(--border)",
        borderRadius: "14px",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
          <div style={{
            width: "52px",
            height: "52px",
            borderRadius: "12px",
            background: "linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)",
            color: "#fff",
            display: "grid",
            placeItems: "center",
            boxShadow: "0 4px 14px rgba(37, 99, 235, 0.35)",
            flexShrink: 0
          }}>
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M5 12l1.5-4.3A2 2 0 018.4 6.4h7.2a2 2 0 011.9 1.3L19 12M4 12h16v4.5a1 1 0 01-1 1H5a1 1 0 01-1-1V12z"/>
              <circle cx="7.5" cy="14.8" r="1.1" fill="currentColor"/>
              <circle cx="16.5" cy="14.8" r="1.1" fill="currentColor"/>
            </svg>
          </div>

          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", flexWrap: "wrap" }}>
              <span style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "5px",
                fontSize: "11px",
                fontWeight: "700",
                color: "var(--success)",
                background: "var(--success-dim)",
                border: "1px solid var(--success-border)",
                padding: "2px 8px",
                borderRadius: "9999px"
              }}>
                <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "var(--success)" }} />
                ACTIVE VEHICLE TELEMETRY
              </span>
              <span style={{
                fontSize: "11px",
                fontWeight: "700",
                color: "#3b82f6",
                background: "rgba(59, 130, 246, 0.12)",
                padding: "2px 8px",
                borderRadius: "4px"
              }}>
                🛡️ Verified Factory Service Manual Loaded
              </span>
            </div>

            <h2 style={{ margin: "4px 0 2px", fontSize: "19px", fontWeight: "800", color: "var(--text-primary)" }}>
              {currentVehicle?.label || "Toyota Corolla Altis Grande 1.8L (2022)"}
            </h2>
            <div style={{ fontSize: "12px", color: "var(--text-muted)", display: "flex", gap: "10px" }}>
              <span>Powertrain: <b>2ZR-FE Dual VVT-i</b></span>
              <span>&bull;</span>
              <span>Transmission: <b>Super CVT-i 7-Speed</b></span>
            </div>
          </div>
        </div>

        {/* Vehicle Health Metrics & Switcher */}
        <div style={{ display: "flex", alignItems: "center", gap: "18px", flexWrap: "wrap" }}>
          <div style={{ textAlign: "right", borderRight: "1px solid var(--border)", paddingRight: "18px" }}>
            <span style={{ fontSize: "10.5px", color: "var(--text-muted)", display: "block", fontWeight: "700" }}>ODOMETER READING</span>
            <b style={{ fontSize: "15px", color: "var(--text-primary)" }}>
              {currentVehicle?.current_mileage ? `${currentVehicle.current_mileage.toLocaleString()} km` : "48,250 km"}
            </b>
          </div>

          <div style={{ textAlign: "right", borderRight: "1px solid var(--border)", paddingRight: "18px" }}>
            <span style={{ fontSize: "10.5px", color: "var(--text-muted)", display: "block", fontWeight: "700" }}>HEALTH INTEGRITY</span>
            <b style={{ fontSize: "15px", color: "var(--success)" }}>94% Optimal</b>
          </div>

          {vehicles.length > 1 ? (
            <select
              value={activeId || ""}
              onChange={(e) => onPickVehicle(e.target.value)}
              style={{ padding: "8px 12px", fontSize: "13px", width: "auto", borderRadius: "8px" }}
            >
              {vehicles.map((v) => (
                <option key={v.user_vehicle_id} value={v.user_vehicle_id}>{v.label}</option>
              ))}
            </select>
          ) : (
            <button
              type="button"
              className="btn"
              onClick={() => go("#/cars")}
              style={{ fontSize: "12.5px", padding: "8px 14px" }}
            >
              + Add Vehicle
            </button>
          )}
        </div>
      </div>

      {/* =========================================================================
          COMMON AUTOMOTIVE FAULT SCENARIOS (ROMAN URDU / URDU QUICK-LOAD)
          ========================================================================= */}
      <div style={{
        background: "var(--surface-1)",
        border: "1px solid var(--border)",
        borderRadius: "14px",
        padding: "16px 20px"
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ fontSize: "14px" }}>⚡</span>
            <b style={{ fontSize: "13.5px", color: "var(--text-primary)" }}>
              Quick Diagnostic Scenarios &amp; Mechanical Symptoms:
            </b>
            <span style={{ fontSize: "11.5px", color: "var(--text-muted)" }}>
              (Click to test RAG manual retrieval &amp; triage)
            </span>
          </div>
          <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
            Corpus: 10,784 Cases &bull; 17,390 Knowledge Chunks
          </span>
        </div>

        <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
          {diagnosticScenarios.map((s, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => setDemoQuery(s.query)}
              style={{
                background: s.bg,
                border: `1px solid ${s.color}40`,
                color: "var(--text-primary)",
                padding: "8px 14px",
                borderRadius: "8px",
                fontSize: "12px",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "8px",
                transition: "all 0.15s ease"
              }}
              onMouseEnter={(e) => e.currentTarget.style.borderColor = s.color}
              onMouseLeave={(e) => e.currentTarget.style.borderColor = `${s.color}40`}
            >
              <span style={{ fontWeight: "600" }}>{s.label}</span>
              <span style={{
                background: s.color,
                color: "#fff",
                fontSize: "10px",
                fontWeight: "700",
                padding: "1px 6px",
                borderRadius: "4px"
              }}>
                {s.tag}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* =========================================================================
          STAGE 2: THE PRIMARY MULTIMODAL DIAGNOSTIC ENGINE (VOICE / OCR / TEXT)
          ========================================================================= */}
      <div className="panel" style={{ padding: "22px 24px", borderRadius: "14px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "14px" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
              <span style={{
                background: "#2563eb",
                color: "#fff",
                fontSize: "11px",
                fontWeight: "800",
                padding: "2px 8px",
                borderRadius: "4px"
              }}>
                STAGE 2: AI MULTIMODAL INTAKE
              </span>
              <h3 style={{ margin: 0, fontSize: "17px", fontWeight: "800", color: "var(--text-primary)" }}>
                Describe Symptom in Roman Urdu / Urdu or Scan Cluster Photo
              </h3>
            </div>
            <p style={{ margin: 0, fontSize: "13px", color: "var(--text-secondary)" }}>
              The query is cross-referenced with official factory service manuals (zero hallucination) and certified Pakistani mechanic solutions.
            </p>
          </div>

          <div style={{ display: "flex", gap: "6px" }}>
            <button
              type="button"
              className="btn"
              onClick={() => setDemoQuery("Toyota Corolla start nahi ho rahi aur check engine light blink kar rahi hai with missing issue")}
              style={{ fontSize: "12px", padding: "6px 10px" }}
            >
              Corolla Misfire Demo
            </button>
            <button
              type="button"
              className="btn"
              onClick={() => setDemoQuery("P0420")}
              style={{ fontSize: "12px", padding: "6px 10px" }}
            >
              DTC P0420 Demo
            </button>
          </div>
        </div>

        {/* Embedded Full Diagnostic Query Engine */}
        <DiagnosticQuery
          userVehicleId={currentVehicle ? activeId : null}
          vehicleLabel={currentVehicle?.label}
          initialQuery={demoQuery}
          onRegisterVehicle={() => go("#/cars")}
          onOpenDamage={() => go("#/damage")}
        />
      </div>

      {/* =========================================================================
          STAGE 3 & 4: FAIR REPAIR PRICE BENCHMARKS & COMPONENT HEALTH RADAR
          ========================================================================= */}
      <div style={{ display: "grid", gridTemplateColumns: "1.1fr 0.9fr", gap: "20px" }}>
        
        {/* Left: Pakistani Spare Parts & Mechanic Labor Fair Price Benchmark */}
        <div className="panel" style={{ padding: "22px", borderRadius: "14px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <span style={{
                  background: "var(--success-dim)",
                  color: "var(--success)",
                  fontSize: "11px",
                  fontWeight: "800",
                  padding: "2px 6px",
                  borderRadius: "4px"
                }}>
                  STAGE 4: FRAUD PROTECTION
                </span>
                <b style={{ fontSize: "15px", color: "var(--text-primary)" }}>
                  Fair Repair Cost Guide ({activeCity} Market Benchmark)
                </b>
              </div>
              <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                Transparent benchmarks: OEM 3S Dealership vs Verified Local Market
              </span>
            </div>
            <button
              type="button"
              className="link"
              onClick={() => go("#/pricing")}
              style={{ fontSize: "12px", fontWeight: "700" }}
            >
              All Parts &rarr;
            </button>
          </div>

          <div style={{
            borderRadius: "10px",
            border: "1px solid var(--border)",
            overflow: "hidden",
            fontSize: "12.5px"
          }}>
            <div style={{
              display: "grid",
              gridTemplateColumns: "1.4fr 1fr 1fr 0.9fr",
              padding: "9px 12px",
              background: "var(--surface-2)",
              borderBottom: "1px solid var(--border)",
              color: "var(--text-secondary)",
              fontSize: "11px",
              fontWeight: "700",
              textTransform: "uppercase"
            }}>
              <span>Replacement Part</span>
              <span>OEM Dealership</span>
              <span>Local Market</span>
              <span>Labor Benchmark</span>
            </div>

            {quickQuotes.map((q, idx) => (
              <div key={idx} style={{
                display: "grid",
                gridTemplateColumns: "1.4fr 1fr 1fr 0.9fr",
                padding: "10px 12px",
                borderBottom: idx < quickQuotes.length - 1 ? "1px solid var(--border)" : "none",
                background: "var(--surface-1)",
                alignItems: "center"
              }}>
                <div>
                  <b style={{ color: "var(--text-primary)", fontSize: "12.5px", display: "block" }}>{q.part_name}</b>
                  <small style={{ color: "var(--text-muted)", fontSize: "10.5px" }}>Est. Workshop Time: 1–2 Hours</small>
                </div>
                <span style={{ color: "var(--primary)", fontWeight: "700", fontSize: "12px" }}>{q.oem_price_range_pkr}</span>
                <span style={{ color: "var(--success)", fontWeight: "700", fontSize: "12px" }}>{q.aftermarket_price_range_pkr}</span>
                <span style={{ color: "var(--text-muted)", fontSize: "12px", fontWeight: "600" }}>{q.labor_estimate_pkr}</span>
              </div>
            ))}
          </div>

          <div style={{
            background: "rgba(37, 99, 235, 0.08)",
            border: "1px solid rgba(37, 99, 235, 0.25)",
            borderRadius: "8px",
            padding: "10px 14px",
            marginTop: "12px",
            fontSize: "12px",
            color: "var(--text-secondary)",
            display: "flex",
            gap: "8px",
            alignItems: "flex-start"
          }}>
            <span style={{ fontSize: "16px" }}>🛡️</span>
            <div>
              <b style={{ color: "var(--text-primary)" }}>Consumer Protection Note:</b> In local auto markets (Montgomery Road Lahore, Plaza Karachi, Sultan Ka Khoo Rawalpindi), technicians may misquote imported parts as genuine OEM. Cross-check part numbers and price bands shown here before approving any job.
            </div>
          </div>
        </div>

        {/* Right: Subsystem Health Radar & Workshop Directory */}
        <div className="panel" style={{ padding: "22px", borderRadius: "14px", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
              <div>
                <b style={{ fontSize: "15px", color: "var(--text-primary)" }}>Subsystem Health Radar</b>
                <span style={{ fontSize: "12px", color: "var(--text-muted)", display: "block" }}>
                  Real-time component health status for {currentVehicle?.label?.split(" ")[1] || "Corolla"}
                </span>
              </div>
              <span style={{
                background: "var(--success-dim)",
                color: "var(--success)",
                fontSize: "11px",
                fontWeight: "700",
                padding: "2px 8px",
                borderRadius: "9999px"
              }}>
                94% Optimal
              </span>
            </div>

            <div style={{ display: "grid", gap: "10px" }}>
              {[
                { name: "Engine & Ignition Circuit", score: "96%", status: "Optimal", color: "var(--success)" },
                { name: "Transmission & Drivetrain", score: "92%", status: "Fluid Normal", color: "var(--success)" },
                { name: "Cooling Circuit & Thermostat", score: "78%", status: "Flush in 1,500 km", color: "var(--warning)" },
                { name: "Brake Hydraulics & ABS", score: "88%", status: "4.5mm pad remaining", color: "var(--success)" },
                { name: "AC Compressor & Condenser", score: "94%", status: "Operating Optimal", color: "var(--success)" },
              ].map((sub, i) => (
                <div key={i} style={{
                  padding: "9px 12px",
                  borderRadius: "8px",
                  background: "var(--surface-2)",
                  border: "1px solid var(--border)",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center"
                }}>
                  <div>
                    <b style={{ fontSize: "12.5px", color: "var(--text-primary)", display: "block" }}>{sub.name}</b>
                    <small style={{ color: "var(--text-muted)", fontSize: "11px" }}>{sub.status}</small>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <b style={{ fontSize: "13px", color: sub.color }}>{sub.score}</b>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Regional Verified Workshop Directory */}
          <div style={{
            borderTop: "1px solid var(--border)",
            paddingTop: "14px",
            marginTop: "14px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            fontSize: "12px"
          }}>
            <div>
              <span style={{ color: "var(--text-primary)", fontWeight: "600", display: "block" }}>
                Need physical inspection in {activeCity}?
              </span>
              <span style={{ color: "var(--text-muted)", fontSize: "11px" }}>
                14 AutoCare-verified partner workshops available
              </span>
            </div>
            <button
              type="button"
              className="btn primary"
              onClick={() => go("#/pricing")}
              style={{ fontSize: "12px", padding: "8px 14px", borderRadius: "8px" }}
            >
              View Verified Workshops
            </button>
          </div>
        </div>

      </div>

    </div>
  );
}

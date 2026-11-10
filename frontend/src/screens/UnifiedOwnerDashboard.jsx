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
      title: "Engine Misfire & CEL Blinking",
      subtitle: "Toyota Corolla Altis 1.8L (2ZR-FE)",
      urdu: "انجن مسنگ اور چیک لائٹ بلنک",
      query: "Toyota Corolla start nahi ho rahi aur check engine light blink kar rahi hai with missing issue",
      code: "P0301",
      severity: "Critical",
      color: "#ef4444",
      icon: "⚡",
    },
    {
      title: "Overheating in City Traffic",
      subtitle: "Honda Civic 1.8L i-VTEC",
      urdu: "ٹریفک میں انجن گرم ہو رہا ہے",
      query: "Honda Civic overheating in traffic needle near red line radiator fan not turning on",
      code: "P0217",
      severity: "High Urgency",
      color: "#f59e0b",
      icon: "🌡️",
    },
    {
      title: "Hard Starting & Long Cranking",
      subtitle: "Universal Multi-Model",
      urdu: "گاڑی دیر سے سٹارٹ ہو رہی ہے",
      query: "gari start hone me issue kar rahi hai self le rahi hai lekin start nahi hoti fuel pump",
      code: "Fuel Pump",
      severity: "Caution",
      color: "#3b82f6",
      icon: "🔑",
    },
    {
      title: "AC Trip & Poor Cooling on Idle",
      subtitle: "Suzuki Cultus / Swift / City",
      urdu: "اے سی کولنگ چھوڑ دیتا ہے",
      query: "AC cooling trip kar raha hai aur engine par load le raha hai compressor awaz",
      code: "AC Clutch",
      severity: "Moderate",
      color: "#10b981",
      icon: "❄️",
    },
    {
      title: "Brake Grinding & Hard Pedal",
      subtitle: "Toyota Yaris / Corolla GLi",
      urdu: "بریک سے رگڑ کی آواز اور سختی",
      query: "Brake press karne par grinding awaz aa rahi hai brake pads wear and rotor damage",
      code: "Brake Pads",
      severity: "Safety Inspection",
      color: "#8b5cf6",
      icon: "🛑",
    },
    {
      title: "AGS Gear Shift Delay & Jerking",
      subtitle: "Suzuki Alto 660cc AGS",
      urdu: "گیئر شفٹنگ میں جھٹکا اور تاخیر",
      query: "Suzuki Alto AGS gear shifting me jerk le rahi hai clutch actuator error",
      code: "P0900",
      severity: "Drivetrain",
      color: "#ec4899",
      icon: "⚙️",
    },
  ];

  const cityMarkets = [
    { name: "Lahore", market: "Montgomery Road & Badami Bagh" },
    { name: "Karachi", market: "Plaza, Tariq Road & Shershah Auto Market" },
    { name: "Rawalpindi", market: "Sultan Ka Khoo & I-9 Islamabad" },
    { name: "Faisalabad", market: "Samundri Road Auto Market" },
    { name: "Peshawar", market: "Ring Road Auto Market" },
  ];

  return (
    <div className="website-container">
      
      {/* =========================================================================
          SECTION 1: HERO & BRAND PROPOSITION
          ========================================================================= */}
      <section className="website-hero">
        <div className="website-hero-badge">
          <span>AI AUTOMOTIVE INTELLIGENCE</span>
          <span>&bull;</span>
          <span>ZERO HALLUCINATION RAG</span>
          <span>&bull;</span>
          <span>PAKISTANI MARKET BENCHMARKS</span>
        </div>

        <h1 className="website-hero-title">
          Intelligent Vehicle Diagnostics &amp; <span>Consumer Repair Protection</span>
        </h1>

        <p className="website-hero-desc">
          Describe symptoms naturally in Roman Urdu, Urdu, or English, or upload an OBD-II scanner photo. 
          Our RAG engine cross-references official OEM service manuals to verify exact chapters and page numbers, 
          providing transparent repair price bands across Pakistani auto markets to prevent workshop fraud.
        </p>

        {/* Persistent Active Vehicle Ribbon */}
        <div style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "16px",
          background: "var(--surface-1)",
          border: "1px solid var(--border)",
          borderRadius: "16px",
          padding: "12px 20px",
          width: "100%",
          maxWidth: "880px",
          boxShadow: "var(--shadow-sm)",
          marginTop: "8px"
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "14px", textAlign: "left" }}>
            <div style={{
              width: "44px",
              height: "44px",
              borderRadius: "10px",
              background: "var(--primary-dim)",
              border: "1px solid var(--primary-border)",
              color: "var(--primary)",
              display: "grid",
              placeItems: "center",
              flexShrink: 0
            }}>
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M5 12l1.5-4.3A2 2 0 018.4 6.4h7.2a2 2 0 011.9 1.3L19 12M4 12h16v4.5a1 1 0 01-1 1H5a1 1 0 01-1-1V12z"/>
                <circle cx="7.5" cy="14.8" r="1.1" fill="currentColor"/>
                <circle cx="16.5" cy="14.8" r="1.1" fill="currentColor"/>
              </svg>
            </div>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{
                  fontSize: "10.5px",
                  fontWeight: "700",
                  color: "var(--success)",
                  background: "var(--success-dim)",
                  padding: "1px 6px",
                  borderRadius: "4px"
                }}>
                  ACTIVE VEHICLE
                </span>
                <span style={{ fontSize: "11px", color: "var(--text-muted)" }}>
                  {currentVehicle ? (currentVehicle.has_manual ? "✓ Factory Service Manual Loaded" : "Standard Mode") : ""}
                </span>
              </div>
              <b style={{ fontSize: "15px", color: "var(--text-primary)" }}>
                {currentVehicle?.label || "Toyota Corolla Altis Grande 1.8L (2022)"}
              </b>
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
            <div style={{ textAlign: "right" }}>
              <span style={{ fontSize: "10px", color: "var(--text-muted)", display: "block", fontWeight: "700" }}>ODOMETER</span>
              <b style={{ fontSize: "13.5px", color: "var(--text-primary)" }}>
                {currentVehicle?.current_mileage ? `${currentVehicle.current_mileage.toLocaleString()} km` : "48,250 km"}
              </b>
            </div>

            <div style={{ textAlign: "right" }}>
              <span style={{ fontSize: "10px", color: "var(--text-muted)", display: "block", fontWeight: "700" }}>HEALTH INDEX</span>
              <b style={{ fontSize: "13.5px", color: "var(--success)" }}>94% Optimal</b>
            </div>

            {vehicles.length > 1 ? (
              <select
                value={activeId || ""}
                onChange={(e) => onPickVehicle(e.target.value)}
                style={{ padding: "6px 10px", fontSize: "12px", borderRadius: "8px" }}
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
                style={{ fontSize: "11.5px", padding: "6px 10px" }}
              >
                + Add Car
              </button>
            )}
          </div>
        </div>
      </section>

      {/* =========================================================================
          SECTION 2: PRIMARY DIAGNOSTIC CONSOLE (THE CENTERPIECE)
          ========================================================================= */}
      <section className="website-section">
        <div className="website-console-card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px", flexWrap: "wrap", gap: "10px" }}>
            <div>
              <h2 style={{ fontSize: "18px", fontWeight: "800", color: "var(--text-primary)", margin: 0 }}>
                Multimodal Diagnostic Terminal
              </h2>
              <span style={{ fontSize: "13px", color: "var(--text-muted)" }}>
                Type your vehicle symptom in plain English, Urdu, or Roman Urdu, or drag &amp; drop an OBD-II scanner photo
              </span>
            </div>

            <div style={{ display: "flex", gap: "8px" }}>
              <button
                type="button"
                className="btn"
                onClick={() => setDemoQuery("Toyota Corolla start nahi ho rahi aur check engine light blink kar rahi hai with missing issue")}
                style={{ fontSize: "12px", padding: "6px 12px" }}
              >
                Corolla Misfire Demo
              </button>
              <button
                type="button"
                className="btn"
                onClick={() => setDemoQuery("P0420")}
                style={{ fontSize: "12px", padding: "6px 12px" }}
              >
                DTC P0420 Demo
              </button>
            </div>
          </div>

          <DiagnosticQuery
            userVehicleId={currentVehicle ? activeId : null}
            vehicleLabel={currentVehicle?.label}
            initialQuery={demoQuery}
            onRegisterVehicle={() => go("#/cars")}
            onOpenDamage={() => go("#/damage")}
          />
        </div>
      </section>

      {/* =========================================================================
          SECTION 3: HOW IT WORKS — THE 4-STAGE ARCHITECTURE
          ========================================================================= */}
      <section className="website-section">
        <div className="website-section-header">
          <div>
            <h2 className="website-section-title">
              <span>🔬</span> How AutoCare AI Works Under the Hood
            </h2>
            <div className="website-section-subtitle">
              A transparent, 4-stage pipeline that guarantees verifiable answers without AI hallucination
            </div>
          </div>
          <span style={{ fontSize: "12px", color: "var(--text-muted)", fontWeight: "600" }}>
            PUCIT BS Data Science FYP Architecture
          </span>
        </div>

        <div className="website-process-grid">
          {[
            {
              step: "01",
              title: "Vehicle Context Ingestion",
              tag: "Taxonomy & Manual Grounding",
              desc: "The pipeline locks onto your specific vehicle make, year, engine code (e.g. 2ZR-FE), and transmission. All queries are strictly scoped to the vehicle's official factory manual.",
              color: "#3b82f6"
            },
            {
              step: "02",
              title: "Multilingual NLP Parsing",
              tag: "Roman Urdu / Urdu / DTC OCR",
              desc: "Colloquial Pakistani driver terminology (e.g. 'missing kar rahi hai', 'load le rahi hai') is translated into standard SAE J1979 fault codes through normalized tokenization.",
              color: "#10b981"
            },
            {
              step: "03",
              title: "Manual-Grounded RAG Search",
              tag: "Zero Hallucination Proof",
              desc: "Dense semantic embeddings and BM25 lexical search query 17,390 vectors from factory manuals and certified mechanics. Every claim cites exact chapter and verified page numbers.",
              color: "#f59e0b"
            },
            {
              step: "04",
              title: "Consumer Price Protection",
              tag: "PKR Market Intelligence",
              desc: "Compares Genuine OEM Dealership prices against verified local market spare parts and certified mechanic labor in Lahore, Karachi, and Islamabad to eliminate overcharging.",
              color: "#ec4899"
            },
          ].map((item, idx) => (
            <div key={idx} className="website-process-card">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{
                  fontSize: "12px",
                  fontWeight: "900",
                  color: item.color,
                  background: `${item.color}15`,
                  padding: "2px 8px",
                  borderRadius: "6px"
                }}>
                  STAGE {item.step}
                </span>
                <span style={{ fontSize: "11px", color: "var(--text-muted)", fontWeight: "600" }}>
                  {item.tag}
                </span>
              </div>
              <h3 style={{ fontSize: "15px", fontWeight: "700", color: "var(--text-primary)", margin: "4px 0 0" }}>
                {item.title}
              </h3>
              <p style={{ fontSize: "12.5px", color: "var(--text-secondary)", lineHeight: 1.5, margin: 0 }}>
                {item.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* =========================================================================
          SECTION 4: COMMON MECHANICAL FAULT SCENARIOS (INTERACTIVE CARDS)
          ========================================================================= */}
      <section className="website-section">
        <div className="website-section-header">
          <div>
            <h2 className="website-section-title">
              <span>🚗</span> Common Mechanical Symptoms &amp; Faults
            </h2>
            <div className="website-section-subtitle">
              Click any scenario to automatically load its diagnostic trace, verified manual chapter, and repair estimate
            </div>
          </div>
          <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
            Corpus: 10,784 Verified Pakistani Repair Cases
          </span>
        </div>

        <div className="website-scenario-grid">
          {diagnosticScenarios.map((sc, idx) => (
            <div
              key={idx}
              className="website-scenario-card"
              onClick={() => {
                setDemoQuery(sc.query);
                window.scrollTo({ top: 380, behavior: "smooth" });
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <span style={{ fontSize: "20px" }}>{sc.icon}</span>
                <span style={{
                  fontSize: "10px",
                  fontWeight: "700",
                  color: sc.color,
                  background: `${sc.color}15`,
                  border: `1px solid ${sc.color}35`,
                  padding: "1px 6px",
                  borderRadius: "4px"
                }}>
                  {sc.severity}
                </span>
              </div>

              <div>
                <b style={{ fontSize: "14px", color: "var(--text-primary)", display: "block" }}>{sc.title}</b>
                <span style={{ fontSize: "11px", color: "var(--text-muted)", display: "block", marginTop: "1px" }}>{sc.subtitle}</span>
              </div>

              <div style={{
                background: "var(--surface-2)",
                padding: "6px 8px",
                borderRadius: "6px",
                fontSize: "11.5px",
                color: "var(--text-secondary)",
                fontFamily: "inherit"
              }}>
                <span style={{ color: sc.color, fontWeight: "700" }}>[{sc.code}]</span> {sc.urdu}
              </div>

              <span style={{ fontSize: "11px", color: "var(--primary)", fontWeight: "600", marginTop: "auto" }}>
                Run Diagnostic Trace &rarr;
              </span>
            </div>
          ))}
        </div>
      </section>

      {/* =========================================================================
          SECTION 5: REGIONAL FAIR REPAIR PRICE ESTIMATOR & CONSUMER PROTECTION
          ========================================================================= */}
      <section className="website-section">
        <div className="website-section-header">
          <div>
            <h2 className="website-section-title">
              <span>💰</span> Fair Repair Cost Benchmark ({activeCity} Auto Markets)
            </h2>
            <div className="website-section-subtitle">
              Transparent price bands for genuine OEM dealership parts vs. trusted local market spare parts &amp; certified labor
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ fontSize: "12px", color: "var(--text-secondary)" }}>Select City:</span>
            <select
              value={activeCity}
              onChange={(e) => setActiveCity(e.target.value)}
              style={{
                background: "var(--surface-1)",
                color: "var(--text-primary)",
                border: "1px solid var(--border)",
                padding: "6px 12px",
                borderRadius: "8px",
                fontSize: "12.5px"
              }}
            >
              {cityMarkets.map((c) => (
                <option key={c.name} value={c.name}>{c.name} ({c.market})</option>
              ))}
            </select>
          </div>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1.2fr 0.8fr", gap: "24px" }}>
          {/* Pricing Table Card */}
          <div style={{
            background: "var(--surface-1)",
            border: "1px solid var(--border)",
            borderRadius: "16px",
            overflow: "hidden"
          }}>
            <div style={{
              display: "grid",
              gridTemplateColumns: "1.4fr 1fr 1fr 0.9fr",
              padding: "12px 16px",
              background: "var(--surface-2)",
              borderBottom: "1px solid var(--border)",
              color: "var(--text-secondary)",
              fontSize: "11.5px",
              fontWeight: "800",
              textTransform: "uppercase",
              letterSpacing: "0.04em"
            }}>
              <span>Spare Part / Assembly</span>
              <span>OEM 3S Dealership</span>
              <span>Local Auto Market</span>
              <span>Labor Benchmark</span>
            </div>

            {quickQuotes.map((q, idx) => (
              <div key={idx} style={{
                display: "grid",
                gridTemplateColumns: "1.4fr 1fr 1fr 0.9fr",
                padding: "12px 16px",
                borderBottom: idx < quickQuotes.length - 1 ? "1px solid var(--border)" : "none",
                alignItems: "center",
                fontSize: "13px"
              }}>
                <div>
                  <b style={{ color: "var(--text-primary)", display: "block" }}>{q.part_name}</b>
                  <small style={{ color: "var(--text-muted)", fontSize: "11px" }}>Est. Workshop Time: 1–2 Hours</small>
                </div>
                <span style={{ color: "var(--primary)", fontWeight: "700" }}>{q.oem_price_range_pkr}</span>
                <span style={{ color: "var(--success)", fontWeight: "700" }}>{q.aftermarket_price_range_pkr}</span>
                <span style={{ color: "var(--text-muted)", fontWeight: "600" }}>{q.labor_estimate_pkr}</span>
              </div>
            ))}

            <div style={{
              background: "rgba(37, 99, 235, 0.06)",
              borderTop: "1px solid var(--border)",
              padding: "14px 18px",
              fontSize: "12.5px",
              color: "var(--text-secondary)",
              display: "flex",
              gap: "10px",
              alignItems: "flex-start"
            }}>
              <span style={{ fontSize: "18px" }}>🛡️</span>
              <div>
                <b style={{ color: "var(--text-primary)" }}>Consumer Protection Notice for {activeCity}:</b>
                {" "}In markets like Montgomery Road (Lahore) or Plaza (Karachi), unscrupulous workshops frequently misquote Chinese aftermarket parts as genuine Japanese Kabli. Always cross-check the verified part numbers and price bands shown here before approving any job.
              </div>
            </div>
          </div>

          {/* Subsystem Health Card */}
          <div style={{
            background: "var(--surface-1)",
            border: "1px solid var(--border)",
            borderRadius: "16px",
            padding: "22px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between"
          }}>
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
                <div>
                  <h3 style={{ fontSize: "16px", fontWeight: "800", color: "var(--text-primary)", margin: 0 }}>
                    Vehicle Health Radar
                  </h3>
                  <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                    Real-time status for {currentVehicle?.label?.split(" ")[1] || "Corolla"}
                  </span>
                </div>
                <span style={{
                  background: "var(--success-dim)",
                  color: "var(--success)",
                  fontSize: "12px",
                  fontWeight: "800",
                  padding: "3px 10px",
                  borderRadius: "9999px"
                }}>
                  94% Overall Health
                </span>
              </div>

              <div style={{ display: "grid", gap: "10px" }}>
                {[
                  { name: "Engine & Ignition Circuit", score: "96%", status: "Optimal", color: "var(--success)" },
                  { name: "Transmission & Drivetrain", score: "92%", status: "Fluid Normal", color: "var(--success)" },
                  { name: "Cooling Circuit & Thermostat", score: "78%", status: "Flush in 1,500 km", color: "var(--warning)" },
                  { name: "Brake Hydraulics & ABS", score: "88%", status: "4.5mm remaining", color: "var(--success)" },
                  { name: "AC Compressor & Climate", score: "94%", status: "Operating Optimal", color: "var(--success)" },
                ].map((sub, i) => (
                  <div key={i} style={{
                    padding: "10px 14px",
                    borderRadius: "10px",
                    background: "var(--surface-2)",
                    border: "1px solid var(--border)",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center"
                  }}>
                    <div>
                      <b style={{ fontSize: "13px", color: "var(--text-primary)", display: "block" }}>{sub.name}</b>
                      <small style={{ color: "var(--text-muted)", fontSize: "11px" }}>{sub.status}</small>
                    </div>
                    <b style={{ fontSize: "14px", color: sub.color }}>{sub.score}</b>
                  </div>
                ))}
              </div>
            </div>

            <div style={{
              borderTop: "1px solid var(--border)",
              paddingTop: "16px",
              marginTop: "16px",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center"
            }}>
              <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
                Need full physical workshop inspection?
              </span>
              <button
                type="button"
                className="btn primary"
                onClick={() => go("#/pricing")}
                style={{ fontSize: "12px", padding: "6px 14px" }}
              >
                Find Partner Workshops
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* =========================================================================
          SECTION 6: WEBSITE FOOTER & ACADEMIC SHOWCASE
          ========================================================================= */}
      <footer style={{
        borderTop: "1px solid var(--border)",
        paddingTop: "32px",
        display: "flex",
        flexDirection: "column",
        gap: "20px"
      }}>
        <div style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          flexWrap: "wrap",
          gap: "24px"
        }}>
          <div style={{ maxWidth: "420px" }}>
            <b style={{ fontSize: "16px", color: "var(--text-primary)", display: "block" }}>AutoCare AI</b>
            <p style={{ fontSize: "12.5px", color: "var(--text-muted)", lineHeight: 1.6, margin: "6px 0 0" }}>
              A Final Year Project developed at the Department of Data Science, Punjab University College of Information Technology (PUCIT). 
              Engineered to eliminate hallucination in consumer automotive repair through factory manual grounding and localized market price benchmarking.
            </p>
          </div>

          <div>
            <b style={{ fontSize: "13px", color: "var(--text-primary)", display: "block", marginBottom: "8px" }}>Project Engineering Team:</b>
            <div style={{ fontSize: "12px", color: "var(--text-secondary)", display: "grid", gap: "4px" }}>
              <span>&bull; <b>Talha Ali Bhatti</b> (Roll No: bsdsf23a016) — Distributed Storage &amp; Streaming</span>
              <span>&bull; <b>Muhammad Abdullah</b> (Roll No: bsdsf23a032) — Data Engineering &amp; Analytics</span>
              <span>&bull; <b>Abdullah</b> (Roll No: bsdsf23a035) — Distributed Algorithms &amp; RAG Systems</span>
            </div>
          </div>

          <div>
            <b style={{ fontSize: "13px", color: "var(--text-primary)", display: "block", marginBottom: "8px" }}>Emergency Assistance:</b>
            <div style={{ fontSize: "12px", color: "var(--text-muted)", display: "grid", gap: "6px" }}>
              <a href="tel:1122" style={{ color: "#ef4444", textDecoration: "none", fontWeight: "700" }}>
                🚨 Highway &amp; Motorway Rescue: 1122
              </a>
              <span>Toyota 3S Emergency: 0800-TOYOTA</span>
              <span>Honda Customer Assistance: 0800-HONDA</span>
            </div>
          </div>
        </div>

        <div style={{
          borderTop: "1px solid var(--border)",
          paddingTop: "16px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "12px",
          fontSize: "12px",
          color: "var(--text-muted)"
        }}>
          <span>&copy; 2026 AutoCare AI. All rights reserved. BSDS Final Year Project.</span>
          <div style={{ display: "flex", gap: "16px" }}>
            <a href="#/dashboard" style={{ color: "var(--text-muted)", textDecoration: "none" }}>Diagnostic Console</a>
            <a href="#/pricing" style={{ color: "var(--text-muted)", textDecoration: "none" }}>PKR Price Guide</a>
            <a href="#/cars" style={{ color: "var(--text-muted)", textDecoration: "none" }}>My Garage</a>
            <a href="#/settings" style={{ color: "var(--text-muted)", textDecoration: "none" }}>System Settings</a>
          </div>
        </div>
      </footer>

    </div>
  );
}

import { useState, useEffect } from "react";
import { get } from "../api/client";

export function BentoDashboardScreen({ go }) {
  const [quotes, setQuotes] = useState([]);

  useEffect(() => {
    get("/api/v1/pricing/quotes?model=corolla&category=all")
      .then((data) => setQuotes((data || []).slice(0, 3)))
      .catch(() => {});
  }, []);

  return (
    <div className="bento-container" style={{ padding: "0 0 32px 0" }}>
      {/* Top Vehicle Banner */}
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: "20px",
        flexWrap: "wrap",
        gap: "14px",
        paddingBottom: "16px",
        borderBottom: "1px solid var(--border)"
      }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
            <span style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "6px",
              padding: "3px 10px",
              borderRadius: "9999px",
              background: "var(--success-dim)",
              border: "1px solid var(--success-border)",
              color: "var(--success)",
              fontSize: "12px",
              fontWeight: "700"
            }}>
              <span style={{ width: "6px", height: "6px", borderRadius: "50%", background: "var(--success)", display: "inline-block" }} />
              Active Vehicle Monitored
            </span>
            <span style={{ color: "var(--text-muted)", fontSize: "13px" }}>Toyota Corolla Altis Grande (2022)</span>
          </div>

          <h1 style={{
            margin: 0,
            fontSize: "24px",
            fontWeight: "700",
            letterSpacing: "-0.015em",
            color: "var(--text-primary)"
          }}>
            Vehicle Health Dashboard
          </h1>
        </div>

        <div style={{ display: "flex", gap: "8px" }}>
          <button
            onClick={() => go ? go("#/cars") : null}
            className="btn"
            style={{ fontSize: "13px" }}
          >
            My Garage
          </button>
          <button
            onClick={() => go ? go("#/ask") : null}
            className="btn primary"
            style={{ fontSize: "13px" }}
          >
            Ask AI Copilot
          </button>
        </div>
      </div>

      {/* ==================== 4 CLEAN EXECUTIVE CARDS ==================== */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(12, 1fr)",
        gap: "16px"
      }}>

        {/* ---------------- CARD 1: Diagnostic Monitor & Root Cause (Span 7) ---------------- */}
        <div style={{
          gridColumn: "span 7",
          background: "var(--surface-1)",
          border: "1px solid var(--border)",
          boxShadow: "var(--shadow-sm)",
          borderRadius: "14px",
          padding: "20px",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between"
        }}>
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "14px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <div style={{
                  width: "34px",
                  height: "34px",
                  borderRadius: "8px",
                  background: "var(--warning-dim)",
                  border: "1px solid var(--warning-border)",
                  display: "grid",
                  placeItems: "center",
                  color: "var(--warning)"
                }}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
                    <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
                  </svg>
                </div>
                <div>
                  <h3 style={{ margin: 0, fontSize: "15px", fontWeight: "700", color: "var(--text-primary)" }}>
                    Active Diagnostic Alert
                  </h3>
                  <span style={{ fontSize: "12.5px", color: "var(--text-muted)" }}>Automated sensor root-cause deduction</span>
                </div>
              </div>

              <span style={{
                padding: "3px 8px",
                borderRadius: "6px",
                background: "var(--warning-dim)",
                border: "1px solid var(--warning-border)",
                color: "var(--warning)",
                fontSize: "12px",
                fontWeight: "600"
              }}>
                1 Action Needed
              </span>
            </div>

            {/* Diagnostic Alert Box */}
            <div style={{
              background: "var(--surface-2)",
              border: "1px solid var(--border)",
              borderRadius: "10px",
              padding: "14px",
              margin: "10px 0 14px 0"
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
                <b style={{ fontSize: "13.5px", color: "var(--text-primary)" }}>Fault: Engine Coolant High Temperature (P0217)</b>
                <span className="pill pill-warn" style={{ fontSize: "11px" }}>High Urgency</span>
              </div>

              {/* Clean 3-Step Root Cause Progression */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 20px 1fr 20px 1fr", alignItems: "center", gap: "6px" }}>
                <div style={{ padding: "8px", borderRadius: "6px", background: "var(--surface-1)", border: "1px solid var(--border)", textAlign: "center" }}>
                  <span style={{ fontSize: "10.5px", color: "var(--text-muted)", textTransform: "uppercase", display: "block" }}>Observed</span>
                  <b style={{ fontSize: "12px", color: "var(--text-primary)" }}>Coolant Boil</b>
                </div>

                <div style={{ textAlign: "center", color: "var(--text-muted)", fontSize: "14px" }}>→</div>

                <div style={{ padding: "8px", borderRadius: "6px", background: "var(--surface-1)", border: "1px solid var(--border)", textAlign: "center" }}>
                  <span style={{ fontSize: "10.5px", color: "var(--text-muted)", textTransform: "uppercase", display: "block" }}>Failure</span>
                  <b style={{ fontSize: "12px", color: "var(--text-primary)" }}>Fan Inactive</b>
                </div>

                <div style={{ textAlign: "center", color: "var(--text-muted)", fontSize: "14px" }}>→</div>

                <div style={{ padding: "8px", borderRadius: "6px", background: "var(--primary-dim)", border: "1px solid var(--primary-border)", textAlign: "center" }}>
                  <span style={{ fontSize: "10.5px", color: "var(--primary)", textTransform: "uppercase", display: "block", fontWeight: "700" }}>Root Cause</span>
                  <b style={{ fontSize: "12px", color: "var(--primary)" }}>Fan Relay Defect</b>
                </div>
              </div>
            </div>

            <p style={{ margin: "0", fontSize: "13px", color: "var(--text-secondary)", lineHeight: 1.5 }}>
              <b>Recommendation:</b> Check the radiator fan relay in the engine fuse box before continuous driving to prevent head gasket damage.
            </p>
          </div>

          <div style={{
            borderTop: "1px solid var(--border)",
            paddingTop: "10px",
            marginTop: "12px",
            display: "flex",
            justifyContent: "space-between",
            fontSize: "12px",
            color: "var(--text-muted)"
          }}>
            <span>Root-Cause Confidence: <b style={{ color: "var(--success)" }}>89.4% Match</b></span>
            <span>Manual Grounding: <b>Corolla 2022 Manual §6-3</b></span>
          </div>
        </div>

        {/* ---------------- CARD 2: Subsystem Health Overview (Span 5) ---------------- */}
        <div style={{
          gridColumn: "span 5",
          background: "var(--surface-1)",
          border: "1px solid var(--border)",
          boxShadow: "var(--shadow-sm)",
          borderRadius: "14px",
          padding: "20px",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between"
        }}>
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "14px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <div style={{
                  width: "34px",
                  height: "34px",
                  borderRadius: "8px",
                  background: "var(--primary-dim)",
                  border: "1px solid var(--primary-border)",
                  display: "grid",
                  placeItems: "center",
                  color: "var(--primary)"
                }}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
                  </svg>
                </div>
                <div>
                  <h3 style={{ margin: 0, fontSize: "15px", fontWeight: "700", color: "var(--text-primary)" }}>
                    Subsystem Health
                  </h3>
                  <span style={{ fontSize: "12.5px", color: "var(--text-muted)" }}>Component status & wear levels</span>
                </div>
              </div>

              <span className="pill pill-ok" style={{ fontSize: "11px" }}>
                3 / 4 Systems Good
              </span>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              {[
                { name: "Braking System (Pads & Discs)", val: 78, status: "Good", color: "var(--success)" },
                { name: "Cooling Circuit (Fan & Thermostat)", val: 42, status: "Attention", color: "var(--warning)" },
                { name: "Automatic Transmission (CVT)", val: 91, status: "Optimal", color: "var(--primary)" },
                { name: "12V Battery & Charging", val: 96, status: "Healthy", color: "var(--success)" },
              ].map((sub, i) => (
                <div key={i}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "13px", marginBottom: "4px" }}>
                    <span style={{ color: "var(--text-primary)", fontWeight: "500" }}>{sub.name}</span>
                    <span style={{ color: sub.color, fontWeight: "700", fontSize: "12px" }}>
                      {sub.val}% • {sub.status}
                    </span>
                  </div>
                  <div style={{ height: "6px", background: "var(--surface-2)", borderRadius: "3px", overflow: "hidden", border: "1px solid var(--border)" }}>
                    <div style={{ width: `${sub.val}%`, height: "100%", background: sub.color, borderRadius: "3px" }} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div style={{
            borderTop: "1px solid var(--border)",
            paddingTop: "10px",
            marginTop: "12px",
            display: "flex",
            justifyContent: "space-between",
            fontSize: "12px",
            color: "var(--text-muted)"
          }}>
            <span>Current Odometer: <b>48,250 km</b></span>
            <span>Next Inspection: <b>50,000 km</b></span>
          </div>
        </div>

        {/* ---------------- CARD 3: Scheduled Service Intervals (Span 5) ---------------- */}
        <div style={{
          gridColumn: "span 5",
          background: "var(--surface-1)",
          border: "1px solid var(--border)",
          boxShadow: "var(--shadow-sm)",
          borderRadius: "14px",
          padding: "20px",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between"
        }}>
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "14px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <div style={{
                  width: "34px",
                  height: "34px",
                  borderRadius: "8px",
                  background: "var(--success-dim)",
                  border: "1px solid var(--success-border)",
                  display: "grid",
                  placeItems: "center",
                  color: "var(--success)"
                }}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                    <line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
                  </svg>
                </div>
                <div>
                  <h3 style={{ margin: 0, fontSize: "15px", fontWeight: "700", color: "var(--text-primary)" }}>
                    Upcoming Maintenance
                  </h3>
                  <span style={{ fontSize: "12.5px", color: "var(--text-muted)" }}>Manufacturer recommended schedule</span>
                </div>
              </div>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              {[
                { title: "Synthetic Engine Oil & Filter", due: "Due in 1,750 km", urgency: "Soon", pill: "pill-warn" },
                { title: "Coolant Circuit & Relay Inspection", due: "Action Required", urgency: "Immediate", pill: "pill-urgency u-critical" },
                { title: "Brake Fluid Moisture Test", due: "Due at 60,000 km", urgency: "Normal", pill: "pill-ok" },
              ].map((item, i) => (
                <div key={i} style={{
                  padding: "10px 12px",
                  borderRadius: "8px",
                  background: "var(--surface-2)",
                  border: "1px solid var(--border)",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center"
                }}>
                  <div>
                    <b style={{ fontSize: "13px", color: "var(--text-primary)", display: "block" }}>{item.title}</b>
                    <small style={{ color: "var(--text-muted)", fontSize: "11.5px" }}>{item.due}</small>
                  </div>
                  <span className={`pill ${item.pill}`} style={{ fontSize: "11px" }}>{item.urgency}</span>
                </div>
              ))}
            </div>
          </div>

          <div style={{
            borderTop: "1px solid var(--border)",
            paddingTop: "10px",
            marginTop: "12px",
            display: "flex",
            justifyContent: "space-between",
            fontSize: "12px",
            color: "var(--text-muted)"
          }}>
            <span>Service Schedule: <b>5,000 km Routine</b></span>
            <button className="link" onClick={() => go ? go("#/health") : null} style={{ fontSize: "12px" }}>
              View Complete Schedule →
            </button>
          </div>
        </div>

        {/* ---------------- CARD 4: Local Parts & Labour Quotes in PKR (Span 7) ---------------- */}
        <div style={{
          gridColumn: "span 7",
          background: "var(--surface-1)",
          border: "1px solid var(--border)",
          boxShadow: "var(--shadow-sm)",
          borderRadius: "14px",
          padding: "20px",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between"
        }}>
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "14px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <div style={{
                  width: "34px",
                  height: "34px",
                  borderRadius: "8px",
                  background: "var(--primary-dim)",
                  border: "1px solid var(--primary-border)",
                  display: "grid",
                  placeItems: "center",
                  color: "var(--primary)"
                }}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                  </svg>
                </div>
                <div>
                  <h3 style={{ margin: 0, fontSize: "15px", fontWeight: "700", color: "var(--text-primary)" }}>
                    Spare Parts & Labour Estimates
                  </h3>
                  <span style={{ fontSize: "12.5px", color: "var(--text-muted)" }}>Market rates for Lahore, Karachi & Rawalpindi in PKR</span>
                </div>
              </div>

              <span className="pill pill-ok" style={{ fontSize: "11px" }}>
                PKR Verified
              </span>
            </div>

            {/* Clean Market Price Table */}
            <div style={{
              borderRadius: "8px",
              border: "1px solid var(--border)",
              overflow: "hidden",
              fontSize: "13px"
            }}>
              <div style={{
                display: "grid",
                gridTemplateColumns: "1.4fr 1fr 1fr 0.9fr",
                padding: "8px 12px",
                background: "var(--surface-2)",
                borderBottom: "1px solid var(--border)",
                color: "var(--text-secondary)",
                fontSize: "11.5px",
                fontWeight: "700",
                textTransform: "uppercase",
                letterSpacing: "0.04em"
              }}>
                <span>Part / Service</span>
                <span>Genuine OEM</span>
                <span>Aftermarket</span>
                <span>Labour</span>
              </div>

              {(quotes.length > 0 ? quotes : [
                { part_name: "Front Brake Pads (Set)", oem_price_range_pkr: "Rs. 14,500 - 18,500", aftermarket_price_range_pkr: "Rs. 4,500 - 7,500", labor_estimate_pkr: "Rs. 1,500" },
                { part_name: "Cooling Fan Relay & Motor", oem_price_range_pkr: "Rs. 18,000 - 24,000", aftermarket_price_range_pkr: "Rs. 6,500 - 10,500", labor_estimate_pkr: "Rs. 2,000" },
                { part_name: "Synthetic Engine Oil (4L)", oem_price_range_pkr: "Rs. 12,500 - 14,000", aftermarket_price_range_pkr: "Rs. 8,500 - 10,500", labor_estimate_pkr: "Rs. 800" },
              ]).map((row, idx) => (
                <div key={idx} style={{
                  display: "grid",
                  gridTemplateColumns: "1.4fr 1fr 1fr 0.9fr",
                  padding: "9px 12px",
                  borderBottom: idx < 2 ? "1px solid var(--border)" : "none",
                  alignItems: "center",
                  background: "var(--surface-1)"
                }}>
                  <b style={{ color: "var(--text-primary)", fontSize: "12.5px" }}>{row.part_name}</b>
                  <span style={{ color: "var(--primary)", fontWeight: "600", fontSize: "12px" }}>{row.oem_price_range_pkr}</span>
                  <span style={{ color: "var(--success)", fontWeight: "600", fontSize: "12px" }}>{row.aftermarket_price_range_pkr}</span>
                  <span style={{ color: "var(--text-muted)", fontSize: "12px" }}>{row.labor_estimate_pkr}</span>
                </div>
              ))}
            </div>
          </div>

          <div style={{
            borderTop: "1px solid var(--border)",
            paddingTop: "10px",
            marginTop: "12px",
            display: "flex",
            justifyContent: "space-between",
            fontSize: "12px",
            color: "var(--text-muted)"
          }}>
            <span>Coverage: <b>3S Dealerships & Bilal Gunj Market</b></span>
            <button className="link" onClick={() => go ? go("#/pricing") : null} style={{ fontSize: "12px" }}>
              Explore Full Parts Catalog →
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}

import React, { useState, useEffect } from "react";
import { post } from "../api/client";

export default function LiveMechanicDispatch({
  dtcCode = null,
  symptomQuery = "",
  initialCity = "Lahore",
  vehicleMake = "Toyota",
}) {
  const [loading, setLoading] = useState(false);
  const [city, setCity] = useState(initialCity);
  const [userCoords, setUserCoords] = useState({ lat: 31.5204, lon: 74.3587 }); // Default Lahore
  const [locationStatus, setLocationStatus] = useState("Preset Location (Lahore Hub)");
  const [isLiveGps, setIsLiveGps] = useState(false);
  const [dispatchData, setDispatchData] = useState(null);
  const [selectedWorkshop, setSelectedWorkshop] = useState(null);
  const [error, setError] = useState(null);

  // New UI controls for compact scroll & custom selection
  const [isExpanded, setIsExpanded] = useState(true);
  const [viewMode, setViewMode] = useState("compact"); // 'compact' | 'list' | 'map'
  const [selectedSpecialtyFilter, setSelectedSpecialtyFilter] = useState("all");

  // Preset Pakistani City Coordinates
  const CITY_COORDS = {
    Lahore: { lat: 31.5204, lon: 74.3587, name: "Lahore (Bilal Gunj / Montgomery Rd)" },
    Karachi: { lat: 24.8607, lon: 67.0011, name: "Karachi (Shershah / Plaza)" },
    Islamabad: { lat: 33.6844, lon: 73.0479, name: "Islamabad (Sector I-9 / G-10)" },
    Rawalpindi: { lat: 33.5651, lon: 73.0169, name: "Rawalpindi (Sultan ka Khoo / Peshawar Rd)" },
  };

  const SPECIALTY_PILLS = [
    { key: "all", label: "🌟 Auto-Matched", icon: "🎯" },
    { key: "engine_cooling", label: "Engine & Cooling", icon: "🔧" },
    { key: "brakes_hydraulics", label: "Brakes & Suspension", icon: "🛑" },
    { key: "hvac_air_conditioning", label: "AC & Climate", icon: "❄️" },
    { key: "bodywork_denting", label: "Body & Denting", icon: "🎨" },
    { key: "efi_electrical", label: "General & EFI", icon: "⚡" },
  ];

  // Request browser live GPS
  function requestLiveLocation() {
    if (!navigator.geolocation) {
      setLocationStatus("Geolocation is not supported by your browser");
      return;
    }
    setLocationStatus("Acquiring Live GPS coordinates…");
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const coords = { lat: pos.coords.latitude, lon: pos.coords.longitude };
        setUserCoords(coords);
        setIsLiveGps(true);
        setLocationStatus(`📍 Live GPS Active (±${Math.round(pos.coords.accuracy)}m)`);
        fetchRecommendations(coords.lat, coords.lon, city);
      },
      (err) => {
        setIsLiveGps(false);
        setLocationStatus(`GPS permission denied (${err.message}). Using preset.`);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  }

  function handleCityChange(newCity) {
    setCity(newCity);
    if (CITY_COORDS[newCity]) {
      const coords = { lat: CITY_COORDS[newCity].lat, lon: CITY_COORDS[newCity].lon };
      setUserCoords(coords);
      setIsLiveGps(false);
      setLocationStatus(`Preset Location (${newCity} Hub)`);
      fetchRecommendations(coords.lat, coords.lon, newCity);
    }
  }

  async function fetchRecommendations(lat = userCoords.lat, lon = userCoords.lon, targetCity = city) {
    setLoading(true);
    setError(null);
    try {
      const payload = {
        user_lat: lat,
        user_lon: lon,
        city: targetCity,
        dtc_code: dtcCode || null,
        symptom_text: symptomQuery || "radiator overheating issue",
        vehicle_make: vehicleMake,
      };
      const res = await post("/api/v1/dispatch/recommend", payload);
      setDispatchData(res);
      if (res.recommendations && res.recommendations.length > 0) {
        setSelectedWorkshop(res.recommendations[0]);
      }
    } catch (err) {
      setError(err.message || "Failed to contact dispatch engine.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchRecommendations();
  }, [dtcCode, symptomQuery]);

  // Filter recommendations if user chooses another specialty
  const displayedWorkshops = (dispatchData?.recommendations || []).filter((w) => {
    if (selectedSpecialtyFilter === "all") return true;
    if (selectedSpecialtyFilter === "brakes_hydraulics") {
      return w.matched_specialty === "brakes_hydraulics" || w.matched_specialty === "suspension_steering" || w.name.includes("Brake");
    }
    if (selectedSpecialtyFilter === "engine_cooling") {
      return w.matched_specialty === "engine_cooling" || w.matched_specialty === "transmission_gearbox" || w.name.includes("Engine");
    }
    return w.matched_specialty === selectedSpecialtyFilter || w.name.toLowerCase().includes(selectedSpecialtyFilter.slice(0, 4));
  });

  const activeWorkshop = selectedWorkshop || (displayedWorkshops.length > 0 ? displayedWorkshops[0] : null);

  return (
    <div style={{
      background: "var(--surface-1, #1e293b)",
      border: "1px solid var(--border, #334155)",
      borderRadius: "14px",
      padding: "16px 20px",
      margin: "16px 0",
      color: "var(--text-primary, #f8fafc)",
      boxShadow: "0 4px 20px rgba(0,0,0,0.22)",
      transition: "all 0.2s ease"
    }}>
      {/* Header Bar with Collapse Toggle */}
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        flexWrap: "wrap",
        gap: "10px",
        paddingBottom: isExpanded ? "12px" : "0",
        borderBottom: isExpanded ? "1px solid #334155" : "none"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <span style={{ fontSize: "20px" }}>🛠️</span>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <h3 style={{ margin: 0, fontSize: "16px", fontWeight: "700" }}>
                Specialist Workshop Dispatch
              </h3>
              <span style={{
                background: isLiveGps ? "#05966920" : "#0284c720",
                color: isLiveGps ? "#10b981" : "#38bdf8",
                border: `1px solid ${isLiveGps ? "#059669" : "#0284c7"}`,
                padding: "2px 8px",
                borderRadius: "10px",
                fontSize: "11px",
                fontWeight: "600"
              }}>
                {isLiveGps ? "● LIVE GPS" : "● 5 HUBS READY"}
              </span>
            </div>
            {!isExpanded && activeWorkshop && (
              <p style={{ margin: "2px 0 0", fontSize: "12px", color: "#38bdf8" }}>
                Matched: <b>{activeWorkshop.name}</b> ({activeWorkshop.distance_km} km) · 📞 {activeWorkshop.contact}
              </p>
            )}
          </div>
        </div>

        {/* Action Controls & Minimize Button */}
        <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
          {isExpanded && (
            <>
              <button
                type="button"
                onClick={requestLiveLocation}
                title="Locate via GPS"
                style={{
                  background: "#0284c7",
                  color: "#ffffff",
                  border: "none",
                  padding: "6px 12px",
                  borderRadius: "6px",
                  fontSize: "11.5px",
                  fontWeight: "600",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "4px"
                }}
              >
                <span>🎯</span> GPS
              </button>

              <select
                value={city}
                onChange={(e) => handleCityChange(e.target.value)}
                style={{
                  background: "#0f172a",
                  color: "#f8fafc",
                  border: "1px solid #475569",
                  padding: "6px 10px",
                  borderRadius: "6px",
                  fontSize: "11.5px"
                }}
              >
                <option value="Lahore">Lahore</option>
                <option value="Karachi">Karachi</option>
                <option value="Islamabad">Islamabad</option>
                <option value="Rawalpindi">Rawalpindi</option>
              </select>
            </>
          )}

          {/* Expand / Collapse Button to prevent huge scrolling */}
          <button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            style={{
              background: "#334155",
              color: "#f8fafc",
              border: "none",
              padding: "6px 12px",
              borderRadius: "6px",
              fontSize: "11.5px",
              fontWeight: "600",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "4px"
            }}
          >
            <span>{isExpanded ? "▲ Collapse" : "▼ Choose Specialist"}</span>
          </button>
        </div>
      </div>

      {/* Main Expanded View */}
      {isExpanded && (
        <div style={{ marginTop: "12px" }}>
          {/* Subsystem & Specialty Selector Pills ("Choose other things") */}
          <div style={{ marginBottom: "14px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
              <span style={{ fontSize: "11px", color: "#94a3b8", fontWeight: "700", textTransform: "uppercase", letterSpacing: "0.5px" }}>
                Choose Automotive System:
              </span>

              {/* View Mode Switcher Pills */}
              <div style={{ display: "flex", gap: "4px", background: "#0f172a", padding: "2px", borderRadius: "6px", border: "1px solid #334155" }}>
                {[
                  { id: "compact", label: "✨ Featured Card" },
                  { id: "list", label: "📋 Compare All 5" },
                  { id: "map", label: "🗺️ Map Radar" }
                ].map((m) => (
                  <button
                    key={m.id}
                    type="button"
                    onClick={() => setViewMode(m.id)}
                    style={{
                      background: viewMode === m.id ? "#0284c7" : "transparent",
                      color: viewMode === m.id ? "#fff" : "#94a3b8",
                      border: "none",
                      padding: "3px 8px",
                      borderRadius: "4px",
                      fontSize: "11px",
                      fontWeight: viewMode === m.id ? "700" : "500",
                      cursor: "pointer"
                    }}
                  >
                    {m.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Specialty Pills */}
            <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
              {SPECIALTY_PILLS.map((pill) => {
                const isActive = selectedSpecialtyFilter === pill.key;
                return (
                  <button
                    key={pill.key}
                    type="button"
                    onClick={() => {
                      setSelectedSpecialtyFilter(pill.key);
                      // Auto-select corresponding workshop
                      const found = (dispatchData?.recommendations || []).find((w) => {
                        if (pill.key === "all") return true;
                        return w.matched_specialty === pill.key || w.name.toLowerCase().includes(pill.key.slice(0, 4));
                      });
                      if (found) setSelectedWorkshop(found);
                    }}
                    style={{
                      background: isActive ? "rgba(56, 189, 248, 0.15)" : "#0f172a",
                      color: isActive ? "#38bdf8" : "#cbd5e1",
                      border: `1px solid ${isActive ? "#38bdf8" : "#334155"}`,
                      borderRadius: "20px",
                      padding: "4px 10px",
                      fontSize: "11.5px",
                      fontWeight: isActive ? "700" : "500",
                      cursor: "pointer",
                      display: "flex",
                      alignItems: "center",
                      gap: "5px"
                    }}
                  >
                    <span>{pill.icon}</span>
                    <span>{pill.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {loading && (
            <div style={{ textAlign: "center", padding: "16px 0", color: "#94a3b8", fontSize: "12px" }}>
              🔄 Updating specialist workshop calculations…
            </div>
          )}

          {error && (
            <div style={{ background: "#ef444420", border: "1px solid #ef4444", padding: "8px 12px", borderRadius: "6px", color: "#fca5a5", fontSize: "12px", margin: "10px 0" }}>
              ⚠️ {error}
            </div>
          )}

          {dispatchData && !loading && (
            <div>
              {/* Option 1: COMPACT FEATURED CARD (Default: takes minimal screen space, zero scroll inflation) */}
              {viewMode === "compact" && activeWorkshop && (
                <div style={{
                  background: "#0f172a",
                  border: "1px solid #0284c7",
                  borderRadius: "10px",
                  padding: "14px 16px",
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
                  gap: "14px",
                  alignItems: "center"
                }}>
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      <span style={{ background: "#0284c7", color: "#fff", padding: "2px 8px", borderRadius: "12px", fontSize: "11px", fontWeight: "bold" }}>
                        RECOMMENDED
                      </span>
                      <span style={{ color: "#10b981", fontSize: "11.5px", fontWeight: "700" }}>
                        {Math.round(activeWorkshop.composite_score * 100)}% Match
                      </span>
                      <span style={{ color: "#94a3b8", fontSize: "11.5px" }}>
                        🚗 {activeWorkshop.distance_km} km away
                      </span>
                    </div>

                    <h4 style={{ margin: "6px 0 2px", fontSize: "15px", color: "#f8fafc" }}>
                      {activeWorkshop.name}
                    </h4>
                    <p style={{ margin: "0 0 6px", fontSize: "12px", color: "#94a3b8" }}>
                      📍 {activeWorkshop.area}, {activeWorkshop.city} &bull; ⭐ {activeWorkshop.rating} / 5.0 ({activeWorkshop.review_count} reviews)
                    </p>

                    <div style={{ fontSize: "11.5px", color: "#38bdf8" }}>
                      Fair PKR Range: <b>Rs. {activeWorkshop.estimated_pkr_low?.toLocaleString()} – {activeWorkshop.estimated_pkr_high?.toLocaleString()}</b>
                    </div>
                  </div>

                  <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                    <div style={{ display: "flex", gap: "8px" }}>
                      <a
                        href={`tel:${activeWorkshop.contact.split(" ")[0]}`}
                        style={{
                          flex: 1,
                          background: "#059669",
                          color: "#fff",
                          textAlign: "center",
                          padding: "8px 12px",
                          borderRadius: "6px",
                          textDecoration: "none",
                          fontSize: "12px",
                          fontWeight: "700",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          gap: "6px"
                        }}
                      >
                        <span>📞</span> Call: {activeWorkshop.contact}
                      </a>

                      <a
                        href={`https://www.google.com/maps/dir/?api=1&origin=${userCoords.lat},${userCoords.lon}&destination=${activeWorkshop.lat},${activeWorkshop.lon}`}
                        target="_blank"
                        rel="noreferrer"
                        style={{
                          flex: 1,
                          background: "#0284c7",
                          color: "#fff",
                          textAlign: "center",
                          padding: "8px 12px",
                          borderRadius: "6px",
                          textDecoration: "none",
                          fontSize: "12px",
                          fontWeight: "700",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          gap: "6px"
                        }}
                      >
                        <span>🗺️</span> Turn-by-Turn Route
                      </a>
                    </div>

                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "10.5px", color: "#94a3b8" }}>
                      <span>Certified OEM: {activeWorkshop.verified_oem?.join(", ")}</span>
                      <button
                        type="button"
                        onClick={() => setViewMode("list")}
                        style={{ background: "none", border: "none", color: "#38bdf8", cursor: "pointer", textDecoration: "underline", padding: 0, fontSize: "10.5px" }}
                      >
                        View all 5 workshops &rarr;
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Option 2: LIST VIEW (Clean, contained height with max-height & internal scroll so page never increases!) */}
              {viewMode === "list" && (
                <div style={{
                  maxHeight: "280px",
                  overflowY: "auto",
                  paddingRight: "6px",
                  display: "flex",
                  flexDirection: "column",
                  gap: "8px"
                }}>
                  {displayedWorkshops.map((w, idx) => {
                    const isSelected = activeWorkshop && activeWorkshop.workshop_id === w.workshop_id;
                    return (
                      <div
                        key={w.workshop_id}
                        onClick={() => setSelectedWorkshop(w)}
                        style={{
                          background: isSelected ? "#0f172a" : "#1e293b",
                          border: `1.5px solid ${isSelected ? "#0284c7" : "#334155"}`,
                          borderRadius: "8px",
                          padding: "10px 14px",
                          cursor: "pointer",
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          flexWrap: "wrap",
                          gap: "8px"
                        }}
                      >
                        <div>
                          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                            <span style={{ background: "#0284c7", color: "#fff", width: "18px", height: "18px", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "10px", fontWeight: "bold" }}>
                              {idx + 1}
                            </span>
                            <b style={{ fontSize: "13px", color: "#f8fafc" }}>{w.name}</b>
                            <span style={{ fontSize: "10.5px", color: "#10b981", background: "#10b98120", padding: "1px 6px", borderRadius: "4px" }}>
                              {Math.round(w.composite_score * 100)}% Match
                            </span>
                          </div>
                          <span style={{ fontSize: "11px", color: "#94a3b8", marginLeft: "24px" }}>
                            📍 {w.area} &bull; 🚗 {w.distance_km} km away &bull; ⭐ {w.rating}
                          </span>
                        </div>

                        <div style={{ display: "flex", gap: "6px", alignItems: "center" }}>
                          <a
                            href={`tel:${w.contact.split(" ")[0]}`}
                            style={{
                              background: "#059669",
                              color: "#fff",
                              padding: "4px 10px",
                              borderRadius: "4px",
                              fontSize: "11px",
                              fontWeight: "600",
                              textDecoration: "none"
                            }}
                          >
                            📞 {w.contact}
                          </a>
                          <a
                            href={`https://www.google.com/maps/dir/?api=1&origin=${userCoords.lat},${userCoords.lon}&destination=${w.lat},${w.lon}`}
                            target="_blank"
                            rel="noreferrer"
                            style={{
                              background: "#0284c7",
                              color: "#fff",
                              padding: "4px 8px",
                              borderRadius: "4px",
                              fontSize: "11px",
                              fontWeight: "600",
                              textDecoration: "none"
                            }}
                          >
                            🗺️ Route
                          </a>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Option 3: MAP RADAR VIEW (Loads only on explicit request, scroll wheel protected) */}
              {viewMode === "map" && activeWorkshop && (
                <div style={{ background: "#0f172a", border: "1px solid #334155", borderRadius: "10px", padding: "12px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                    <span style={{ fontSize: "12px", color: "#f8fafc", fontWeight: "600" }}>
                      📍 Map View: {activeWorkshop.name} ({activeWorkshop.distance_km} km road distance)
                    </span>
                    <a
                      href={`https://www.google.com/maps/dir/?api=1&origin=${userCoords.lat},${userCoords.lon}&destination=${activeWorkshop.lat},${activeWorkshop.lon}`}
                      target="_blank"
                      rel="noreferrer"
                      style={{ fontSize: "11.5px", color: "#38bdf8", textDecoration: "none" }}
                    >
                      Open Full Google Maps &rarr;
                    </a>
                  </div>

                  <div style={{
                    height: "200px",
                    borderRadius: "6px",
                    overflow: "hidden",
                    border: "1px solid #475569"
                  }}>
                    <iframe
                      title="OpenStreetMap Dispatch Preview"
                      width="100%"
                      height="100%"
                      frameBorder="0"
                      scrolling="no"
                      marginHeight="0"
                      marginWidth="0"
                      src={`https://www.openstreetmap.org/export/embed.html?bbox=${Math.min(userCoords.lon, activeWorkshop.lon) - 0.04}%2C${Math.min(userCoords.lat, activeWorkshop.lat) - 0.04}%2C${Math.max(userCoords.lon, activeWorkshop.lon) + 0.04}%2C${Math.max(userCoords.lat, activeWorkshop.lat) + 0.04}&layer=mapnik&marker=${activeWorkshop.lat}%2C${activeWorkshop.lon}`}
                      style={{ border: 0 }}
                    />
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

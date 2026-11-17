import React, { useState, useEffect } from "react";
import { post, get } from "../api/client";

export default function LiveMechanicDispatch({
  dtcCode = null,
  symptomQuery = "",
  initialCity = "Lahore",
  vehicleMake = "Toyota",
}) {
  const [loading, setLoading] = useState(false);
  const [city, setCity] = useState(initialCity);
  const [userCoords, setUserCoords] = useState({ lat: 31.5204, lon: 74.3587 }); // Default Lahore
  const [locationStatus, setLocationStatus] = useState("Preset Location (Lahore Center)");
  const [isLiveGps, setIsLiveGps] = useState(false);
  const [dispatchData, setDispatchData] = useState(null);
  const [selectedWorkshop, setSelectedWorkshop] = useState(null);
  const [error, setError] = useState(null);

  // Preset Pakistani City Coordinates
  const CITY_COORDS = {
    Lahore: { lat: 31.5204, lon: 74.3587, name: "Lahore (Bilal Gunj / Montgomery Rd)" },
    Karachi: { lat: 24.8607, lon: 67.0011, name: "Karachi (Shershah / Plaza)" },
    Islamabad: { lat: 33.6844, lon: 73.0479, name: "Islamabad (Sector I-9 / G-10)" },
    Rawalpindi: { lat: 33.5651, lon: 73.0169, name: "Rawalpindi (Sultan ka Khoo / Peshawar Rd)" },
  };

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
        setLocationStatus(`📍 Live GPS Active (Accurate to ${Math.round(pos.coords.accuracy)}m)`);
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
      setLocationStatus(`Preset Location (${newCity} Market Hub)`);
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

  return (
    <div style={{
      background: "var(--surface-1, #1e293b)",
      border: "1px solid var(--border, #334155)",
      borderRadius: "16px",
      padding: "20px",
      marginTop: "20px",
      color: "var(--text-primary, #f8fafc)",
      boxShadow: "0 8px 24px rgba(0,0,0,0.25)"
    }}>
      {/* Header Bar */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px", borderBottom: "1px solid #334155", paddingBottom: "14px", marginBottom: "16px" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ fontSize: "20px" }}>📍</span>
            <h3 style={{ margin: 0, fontSize: "17px", fontWeight: "700" }}>
              Live Fault-to-Specialist Dispatch Engine
            </h3>
            <span style={{
              background: isLiveGps ? "#05966920" : "#0284c720",
              color: isLiveGps ? "#10b981" : "#38bdf8",
              border: `1px solid ${isLiveGps ? "#059669" : "#0284c7"}`,
              padding: "2px 8px",
              borderRadius: "12px",
              fontSize: "11px",
              fontWeight: "600"
            }}>
              {isLiveGps ? "● LIVE GPS" : "● PRESET CITY"}
            </span>
          </div>
          <p style={{ margin: "4px 0 0", fontSize: "12px", color: "#94a3b8" }}>
            {locationStatus} — Lat: {userCoords.lat.toFixed(4)}°, Lon: {userCoords.lon.toFixed(4)}°
          </p>
        </div>

        <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
          <button
            type="button"
            onClick={requestLiveLocation}
            style={{
              background: "#0284c7",
              color: "#ffffff",
              border: "none",
              padding: "7px 14px",
              borderRadius: "8px",
              fontSize: "12px",
              fontWeight: "600",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "6px"
            }}
          >
            <span>🎯</span> Use My Live Location
          </button>

          <select
            value={city}
            onChange={(e) => handleCityChange(e.target.value)}
            style={{
              background: "#0f172a",
              color: "#f8fafc",
              border: "1px solid #475569",
              padding: "7px 12px",
              borderRadius: "8px",
              fontSize: "12px"
            }}
          >
            <option value="Lahore">Lahore Market</option>
            <option value="Karachi">Karachi Market</option>
            <option value="Islamabad">Islamabad Hub</option>
            <option value="Rawalpindi">Rawalpindi Market</option>
          </select>
        </div>
      </div>

      {loading && (
        <div style={{ textAlign: "center", padding: "30px 0", color: "#94a3b8", fontSize: "13px" }}>
          🔄 Computing Haversine Proximity &amp; Specialty Match Scores…
        </div>
      )}

      {error && (
        <div style={{ background: "#ef444420", border: "1px solid #ef4444", padding: "12px", borderRadius: "8px", color: "#fca5a5", fontSize: "12.5px" }}>
          ⚠️ {error}
        </div>
      )}

      {dispatchData && !loading && (
        <div>
          {/* Diagnostic Match Banner */}
          <div style={{
            background: "#0f172a",
            border: "1px solid #334155",
            borderRadius: "10px",
            padding: "12px 16px",
            marginBottom: "16px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: "10px"
          }}>
            <div>
              <span style={{ fontSize: "11px", color: "#94a3b8", textTransform: "uppercase", fontWeight: "700" }}>Diagnosed Subsystem Specialty</span>
              <h4 style={{ margin: "2px 0", fontSize: "15px", color: "#38bdf8" }}>
                🛠️ {dispatchData.specialty_title}
              </h4>
              <p style={{ margin: 0, fontSize: "12px", color: "#cbd5e1" }}>
                {dispatchData.specialty_description}
              </p>
            </div>
            <div style={{ textAlign: "right" }}>
              <span style={{ fontSize: "11px", color: "#94a3b8", textTransform: "uppercase", fontWeight: "700" }}>Verified Fair PKR Range</span>
              <div style={{ fontSize: "16px", fontWeight: "800", color: "#10b981" }}>
                Rs. {dispatchData.fair_price_pkr.low.toLocaleString()} – {dispatchData.fair_price_pkr.high.toLocaleString()}
              </div>
              <small style={{ color: "#64748b", fontSize: "10px" }}>Market median: Rs. {dispatchData.fair_price_pkr.median.toLocaleString()}</small>
            </div>
          </div>

          {/* 2-Column Layout: Left List, Right Map Radar */}
          <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: "16px" }}>
            
            {/* Workshop Cards List */}
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              <span style={{ fontSize: "12px", color: "#94a3b8", fontWeight: "700", textTransform: "uppercase" }}>
                Top Ranked Specialist Workshops Nearby ({dispatchData.recommendations.length} Found)
              </span>

              {dispatchData.recommendations.map((w, idx) => {
                const isSelected = selectedWorkshop && selectedWorkshop.workshop_id === w.workshop_id;
                return (
                  <div
                    key={w.workshop_id}
                    onClick={() => setSelectedWorkshop(w)}
                    style={{
                      background: isSelected ? "#1e293b" : "#0f172a",
                      border: `2px solid ${isSelected ? "#0284c7" : "#334155"}`,
                      borderRadius: "10px",
                      padding: "12px 14px",
                      cursor: "pointer",
                      transition: "all 0.2s ease"
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                      <div>
                        <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                          <span style={{ background: "#0284c7", color: "#fff", width: "20px", height: "20px", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "11px", fontWeight: "bold" }}>
                            {idx + 1}
                          </span>
                          <b style={{ fontSize: "14px", color: "#f8fafc" }}>{w.name}</b>
                        </div>
                        <p style={{ margin: "3px 0 0 26px", fontSize: "11.5px", color: "#94a3b8" }}>
                          📍 {w.area}, {w.city}
                        </p>
                      </div>

                      <div style={{ textAlign: "right" }}>
                        <span style={{
                          background: "#10b98120",
                          color: "#10b981",
                          border: "1px solid #10b98140",
                          padding: "2px 6px",
                          borderRadius: "4px",
                          fontSize: "11px",
                          fontWeight: "700"
                        }}>
                          {Math.round(w.composite_score * 100)}% Match
                        </span>
                        <div style={{ fontSize: "12px", color: "#38bdf8", fontWeight: "700", marginTop: "3px" }}>
                          🚗 {w.distance_km} km away
                        </div>
                      </div>
                    </div>

                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "10px", paddingTop: "8px", borderTop: "1px solid #334155/60", fontSize: "11px", color: "#cbd5e1" }}>
                      <span>⭐ {w.rating} / 5.0 ({w.review_count} reviews)</span>
                      <span>🟢 {w.active_queue_slots ? `${w.active_queue_slots} Bays Open` : "Available Now"}</span>
                      <span style={{ color: "#38bdf8" }}>OEM: {w.verified_oem.join(", ")}</span>
                    </div>

                    {/* Action buttons on active card */}
                    {isSelected && (
                      <div style={{ display: "flex", gap: "8px", marginTop: "10px", paddingTop: "8px", borderTop: "1px solid #0284c7" }}>
                        <a
                          href={`https://www.google.com/maps/dir/?api=1&origin=${userCoords.lat},${userCoords.lon}&destination=${w.lat},${w.lon}`}
                          target="_blank"
                          rel="noreferrer"
                          style={{
                            flex: 1,
                            background: "#0284c7",
                            color: "#fff",
                            textAlign: "center",
                            padding: "6px 0",
                            borderRadius: "6px",
                            textDecoration: "none",
                            fontSize: "11.5px",
                            fontWeight: "600"
                          }}
                        >
                          🗺️ Turn-by-Turn Route
                        </a>
                        <a
                          href={`tel:${w.contact}`}
                          style={{
                            flex: 1,
                            background: "#059669",
                            color: "#fff",
                            textAlign: "center",
                            padding: "6px 0",
                            borderRadius: "6px",
                            textDecoration: "none",
                            fontSize: "11.5px",
                            fontWeight: "600"
                          }}
                        >
                          📞 Call: {w.contact}
                        </a>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Right Map Preview & Radar */}
            <div style={{
              background: "#0f172a",
              border: "1px solid #334155",
              borderRadius: "10px",
              padding: "14px",
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between"
            }}>
              <div>
                <span style={{ fontSize: "12px", color: "#94a3b8", fontWeight: "700", textTransform: "uppercase" }}>
                  Live Navigation &amp; Routing View
                </span>
                
                {selectedWorkshop ? (
                  <div style={{ marginTop: "10px" }}>
                    <div style={{ background: "#1e293b", padding: "10px", borderRadius: "8px", marginBottom: "12px", border: "1px solid #475569" }}>
                      <div style={{ fontSize: "11px", color: "#94a3b8" }}>TARGET SPECIALIST DESTINATION:</div>
                      <b style={{ fontSize: "13px", color: "#f8fafc" }}>{selectedWorkshop.name}</b>
                      <div style={{ fontSize: "11.5px", color: "#38bdf8", marginTop: "2px" }}>
                        📍 {selectedWorkshop.area} ({selectedWorkshop.distance_km} km road distance)
                      </div>
                    </div>

                    {/* OpenStreetMap Dynamic Embed */}
                    <div style={{
                      height: "220px",
                      borderRadius: "8px",
                      overflow: "hidden",
                      border: "1px solid #475569",
                      position: "relative"
                    }}>
                      <iframe
                        title="OpenStreetMap Dispatch Preview"
                        width="100%"
                        height="100%"
                        frameBorder="0"
                        scrolling="no"
                        marginHeight="0"
                        marginWidth="0"
                        src={`https://www.openstreetmap.org/export/embed.html?bbox=${Math.min(userCoords.lon, selectedWorkshop.lon) - 0.05}%2C${Math.min(userCoords.lat, selectedWorkshop.lat) - 0.05}%2C${Math.max(userCoords.lon, selectedWorkshop.lon) + 0.05}%2C${Math.max(userCoords.lat, selectedWorkshop.lat) + 0.05}&layer=mapnik&marker=${selectedWorkshop.lat}%2C${selectedWorkshop.lon}`}
                        style={{ border: 0 }}
                      />
                    </div>
                  </div>
                ) : (
                  <div style={{ color: "#64748b", padding: "40px 0", textAlign: "center" }}>
                    Select a workshop to preview route
                  </div>
                )}
              </div>

              <div style={{ marginTop: "12px", fontSize: "10.5px", color: "#64748b", lineHeight: 1.4 }}>
                ℹ️ <b>Routing Logic:</b> Computed using Haversine great-circle distance from your location with multi-criteria composite weighting (40% Skill Match, 30% Distance, 20% Customer Rating, 10% Open Bay Slots).
              </div>
            </div>

          </div>
        </div>
      )}
    </div>
  );
}

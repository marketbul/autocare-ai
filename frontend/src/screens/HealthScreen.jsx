import { useEffect, useState } from "react";
import { fetchMaintenancePrediction, fetchVehicleHealth } from "../api/diagnose";
import { VehiclePicker } from "./ui";

export function HealthScreen({ vehicles, activeId, onPickVehicle, go }) {
  const [health, setHealth] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const car = vehicles.find((v) => v.user_vehicle_id === activeId);

  useEffect(() => {
    if (!activeId) return;
    setLoading(true);
    setError("");
    Promise.all([
      fetchVehicleHealth(activeId),
      fetchMaintenancePrediction(activeId),
    ])
      .then(([hData, pData]) => {
        setHealth(hData);
        setPrediction(pData);
      })
      .catch((err) => setError(err?.message || "Could not load health metrics."))
      .finally(() => setLoading(false));
  }, [activeId]);

  return (
    <div className="view-page">
      <header className="page-head">
        <div>
          <h2>Vehicle Health Index & Maintenance Predictor</h2>
          <p className="page-lead">
            Structured condition summary across 6 component groups and personalized prediction of your next required service.
          </p>
        </div>
        <VehiclePicker vehicles={vehicles} activeId={activeId} onPick={onPickVehicle} go={go} />
      </header>

      {!activeId && (
        <div className="notice notice-info">Please select one of your vehicles to view its health index.</div>
      )}

      {loading && <div className="notice">Analyzing service records and maintenance schedules...</div>}
      {error && <div className="notice notice-danger">{error}</div>}

      {prediction && (
        <div className="card prediction-card">
          <div className="pred-header">
            <span className="pred-label">FORECASTED NEXT SERVICE</span>
            <span className={`badge badge-urgency-${prediction.urgency}`}>
              {prediction.urgency.toUpperCase()}
            </span>
          </div>
          <h3 className="pred-item">{prediction.next_item}</h3>
          <p className="pred-details">
            Expected at <b>{prediction.target_mileage.toLocaleString()} km</b> (Window: {prediction.mileage_window[0].toLocaleString()} – {prediction.mileage_window[1].toLocaleString()} km)
          </p>
          <p className="pred-date">
            Estimated Due Date: <b>{new Date(prediction.estimated_due_date).toLocaleDateString()}</b> ({prediction.days_remaining} days remaining)
          </p>
          <small className="pred-rationale">{prediction.rationale}</small>
        </div>
      )}

      {health && (
        <div className="card health-card">
          <div className="composite-header">
            <div>
              <h3>Overall Vehicle Health Index</h3>
              <p className="composite-status">Status: <b>{health.status.toUpperCase()}</b></p>
            </div>
            <div className="composite-badge">
              <span className="composite-score">{health.composite_score}%</span>
            </div>
          </div>

          <div className="groups-grid">
            {Object.entries(health.groups).map(([groupKey, g]) => (
              <div key={groupKey} className={`group-item group-status-${g.status}`}>
                <div className="group-title-row">
                  <b>{g.group.toUpperCase()}</b>
                  <span className="group-score">{g.score}%</span>
                </div>
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{
                      width: `${g.score}%`,
                      backgroundColor: g.score > 75 ? "#16a34a" : g.score > 50 ? "#eab308" : "#dc2626"
                    }}
                  />
                </div>
                <div className="group-meta">
                  <small>Mileage since service: {g.mileage_since_service.toLocaleString()} km</small>
                  {g.open_faults_count > 0 && (
                    <small className="text-danger">⚠️ {g.open_faults_count} active fault recorded</small>
                  )}
                </div>
                <p className="group-rec">{g.recommendation}</p>
              </div>
            ))}
          </div>

          <div className="health-disclaimer">
            <small>{health.disclaimer}</small>
          </div>
        </div>
      )}
    </div>
  );
}

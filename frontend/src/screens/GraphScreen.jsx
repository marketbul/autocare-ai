import { useEffect, useState } from "react";
import { get } from "../api/client";

export function GraphScreen() {
  const [graphData, setGraphData] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [filterType, setFilterType] = useState("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    get("/api/v1/diagnose/graph/export")
      .then((data) => {
        setGraphData(data);
        if (data?.nodes?.length > 0) {
          // Default to engine_overheating or first symptom
          const init = data.nodes.find((n) => n.id.includes("overheating")) || data.nodes[0];
          setSelectedNode(init);
        }
      })
      .catch((err) => console.error("Could not fetch graph:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="card loading-state">Constructing Causal Knowledge Graph...</div>;
  }

  const nodes = graphData?.nodes || [];
  const edges = graphData?.edges || [];
  const stats = graphData?.stats || { total_nodes: 0, total_edges: 0 };

  const filteredNodes = filterType === "all" ? nodes : nodes.filter((n) => n.type === filterType);

  // Incoming and outgoing causal edges for selected node
  const outgoing = edges.filter((e) => e.source === selectedNode?.id);
  const incoming = edges.filter((e) => e.target === selectedNode?.id);

  return (
    <div className="card graph-screen">
      <div className="screen-header">
        <div>
          <h2>Automotive Causal Knowledge Graph (M6)</h2>
          <p className="screen-subtitle">
            Multi-hop directed causal inference engine developed by <b>Talha Ali Bhatti</b> (AI-ML Lead).
          </p>
        </div>
        <div className="badge-group">
          <span className="badge badge-accent">{stats.total_nodes} Nodes</span>
          <span className="badge badge-success">{stats.total_edges} Causal Edges</span>
        </div>
      </div>

      {/* Filter Chips */}
      <div className="filter-bar" style={{ display: "flex", gap: "8px", margin: "16px 0" }}>
        {["all", "symptom", "failure_mode", "root_cause", "dtc"].map((type) => (
          <button
            key={type}
            className={`btn-filter ${filterType === type ? "active" : ""}`}
            onClick={() => setFilterType(type)}
            style={{
              padding: "6px 14px",
              borderRadius: "20px",
              fontSize: "0.82rem",
              textTransform: "capitalize",
              border: "1px solid var(--border)",
              background: filterType === type ? "var(--accent)" : "transparent",
              color: filterType === type ? "#fff" : "var(--muted)",
              cursor: "pointer"
            }}
          >
            {type.replace("_", " ")}
          </button>
        ))}
      </div>

      <div className="graph-layout" style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: "20px" }}>
        {/* Node Grid / Map */}
        <div className="node-canvas-box" style={{ background: "rgba(0,0,0,0.2)", borderRadius: "10px", padding: "16px", maxHeight: "520px", overflowY: "auto" }}>
          <h4 style={{ margin: "0 0 12px 0", fontSize: "0.9rem", color: "var(--muted)" }}>
            Select a Graph Node to Inspect Causal Traversal:
          </h4>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
            {filteredNodes.map((n) => {
              const isSelected = n.id === selectedNode?.id;
              let bg = "rgba(255,255,255,0.05)";
              let color = "#e2e8f0";
              if (n.type === "root_cause") { bg = "rgba(239, 68, 68, 0.15)"; color = "#f87171"; }
              if (n.type === "symptom") { bg = "rgba(245, 158, 11, 0.15)"; color = "#fbbf24"; }
              if (n.type === "failure_mode") { bg = "rgba(59, 130, 246, 0.15)"; color = "#60a5fa"; }

              return (
                <button
                  key={n.id}
                  onClick={() => setSelectedNode(n)}
                  style={{
                    background: isSelected ? "var(--accent)" : bg,
                    color: isSelected ? "#fff" : color,
                    border: `1px solid ${isSelected ? "var(--accent)" : "rgba(255,255,255,0.1)"}`,
                    borderRadius: "6px",
                    padding: "8px 12px",
                    cursor: "pointer",
                    fontSize: "0.8rem",
                    fontWeight: isSelected ? "600" : "normal",
                    transition: "all 0.15s ease"
                  }}
                >
                  {n.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Selected Node Details & Causal Pathways */}
        <div className="node-detail-panel" style={{ background: "rgba(255,255,255,0.02)", border: "1px solid var(--border)", borderRadius: "10px", padding: "18px" }}>
          {selectedNode ? (
            <>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "12px" }}>
                <div>
                  <span style={{ fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--muted)" }}>
                    Type: {selectedNode.type.replace("_", " ")}
                  </span>
                  <h3 style={{ margin: "4px 0 0 0", color: "#f8fafc" }}>{selectedNode.label}</h3>
                  <code style={{ fontSize: "0.75rem", color: "#94a3b8" }}>node_id: {selectedNode.id}</code>
                </div>
              </div>

              {/* Outgoing Causal Consequence */}
              <div style={{ marginTop: "18px" }}>
                <h4 style={{ fontSize: "0.85rem", color: "#38bdf8", marginBottom: "8px" }}>
                  → Downstream Causal Consequences ({outgoing.length}):
                </h4>
                {outgoing.length > 0 ? (
                  <ul style={{ paddingLeft: "18px", margin: 0, fontSize: "0.85rem", lineHeight: "1.6" }}>
                    {outgoing.map((e, idx) => (
                      <li key={idx}>
                        Causes <b>{nodes.find((n) => n.id === e.target)?.label || e.target}</b>{" "}
                        <span style={{ color: "var(--muted)", fontSize: "0.78rem" }}>
                          (rel: {e.relation}, weight: {e.weight})
                        </span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p style={{ color: "var(--muted)", fontSize: "0.8rem", margin: 0 }}>
                    Terminal leaf node (observable symptom).
                  </p>
                )}
              </div>

              {/* Incoming Root Cause */}
              <div style={{ marginTop: "18px" }}>
                <h4 style={{ fontSize: "0.85rem", color: "#f43f5e", marginBottom: "8px" }}>
                  ← Upstream Mechanical Root Causes ({incoming.length}):
                </h4>
                {incoming.length > 0 ? (
                  <ul style={{ paddingLeft: "18px", margin: 0, fontSize: "0.85rem", lineHeight: "1.6" }}>
                    {incoming.map((e, idx) => (
                      <li key={idx}>
                        Triggered by <b>{nodes.find((n) => n.id === e.source)?.label || e.source}</b>{" "}
                        <span style={{ color: "var(--muted)", fontSize: "0.78rem" }}>
                          (rel: {e.relation}, weight: {e.weight})
                        </span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p style={{ color: "var(--muted)", fontSize: "0.8rem", margin: 0 }}>
                    Root causal origin (physical hardware defect or failure).
                  </p>
                )}
              </div>
            </>
          ) : (
            <p style={{ color: "var(--muted)" }}>Click any node on the left to inspect causal paths.</p>
          )}
        </div>
      </div>
    </div>
  );
}

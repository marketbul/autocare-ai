import { useEffect, useState } from "react";
import { get } from "../api/client";

export function CorpusScreen() {
  const [data, setData] = useState(null);
  const [filterVehicle, setFilterVehicle] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedManual, setSelectedManual] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    get("/api/v1/corpus/overview")
      .then((res) => {
        setData(res);
        if (res?.manuals?.length > 0) {
          setSelectedManual(res.manuals[0]);
        }
      })
      .catch((err) => console.error("Error fetching corpus overview:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="card loading-state">Indexing 45 Workshop Manuals Corpus...</div>;
  }

  const manuals = data?.manuals || [];
  const filtered = manuals.filter((m) => {
    const matchesVehicle = filterVehicle === "all" || m.vehicle === filterVehicle;
    const matchesSearch = !searchTerm || m.title.toLowerCase().includes(searchTerm.toLowerCase()) || String(m.year).includes(searchTerm);
    return matchesVehicle && matchesSearch;
  });

  return (
    <div className="card corpus-screen">
      <div className="screen-header">
        <div>
          <h2>Automotive Technical Manuals Corpus (45 Manuals)</h2>
          <p className="screen-subtitle">
            Curated workshop and owner manuals corpus spanning 2015-2025 across Pakistan&apos;s leading passenger cars.
            Engineered by <b>Danial Hameed</b> (Data & Retrieval Lead).
          </p>
        </div>
        <div className="badge-group" style={{ display: "flex", gap: "8px" }}>
          <span className="badge badge-accent">45 Manuals (100% Complete)</span>
          <span className="badge badge-success">326 Indexed Chunks</span>
        </div>
      </div>

      {/* Metric Cards Banner */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "12px", margin: "18px 0" }}>
        <div style={{ background: "rgba(56, 189, 248, 0.05)", border: "1px solid rgba(56, 189, 248, 0.2)", borderRadius: "8px", padding: "12px 16px" }}>
          <span style={{ fontSize: "0.75rem", color: "var(--muted)" }}>Vehicles Covered</span>
          <div style={{ fontSize: "1.2rem", fontWeight: "700", color: "#38bdf8", marginTop: "4px" }}>Corolla, Civic, Swift</div>
          <small style={{ color: "var(--muted)", fontSize: "0.72rem" }}>15 Manuals per model line</small>
        </div>

        <div style={{ background: "rgba(52, 211, 153, 0.05)", border: "1px solid rgba(52, 211, 153, 0.2)", borderRadius: "8px", padding: "12px 16px" }}>
          <span style={{ fontSize: "0.75rem", color: "var(--muted)" }}>Hybrid Retrieval Index</span>
          <div style={{ fontSize: "1.2rem", fontWeight: "700", color: "#34d399", marginTop: "4px" }}>BM25 + BGE-M3</div>
          <small style={{ color: "var(--muted)", fontSize: "0.72rem" }}>Dense + sparse reciprocal rank fusion</small>
        </div>

        <div style={{ background: "rgba(168, 85, 247, 0.05)", border: "1px solid rgba(168, 85, 247, 0.2)", borderRadius: "8px", padding: "12px 16px" }}>
          <span style={{ fontSize: "0.75rem", color: "var(--muted)" }}>Multilingual Query Parser</span>
          <div style={{ fontSize: "1.2rem", fontWeight: "700", color: "#c084fc", marginTop: "4px" }}>Urdu & Roman Urdu</div>
          <small style={{ color: "var(--muted)", fontSize: "0.72rem" }}>140+ colloquial automotive terms</small>
        </div>

        <div style={{ background: "rgba(245, 158, 11, 0.05)", border: "1px solid rgba(245, 158, 11, 0.2)", borderRadius: "8px", padding: "12px 16px" }}>
          <span style={{ fontSize: "0.75rem", color: "var(--muted)" }}>Citation Grounding</span>
          <div style={{ fontSize: "1.2rem", fontWeight: "700", color: "#fbbf24", marginTop: "4px" }}>Verbatim NLI Bounds</div>
          <small style={{ color: "var(--muted)", fontSize: "0.72rem" }}>Zero hallucination tolerance</small>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div style={{ display: "flex", gap: "12px", alignItems: "center", marginBottom: "16px", flexWrap: "wrap" }}>
        <input
          type="search"
          placeholder="Search manuals by year, trim, or subsystem..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            flex: "1 1 240px",
            padding: "8px 12px",
            borderRadius: "6px",
            border: "1px solid var(--border)",
            background: "var(--card-bg)",
            color: "#fff",
            fontSize: "0.85rem"
          }}
        />

        <div style={{ display: "flex", gap: "6px" }}>
          {[
            { id: "all", label: "All Vehicles (45)" },
            { id: "toyota_corolla", label: "Corolla (15)" },
            { id: "honda_civic", label: "Civic (15)" },
            { id: "suzuki_swift", label: "Swift (15)" }
          ].map((v) => (
            <button
              key={v.id}
              onClick={() => setFilterVehicle(v.id)}
              style={{
                padding: "6px 12px",
                borderRadius: "6px",
                border: filterVehicle === v.id ? "1px solid #38bdf8" : "1px solid var(--border)",
                background: filterVehicle === v.id ? "rgba(56, 189, 248, 0.15)" : "rgba(255, 255, 255, 0.02)",
                color: filterVehicle === v.id ? "#38bdf8" : "var(--muted)",
                cursor: "pointer",
                fontSize: "0.8rem",
                fontWeight: filterVehicle === v.id ? "600" : "normal"
              }}
            >
              {v.label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Two-Pane Explorer */}
      <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr", gap: "16px" }}>
        {/* Left List */}
        <div style={{ maxHeight: "560px", overflowY: "auto", border: "1px solid var(--border)", borderRadius: "8px", padding: "10px" }}>
          <div style={{ fontSize: "0.78rem", color: "var(--muted)", marginBottom: "8px", padding: "0 4px" }}>
            Showing {filtered.length} of {manuals.length} manuals:
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {filtered.map((m, idx) => {
              const isSelected = selectedManual?.title === m.title;
              return (
                <div
                  key={idx}
                  onClick={() => setSelectedManual(m)}
                  style={{
                    padding: "10px 12px",
                    borderRadius: "6px",
                    cursor: "pointer",
                    border: isSelected ? "1px solid #38bdf8" : "1px solid rgba(255, 255, 255, 0.05)",
                    background: isSelected ? "rgba(56, 189, 248, 0.08)" : "rgba(255, 255, 255, 0.02)",
                    transition: "all 0.15s ease"
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontWeight: "600", fontSize: "0.88rem", color: isSelected ? "#38bdf8" : "#f1f5f9" }}>
                      {m.title}
                    </span>
                    <span className="badge" style={{ fontSize: "0.7rem" }}>
                      {m.year}
                    </span>
                  </div>
                  <div style={{ display: "flex", gap: "10px", marginTop: "4px", fontSize: "0.75rem", color: "var(--muted)" }}>
                    <span>Model: {m.vehicle.replace("_", " ").toUpperCase()}</span>
                    <span>•</span>
                    <span>Format: PDF + Processed TXT Chunks</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Detail Inspector */}
        <div style={{ background: "rgba(255, 255, 255, 0.02)", border: "1px solid var(--border)", borderRadius: "8px", padding: "16px" }}>
          {selectedManual ? (
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "12px" }}>
                <div>
                  <h3 style={{ margin: "0 0 4px 0", fontSize: "1.05rem" }}>{selectedManual.title}</h3>
                  <span style={{ fontSize: "0.78rem", color: "var(--muted)" }}>
                    Vehicle Line: <b>{selectedManual.vehicle.replace("_", " ").toUpperCase()}</b> (Year {selectedManual.year})
                  </span>
                </div>
                <span className="badge badge-accent">Indexed</span>
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: "12px", marginTop: "16px", fontSize: "0.82rem" }}>
                <div>
                  <label style={{ color: "var(--muted)", display: "block", marginBottom: "2px" }}>Local Processed Text Chunks:</label>
                  <code style={{ fontSize: "0.78rem", background: "rgba(0,0,0,0.3)", padding: "4px 8px", borderRadius: "4px", display: "block" }}>
                    backend/{selectedManual.txt_path}
                  </code>
                </div>

                <div>
                  <label style={{ color: "var(--muted)", display: "block", marginBottom: "2px" }}>Local PDF Archive Path:</label>
                  <code style={{ fontSize: "0.78rem", background: "rgba(0,0,0,0.3)", padding: "4px 8px", borderRadius: "4px", display: "block" }}>
                    backend/{selectedManual.pdf_path}
                  </code>
                </div>

                <div>
                  <label style={{ color: "var(--muted)", display: "block", marginBottom: "2px" }}>Manufacturer Official Reference:</label>
                  <a
                    href={selectedManual.url}
                    target="_blank"
                    rel="noreferrer"
                    style={{ color: "#38bdf8", textDecoration: "underline", wordBreak: "break-all" }}
                  >
                    {selectedManual.url}
                  </a>
                </div>

                <div style={{ marginTop: "12px", padding: "12px", borderRadius: "6px", background: "rgba(56, 189, 248, 0.04)", border: "1px solid rgba(56, 189, 248, 0.15)" }}>
                  <h4 style={{ margin: "0 0 6px 0", fontSize: "0.85rem", color: "#38bdf8" }}>RAG Ingestion Architecture</h4>
                  <ul style={{ margin: 0, paddingLeft: "18px", color: "var(--muted)", fontSize: "0.76rem", lineHeight: 1.5 }}>
                    <li>Extracted with PyPDF2 / pdfplumber with hierarchical section boundary detection.</li>
                    <li>Tokenized with recursive text splitters (512-token chunks with 64-token overlap).</li>
                    <li>Dual indexed into SQLite FTS5 for BM25 lexical search and dense embedding tables.</li>
                    <li>Queried through hybrid Reciprocal Rank Fusion ($RRF(d) = \sum \frac&#123;1&#125;&#123;60 + r_k(d)&#125;$).</li>
                  </ul>
                </div>
              </div>
            </div>
          ) : (
            <div style={{ color: "var(--muted)", textAlign: "center", paddingTop: "80px" }}>
              Select a manual from the index to inspect metadata and retrieval pipeline specs.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

const statusLabels = {
  ready: "System ready",
  working: "Processing",
  complete: "Answer ready",
  error: "Needs attention",
};

export default function Header({
  requestState,
  ingest,
  ingesting,
  systemStatus,
  onRefreshStatus,
  activeTab,
  setActiveTab,
}) {
  const isHealthy = systemStatus?.status === "healthy";
  const pointsCount = systemStatus?.stats?.points_count ?? null;

  return (
    <header className="site-header">
      <div className="brand-lockup">
        <div className="signal-mark" aria-hidden="true">
          <span />
        </div>
        <div>
          <div className="brand-badge-row">
            <p className="eyebrow">NEXUSRAG / KNOWLEDGE CONSOLE</p>
            <span className="version-pill">v2.0</span>
          </div>
          <h1>Ask the corpus.</h1>
          <p className="subtitle">
            Grounded enterprise answers with real-time vector retrieval, document management, and latency telemetry.
          </p>
        </div>
      </div>

      <div className="header-actions">
        <div className="status-indicators">
          <span className={`status status-${requestState}`}>
            <span className="status-dot" />
            {statusLabels[requestState]}
          </span>

          {systemStatus && (
            <span
              className={`health-badge ${isHealthy ? "health-ok" : "health-warn"}`}
              title="System Connectivity"
              onClick={onRefreshStatus}
              role="button"
              tabIndex={0}
            >
              ● {isHealthy ? "Services Online" : "Degraded"}
              {pointsCount !== null && ` (${pointsCount} vectors)`}
            </span>
          )}
        </div>

        <div className="header-controls">
          <nav className="tab-navigation" aria-label="Console navigation">
            <button
              type="button"
              className={`tab-btn ${activeTab === "query" ? "active" : ""}`}
              onClick={() => setActiveTab("query")}
            >
              Query Console
            </button>
            <button
              type="button"
              className={`tab-btn ${activeTab === "documents" ? "active" : ""}`}
              onClick={() => setActiveTab("documents")}
            >
              Add Document
            </button>
            <button
              type="button"
              className={`tab-btn ${activeTab === "system" ? "active" : ""}`}
              onClick={() => setActiveTab("system")}
            >
              System Health
            </button>
          </nav>

          <button
            className="secondary-button"
            onClick={ingest}
            disabled={ingesting}
            title="Re-index corpus.json into Qdrant"
          >
            {ingesting ? "Indexing..." : "Index Corpus"}
          </button>
        </div>
      </div>
    </header>
  );
}


export default function SystemStatusModal({ systemStatus, onRefresh, loading }) {
  if (!systemStatus) return null;

  const { status, version, qdrant, embedding_service, llm_service, stats } = systemStatus;

  return (
    <section className="system-health-panel">
      <div className="panel-heading">
        <div>
          <p className="section-kicker">INFRASTRUCTURE TELEMETRY</p>
          <h2>System Health & Diagnostics</h2>
        </div>
        <button
          type="button"
          className="secondary-button refresh-btn"
          onClick={onRefresh}
          disabled={loading}
        >
          {loading ? "Checking..." : "↻ Refresh Diagnostics"}
        </button>
      </div>

      <div className="health-grid">
        <div className="health-card">
          <div className="health-card-header">
            <h3>Qdrant Vector DB</h3>
            <span className={`status-pill ${qdrant?.reachable ? "pill-ok" : "pill-fail"}`}>
              {qdrant?.reachable ? "Reachable" : "Unreachable"}
            </span>
          </div>
          <p className="health-card-metric">
            Vectors Indexed: <b>{stats?.points_count ?? 0}</b>
          </p>
          <p className="health-card-meta">
            Target Collection: <code>{stats?.name || "rag_documents"}</code>
          </p>
          <p className="health-card-meta">
            State: <b>{stats?.status || "Unknown"}</b>
          </p>
        </div>

        <div className="health-card">
          <div className="health-card-header">
            <h3>Embedding Service</h3>
            <span className={`status-pill ${embedding_service?.reachable ? "pill-ok" : "pill-fail"}`}>
              {embedding_service?.reachable ? "Reachable" : "Unreachable"}
            </span>
          </div>
          <p className="health-card-metric">
            Model: <b>{embedding_service?.details?.model || "all-MiniLM-L6-v2"}</b>
          </p>
          <p className="health-card-meta">
            Vector Dimension: <b>{embedding_service?.details?.dimension || 384}d</b>
          </p>
          <p className="health-card-meta">
            Port: <code>8001</code>
          </p>
        </div>

        <div className="health-card">
          <div className="health-card-header">
            <h3>Ollama LLM Engine</h3>
            <span className={`status-pill ${llm_service?.reachable ? "pill-ok" : "pill-fail"}`}>
              {llm_service?.reachable ? "Reachable" : "Unreachable"}
            </span>
          </div>
          <p className="health-card-metric">
            Available Models: <b>{llm_service?.models?.length ?? 0}</b>
          </p>
          <div className="model-tags">
            {llm_service?.models?.map((m) => (
              <span key={m} className="model-chip">
                {m}
              </span>
            ))}
          </div>
          <p className="health-card-meta">
            Endpoint: <code>11434</code>
          </p>
        </div>
      </div>

      <div className="system-summary-footer">
        <span>Overall Pipeline State: <b>{status.toUpperCase()}</b></span>
        <span>Version: <b>{version}</b></span>
      </div>
    </section>
  );
}

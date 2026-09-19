const statusLabels = {
  ready: "System ready",
  working: "Processing",
  complete: "Answer ready",
  error: "Needs attention",
};

export default function Header({ requestState, ingest, ingesting }) {
  return (
    <header>
      <div className="brand-lockup">
        <div className="signal-mark" aria-hidden="true"><span /></div>
        <div>
          <p className="eyebrow">NEXUSRAG / KNOWLEDGE CONSOLE</p>
          <h1>Ask the corpus.</h1>
          <p className="subtitle">
            Grounded answers from your indexed documents, with every source
            and latency signal visible.
          </p>
        </div>
      </div>
      <div className="header-actions">
        <span className={`status status-${requestState}`}>
          <span className="status-dot" />
          {statusLabels[requestState]}
        </span>
        <button className="secondary-button" onClick={ingest} disabled={ingesting}>
          {ingesting ? "Indexing..." : "Index corpus"}
        </button>
      </div>
    </header>
  );
}

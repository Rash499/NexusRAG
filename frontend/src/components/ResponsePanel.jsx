import { useState } from "react";

export default function ResponsePanel({ answer, question }) {
  const [copied, setCopied] = useState(false);
  const [filterQuery, setFilterQuery] = useState("");

  const copyToClipboard = () => {
    if (!answer?.answer) return;
    navigator.clipboard.writeText(answer.answer);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const sources = answer?.sources || [];
  const filteredSources = filterQuery.trim()
    ? sources.filter(
        (s) =>
          s.title.toLowerCase().includes(filterQuery.toLowerCase()) ||
          s.text.toLowerCase().includes(filterQuery.toLowerCase())
      )
    : sources;

  return (
    <section className="result">
      <div className="result-heading">
        <div>
          <p className="section-kicker">02 / RESPONSE & SYNTHESIS</p>
          <h2>Grounded Answer</h2>
        </div>
        <div className="result-actions">
          <button
            type="button"
            className="copy-button"
            onClick={copyToClipboard}
            title="Copy answer markdown to clipboard"
          >
            {copied ? "✓ Copied" : "Copy Markdown"}
          </button>
          <span className="confidence-label">
            {sources.length} sources retrieved
          </span>
        </div>
      </div>

      <div className="answer">
        <span className="quote-mark">“</span>
        {answer.answer}
      </div>

      {answer.grounded === false && (
        <div className="low-grounding-notice">
          ⚠️ Low similarity score detected. Answer might be generalized or outside indexed corpus.
        </div>
      )}

      <div className="metrics">
        <span>
          <b>Retrieval</b>
          {answer.retrieval_latency_ms ?? 0} ms
        </span>
        <span>
          <b>Generation</b>
          {answer.llm_latency_ms ?? 0} ms
        </span>
        <span>
          <b>Total</b>
          {answer.total_latency_ms ?? 0} ms
        </span>
        <span>
          <b>Similarity</b>
          {answer.average_similarity ?? 0}
        </span>
      </div>

      <div className="sources-heading">
        <div>
          <p className="section-kicker">03 / EVIDENCE & RELEVANCE</p>
          <h2>Retrieved Context Chunks</h2>
        </div>
        <div className="sources-search-filter">
          <input
            type="text"
            placeholder="Filter source chunks..."
            value={filterQuery}
            onChange={(e) => setFilterQuery(e.target.value)}
            className="filter-input"
          />
        </div>
      </div>

      <div className="sources">
        {filteredSources.map((source, index) => (
          <article key={source.id || index} className="source-card">
            <div className="source-header">
              <div className="source-title">
                <span className="source-rank">0{index + 1}</span>
                <strong>{source.title}</strong>
                {source.source && (
                  <span className="source-file-badge">{source.source}</span>
                )}
              </div>
              <span className="score">
                score: {typeof source.score === "number" ? source.score.toFixed(3) : source.score}
              </span>
            </div>
            <p>{source.text}</p>
          </article>
        ))}

        {filteredSources.length === 0 && (
          <div className="no-sources-message">
            No source chunks matched &apos;{filterQuery}&apos;
          </div>
        )}
      </div>
    </section>
  );
}


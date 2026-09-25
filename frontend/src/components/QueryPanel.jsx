import { useState } from "react";

const examples = [
  "What does an NSG control?",
  "What is Terraform used for?",
  "What does a Kubernetes Deployment manage?",
  "What is Docker containerization?",
];

export default function QueryPanel({
  question,
  loading,
  setQuestion,
  ask,
  clearQuestion,
  topK,
  setTopK,
  minSimilarity,
  setMinSimilarity,
  isStreaming,
  setIsStreaming,
  searchHistory,
  onSelectHistory,
}) {
  const [showAdvanced, setShowAdvanced] = useState(false);

  return (
    <section className="query-panel">
      <div className="panel-heading">
        <div>
          <p className="section-kicker">01 / RETRIEVAL & QUERY</p>
          <h2>What do you want to know?</h2>
        </div>
        <div className="panel-heading-meta">
          <button
            type="button"
            className="config-toggle-btn"
            onClick={() => setShowAdvanced(!showAdvanced)}
          >
            {showAdvanced ? "▲ Hide Parameters" : "⚙ Advanced Parameters"}
          </button>
          <span className="model-label">llama3.2:3b</span>
        </div>
      </div>

      {showAdvanced && (
        <div className="advanced-controls-card">
          <div className="control-group">
            <label htmlFor="top-k-input">
              Top K Chunks: <b>{topK}</b>
            </label>
            <input
              id="top-k-input"
              type="range"
              min="1"
              max="15"
              value={topK}
              onChange={(e) => setTopK(Number(e.target.value))}
            />
          </div>

          <div className="control-group">
            <label htmlFor="similarity-input">
              Min Similarity Threshold: <b>{minSimilarity}</b>
            </label>
            <input
              id="similarity-input"
              type="range"
              min="0.10"
              max="0.80"
              step="0.05"
              value={minSimilarity}
              onChange={(e) => setMinSimilarity(Number(e.target.value))}
            />
          </div>

          <div className="control-group checkbox-group">
            <label htmlFor="stream-toggle">
              <input
                id="stream-toggle"
                type="checkbox"
                checked={isStreaming}
                onChange={(e) => setIsStreaming(e.target.checked)}
              />
              Stream Token Responses
            </label>
          </div>
        </div>
      )}

      <form onSubmit={ask} className="search">
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask a technical question about the indexed infrastructure corpus..."
          maxLength={2000}
          rows={4}
          aria-label="Question input"
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              if (!loading && question.trim().length >= 2) {
                ask(e);
              }
            }
          }}
        />
        <div className="query-footer">
          <span className="character-count">{question.length} / 2000</span>
          <div className="query-actions">
            {question && (
              <button
                type="button"
                className="text-button"
                onClick={clearQuestion}
              >
                Clear
              </button>
            )}
            <button
              type="submit"
              disabled={loading || question.trim().length < 2}
            >
              {loading ? (isStreaming ? "Streaming..." : "Retrieving & Generating...") : "Ask Question"}
            </button>
          </div>
        </div>
      </form>

      <div className="examples">
        <span className="examples-title">Sample Prompts:</span>
        {examples.map((example) => (
          <button
            key={example}
            type="button"
            className="example-pill"
            onClick={() => setQuestion(example)}
          >
            {example}
          </button>
        ))}
      </div>

      {searchHistory && searchHistory.length > 0 && (
        <div className="search-history-row">
          <span className="history-title">Recent queries:</span>
          {searchHistory.slice(-4).map((hist, i) => (
            <button
              key={i}
              type="button"
              className="history-pill"
              onClick={() => onSelectHistory(hist)}
            >
              {hist}
            </button>
          ))}
        </div>
      )}
    </section>
  );
}


const examples = [
  "What does an NSG control?",
  "What is Terraform used for?",
  "What does a Kubernetes Deployment manage?",
];

export default function QueryPanel({ question, loading, setQuestion, ask, clearQuestion }) {
  return (
    <section className="query-panel">
      <div className="panel-heading">
        <div>
          <p className="section-kicker">01 / QUERY</p>
          <h2>What do you want to know?</h2>
        </div>
        <span className="model-label">llama3.2:3b</span>
      </div>
      <form onSubmit={ask} className="search">
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask about the indexed knowledge base..."
          maxLength="2000"
          rows="4"
          aria-label="Question"
        />
        <div className="query-footer">
          <span className="character-count">{question.length} / 2000</span>
          <div className="query-actions">
            {question && <button type="button" className="text-button" onClick={clearQuestion}>Clear</button>}
            <button type="submit" disabled={loading || question.trim().length < 2}>
              {loading ? "Generating..." : "Ask question"}
            </button>
          </div>
        </div>
      </form>
      <div className="examples">
        <span>Try asking</span>
        {examples.map((example) => (
          <button key={example} type="button" onClick={() => setQuestion(example)}>{example}</button>
        ))}
      </div>
    </section>
  );
}

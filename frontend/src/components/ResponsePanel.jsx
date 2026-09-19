export default function ResponsePanel({ answer }) {
  return (
    <section className="result">
      <div className="result-heading">
        <div>
          <p className="section-kicker">02 / RESPONSE</p>
          <h2>Answer</h2>
        </div>
        <span className="confidence-label">{answer.sources.length} sources retrieved</span>
      </div>
      <div className="answer"><span className="quote-mark">“</span>{answer.answer}</div>

      <div className="metrics">
        <span><b>Retrieval</b>{answer.retrieval_latency_ms} ms</span>
        <span><b>Generation</b>{answer.llm_latency_ms} ms</span>
        <span><b>Total</b>{answer.total_latency_ms} ms</span>
        <span><b>Similarity</b>{answer.average_similarity}</span>
      </div>

      <div className="sources-heading">
        <div>
          <p className="section-kicker">03 / EVIDENCE</p>
          <h2>Retrieved sources</h2>
        </div>
        <span>Ranked by semantic similarity</span>
      </div>
      <div className="sources">
        {answer.sources.map((source, index) => (
          <article key={source.id}>
            <div className="source-header">
              <div className="source-title"><span className="source-rank">0{index + 1}</span><strong>{source.title}</strong></div>
              <span className="score">{source.score.toFixed(3)}</span>
            </div>
            <p>{source.text}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

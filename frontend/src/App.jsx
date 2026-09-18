import { useState } from "react";

const API = import.meta.env.VITE_API_URL || "";

export default function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [ingesting, setIngesting] = useState(false);
  const [message, setMessage] = useState("");

  async function ingest() {
    setIngesting(true);
    setMessage("");
    try {
      const response = await fetch(`${API}/api/v1/ingest`, { method: "POST" });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Ingestion failed");
      setMessage(`Indexed ${data.indexed} documents.`);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setIngesting(false);
    }
  }

  async function ask(event) {
    event.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setAnswer(null);
    setMessage("");

    try {
      const response = await fetch(`${API}/api/v1/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question })
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Query failed");
      setAnswer(data);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="container">
      <header>
        <div>
          <p className="eyebrow">DEVOPS-FIRST AI PLATFORM</p>
          <h1>Production RAG</h1>
          <p className="subtitle">
            Ask questions against your indexed knowledge base with retrieval,
            source citations, and operational metrics.
          </p>
        </div>
        <button onClick={ingest} disabled={ingesting}>
          {ingesting ? "Indexing..." : "Index Corpus"}
        </button>
      </header>

      {message && <div className="notice">{message}</div>}

      <form onSubmit={ask} className="search">
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask something about the knowledge base..."
          rows="4"
        />
        <button type="submit" disabled={loading}>
          {loading ? "Generating..." : "Ask"}
        </button>
      </form>

      {answer && (
        <section className="result">
          <h2>Answer</h2>
          <div className="answer">{answer.answer}</div>

          <div className="metrics">
            <span>Retrieval: {answer.retrieval_latency_ms} ms</span>
            <span>LLM: {answer.llm_latency_ms} ms</span>
            <span>Total: {answer.total_latency_ms} ms</span>
            <span>Similarity: {answer.average_similarity}</span>
          </div>

          <h2>Retrieved Sources</h2>
          <div className="sources">
            {answer.sources.map((source) => (
              <article key={source.id}>
                <div className="source-header">
                  <strong>{source.title}</strong>
                  <span>{source.score.toFixed(3)}</span>
                </div>
                <p>{source.text}</p>
              </article>
            ))}
          </div>
        </section>
      )}
    </main>
  );
}

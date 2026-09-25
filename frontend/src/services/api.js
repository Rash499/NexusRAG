const API_BASE = import.meta.env.VITE_API_URL || "";

export const apiService = {
  /**
   * Fetch backend system health & connectivity to Qdrant, Embedding, and Ollama
   */
  async getSystemStatus() {
    const res = await fetch(`${API_BASE}/api/v1/status`);
    if (!res.ok) {
      throw new Error(`Failed to fetch system status (${res.status})`);
    }
    return res.json();
  },

  /**
   * Re-index static corpus.json
   */
  async ingestCorpus() {
    const res = await fetch(`${API_BASE}/api/v1/ingest`, {
      method: "POST",
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || "Ingestion failed");
    }
    return data;
  },

  /**
   * Direct ingest arbitrary documents
   */
  async directIngest(documents, collection = null) {
    const res = await fetch(`${API_BASE}/api/v1/ingest/direct`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ documents, collection }),
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || "Direct ingestion failed");
    }
    return data;
  },

  /**
   * Send question to RAG pipeline
   */
  async query({ question, top_k = 5, min_similarity = 0.25, model = null }) {
    const payload = {
      question,
      top_k: Number(top_k),
      min_similarity: Number(min_similarity),
    };
    if (model) payload.model = model;

    const res = await fetch(`${API_BASE}/api/v1/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || "Query failed");
    }
    return data;
  },

  /**
   * Stream question response tokens
   */
  async queryStream({ question, top_k = 5, onChunk, onError, onComplete }) {
    try {
      const res = await fetch(`${API_BASE}/api/v1/query/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, top_k: Number(top_k) }),
      });

      if (!res.ok) {
        throw new Error(`Stream request failed (${res.status})`);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let done = false;

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          const chunk = decoder.decode(value, { stream: true });
          onChunk(chunk);
        }
      }

      if (onComplete) onComplete();
    } catch (err) {
      if (onError) onError(err);
      else console.error(err);
    }
  },
};

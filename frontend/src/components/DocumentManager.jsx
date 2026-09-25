import { useState } from "react";
import { apiService } from "../services/api";

export default function DocumentManager({ onDocumentAdded }) {
  const [title, setTitle] = useState("");
  const [source, setSource] = useState("");
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) return;

    setLoading(true);
    setStatusMessage(null);

    try {
      const doc = {
        title: title.trim(),
        text: content.trim(),
        source: source.trim() || "Web Console Direct Ingest",
      };

      const result = await apiService.directIngest([doc]);
      setStatusMessage({
        type: "success",
        text: `Document "${title}" successfully embedded and indexed into Qdrant!`,
      });
      setTitle("");
      setSource("");
      setContent("");
      if (onDocumentAdded) onDocumentAdded(result);
    } catch (err) {
      setStatusMessage({
        type: "error",
        text: `Error adding document: ${err.message}`,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="document-manager-panel">
      <div className="panel-heading">
        <div>
          <p className="section-kicker">INGESTION & CONTEXT EXPANSION</p>
          <h2>Add Knowledge Document</h2>
        </div>
        <span className="model-label">Direct Qdrant Ingestion</span>
      </div>

      <p className="panel-description">
        Directly inject technical documentation, playbooks, or runbooks into the vector store.
        Documents are instantly embedded and made available for RAG queries.
      </p>

      {statusMessage && (
        <div
          className={`notice ${statusMessage.type === "success" ? "notice-success" : "notice-error"}`}
          role="alert"
        >
          {statusMessage.text}
        </div>
      )}

      <form onSubmit={handleSubmit} className="doc-form">
        <div className="form-row">
          <div className="form-group flex-1">
            <label htmlFor="doc-title">Document Title *</label>
            <input
              id="doc-title"
              type="text"
              required
              placeholder="e.g. Kubernetes Ingress Configuration"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>

          <div className="form-group flex-1">
            <label htmlFor="doc-source">Source / File Reference</label>
            <input
              id="doc-source"
              type="text"
              placeholder="e.g. docs/k8s/ingress.md"
              value={source}
              onChange={(e) => setSource(e.target.value)}
            />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="doc-content">Document Content (Markdown or Text) *</label>
          <textarea
            id="doc-content"
            required
            rows={8}
            placeholder="Paste your operational guides, code snippets, or architecture documentation..."
            value={content}
            onChange={(e) => setContent(e.target.value)}
          />
        </div>

        <div className="form-actions">
          <button
            type="submit"
            disabled={loading || !title.trim() || !content.trim()}
          >
            {loading ? "Embedding & Storing..." : "Index Document"}
          </button>
        </div>
      </form>
    </section>
  );
}

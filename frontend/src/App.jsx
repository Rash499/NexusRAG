import { useState, useEffect, useCallback } from "react";
import Header from "./components/Header";
import QueryPanel from "./components/QueryPanel";
import ResponsePanel from "./components/ResponsePanel";
import DocumentManager from "./components/DocumentManager";
import SystemStatusModal from "./components/SystemStatusModal";
import { apiService } from "./services/api";

export default function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [ingesting, setIngesting] = useState(false);
  const [message, setMessage] = useState("");
  const [requestState, setRequestState] = useState("ready");
  const [activeTab, setActiveTab] = useState("query"); // "query", "documents", "system"

  // Advanced query options
  const [topK, setTopK] = useState(5);
  const [minSimilarity, setMinSimilarity] = useState(0.25);
  const [isStreaming, setIsStreaming] = useState(false);
  const [searchHistory, setSearchHistory] = useState([]);

  // System Diagnostics
  const [systemStatus, setSystemStatus] = useState(null);
  const [statusLoading, setStatusLoading] = useState(false);

  const fetchStatus = useCallback(async () => {
    setStatusLoading(true);
    try {
      const data = await apiService.getSystemStatus();
      setSystemStatus(data);
    } catch {
      // Backend might be offline during initial boot
      setSystemStatus({
        status: "offline",
        version: "2.0.0",
        qdrant: { reachable: false },
        embedding_service: { reachable: false },
        llm_service: { reachable: false },
      });
    } finally {
      setStatusLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  async function ingest() {
    setIngesting(true);
    setMessage("");
    try {
      const data = await apiService.ingestCorpus();
      setMessage(`Indexed ${data.indexed} documents into ${data.collection}.`);
      fetchStatus();
    } catch (error) {
      setMessage(`Ingestion error: ${error.message}`);
    } finally {
      setIngesting(false);
    }
  }

  async function ask(event) {
    if (event && event.preventDefault) event.preventDefault();
    const queryText = question.trim();
    if (!queryText) return;

    setLoading(true);
    setRequestState("working");
    setAnswer(null);
    setMessage("");

    // Add query text to local search history
    setSearchHistory((prev) => {
      const filtered = prev.filter((q) => q !== queryText);
      return [...filtered, queryText].slice(-10);
    });

    if (isStreaming) {
      let accumulatedAnswer = "";
      const startTime = performance.now();

      await apiService.queryStream({
        question: queryText,
        top_k: topK,
        onChunk: (token) => {
          accumulatedAnswer += token;
          setAnswer((prev) => ({
            answer: accumulatedAnswer,
            sources: prev?.sources || [],
            retrieval_latency_ms: prev?.retrieval_latency_ms ?? 0,
            llm_latency_ms: Math.round(performance.now() - startTime),
            total_latency_ms: Math.round(performance.now() - startTime),
            average_similarity: prev?.average_similarity ?? 0,
            grounded: true,
          }));
        },
        onError: (err) => {
          setMessage(err.message);
          setRequestState("error");
          setLoading(false);
        },
        onComplete: () => {
          setRequestState("complete");
          setLoading(false);
        },
      });
    } else {
      try {
        const data = await apiService.query({
          question: queryText,
          top_k: topK,
          min_similarity: minSimilarity,
        });
        setAnswer(data);
        setRequestState("complete");
      } catch (error) {
        setMessage(error.message);
        setRequestState("error");
      } finally {
        setLoading(false);
      }
    }
  }

  function clearQuestion() {
    setQuestion("");
    setAnswer(null);
    setMessage("");
    setRequestState("ready");
  }

  return (
    <main className="container">
      <Header
        requestState={requestState}
        ingest={ingest}
        ingesting={ingesting}
        systemStatus={systemStatus}
        onRefreshStatus={fetchStatus}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />

      {message && (
        <div className="notice" role="status">
          {message}
        </div>
      )}

      {activeTab === "query" && (
        <>
          <QueryPanel
            question={question}
            loading={loading}
            setQuestion={setQuestion}
            ask={ask}
            clearQuestion={clearQuestion}
            topK={topK}
            setTopK={setTopK}
            minSimilarity={minSimilarity}
            setMinSimilarity={setMinSimilarity}
            isStreaming={isStreaming}
            setIsStreaming={setIsStreaming}
            searchHistory={searchHistory}
            onSelectHistory={(q) => {
              setQuestion(q);
            }}
          />

          {answer && <ResponsePanel answer={answer} question={question} />}
        </>
      )}

      {activeTab === "documents" && (
        <DocumentManager
          onDocumentAdded={() => {
            fetchStatus();
          }}
        />
      )}

      {activeTab === "system" && (
        <SystemStatusModal
          systemStatus={systemStatus}
          onRefresh={fetchStatus}
          loading={statusLoading}
        />
      )}
    </main>
  );
}


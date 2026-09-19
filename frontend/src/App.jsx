import { useState } from "react";
import Header from "./components/Header";
import QueryPanel from "./components/QueryPanel";
import ResponsePanel from "./components/ResponsePanel";

const API = import.meta.env.VITE_API_URL || "";

export default function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [ingesting, setIngesting] = useState(false);
  const [message, setMessage] = useState("");
  const [requestState, setRequestState] = useState("ready");

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
    setRequestState("working");
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
      setRequestState("complete");
    } catch (error) {
      setMessage(error.message);
      setRequestState("error");
    } finally {
      setLoading(false);
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
      <Header requestState={requestState} ingest={ingest} ingesting={ingesting} />

      {message && <div className="notice" role="status">{message}</div>}

      <QueryPanel question={question} loading={loading} setQuestion={setQuestion} ask={ask} clearQuestion={clearQuestion} />

      {answer && <ResponsePanel answer={answer} />}
    </main>
  );
}

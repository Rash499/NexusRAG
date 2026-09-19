Currently, the reliable topics are the five documents in `corpus.json`:

- Azure NSGs
- Terraform
- Kubernetes
- Docker
- RAG

You can ask other questions, but because the API instructs Ollama to use only retrieved context, it should respond that the documents do not contain enough information. The current code still sends low-similarity questions to Ollama, so answers outside the corpus may not always be perfect.

To add more topics:

1. Add `.md` or `.txt` files to `documents`.
2. Run:

```powershell
python ingestion/build_corpus.py
```

3. Re-index the updated corpus:

```powershell
Invoke-WebRequest -Method Post http://localhost:8000/api/v1/ingest
```

After that, the new documents become searchable.




Documents
   ↓
build_corpus.py
   ↓
corpus.json
   ↓
FastAPI /ingest
   ↓
Embedding Service
   ↓
Qdrant
   ↓
Semantic Retrieval
   ↓
Ollama
   ↓
Grounded Answer + Sources
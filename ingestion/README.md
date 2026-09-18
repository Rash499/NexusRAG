# Ingestion

This folder contains a simple standalone ingestion utility for turning local
text/Markdown documents into the JSON format used by the API.

Put documents into `ingestion/documents/` and run:

```bash
python ingestion/build_corpus.py
```

The generated corpus is written to `api/data/corpus.json`.

For larger corpora, replace this utility with a proper ingestion worker that
handles parsing, chunking, metadata, deduplication, incremental updates, and
document IDs.

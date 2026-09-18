from pathlib import Path
import json
import hashlib

DOCS = Path(__file__).parent / "documents"
OUTPUT = Path(__file__).parent.parent / "api" / "data" / "corpus.json"

def chunk(text: str, size=900, overlap=100):
    text = " ".join(text.split())
    result = []
    start = 0
    while start < len(text):
        end = start + size
        result.append(text[start:end])
        if end >= len(text):
            break
        start = end - overlap
    return result

def main():
    documents = []
    for path in sorted(DOCS.glob("**/*")):
        if path.suffix.lower() not in {".md", ".txt"}:
            continue

        raw = path.read_text(encoding="utf-8")
        for index, part in enumerate(chunk(raw)):
            digest = hashlib.sha256(
                f"{path}:{index}:{part}".encode()
            ).hexdigest()[:16]

            documents.append({
                "id": digest,
                "title": f"{path.stem} - chunk {index + 1}",
                "source": str(path.relative_to(DOCS)),
                "text": part,
            })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(documents, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Wrote {len(documents)} chunks to {OUTPUT}")

if __name__ == "__main__":
    main()

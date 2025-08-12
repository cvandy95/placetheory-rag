import os, glob, uuid
from rag import RAG

DOC_DIR = os.path.join("..","..","docs","placetheory")
ALLOWED = (".md",".markdown",".txt")

def read_file(p):
    with open(p, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def chunk(text, max_chars=1200, overlap=200):
    parts, start = [], 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        slice_ = text[start:end]
        if end < len(text):
            last_nl = slice_.rfind("\n\n")
            if last_nl > 0 and last_nl > max_chars // 2:
                end = start + last_nl
                slice_ = text[start:end]
        parts.append(slice_.strip())
        start = max(0, end - overlap)
    return [p for p in parts if p]

def main():
    rag = RAG(persist_path="chroma", collection_name="placetheory")
    rows = []
    for path in glob.glob(os.path.join(DOC_DIR, "**/*"), recursive=True):
        if not path.lower().endswith(ALLOWED):
            continue
        text = read_file(path)
        base = os.path.basename(path)
        for i, chunk_text in enumerate(chunk(text)):
            rows.append({
                "id": f"{base}-{i}",
                "text": chunk_text,
                "source": base,
                "section": os.path.splitext(base)[0],
            })
    rag.ingest_rows(rows)
    print(f"Ingested {len(rows)} chunks from {DOC_DIR}")

if __name__ == "__main__":
    main()

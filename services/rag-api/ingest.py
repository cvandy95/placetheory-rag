import os, pandas as pd
from rag import RAG
CSV_PATH = os.path.join("data","nuggets.csv")

def main():
    df = pd.read_csv(CSV_PATH)
    rows = df.to_dict(orient="records")
    rag = RAG(persist_path="chroma", collection_name="nuggets")
    rag.ingest_rows(rows)
    print(f"Ingested {len(rows)} rows from {CSV_PATH}.")

if __name__ == "__main__":
    main()

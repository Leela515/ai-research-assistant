import json
from pathlib import Path

from core.embeddings import EmbeddingModel
from core.vector_store_faiss import FaissVectorStore

EVAL_PATH = Path("eval/eval_set.json")
INDEX_DIR = Path("library/index")

def load_eval_set():
    if not EVAL_PATH.exists():
        return []
    return json.loads(EVAL_PATH.read_text(encoding="utf-8"))

def save_eval_set(data):
    EVAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVAL_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")

def main():
    if not (INDEX_DIR / "index.faiss").exists():
        raise FileNotFoundError("Library index not found. Run ingestion first.")
    
    store = FaissVectorStore.load(str(INDEX_DIR))
    embedder = EmbeddingModel()

    eval_data = load_eval_set()
    print("\n ===Interactive Evaluation Builder===")

    while True:
        query = input("\nEnter query or 'exit' to quit: ").strip()

        if query.lower() == "exit":
            break

        if not query:
            continue

        qvec = embedder.embed_query(query)
        results = store.search(qvec, top_k=8)

        if not results:
            print("No results found.")
            continue

        print("\nTop Candidates:\n")

        for i, r in enumerate(results, start=1):
            md = r["metadata"]
            preview = md.get("text_preview", "")[:200]

            print(f"[{i}]")
            print(f"paper_id: {md['paper_id']}")
            print(f"chunk_id: {r['chunk_id']}")
            print(preview)
            print("-" * 60)

        selection = input(
            "\n Relevant chunk numbers (coma separated, or skip):"
        ).strip()

        if not selection:
            print("Skipped.")
            continue
        try:
            indices = [
                int(x.strip()) -1 for x in selection.split(",")
            ]

            relevant_chunks = [
                results[i]["chunk_id"] for i in indices if 0 <= i < len(results)
            ]

            entry = {
                "query_id": f"q{len(eval_data)+1}",
                "query": query,
                "relevant_chunk_ids": relevant_chunks,
            }

            eval_data.append(entry)
            save_eval_set(eval_data)

            print(f"\n Saved query {entry['query_id']}")

        except Exception as e:
            print(f"Invalid selection: {e}")

    print("\nEvaluation building finished.")

if __name__ == "__main__":
    main()
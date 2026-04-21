from __future__ import annotations

from pathlib import Path

from core.embeddings import EmbeddingModel
from core.vector_store_faiss import FaissVectorStore

def main():
    index_dir = Path("library/index")
    if not (index_dir / "index.faiss").exists():
        raise FileNotFoundError(
            "No library index found. Run scripts/build_index.py or scripts/ingest_library.py first."
        )

    store = FaissVectorStore.load(str(index_dir))
    embedder = EmbeddingModel()

    print(f"[INFO] Loaded library index: ntotal={store.index.ntotal}, dim={store.dimension}")

    while True:
        query = input("\nAsk a question (type 'exit' to quit): ").strip()
        if query.lower() == "exit":
            break
        if not query:
            continue

        qvec = embedder.embed_query(query)
        results = store.search_diverse(qvec, top_k_raw=40, max_per_paper=2)

        if not results:
            print("No results.")
            continue

        unique_papers = len({r["metadata"]["paper_id"] for r in results})
        print(f"\nTop results (unique papers in top_k={unique_papers}):\n")

        for i, r in enumerate(results, start=1):
            md = r["metadata"]
            print(f"{i}. score={r['score']:.4f} paper_id={md['paper_id']} section_id={md['section_id']} chunk_id={md['chunk_id']}")
            preview = md.get("text_preview") or md.get("text", "")[:240]
            print(f"   preview: {preview}\n")

if __name__ == "__main__":
    main()

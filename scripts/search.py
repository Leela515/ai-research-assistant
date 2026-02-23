from core.embeddings import EmbeddingModel
from core.vector_store_faiss import FaissVectorStore

def main():
    store = FaissVectorStore.load("indexes/spiking_nn")
    embedder = EmbeddingModel()

    query = input("Query:").strip()
    query_vec = embedder.embed_query(query)

    results = store.search(query_vec, top_k=5)

    print("\nQuery:", query)
    print("\nTop Results:")
    for r in results:
        print(f"\nScore: {r['score']:.4f}")
        print("Chunk:", r["chunk_id"])
        print("Preview:", r["metadata"]["text_preview"])

if __name__ == "__main__":
    main()
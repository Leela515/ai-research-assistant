from typing import Any, List, Dict
import numpy as np
import faiss

class FaissVectorStore:
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.metadata:List[Dict[str, Any]] = []

    def add(self, vectors: np.ndarray, metadata: List[Dict[str, Any]]):
        if vectors.ndim != 2 or vectors.shape[1] != self.dimension:
            raise ValueError(f"Vectors dimension mismatch")
        
        if len(metadata) != vectors.shape[0]:
            raise ValueError("Metadata size mismatch")
        
        # Normalize vectors for cosine similarity
        faiss.normalize_L2(vectors)

        self.index.add(vectors)
        self.metadata.extend(metadata)

    def search(self, query_vector: np.ndarray, top_k: int = 5):
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)

        faiss.normalize_L2(query_vector)

        scores, indices = self.index.search(query_vector, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue

            results.append({
                "score": float(score),
                "chunk_id": self.metadata[idx]["chunk_id"],
                "metadata": self.metadata[idx]
            })

        return results
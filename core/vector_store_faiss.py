from typing import Any, List, Dict, Optional
import numpy as np
import faiss
import json
from pathlib import Path
from collections import defaultdict


class FaissVectorStore:
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)
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
    
    def search_diverse(
            self,
            query_vector: np.ndarray,
            topk: int = 8,
            top_k_raw: int = 40,
            max_per_paper: int = 2,
    ) -> List[Dict[str, Any]]:
        
        raw_results = self.search(query_vector, top_k=top_k_raw)

        per_paper_count = defaultdict(int)
        diverse = []

        for r in raw_results:
            paper_id = r["metadata"].get("paper_id")
            if paper_id is None:
                diverse.append(r)
            else:
                if per_paper_count[paper_id] >= max_per_paper:
                    continue
                per_paper_count[paper_id] += 1
                diverse.append(r)
            
            if len(diverse) >= topk:
                break
        
        return diverse

    
    def save(self, dir_path: str) -> None:
        p = Path(dir_path)
        p.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self.index, str(p / "index.faiss"))

        with open(p / "metadata.jsonl", "w", encoding="utf-8") as f:
            for item in self.metadata:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

    @classmethod
    def load(cls, dir_path: str) -> "FaissVectorStore":
        p = Path(dir_path)
        index = faiss.read_index(str(p / "index.faiss"))

        store = cls(dimension=index.d)
        store.index = index

        meta = []
        with open(p / "metadata.jsonl", "r", encoding="utf-8") as f:
                  for line in f:
                    meta.append(json.loads(line))
        store.metadata = meta
        return store
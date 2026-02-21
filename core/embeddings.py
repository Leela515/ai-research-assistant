from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

class EmbeddingModel:
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        vectors = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=False,
        )

        return vectors.astype(np.float32)
    
    def embed_query(self, text: str) -> np.ndarray:
        return self.embed_texts([text])[0]
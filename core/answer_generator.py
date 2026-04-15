from typing import List, Dict
from core.vector_store_faiss import FaissVectorStore
from core.embeddings import EmbeddingModel

class AnswerGenerator:
    def __init__(self, index_path:str = "library/index"):
        self.embedder = EmbeddingModel()
        self.store = FaissVectorStore.load(index_path)

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        query_embedding = self.embedder.embed_query(query)
        results = self.store.search(query_embedding, top_k=top_k)
        return results
    
    def build_prompt(self, query: str, chunks: List[Dict]) -> str:
        context = "n\n".join(
            [f"[Source {i+1}] {chunk['metadata']['text']}" for i, chunk in enumerate(chunks)]
        )

        prompt = f"""
You are an AI research assistant. 

Answer the question using ONLY the provided sources.

If the answer is not contained in the sources, say:
"I could not find sufficient evidence."

Question:
{query}

Sources:
{context}

Answer:
"""
        return prompt
    
    def generate_answer(self, prompt: str) -> str:
        return "LLM integration not added yet."
    
    def format_output(self, answer: str, chunks: List[Dict]) -> str:
        sources = "\n".join(
            [
                f"[{i+1}] {chunk['metadata'].get('title', 'Unknown')} - {chunk['metadata'].get('section_title', '')}"
                for i, chunk in enumerate(chunks)
            ]
        )

        return f"""

Answer:
{answer}

Sources:
{sources}
"""
    
    def answer(self, query: str) -> str:
        chunks = self.retrieve(query)
        prompt = self.build_prompt(query, chunks)
        answer = self.generate_answer(prompt)
        return self.format_output(answer, chunks)

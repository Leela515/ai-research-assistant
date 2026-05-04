from typing import List, Dict
from core.vector_store_faiss import FaissVectorStore
from core.embeddings import EmbeddingModel
from core.llm.ollama_client import OllamaClient

class AnswerGenerator:
    def __init__(self, index_path:str = "library/index"):
        self.embedder = EmbeddingModel()
        self.store = FaissVectorStore.load(index_path)
        self.llm = OllamaClient()

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        query_embedding = self.embedder.embed_query(query)
        results = self.store.search_diverse(
            query_embedding, 
            topk=top_k,
            top_k_raw=40,
            max_per_paper=2)
        return results
    
    def build_prompt(self, query: str, chunks: List[Dict]) -> str:
        context = "\n\n".join(
            [f"[Source {i+1}] {chunk['metadata']['text']}" for i, chunk in enumerate(chunks)]
        )

        prompt = f"""
You are an AI research assistant. 

Answer the question using ONLY the provided sources.
Do not use outside knowledge.
Do not make up information.
Do not write in fragments. Write clearly and coherently.

If the sources contain enough evidence, provide a concise and accurate answer.
If multiple methods are mentioned, list them as bullet points.
Each bullet point must end with a citation to the source in the format [Source X], where X is the source number.
Use only [source X] citations.
Do not use citations that appear inside the source text.

If the sources provide only partial or unclear evidence, answer cautiously and explicitly state that the evidence is limited.

If the sources do not contain enough evidence to answer the question, say:
"I could not find sufficient evidence in the provided sources to answer the question."

Question: 
{query}

Sources:
{context}

Answer:
"""
        return prompt
    
    def generate_answer(self, prompt: str) -> str:
        return self.llm.generate(prompt)
    
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
        print("Generated Prompt:\n", prompt)  # Debugging line to check the generated prompt
        answer = self.generate_answer(prompt)
        return self.format_output(answer, chunks)

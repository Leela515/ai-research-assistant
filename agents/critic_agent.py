from core.llm.ollama_client import OllamaClient
from typing import Dict, List

class CriticAgent:
    def __init__(self):
        self.llm = OllamaClient()

    def review_answer(self, question: str, answer: str, chunks: List[Dict]) -> str:
        context = "\n\n".join(
            [
                f"[Source {i+1}] {chunk['metadata'].get('text', '')}"
                for i, chunk in enumerate(chunks)
            ]
        )

        prompt = f"""
You are a critical reviewer of AI-generated answers.

Your job is to check whether the answer is fully supported by the provided sources.

Rules:
- Use ONLY the provided sources.
- Do not use outside knowledge.
- Mark the answer as SUPPORTED only if all important claims are grounded in the sources.
- Mark NEEDS_REVISION as yes if the answer contains unsupported, misleading, incomplete, weakly grounded, or incorrectly cited claims.
- Citation format is part of the review.
- The only valid citations are [Source 1], [Source 2], [Source 3], etc.
- Any citation copied from inside the source text, such as [9], [10, 11, 12], (Xiao et al., 2021), or author-year citations, is invalid.
- Do not include a References section.
- Do not include paper-native citation numbers or author-year citations in the revised answer.
- If a method is mentioned in Source 5, cite it as [Source 5], even if the source text itself contains author-year citations.
- If revision is needed, rewrite the answer so it is strictly supported by the sources.
- In REVISED_ANSWER, every bullet point must end with one or more valid source citations.

Return your output in exactly this format:

SUPPORTED: yes or no
NEEDS_REVISION: yes or no
CRITIQUE: <short explanation>
REVISED_ANSWER: <final revised answer, or repeat the original answer if no revision is needed>

Question:
{question}

Answer:
{answer}

Sources:
{context}

Critique:
"""
        response = self.llm.generate(prompt)
        return response
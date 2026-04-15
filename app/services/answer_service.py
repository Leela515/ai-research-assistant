from core.answer_generator import AnswerGenerator
from app.core.config import settings

class AnswerService:
    def __init__(self):
        self.generator = AnswerGenerator()

    def answer_question(self, question: str):
        chunks = self.generator.retrieve(question, top_k=settings.top_k)
        prompt = self.generator.build_prompt(question, chunks)
        answer = self.generator.generate_answer(prompt)

        sources = [
            {
                "title": chunk["metadata"].get("title"),
                "section_title": chunk["metadata"].get("section_title"),
            }
            for chunk in chunks
        ]

        return {
            "answer": answer,
            "sources": sources,
        }
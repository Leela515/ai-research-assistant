from core.answer_generator import AnswerGenerator
from app.core.config import settings
from fastapi import HTTPException, status

class AnswerService:
    def __init__(self):
        self.generator = AnswerGenerator()

    def answer_question(self, question: str):
        try:
            chunks = self.generator.retrieve(question, top_k=settings.top_k)

            # No results found
            if not chunks:
                raise HTTPException(
                    status_code=404,
                    detail="No relevant information found for the query."
                )
            # Low relevance
            top_score = chunks[0].get("score", 0.0)

            if top_score < settings.min_relevance_score:
                raise HTTPException(
                    status_code=404,
                    detail="Query not supported by indexed documents."
                )
        
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
                "confidence": 0.5, # placeholder
            }
        except HTTPException:
            raise

        except Exception as e:
            # unexpected error
            raise HTTPException(
                status_code=500,
                detail=f"Internal error: {str(e)}"
            )

from core.answer_generator import AnswerGenerator
from app.core.config import settings
from fastapi import HTTPException
import re
from typing import List, Dict
from agents.critic_agent import CriticAgent

class AnswerService:
    def __init__(self):
        self.generator = AnswerGenerator()
        self.critic = CriticAgent()

    def _split_sentences(self, text: str) -> List[str]:
        if not text:
            return []
        parts = re.split(r'(?<=[.!?])\s+', text.strip())
        return [p.strip() for p in parts if p.strip()]

    def _extract_query_terms(self, query: str) -> List[str]:
        tokens = re.findall(r'\b\w+\b', query.lower())
        return [t for t in tokens if len(t) > 2]
    
    def _build_snippet(self, query: str, text: str, max_chars: int = 320) -> str:
        if not text:
            return ""
        
        sentences = self._split_sentences(text)
        if not sentences:
            return text[:max_chars].strip()
        
        query_terms = set(self._extract_query_terms(query))

        best_idx = 0
        best_score = -1

        for i, sentence in enumerate(sentences):
            sentence_terms = set(re.findall(r"\b\w+\b", sentence.lower()))
            overlap = len(query_terms & sentence_terms)
            score = overlap

            if score > best_score:
                best_score = score
                best_idx = i

        selected = []
        if best_idx > 0:
            selected.append(sentences[best_idx - 1])
        selected.append(sentences[best_idx])
        if best_idx < len(sentences) - 1:
            selected.append(sentences[best_idx + 1])

        snippet = " ".join(selected).strip()

        if len(snippet) > max_chars:
            snippet = snippet[:max_chars].rstrip() + "..."

        return snippet
    
    def _compute_confidence(self, chunks: List[Dict]) -> float:
        if not chunks:
            return 0.0
        
        scores = [float(chunk.get("score", 0.0)) for chunk in chunks]
        top_score = scores[0]
        avg_top3 = sum(scores[:3]) / min(len(scores), 3)

        support_count = sum(1 for s in scores if s >= settings.min_relevance_score)

        unique_papers = len(
            {
                chunk["metadata"].get("paper_id")
                for chunk in chunks
                if chunk["metadata"].get("paper_id")

            }
        )

        support_ratio = support_count / max(len(chunks), 1)
        diversity_ratio = min(unique_papers / 3, 1.0)

        confidence = (
            0.5 * top_score
            + 0.25 * avg_top3
            + 0.15 * support_ratio
            + 0.10 * diversity_ratio
        )

        return round(min(max(confidence, 0.0), 1.0), 3)
    
    def _parse_critic_output(self, critic_output: str) -> Dict:
        text = critic_output.strip()

        supported = bool(re.search(r"SUPPORTED:\s*yes", text, re.IGNORECASE))
        needs_revision = bool(re.search(r"NEEDS_REVISION:\s*yes", text, re.IGNORECASE))

        critique = ""
        revised_answer = ""

        critique_match = re.search(
            r"CRITIQUE:\s*(.*?)(?=REVISED_ANSWER:|$)",
            text,
            re.IGNORECASE | re.DOTALL,
        )

        if critique_match:
            critique = critique_match.group(1).strip()

        revised_match = re.search(
            r"REVISED_ANSWER:\s*(.*)",
            text,
            re.IGNORECASE | re.DOTALL,
        )

        if revised_match:
            revised_answer = revised_match.group(1).strip()

        return {
            "supported": supported,
            "needs_revision": needs_revision,
            "critique": critique,
            "revised_answer": revised_answer,
            "raw": critic_output
        }
    
    def valid_citations(self, text: str, num_sources: int) -> Dict:
        bracketed_items = re.findall(r"\[[^\]]+\]", text)

        valid_pattern = re.compile(r"^\[Source\s+(\d+)\]$")

        invalid_citations = []
        valid_citations = []

        for item in bracketed_items:
            match = valid_pattern.match(item)

            if not match:
                invalid_citations.append(item)
                continue
            source_num = int(match.group(1))

            if source_num < 1 or source_num > num_sources:
                invalid_citations.append(item)
            else:
                valid_citations.append(item)
        
        return {
            "is_valid": len(invalid_citations) == 0,
            "valid_citations": valid_citations,
            "invalid_citations": invalid_citations
        }
        
    
    def _adjust_confidence_with_critic(self, base_confidence: float, critic_result: Dict) -> float:
        confidence = base_confidence

        if critic_result.get("supported") is True:
            confidence += 0.05

        if critic_result.get("needs_revision") is True:
            confidence -= 0.10

        if not critic_result.get("supported"):
            confidence -= 0.15

        return round(min(max(confidence, 0.0), 1.0), 3)

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
            draft_answer = self.generator.generate_answer(prompt)

            critic_output = self.critic.review_answer(question, draft_answer, chunks)
            critic_result = self._parse_critic_output(critic_output)

            candidate_answer = (
                critic_result["revised_answer"]
                if critic_result["needs_revision"] and critic_result["revised_answer"]
                else draft_answer
            )
            
            citation_check = self.valid_citations(candidate_answer, len(chunks))

            if citation_check["is_valid"]:
                final_answer = candidate_answer
            else:
                cleaned_answer = self._cleanup_answer_citations(question, candidate_answer, chunks)

                cleaned_check = self.valid_citations(cleaned_answer, len(chunks))

                if cleaned_check["is_valid"]:
                    final_answer = cleaned_answer
                else:
                    final_answer = "I could not generate a properly grounded answer with valid citations."

            base_confidence = self._compute_confidence(chunks)
            final_confidence = self._adjust_confidence_with_critic(base_confidence, critic_result)

            sources = [
                {
                    "paper_id": chunk["metadata"].get("paper_id"),
                    "chunk_id": chunk.get("chunk_id"),
                    "title": chunk["metadata"].get("title"),
                    "section_id": chunk["metadata"].get("section_id"),
                    "section_title": chunk["metadata"].get("section_title"),
                    "score": chunk.get("score"),
                    "snippet": self._build_snippet(
                        question,
                        chunk["metadata"].get("text", "")
                    ),
                    "char_start": chunk["metadata"].get("char_start"),
                    "char_end": chunk["metadata"].get("char_end"),
                }
                for chunk in chunks
            ]

            return {
                "answer": final_answer,
                "draft_answer": draft_answer,
                "sources": sources,
                "confidence": final_confidence,
                "critic_review": {
                    "supported": critic_result["supported"],
                    "needs_revision": critic_result["needs_revision"],
                    "critique": critic_result["critique"],
                    "invalid_citations": citation_check["invalid_citations"]
                },
            }
        
        except HTTPException:
            raise

        except Exception as e:
            # unexpected error
            raise HTTPException(
                status_code=500,
                detail=f"Internal error: {str(e)}"
            )

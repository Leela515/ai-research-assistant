from typing import List
from models.section import Section
from models.chunk import Chunk
import re


def clean_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text

def is_good_text_block(text: str) -> bool:
    if not text:
        return False
    stripped = text.strip()
    if len(stripped) < 80:
        return False
    if len(stripped.split()) < 20:
        return False
    if stripped in ["Bibliography", "References"]:
        return False
    if "<!-- image -->" in stripped:
        return False
    if stripped.startswith("Figure") and len(stripped) < 150:
        return False
    if "|" in stripped and len(stripped.split()) < 80:
        return False

    alpha_ratio = sum(c.isalpha() for c in stripped) / max(len(stripped), 1)
    if alpha_ratio < 0.55:
        return False

    return True

def split_into_paragraphs(text: str) -> List[str]:
    paragraphs = text.split("\n\n")
    return [p.strip() for p in paragraphs if p.strip()]

def get_overlap_text(text: str, max_overlap_char: int = 120) -> str:
    if len(text) <= max_overlap_char:
        return text
    
    tail = text[-max_overlap_char:]

    sentence_starts = [tail.rfind(sep) for sep in [",", "?", "!"]]
    best_start = max(sentence_starts)

    if best_start != -1:
        return tail[best_start + 2:].strip()
    
    return tail.strip()

def chunk_sections(
        sections: List[Section],
        max_char: int = 1200,
        overlap: int = 120
) -> List[Chunk]:
    chunks: List[Chunk] = []

    for section in sections:
        text = clean_text(section.text or "")
        if not text:
            continue

        paragraphs = split_into_paragraphs(text)
        if not paragraphs:
            continue

        good_paragraphs = [p for p in paragraphs if is_good_text_block(p)]   
        if not good_paragraphs:
            continue

        idx = 0
        current_parts: List[str] = []
        current_length = 0
        char_cursor = 0

        for paragraph in good_paragraphs:
            paragraph_length = len(paragraph)

            # if current chunk is empty , start with this paragraph
            if not current_parts:
                current_parts = [paragraph]
                current_length = paragraph_length
                continue

            # if adding this paragraph says within limit, keep building current chunk
            if current_length + 2 + paragraph_length <= max_char:
                current_parts.append(paragraph)
                current_length += 2 + paragraph_length
                continue

            # Finalize current chunk
            chunk_text = "\n\n".join(current_parts).strip()

            if is_good_text_block(chunk_text):
                chunk_char_start = char_cursor
                chunk_char_end = char_cursor + len(chunk_text)

                chunks.append(
                    Chunk(
                        chunk_id=f"{section.section_id}_chunk_{idx}",
                        paper_id=section.paper_id,
                        title=getattr(section, "paper_title", None),
                        section_id=section.section_id,
                        section_title=getattr(section, "title", None),
                        chunk_index=idx,
                        text=chunk_text,
                        char_start=chunk_char_start,
                        char_end=chunk_char_end,
                        token_count=len(chunk_text.split()),
                    )
                )

                idx += 1
                char_cursor = chunk_char_end

            # start next chunk with overlap + current paragraph
            overlap_text = get_overlap_text(chunk_text, max_overlap_char=overlap) if chunk_text else ""

            if overlap_text:
                current_parts = [overlap_text, paragraph]
                current_length = len(overlap_text) + 2 + paragraph_length
            else:
                current_parts = [paragraph]
                current_length = paragraph_length

            # Finalize any remaining text as last chunk
            if current_parts:
                chunk_text = "\n\n".join(current_parts).strip()

                if is_good_text_block(chunk_text):
                    chunk_char_start = char_cursor
                    chunk_char_end = char_cursor + len(chunk_text)

                    chunks.append(
                        Chunk(
                            chunk_id=f"{section.section_id}_chunk_{idx}",
                            paper_id=section.paper_id,
                            title=getattr(section, "paper_title", None),
                            section_id=section.section_id,
                            section_title=getattr(section, "title", None),
                            chunk_index=idx,
                            text=chunk_text,
                            char_start=chunk_char_start,
                            char_end=chunk_char_end,
                            token_count=len(chunk_text.split()),
                        )
                    )
    return chunks 

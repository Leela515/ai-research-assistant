from typing import List
from models.section import Section
from models.chunk import Chunk
import re


def clean_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text

def is_good_chunk(text: str) -> bool:
    if not text:
        return False
    if len(text) < 50:
        return False
    if len(text.split()) < 40:
        return False
    if text.strip() in ["Bibliography", "References"]:
        return False
    if "<!-- image -->" in text:
        return False
    if text.strip().startswith("Figure") and len(text.strip()) < 100:
        return False
    return True

def find_chunk_end(text: str, start: int, max_char: int) -> int:
    rough_end = min(start + max_char, len(text))

    if rough_end == len(text):
        return rough_end

    window = text[start:rough_end]

    # Try paragraph break first
    idx = window.rfind("\n\n")
    if idx != -1 and idx > max_char * 0.5:
        return start + idx

    # Try sentence boundaries
    for sep in [". ", "? ", "! "]:
        idx = window.rfind(sep)
        if idx != -1 and idx > max_char * 0.5:
            return start + idx + len(sep)

    # Fallback: last space
    idx = window.rfind(" ")
    if idx != -1 and idx > max_char * 0.5:
        return start + idx

    # If nothing found, use rough cut
    return rough_end

def chunk_sections(
        sections: List[Section],
        max_char: int = 1500,
        overlap: int = 200
) -> List[Chunk]:
    chunks: List[Chunk] = []

    for section in sections:
        text = clean_text(section.text or "")
        if not text:
            continue

        start = 0
        idx = 0

        while start < len(text):
            end = find_chunk_end(text, start, max_char)
            chunk_text = text[start:end].strip()

            if chunk_text and is_good_chunk(chunk_text):
                chunks.append(
                    Chunk(
                        chunk_id=f"{section.section_id}_chunk_{idx}",
                        paper_id=section.paper_id,
                        title=getattr(section, "paper_title", None),
                        section_id=section.section_id,
                        section_title=getattr(section, "title", None),
                        chunk_index=idx,
                        text=chunk_text,
                        char_start=start,
                        char_end=end,
                        token_count=len(chunk_text.split()),
                    )
                )

            idx += 1
            if end >= len(text):
                break

            start = max(0, end - overlap)

    return chunks

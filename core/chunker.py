from typing import List
from models.section import Section
from models.chunk import Chunk

def chunk_sections(
        sections: List[Section],
        max_char: int = 1500,
        overlap: int = 200
) -> List[Chunk]:
    chunks: List[Chunk] = []

    for section in sections:
        text = (section.text or "").strip()
        if not text:
            continue

        start = 0
        idx = 0

        while start < len(text):
            end = min(start + max_char, len(text))
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    Chunk(
                        chunk_id=f"{section.section_id}_chunk_{idx}",
                        paper_id=section.paper_id,
                        section_id=section.section_id,
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
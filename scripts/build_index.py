from pathlib import Path
from types import SimpleNamespace

from parsers.docling_parser import DoclingParser
from core.chunker import chunk_sections
from core.embeddings import EmbeddingModel
from core.vector_store_faiss import FaissVectorStore

DOWNLOADS_DIR = Path("downloads")
INDEX_DIR = Path("library/index")


def build_paper_obj(pdf_path: Path):
    paper_id = pdf_path.stem
    arxiv_id = paper_id.replace("paper_", "", 1) if paper_id.startswith("paper_") else paper_id
    return SimpleNamespace(
        paper_id=paper_id,
        arxiv_id=arxiv_id,
        title=paper_id,   # temporary fallback; better titles come from future ingestion
        pdf_path=str(pdf_path),
        source="local_rebuild",
    )


def main():
    pdf_files = sorted(DOWNLOADS_DIR.glob("*.pdf"))
    if not pdf_files:
        print("[ERROR] No PDFs found in downloads/")
        return

    parser = DoclingParser()
    all_chunks = []

    for pdf_path in pdf_files:
        paper = build_paper_obj(pdf_path)
        print(f"[INFO] Parsing {pdf_path.name}")

        sections = parser.parse(paper)

        for sec in sections:
            setattr(sec, "paper_title", paper.title)

        chunks = chunk_sections(sections)
        all_chunks.extend(chunks)

    if not all_chunks:
        print("[ERROR] No chunks were created.")
        return

    texts = [c.text for c in all_chunks]
    embedder = EmbeddingModel()
    embeddings = embedder.embed_texts(texts)

    store = FaissVectorStore(len(embeddings[0]))
    store.add(embeddings, [chunk.model_dump() for chunk in all_chunks])
    store.save(str(INDEX_DIR))

    print(f"[INFO] Rebuild complete. Total chunks: {len(all_chunks)}")


if __name__ == "__main__":
    main()
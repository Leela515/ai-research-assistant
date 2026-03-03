from __future__ import annotations

from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import json

from agents.retriever_agent import RetrieverAgent
from core.downloader import download_pdf
from parsers.docling_parser import DoclingParser
from core.chunker import chunk_sections
from core.embeddings import EmbeddingModel
from core.vector_store_faiss import FaissVectorStore
from core.registry import PaperRegistry

LIBRARY_DIR = Path("library")
INDEX_DIR = LIBRARY_DIR / "index"
REGISTRY_PATH = LIBRARY_DIR / "papers.jsonl"
MANIFEST_PATH = INDEX_DIR / "manifest.json"

def load_manifest() -> Dict[str, Any] | None:
    """Load index manifest if exists."""
    if not MANIFEST_PATH.exists():
        return None
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

def save_manifest(manifest: Dict[str, Any]) -> None:
    """Save index manifest."""
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

def build_manifest(embedder: EmbeddingModel, dimension: int, chunk_cfg: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "created_at": datetime.utcnow().isoformat() + "z",
        "embedding_model": getattr(embedder, "model_name", "unknown"),
        "dimension": dimension,
        "chunk_config": chunk_cfg,
        "faiss_index_type": "IndexFlatIP (cosine via L2-normalization)",
    }

def assert_manifest_compatible(manifest: Dict[str, Any], embedder: EmbeddingModel, dimension: int, chunk_cfg: Dict[str, Any]) -> None:
    """Fail early if the existing index was built with different settings."""
    if manifest.get("dimension") != dimension:
        raise RuntimeError(
            f"Index dimension mismatch: manifest={manifest.get('dimension')} vs current={dimension}"
        )
    
    old_model = manifest.get("embedding_model")
    new_model = getattr(embedder, "model_name", "unknown")
    if old_model != new_model:
        raise RuntimeError(
            f"Embedding model mismatch: manifest={old_model} vs current={new_model}"
        )
    
    if manifest.get("chunk_config") != chunk_cfg:
        raise RuntimeError(
            f"Chunk config mismatch: manifest={manifest.get('chunk_config')} vs current={chunk_cfg}"
        )

def main():
    # User controlled parameters
    topic = "Spiking Neural Networks"
    max_papers = 5

    chunk_cfg = {
        "strategy": "section_chunking",
        "overlap": "as_implemented_in_chunk_sections",
    }

    LIBRARY_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    retriever = RetrieverAgent(max_results=max_papers)
    parser = DoclingParser()
    embedder = EmbeddingModel()

    registry = PaperRegistry(str(REGISTRY_PATH))

    # Load or create FAISS store
    if (INDEX_DIR / "index.faiss").exists():
        store = FaissVectorStore.load(str(INDEX_DIR))
        print(f"[INFO] Loaded existing index: ntotal={store.index.ntotal}, dim={store.dimension}")

        # Verify manifest compatibility
        manifest = load_manifest()
        if manifest is None:
            print("[WARN] No manifest found. Creating one from current settings.")
            manifest = build_manifest(embedder, store.dimension, chunk_cfg)
            save_manifest(manifest)
        else:
            assert_manifest_compatible(manifest, embedder, store.dimension, chunk_cfg)
            print("[INFO] Manifest compatible.")
    else:
        store = None
        print("[INFO] No existing index found. Will create a new one after embedding first batch.")

    papers = retriever.retrieve(topic)

    # De-Duplicate within this run
    seen = set()
    unique_papers = []
    for p in papers:
        if p.arxiv_id in seen:
            continue
        seen.add(p.arxiv_id)
        unique_papers.append(p)
    
    print(f"[INFO] Retrieved {len(unique_papers)} unique papers from arXiv.")

    all_new_chunks = []
    ingested_papers = 0

    for i, paper in enumerate(unique_papers, start=1):
        # Deduplicate across runs using registry
        if registry.has_arxiv_id(paper.arxiv_id):
            print(f"[SKIP] Already in library: arxiv_id={paper.arxiv_id} paper_id={paper.paper_id}")
            continue

        try:
            print(f"\n[{i}/{len(unique_papers)}] Downloading: {paper.paper_id}")
            paper = download_pdf(paper)

            print(f"[{i}/{len(unique_papers)}] Parsing: {paper.pdf_path}")
            sections = parser.parse(paper)

            chunks = chunk_sections(sections)

            all_new_chunks.extend(chunks)

            # Add paper record to registry (append-only)
            registry.add({
                "paper_id": paper.paper_id,
                "arxiv_id": paper.arxiv_id,
                "title": getattr(paper, "title", None),
                "pdf_url": getattr(paper, "pdf_url", None),
                "pdf_path": paper.pdf_path,
                "ingested_at": datetime.utcnow().isoformat() + "Z",
                "source": "arxiv",
                "topic_seed": topic,
            })

            ingested_papers += 1
            print(f"[{i}/{len(unique_papers)}] Sections={len(sections)} Chunks={len(chunks)}")

        except Exception as e:
            print(f"[WARN] Failed to ingest {paper.paper_id}: {e}")

    if not all_new_chunks:
        print("[INFO] No new chunks produced (everything may already be ingested).")
        registry.close()
        return

    print(f"\n[INFO] Total NEW chunks to embed: {len(all_new_chunks)}")

    # Embed new chunks
    vectors = embedder.embed_texts([c.text for c in all_new_chunks])

    # Create store if first time
    if store is None:
        store = FaissVectorStore(dimension=vectors.shape[1])
        print(f"[INFO] Created new FAISS store with dim={store.dimension}")

        # Create manifest for new index
        manifest = build_manifest(embedder, store.dimension, chunk_cfg)
        save_manifest(manifest)
        print("[INFO] Saved new manifest.")

    # IMPORTANT: store full chunk text for later evidence display / RAG grounding.
    metadata: List[Dict[str, Any]] = [{
        "chunk_id": c.chunk_id,
        "paper_id": c.paper_id,
        "section_id": c.section_id,
        "chunk_index": c.chunk_index,
        "char_start": c.char_start,
        "char_end": c.char_end,
        "text": c.text,              # full text for evidence
        "text_preview": c.text[:240] # optional quick preview
    } for c in all_new_chunks]

    # Add to index
    store.add(vectors, metadata)

    # Persist updated index + metadata
    store.save(str(INDEX_DIR))

    registry.close()

    print(f"\n[OK] Ingested new papers: {ingested_papers}")
    print(f"[OK] Index updated: ntotal={store.index.ntotal}")
    print(f"[OK] Saved to: {INDEX_DIR}")


if __name__ == "__main__":
    main()
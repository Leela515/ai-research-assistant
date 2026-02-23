from agents.retriever_agent import RetrieverAgent
from core.downloader import download_pdf
from parsers.docling_parser import DoclingParser
from core.chunker import chunk_sections
from core.embeddings import EmbeddingModel
from core.vector_store_faiss import FaissVectorStore

def main():
    paper = RetrieverAgent(max_results=1).retrieve("spiking neural networks")[0]
    paper = download_pdf(paper)

    sections = DoclingParser().parse(paper)
    chunks = chunk_sections(sections)

    embedder = EmbeddingModel()
    texts = [c.text for c in chunks]
    vectors = embedder.embed_texts(texts)

    store = FaissVectorStore(dimension=vectors.shape[1])

    metadata = [{
        "chunk_id": c.chunk_id,
        "paper_id": c.paper_id,
        "section_id": c.section_id,
        "chunk_index": c.chunk_index,
        "text_preview": c.text[:200]
    } for c in chunks]

    store.add(vectors, metadata)

    store.save("indexes/spiking_nn")
    print("Index saved to indexes/spiking_nn")

if __name__ == "__main__":
    main()
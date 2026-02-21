from agents.retriever_agent import RetrieverAgent
from core.downloader import download_pdf
from parsers.docling_parser import DoclingParser
from core.chunker import chunk_sections

def main():
    paper = RetrieverAgent(max_results=1).retrieve("spiking neural networks")[0]
    paper = download_pdf(paper)

    sections = DoclingParser().parse(paper)
    chunks = chunk_sections(sections)

    print("sections:", len(sections))
    print("chunks:", len(chunks))

    print("\n--- First 3 chunks ---")
    for c in chunks[:3]:
        print("chunk_id:", c.chunk_id)
        print("section_id:", c.section_id)
        print("tokens~:", c.token_count)
        print(c.text[:400])
        print("-" * 60)

if __name__ == "__main__":
    main()
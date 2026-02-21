from agents.retriever_agent import RetrieverAgent
from core.downloader import download_pdf
from parsers.docling_parser import DoclingParser

def main():
    paper = RetrieverAgent(max_results=1).retrieve("spiking neural networks")[0]
    paper = download_pdf(paper)

    parser = DoclingParser()
    sections = parser.parse(paper)

    print("paper_id:", paper.paper_id)
    print("pdf_path:", paper.pdf_path)
    print("sections:", len(sections))
    print("\n--- First section preview ---")
    print("type:", sections[0].section_type)
    print("title:", sections[0].title)
    print(sections[0].text[:800])

    for s in sections[:3]:
        print(s.section_type, "|", s.title)

if __name__ == "__main__":
    main()
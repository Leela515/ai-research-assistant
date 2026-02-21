from agents.retriever_agent import RetrieverAgent
from core.downloader import download_pdf

def main():
    papers = RetrieverAgent(max_results=1).retrieve("spiking neural networks")
    paper = papers[0]
 
    paper = download_pdf(paper)

    print("paper_id:", paper.paper_id)
    print("pdf_url:", paper.pdf_url)
    print("pdf_path:", paper.pdf_path)

if __name__ == "__main__":
    main()
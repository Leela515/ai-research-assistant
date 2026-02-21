from agents.retriever_agent import RetrieverAgent

def main():
    agent = RetrieverAgent(max_results=3)

    papers = agent.retrieve("spiking neural networks")

    print("\n Retrieved papers:\n")

    for paper in papers:
        print("ID:", paper.paper_id)
        print("Title:", paper.title)
        print("Year:", paper.year)
        print("PDF:", paper.pdf_url)
        print("-" * 50)

if __name__ == "__main__":
    main()
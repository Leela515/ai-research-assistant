from core.registry import PaperRegistry

def main():
    registry = PaperRegistry("library/papers.jsonl")

    print("Registry initialized")

    test_record = {
        "paper_id": "test_paper_001",
        "arxiv_id": "1234.56789",
        "title": "Test Paper Title",
        "pdf_path": "/fake/path/test.pdf"
    }

    registry.add(test_record)
    print("Record added.")

    exists = registry.has_arxiv_id("1234.56789")
    print("Has arxiv_id 1234.56789:", exists)

    registry.close()
    print("Registry closed.")

if __name__ == "__main__":
    main()
# AI Research Assistant 

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Vector Search](https://img.shields.io/badge/Vector%20DB-FAISS-purple)
![Status](https://img.shields.io/badge/Project-Active-orange)

A document intelligence system that ingests academic papers, converts them into structured semantic chunks, and enables retrieval of relevant evidence using vector search.

The project explores how AI systems can assist researchers by structuring research papers and enabling semantic queries across documents.

Repository Structure
ai-research-assistant
│
├── agents/                    # Paper retrieval logic
│   └── retriever_agent.py
│
├── core/                      # Core system components
│   ├── chunker.py
│   ├── embeddings.py
│   ├── registry.py
│   └── vector_store_faiss.py
│
├── parsers/                   # PDF parsing
│   └── docling_parser.py
│
├── scripts/                   # System entrypoints
│   ├── ingest_library.py
│   ├── search_library.py
│   └── evaluate_retrieval.py
│
├── eval/                      # Retrieval evaluation dataset
│   ├── build_eval_set.py
│   └── eval_set.json
│
├── tests/
│   └── test_registry.py
│
└── README.md
Technologies

Python
FAISS (vector similarity search)
Sentence Transformers
Docling
NumPy
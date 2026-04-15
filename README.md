# AI Research Assistant

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Vector DB](https://img.shields.io/badge/Vector%20DB-FAISS-purple)
![Project](https://img.shields.io/badge/Project-Active-orange)


AI research assistant system for querying academic literature, performing paper retrieval and ingestion, and generating answers from retrieved evidence.

The system is structured to separate query execution, document processing, and answer generation, allowing controlled retrieval and extensibility toward verification and revision workflows.

---

## 📂 Repository Structure

```
app/        FastAPI interface  
agents/     retrieval components  
core/       chunking, embeddings, vector store, answer pipeline  
models/     internal data structures  
parsers/    document parsing  
scripts/    ingestion and indexing utilities  
eval/       evaluation dataset and scripts  
tests/      test suite   
```
---

## Scope

- paper retrieval (arXiv / local)
- PDF parsing
- section-aware chunking
- FAISS indexing and retrieval
- API-based query execution

---

## API

GET /health  
POST /query

---

## Reproduce

```bash
pip install -r requirements.txt
python -m scripts.build_index
uvicorn app.main:app --reload

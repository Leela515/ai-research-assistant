import json
from pathlib import Path
from typing import Dict, Any, List

from core.embeddings import EmbeddingModel
from core.vector_store_faiss import FaissVectorStore


def hit_at_k(relevant: set, retrieved: List[str], k: int) -> float:
    return 1.0 if any(cid in relevant for cid in retrieved[:k]) else 0.0


def mrr_at_k(relevant: set, retrieved: List[str], k: int) -> float:
    for rank, cid in enumerate(retrieved[:k], start=1):
        if cid in relevant:
            return 1.0 / rank
    return 0.0


def main():
    index_dir = Path("library/index")
    eval_path = Path("eval/eval_set.json")
    report_path = Path("eval/report.json")

    if not (index_dir / "index.faiss").exists():
        raise FileNotFoundError("No library index found. Run scripts/ingest_library.py first.")
    if not eval_path.exists():
        raise FileNotFoundError("Missing eval/eval_set.json. Create it first.")

    store = FaissVectorStore.load(str(index_dir))
    embedder = EmbeddingModel()

    eval_items: List[Dict[str, Any]] = json.loads(eval_path.read_text(encoding="utf-8"))

    ks = [3, 5, 10]
    totals = {f"hit@{k}": 0.0 for k in ks}
    totals.update({f"mrr@{k}": 0.0 for k in ks})

    per_query = []

    for item in eval_items:
        qid = item["query_id"]
        query = item["query"]
        relevant = set(item["relevant_chunk_ids"])

        qvec = embedder.embed_query(query)
        results = store.search(qvec, top_k=max(ks))

        retrieved_ids = [r["chunk_id"] for r in results]

        row = {"query_id": qid, "query": query}

        for k in ks:
            row[f"hit@{k}"] = hit_at_k(relevant, retrieved_ids, k)
            row[f"mrr@{k}"] = mrr_at_k(relevant, retrieved_ids, k)

            totals[f"hit@{k}"] += row[f"hit@{k}"]
            totals[f"mrr@{k}"] += row[f"mrr@{k}"]

        # Extra debug signal: where the first relevant chunk appears
        first_rank = None
        for i, cid in enumerate(retrieved_ids, start=1):
            if cid in relevant:
                first_rank = i
                break
        row["first_relevant_rank"] = first_rank
        row["retrieved_top10"] = retrieved_ids[:10]

        per_query.append(row)

    n = max(1, len(eval_items))
    summary = {metric: value / n for metric, value in totals.items()}

    print("\n=== Retrieval Evaluation ===")
    print(f"Queries: {n}")
    for k in ks:
        print(f"Hit@{k}: {summary[f'hit@{k}']:.3f} | MRR@{k}: {summary[f'mrr@{k}']:.3f}")

    report = {"n_queries": n, "summary": summary, "per_query": per_query}
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nSaved detailed report to: {report_path}")


if __name__ == "__main__":
    main()
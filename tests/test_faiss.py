import numpy as np
import pytest

faiss = pytest.importorskip("faiss")

from core.vector_store_faiss import FaissVectorStore


def test_add_and_search_returns_ranked_results():
    store = FaissVectorStore(dimension=2)
    vectors = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    metadata = [
        {"chunk_id": "c1", "paper_id": "p1"},
        {"chunk_id": "c2", "paper_id": "p2"},
    ]

    store.add(vectors, metadata)
    results = store.search(np.array([1.0, 0.0], dtype=np.float32), top_k=2)

    assert len(results) == 2
    assert results[0]["chunk_id"] == "c1"
    assert results[0]["metadata"]["paper_id"] == "p1"
    assert results[0]["score"] >= results[1]["score"]


def test_add_rejects_dimension_mismatch():
    store = FaissVectorStore(dimension=2)

    with pytest.raises(ValueError, match="dimension mismatch"):
        store.add(np.array([[1.0, 2.0, 3.0]], dtype=np.float32), [{"chunk_id": "c1"}])


def test_search_diverse_limits_results_per_paper():
    store = FaissVectorStore(dimension=2)
    vectors = np.array(
        [
            [1.0, 0.0],
            [0.9, 0.1],
            [0.0, 1.0],
        ],
        dtype=np.float32,
    )
    metadata = [
        {"chunk_id": "c1", "paper_id": "p1"},
        {"chunk_id": "c2", "paper_id": "p1"},
        {"chunk_id": "c3", "paper_id": "p2"},
    ]

    store.add(vectors, metadata)
    results = store.search_diverse(
        np.array([1.0, 0.0], dtype=np.float32),
        topk=3,
        top_k_raw=3,
        max_per_paper=1,
    )

    assert [result["chunk_id"] for result in results] == ["c1", "c3"]


def test_save_and_load_round_trip(tmp_path):
    store = FaissVectorStore(dimension=2)
    vectors = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    metadata = [
        {"chunk_id": "c1", "paper_id": "p1"},
        {"chunk_id": "c2", "paper_id": "p2"},
    ]

    store.add(vectors, metadata)
    store.save(str(tmp_path))

    loaded = FaissVectorStore.load(str(tmp_path))
    results = loaded.search(np.array([0.0, 1.0], dtype=np.float32), top_k=1)

    assert loaded.dimension == 2
    assert loaded.metadata == metadata
    assert results[0]["chunk_id"] == "c2"

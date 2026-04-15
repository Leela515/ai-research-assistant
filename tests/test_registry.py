import json

import pytest

from core.registry import PaperRegistry


def test_registry_adds_and_finds_records(tmp_path):
    registry_path = tmp_path / "papers.jsonl"
    registry = PaperRegistry(str(registry_path))

    record = {
        "paper_id": "paper_1234.5678",
        "arxiv_id": "1234.5678",
        "title": "Test Paper",
        "pdf_path": "downloads/paper_1234.5678.pdf",
    }

    registry.add(record)
    registry.close()

    assert registry.has_arxiv_id("1234.5678") is True
    assert registry_path.exists()
    assert list(PaperRegistry(str(registry_path)).iter_records()) == [record]


def test_registry_ignores_duplicate_arxiv_ids(tmp_path):
    registry_path = tmp_path / "papers.jsonl"
    registry = PaperRegistry(str(registry_path))

    record = {
        "paper_id": "paper_1234.5678",
        "arxiv_id": "1234.5678",
        "title": "Test Paper",
    }

    registry.add(record)
    registry.add(record)
    registry.close()

    lines = registry_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0]) == record


def test_registry_requires_arxiv_id(tmp_path):
    registry = PaperRegistry(str(tmp_path / "papers.jsonl"))

    with pytest.raises(ValueError, match="arxiv_id"):
        registry.add({"paper_id": "paper_without_id"})


def test_iter_records_returns_empty_for_missing_file(tmp_path):
    registry = PaperRegistry(str(tmp_path / "missing" / "papers.jsonl"))

    assert list(registry.iter_records()) == []

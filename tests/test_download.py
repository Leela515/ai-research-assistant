from datetime import datetime
from pathlib import Path

import pytest

from core.downloader import download_pdf
from models.paper import Paper


class DummyResponse:
    def __init__(self, content=b"%PDF-1.4"):
        self.content = content

    def raise_for_status(self):
        return None


def make_paper(pdf_url="https://example.com/paper.pdf"):
    return Paper(
        paper_id="paper_1234.5678",
        title="Test Paper",
        authors=["Alice"],
        year=2024,
        abstract="summary",
        arxiv_id="1234.5678",
        pdf_url=pdf_url,
        ingestion_date=datetime.utcnow(),
        source="arxiv",
    )


def test_download_pdf_requires_pdf_url():
    paper = make_paper(pdf_url=None)

    with pytest.raises(ValueError, match="no pdf_url"):
        download_pdf(paper)


def test_download_pdf_writes_file_and_sets_path(tmp_path, monkeypatch):
    monkeypatch.setattr("core.downloader.requests.get", lambda url, timeout: DummyResponse())

    paper = make_paper()
    result = download_pdf(paper, download_dir=str(tmp_path))

    output_path = tmp_path / "paper_1234.5678.pdf"
    assert result.pdf_path == str(output_path)
    assert output_path.exists()
    assert output_path.read_bytes() == b"%PDF-1.4"


def test_download_pdf_skips_network_if_file_exists(tmp_path, monkeypatch):
    output_path = tmp_path / "paper_1234.5678.pdf"
    output_path.write_bytes(b"existing")

    def fail_if_called(*args, **kwargs):
        raise AssertionError("requests.get should not be called when file already exists")

    monkeypatch.setattr("core.downloader.requests.get", fail_if_called)

    paper = make_paper()
    result = download_pdf(paper, download_dir=str(tmp_path))

    assert result.pdf_path == str(output_path)
    assert output_path.read_bytes() == b"existing"

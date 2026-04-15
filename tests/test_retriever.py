from types import SimpleNamespace

import pytest

from agents.retriever_agent import RetrieverAgent


class DummyResponse:
    def __init__(self, status_code=200, content=b"", text=""):
        self.status_code = status_code
        self.content = content
        self.text = text


ATOM_FEED = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/1234.5678v1</id>
    <updated>2025-01-01T00:00:00Z</updated>
    <published>2024-12-31T00:00:00Z</published>
    <title> Test Paper Title </title>
    <summary> Test abstract text. </summary>
    <author><name>Alice</name></author>
    <author><name>Bob</name></author>
    <link href="http://arxiv.org/abs/1234.5678v1" rel="alternate" type="text/html"/>
  </entry>
</feed>
"""


def test_retrieve_requires_non_empty_topic():
    agent = RetrieverAgent()

    with pytest.raises(ValueError, match="non-empty string"):
        agent.retrieve("   ")


def test_retrieve_parses_papers_from_arxiv_feed(monkeypatch):
    captured = {}

    def fake_get(url, headers, timeout):
        captured["url"] = url
        captured["headers"] = headers
        captured["timeout"] = timeout
        return DummyResponse(status_code=200, content=ATOM_FEED, text=ATOM_FEED.decode("utf-8"))

    monkeypatch.setattr("agents.retriever_agent.requests.get", fake_get)

    papers = RetrieverAgent(max_results=3).retrieve("spiking neural networks")

    assert len(papers) == 1
    assert "all:spiking+neural+networks" in captured["url"]
    assert papers[0].paper_id == "paper_1234.5678v1"
    assert papers[0].title == "Test Paper Title"
    assert papers[0].authors == ["Alice", "Bob"]
    assert papers[0].year == 2024
    assert papers[0].pdf_url == "http://arxiv.org/pdf/1234.5678v1.pdf"


def test_retrieve_raises_for_http_errors(monkeypatch):
    monkeypatch.setattr(
        "agents.retriever_agent.requests.get",
        lambda url, headers, timeout: DummyResponse(status_code=503, text="service unavailable"),
    )

    with pytest.raises(RuntimeError, match="HTTP error 503"):
        RetrieverAgent().retrieve("transformers")


def test_retrieve_skips_broken_entries(monkeypatch):
    broken_feed = SimpleNamespace(
        bozo=False,
        entries=[
            SimpleNamespace(
                id="http://arxiv.org/abs/1111.2222v1",
                title="Broken Entry",
                authors=[],
                summary="summary",
                link="http://arxiv.org/abs/1111.2222v1",
            ),
            SimpleNamespace(
                id="http://arxiv.org/abs/1234.5678v1",
                title="Valid Entry",
                authors=[SimpleNamespace(name="Alice")],
                published="2024-01-01T00:00:00Z",
                summary="summary",
                link="http://arxiv.org/abs/1234.5678v1",
            ),
        ],
    )

    monkeypatch.setattr(
        "agents.retriever_agent.requests.get",
        lambda url, headers, timeout: DummyResponse(status_code=200, content=b"ok", text="ok"),
    )
    monkeypatch.setattr("agents.retriever_agent.feedparser.parse", lambda content: broken_feed)

    papers = RetrieverAgent().retrieve("transformers")

    assert len(papers) == 1
    assert papers[0].title == "Valid Entry"

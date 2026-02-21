import feedparser
from datetime import datetime, timezone
from typing import List
import requests

from models.paper import Paper
from utils.pdf_utils import get_pdf_link
from utils.logger import get_logger

logger = get_logger(__name__)


class RetrieverAgent:
    """
    RetrieverAgent is responsible for retrieving paper metadata and constructing internal paper objects.
    """

    def __init__(self, max_results: int = 5):
        self.max_results = max_results

    def retrieve(self, topic: str) -> List[Paper]:
        if not topic or not topic.strip():
            raise ValueError("Topic must be a non-empty string.")
        
        query = topic.replace(" ", "+").lower()
        url = (
            "https://export.arxiv.org/api/query?"
            f"search_query=all:{query}&start=0&max_results={self.max_results}"
        )

        headers = {
            "User-Agent": "ai-research-assistant/0.1 "
        }

        resp = requests.get(url, headers=headers, timeout=30)

        if resp.status_code != 200:
            logger.error(f"arXiv returned status {resp.status_code}")
            logger.error(resp.text[:300]) # show first part of response
            raise RuntimeError(f"arXiv HTTP error {resp.status_code}")

        content = resp.content
        
        feed = feedparser.parse(content)

        if feed.bozo:
            logger.error("Failed to parse arXiv feed.", exc_info=feed.bozo_exception)
            logger.error(content[:300])
            raise RuntimeError("arXiv feed parsing failed.")
        
        if not getattr(feed, "entries", None):
            logger.error("arXiv feed parsed but contains no entries.")
            logger.error(content[:300])
            raise RuntimeError("No entries returned from arXiv.")
        
        papers: List[Paper] = []

        for entry in feed.entries:
            try:
                arxiv_id = entry.id.split("/")[-1]

                paper = Paper(
                    paper_id=f"paper_{arxiv_id}",
                    title=entry.title.strip(),
                    authors=[author.name for author in entry.authors],
                    year=int(entry.published[:4]),
                    abstract=entry.summary.strip(),
                    arxiv_id=arxiv_id,
                    pdf_url=get_pdf_link(entry.link),
                    ingestion_date=datetime.now(timezone.utc),
                    source="arxiv",
                )

                papers.append(paper)

            except Exception as e:
                logger.warning(
                    "Failed to construct Paper object",
                    extra={"entry_id": getattr(entry, "id", None)},
                    exc_info=e,
                )
                # skip broken entry, continues pipeline

        if not papers:
            raise RuntimeError("No valid papers retrieved")
        
        return papers
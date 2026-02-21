from pathlib import Path
from typing import Optional
import requests

from models.paper import Paper
from utils.logger import get_logger

logger = get_logger(__name__)

def download_pdf(paper: Paper, download_dir: str = "downloads") -> Paper:
    if not paper.pdf_url:
        raise ValueError(f"Paper {paper.paper_id} had no pdf_url")
    
    Path(download_dir).mkdir(parents=True, exist_ok=True)

    # Safe filename: paper_XXXX.pdf
    out_path = Path(download_dir) / f"{paper.paper_id}.pdf"

    # Skip if already downloaded
    if out_path.exists() and out_path.stat().st_size > 0:
        paper.pdf_path = str(out_path)
        return paper
    
    logger.info(f"Downloading PDF for {paper.paper_id} -> {out_path}")

    try:
        resp = requests.get(paper.pdf_url, timeout=60)
        resp.raise_for_status()
        out_path.write_bytes(resp.content)
    except Exception as e:
        logger.error(f"Failed downloading {paper.paper_id}", exc_info=e)
        raise 

    paper.pdf_path = str(out_path)
    return paper

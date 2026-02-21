from agents.retriever_agent import RetrieverAgent
from agents.summarizer_agent import SummarizerAgent
from agents.critic_agent import CriticAgent
# from agents.downloader_agent import DownloaderAgent

from utils.logger import get_logger
from utils.file_utils import save_results_to_json
from utils.config import get_config

import os

logger = get_logger(__name__)
config = get_config()


def run_pipeline(topic: str):
    """Run the full pipeline: retrieve, summarize, critique, and save results."""
    logger.info(f"Starting pipeline for topic: '{topic}'")

    # Step 1: Search and Retrieve
    retriever = RetrieverAgent(topic, max_results=config.get("max_results", 5))
    papers = retriever.search(topic)
    logger.info(f" Retrieved {len(papers)} papers")

    # 2. (Optional Download PDFs - Add this later)
    # downloader = DownloaderAgent()
    # pdf_paths = downloader.download(papers)

    # Step 3. Summarize
    summarizer = SummarizerAgent()
    summaries = summarizer.summarize(papers)

    # Step 4: Critique
    critic = CriticAgent()
    critiques = critic.critique(summaries)

    # Step 5: Save Output
    output_path = os.path.join(config['paths']['outputs'], f"{topic.replace('','_')}.json")
    save_results_to_json(output_path, summaries, critiques)

    logger.info(f"All done. Results saved to: {output_path}")
"""
import json
from datetime import datetime
import os
from agents.retriever_agent import RetrieverAgent
from agents.summarizer_agent import SummarizerAgent
from agents.critic_agent import CriticAgent
from utils.pdf_tools import get_pdf_link, download_pdf, extract_text_from_pdf

TOPIC_FILE = "topics.json"

def save_topic(topic):
    
    topics = []
    
    # Check if the topics file exists, create it if not
    if os.path.exists(TOPIC_FILE):
        try:
            with open(TOPIC_FILE, 'r') as f:
                topics = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            topics = []
    else:
        topics = []

    # Append the new topic with a timestamp
    topics.append({
        "topic": topic,
        "timestamp": datetime.now().isoformat()
    })

    # Save the updated topics list back to the file
    with open(TOPIC_FILE, 'w') as f:
        json.dump(topics, f, indent =4)
        print(f"Topic '{topic}' saved successfully.")

def main():
    print("Welcome to the AI research assistant!")
    topic = input("Enter a research topic: ").strip()
    if not topic:
        print("Topic cannot be empty. Please try again.")
        return
    retriever = RetrieverAgent(topic)
    results = retriever.retrieve() 
    summarizer = SummarizerAgent()
    if not results:
        print("No results found for the given topic.")
        return
    
    topic_safe = topic.replace(" ", "_").lower()
    download_dir = os.path.join("downloads", topic_safe)
    os.makedirs(download_dir, exist_ok=True)

    for i, paper in enumerate(results):
        pdf_link = get_pdf_link(paper["link"])
        
        # Clean and format the filename
        title_safe = ''.join(c for c in paper['title'] if c.isalnum() or c in (' ', '_')).rstrip()
        title_safe = title_safe.replace('','_')[:50]  # Limit length to avoid filesystem issues
        filename = f"{i+1:02d}_{title_safe}.pdf"
        pdf_path = os.path.join(download_dir, filename)

        # Download the PDF
        download_pdf(pdf_link, pdf_path)
        if not os.path.exists(pdf_path):
            print(f"Skipping paper due to download error: {pdf_path}")
            continue
        full_text = extract_text_from_pdf(pdf_path)
        if not full_text.strip():
            print(f"Skipping paper due to empty or unreadable content: {pdf_path}")
            continue
        
        summary = summarizer.summarize_long_text(full_text)
        original_excerpt = full_text[:1000]
        critic = CriticAgent()
        feedback = critic.critique(summary, original_excerpt)
        paper["ai_summary"] = summary
        print("Critique:\n", feedback)
        
        
    
    # Save the topic after retrieval
    with open(f"papers_{topic.replace(' ', '_')}.json", 'w') as f:
        json.dump(results, f, indent=4)
        print(f"Results saved to papers_{topic.replace(' ', '_')}.json")
"""

from core.pipeline import run_pipeline

if __name__ == "__main__":
    topic = input("Enter a research topic: ")
    run_pipeline(topic)
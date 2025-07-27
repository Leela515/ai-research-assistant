import json
from datetime import datetime
import os
from agents.retriever_agent import RetrieverAgent

TOPIC_FILE = "topics.json"

def save_topic(topic):
    """Save a topic to the topics file."""
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
    if results:
        print(f"Retrieved {len(results)} results for topic '{topic}':")
        for i, result in enumerate(results, start=1):
            print(f"{i}. {result['title']} by {', '.join(result['authors'])}")
            print(f"   Published on: {result['published']}")
            print(f"   Summary: {result['summary']}")
            print(f"   Link: {result['link']}\n")
    else:
        print("No results found or an error occurred.")
    
    # Save the topic after retrieval
    with open(f"papers_{topic.replace(' ', '_')}.json", 'w') as f:
        json.dump(results, f, indent=4)
        print(f"Results saved to papers_{topic.replace(' ', '_')}.json")


if __name__ == "__main__":
    main()
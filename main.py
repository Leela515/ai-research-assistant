import json
from datetime import datetime
import os

TOPIC_FILE = "topics.json"

def save_topic(topic):
    """Save a topic to the topics file."""
    
    # Check if the topics file exists, create it if not
    if not os.path.exists(TOPIC_FILE):
        try:
            with open(TOPIC_FILE, 'w') as f:
                topics = json.load(f)
        except json.JSONDecodeError:
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

    if topic:
        save_topic(topic)
    else:
        print("Topic cannot be empty. Please try again.")

if __name__ == "__main__":
    main()
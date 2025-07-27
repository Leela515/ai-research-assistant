import feedparser


class RetrieverAgent:
    def __init__(self, topic, max_results=5):
        """Initialize the RetrieverAgent with a topic and maximum results."""
        self.original_topic = topic.strip()
        # Normalize the topic to ensure consistent API queries
        self.topic = topic.lower().replace(" ", "+")
        self.max_results = max_results
        self.api_url = f"https://export.arxiv.org/api/query?search_query=all:{self.topic}&start=0&max_results={max_results}"

    def retrieve(self):
        """Retrieve information based on the given topic."""
        try:
            feed = feedparser.parse(self.api_url)

            # Check for parsing errors
            if feed.bozo:
                raise ValueError(f"Error parsing feed: {feed.bozo_exception}")
            results = []
            if not feed.entries:
                print("No entries found for the given topic.")
                return []
            for entry in feed.entries:
                results.append({
                    "title": entry.title,
                    "authors": [author.name for author in entry.authors],
                    "summary": entry.summary,
                    "published": entry.published,
                    "link": entry.link
                })
            return results
        except Exception as e:
            print(f"An error occurred while retrieving data: {e}")
            return []
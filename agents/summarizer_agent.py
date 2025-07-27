from dotenv import load_dotenv
import os
import openai

class SummarizerAgent:
    def __init__(self):
        """Initialize the SummarizerAgent with OpenAI API key."""
        load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            raise ValueError("OpenAI API key is not set. Please set it in the .env file.")
        
    def summarize(self, text):
        """Summarize the given text using OpenAI's GPT model."""
        if not text:
            raise ValueError("Input text cannot be empty.")
        
        pass
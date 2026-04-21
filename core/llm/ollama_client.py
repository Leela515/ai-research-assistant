from core.llm.base import BaseLLM
import requests


class OllamaClient(BaseLLM):
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.model = "llama3"
    
    def generate(self, prompt: str) -> str:
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(url, json=payload)

        data = response.json()

        return data["response"]
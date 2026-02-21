from transformers import pipeline
import torch

device = 0 if torch.cuda.is_available() else -1

class CriticAgent:
    def __init__(self, model_name="google/flan-t5-base", device=device):
        """Initialize the CriticAgent with a summarization-capable LLM."""
        self.critic = pipeline("text2text-generation", model=model_name, device=device)
        
    def critique(self, summary, original_text=None):
        """Critique the summary against the original text."""
        if not summary:
            raise ValueError("Summary cannot be empty.")
        
        prompt = (
            f"You are critical reviewer. Analyse the following summary:\n\n"
            f"{summary}\n\n"
        )
        if original_text:
            prompt += f"Based on the original text:\n\n{original_text}\n\n"
            prompt += "Provide feedback on accuracy, clarity and completeness."
        else:
            prompt += "Provide feedback on clarity and completeness only."
        
        response = self.critic(prompt, max_length=300, do_sample=False)
        return response[0]['generated_text'].strip()
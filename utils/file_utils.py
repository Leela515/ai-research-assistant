import json
import os

def save_results_to_json(path, summaries, critiques):
    """Save summaries and critiques to a JSON file."""
    os.makedirs(os.path.dirname(path, exist_ok=True))
    with open(path, "w") as f:
        json.dump({
            "summaries":summaries,
            "critiques": critiques
        }, f, indent=2)

        
                
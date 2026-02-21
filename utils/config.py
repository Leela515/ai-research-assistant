import yaml
import os
from dotenv import load_dotenv

load_dotenv()


def get_config():
    with open("config/config.yaml", "r") as f:
        return yaml.safe_load(f)
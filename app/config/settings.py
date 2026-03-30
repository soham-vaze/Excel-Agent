import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://10.30.1.34:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "gemma3:4b")
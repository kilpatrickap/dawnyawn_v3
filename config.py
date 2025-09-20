# dawnyawn/config.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# --- Centralized LLM Client Configuration ---
def get_llm_client() -> OpenAI:
    """
    Initializes and returns an OpenAI client configured for a local LLM server.
    """
    return OpenAI(
        base_url=os.getenv("OLLAMA_BASE_URL"),
        api_key=os.getenv("OLLAMA_API_KEY"),
    )

LLM_MODEL_NAME = os.getenv("LLM_MODEL")

# --- NEW PERFORMANCE SETTINGS ---
# Timeout for all LLM requests in seconds
LLM_REQUEST_TIMEOUT = 600.0

# Maximum summary
MAX_SUMMARY_INPUT_LENGTH = 5000

# --- Service Configuration ---
class ServiceConfig:
    KALI_DRIVER_URL: str = "http://127.0.0.1:1611"

service_config = ServiceConfig()
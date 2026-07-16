"""Configuration management for PC Configuration Agent."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration class with environment variables."""
    
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
    MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5:7b")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    DATASET_PATH = os.getenv("DATASET_PATH", "../Computer_Components_Dataset/data/csv")
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        # Ollama doesn't require API key, just validate provider is set
        if not cls.LLM_PROVIDER:
            raise ValueError("LLM_PROVIDER is required")

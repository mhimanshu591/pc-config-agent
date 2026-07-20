"""Configuration management for PC Configuration Agent."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration class with environment variables."""
    
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")  # Better tool calling support
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    DATASET_PATH = os.getenv("DATASET_PATH", "../Computer_Components_Dataset/data/csv")
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if cls.LLM_PROVIDER == "groq" and not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required for Groq provider")

"""
Configuration settings for the E-commerce Support Resolution Agent.
Loads environment variables and provides centralized config access.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Centralized configuration for the application."""

    # Groq API (FREE - Fast Inference)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # Embeddings (FREE - HuggingFace local)
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    # Paths
    POLICIES_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "policies")
    VECTOR_STORE_PATH: str = os.getenv(
        "VECTOR_STORE_PATH",
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "faiss_store"),
    )

    # Chunking
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "800"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))

    # Retriever
    RETRIEVER_K: int = int(os.getenv("RETRIEVER_K", "3"))
    MINIMUM_POLICY_SIMILARITY: float = float(os.getenv("MINIMUM_POLICY_SIMILARITY", "0.25"))

    # Debug
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"

    @classmethod
    def validate(cls) -> None:
        """Validate the required Groq API configuration."""
        if not cls.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not set. Add it to your .env file."
            )


settings = Settings()

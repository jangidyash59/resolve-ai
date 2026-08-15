"""
Configuration settings for the E-commerce Support Resolution Agent.
Loads environment variables and provides centralized config access.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Centralized configuration for the application."""

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Models
    LLM_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-5-mini")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

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

    @classmethod
    def validate(cls) -> None:
        """Validate the required OpenAI configuration."""
        if not cls.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is not set. Add it to your .env file."
            )


settings = Settings()

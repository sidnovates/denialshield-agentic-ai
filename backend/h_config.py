"""
Configuration management for the backend application.
Loads environment variables and provides configuration settings.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""

    # API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./backend/data/app.db")

    # Uploads
    # Uploads - RESOLVED ABSOLUTE PATH
    # This ensures uploads always go to [PROJECT_ROOT]/backend/uploads/UserData
    BASE_DIR = Path(__file__).resolve().parent
    UPLOAD_FOLDER: Path = Path(os.getenv("UPLOAD_FOLDER", BASE_DIR / "uploads" / "UserData"))

    # Server
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))

    # LLM Models
    EXTRACTOR_MODEL: str = "llama-3.1-8b-instant"  # Llama-3.1-8B for extraction
    REASONING_MODEL: str = "llama-3.3-70b-versatile"  # Llama-3.3-70B for reasoning

    # Insurance Rules
    INSURANCE_RULES_DIR: Path = Path("./backend/insurance_rules")
    # Development/Testing - Force True for stability on Windows/Python 3.13
    USE_MOCK_OCR: bool = True # os.getenv("USE_MOCK_OCR", "false").lower() == "true"

    # File size limits (in bytes)
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    def __init__(self):
        """Ensure required directories exist."""
        self.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        Path("./backend/data").mkdir(parents=True, exist_ok=True)
        self.INSURANCE_RULES_DIR.mkdir(parents=True, exist_ok=True)

# Global settings instance
settings = Settings()
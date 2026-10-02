import os
import json
from pathlib import Path
from dataclasses import dataclass, field

BASE_DIR = Path(__file__).resolve().parent.parent.parent

@dataclass
class Settings:
    PROJECT_NAME: str = "AI-Powered Labour Market Intelligence Engine"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Directories
    ROOT_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    DATABASES_DIR: Path = BASE_DIR / "DATABASES"
    ENGINE_DB_PATH: Path = BASE_DIR / "DATABASES" / "v2" / "labour_market_extended.sqlite"
    BASE_DB_PATH: Path = BASE_DIR / "DATABASES" / "v2" / "job_seekers.sqlite"
    FAISS_INDEX_PATH: Path = BASE_DIR / "data" / "processed" / "faiss_index.bin"
    FAISS_METADATA_PATH: Path = BASE_DIR / "data" / "processed" / "faiss_metadata.json"

    # Ollama Local LLM & Embeddings Settings
    OLLAMA_BASE_URL: str = field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    OLLAMA_LLM_MODEL: str = field(default_factory=lambda: os.getenv("OLLAMA_LLM_MODEL", "qwen2.5:1.5b"))
    OLLAMA_EMBED_MODEL: str = field(default_factory=lambda: os.getenv("OLLAMA_EMBED_MODEL", "bge-m3"))

    # Configuration Weights File
    WEIGHTS_FILE: Path = field(default_factory=lambda: Path(__file__).resolve().parent / "weights.json")

    def get_weights(self) -> dict:
        if self.WEIGHTS_FILE.exists():
            with open(self.WEIGHTS_FILE, "r") as f:
                return json.load(f)
        return {
            "demand_score_weights": {
                "job_posting_growth": 0.30,
                "active_employer_count": 0.25,
                "plfs_sector_employment_trend": 0.20,
                "ncs_state_year_vacancy": 0.15,
                "vacancy_volume": 0.10
            },
            "demand_score_fallback_weights": {
                "job_posting_growth": 0.35,
                "active_employer_count": 0.30,
                "plfs_sector_employment_trend": 0.20,
                "ncs_state_year_vacancy": 0.15
            }
        }

settings = Settings()

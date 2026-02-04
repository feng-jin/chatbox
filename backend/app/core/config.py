"""App configuration from environment variables."""
import os
from pathlib import Path

# Project root: assume run from repo root (parent of backend/)
PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
if not DATA_DIR.is_absolute():
    DATA_DIR = PROJECT_ROOT / DATA_DIR

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/chat.db")
# Normalize to path for sqlite3 when scheme is sqlite
if DATABASE_URL.startswith("sqlite:///"):
    _db_path = DATABASE_URL.replace("sqlite:///", "")
    if not Path(_db_path).is_absolute():
        DATABASE_PATH = PROJECT_ROOT / _db_path
    else:
        DATABASE_PATH = Path(_db_path)
else:
    DATABASE_PATH = PROJECT_ROOT / "data" / "chat.db"

UPLOADS_DIR = DATA_DIR / "uploads"
FAISS_DIR = DATA_DIR / "faiss"

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.0-flash")
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "60.0"))

EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", LLM_PROVIDER)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-004")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "768"))

RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
MAX_FILE_SIZE_MB = float(os.getenv("MAX_FILE_SIZE_MB", "5.0"))

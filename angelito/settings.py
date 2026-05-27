import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

CHAT_MODEL = os.getenv("CHAT_MODEL", "gemini-2.5-flash")
GITHUB_USER = os.getenv("GITHUB_USER", "JCastellanosDev")

DB_PATH = Path(os.getenv("ANGELITO_DB_PATH", PROJECT_ROOT / "historial_angelito.db"))

MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "20"))
MAX_CONTEXT_RESULTS = int(os.getenv("MAX_CONTEXT_RESULTS", "3"))


def require_google_api_key() -> str:
    if not GOOGLE_API_KEY:
        raise RuntimeError(
            "No se encontro GOOGLE_API_KEY. Crea un archivo .env basado en .env.example."
        )
    return GOOGLE_API_KEY

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = BASE_DIR / "data"
DB_PATH = Path(os.environ.get("IDEATHON_DB", DATA_DIR / "ideathon.db"))
APP_TITLE = os.environ.get("IDEATHON_TITLE", "Ideathon Kit")

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BASE_DIR / ".env"

load_dotenv(dotenv_path=env_path)

class Config:    
    BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")
    BROWSER = os.getenv("BROWSER", "chromium")
    DB_DIR = BASE_DIR / "mail" / "db.sqlite3"
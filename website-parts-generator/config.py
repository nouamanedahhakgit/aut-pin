"""Website parts generator config."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
PORT = int(os.getenv("WEBSITE_PARTS_PORT", "8010"))

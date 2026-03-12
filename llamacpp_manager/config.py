"""Configuration for llama.cpp manager."""
import os

# Directory to store downloaded models (must exist; created on demand if missing)
MODELS_DIR = os.getenv(
    "LLAMACPP_MODELS_DIR",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "models"),
)

# SQLite database path (file-based, no external DB server)
_DB_DIR = os.path.dirname(os.path.abspath(__file__))
LLAMACPP_DB_PATH = os.getenv(
    "LLAMACPP_DB_PATH",
    os.path.join(_DB_DIR, "llamacpp_manager.db"),
)

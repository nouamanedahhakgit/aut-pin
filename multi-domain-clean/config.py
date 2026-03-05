"""Load configuration from environment."""
import os
from dotenv import load_dotenv

load_dotenv()

# AI Provider (openai or openrouter) - default openrouter
AI_PROVIDER = os.getenv("AI_PROVIDER", "openrouter").lower()

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-120b")

# Local (Ollama or similar)
LOCAL_API_URL = os.getenv("LOCAL_API_URL", "http://192.168.1.20:11434")
LOCAL_MODELS = os.getenv("LOCAL_MODELS", "qwen3:8b,llama3.2:3b,gemma3:latest,ibm/granite4:latest,functiongemma:latest").split(",")

def get_ai_config(provider=None):
    """Return (provider, model) for display. provider override uses that, else AI_PROVIDER env."""
    p = (provider or "").strip().lower() or AI_PROVIDER
    if p == "openrouter":
        return "openrouter", OPENROUTER_MODEL
    return "openai", OPENAI_MODEL


def get_openai_client(provider=None):
    """Returns an initialized (client, model_name). provider override or AI_PROVIDER env."""
    import openai
    p = (provider or "").strip().lower() or AI_PROVIDER
    if p == "openrouter":
        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY not set in .env")
        client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )
        return client, OPENROUTER_MODEL
    else:
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in .env")
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        return client, OPENAI_MODEL


# Midjourney (UseAPI)
MIDJOURNEY_API_TOKEN = os.getenv("MIDJOURNEY_API_TOKEN", "")
MIDJOURNEY_CHANNEL_ID = os.getenv("MIDJOURNEY_CHANNEL_ID", "")
USEAPI_BASE_URL = os.getenv("USEAPI_BASE_URL", "https://api.useapi.net/v3/midjourney")

# External article generator API
GENERATE_ARTICLE_API_URL = os.getenv("GENERATE_ARTICLE_API_URL", "http://localhost:8000")
# Website parts generator (headers, footers, categories, sidebars)
WEBSITE_PARTS_API_URL = os.getenv("WEBSITE_PARTS_API_URL", "http://localhost:8010")
# Path to article generators folder (for creating new templates)
_automation_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ARTICLE_GENERATORS_DIR = os.getenv("ARTICLE_GENERATORS_DIR", os.path.join(_automation_dir, "articles-website-generator", "generators"))
# Base directory for generated static projects (when no output_path specified)
STATIC_PROJECT_OUTPUT_DIR = os.getenv("STATIC_PROJECT_OUTPUT_DIR", os.path.join(_automation_dir, "output", "static-projects"))

# Pinterest Pin Editor (generate image from JSON)
PIN_EDITOR_URL = os.getenv("PIN_EDITOR_URL", "http://localhost:8080")  # serve.py
PIN_API_URL = os.getenv("PIN_API_URL", "http://localhost:5000")  # Kimi_Agent_Pin generator.py --serve

# Cloudflare Pages (deploy static projects)
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "")

# Cloudflare R2
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID", "")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID", "")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY", "")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME", "")
R2_PUBLIC_URL = os.getenv("R2_PUBLIC_URL", "")

# Pinterest: uses simple "Pin it" URL (no API key). No config needed.

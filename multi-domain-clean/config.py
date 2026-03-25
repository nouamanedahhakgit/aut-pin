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

# Groq (OpenAI-compatible API — https://console.groq.com/keys)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Local (Ollama or similar)
LOCAL_API_URL = os.getenv("LOCAL_API_URL", "http://192.168.1.20:11434")

# llama.cpp (via llamacpp_manager)
LLAMACPP_MANAGER_URL = os.getenv("LLAMACPP_MANAGER_URL", "http://localhost:5004")
LOCAL_MODELS = os.getenv("LOCAL_MODELS", "qwen3:8b,llama3.2:3b,gemma3:latest,ibm/granite4:latest,functiongemma:latest").split(",")

def get_ai_config(provider=None):
    """Return (provider, model) for display. provider override uses that, else AI_PROVIDER env."""
    p = (provider or "").strip().lower() or AI_PROVIDER
    if p == "openrouter":
        return "openrouter", OPENROUTER_MODEL
    if p == "groq":
        return "groq", GROQ_MODEL
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
    if p == "groq":
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not set in .env")
        client = openai.OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=GROQ_API_KEY,
        )
        return client, GROQ_MODEL
    else:
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in .env")
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        return client, OPENAI_MODEL


# Midjourney (UseAPI)
MIDJOURNEY_API_TOKEN = os.getenv("MIDJOURNEY_API_TOKEN", "")
MIDJOURNEY_CHANNEL_ID = os.getenv("MIDJOURNEY_CHANNEL_ID", "")
USEAPI_BASE_URL = os.getenv("USEAPI_BASE_URL", "https://api.useapi.net/v3/midjourney")

# Microservice API base URLs (from .env; multi-domain-clean calls these over HTTP)
GENERATE_ARTICLE_API_URL = os.getenv("GENERATE_ARTICLE_API_URL", "http://localhost:5002")   # articles-website-generator
WEBSITE_PARTS_API_URL = os.getenv("WEBSITE_PARTS_API_URL", "http://localhost:5003")         # website-parts-generator
PIN_API_URL = os.getenv("PIN_API_URL", "http://localhost:5000")                            # pin_generator --serve
PIN_EDITOR_URL = os.getenv("PIN_EDITOR_URL", "http://localhost:5004")                      # optional pin editor
# Path to article generators folder (for creating new templates)
_automation_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ARTICLE_GENERATORS_DIR = os.getenv("ARTICLE_GENERATORS_DIR", os.path.join(_automation_dir, "articles-website-generator", "generators"))
# Base directory for generated static projects (when no output_path specified)
STATIC_PROJECT_OUTPUT_DIR = os.getenv("STATIC_PROJECT_OUTPUT_DIR", os.path.join(_automation_dir, "output", "static-projects"))

# Cloudflare Pages (deploy static projects)
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "")

# Cloudflare R2 (optional if using local image hosting below)
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID", "")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID", "")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY", "")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME", "")
R2_PUBLIC_URL = os.getenv("R2_PUBLIC_URL", "")

# When R2 is not configured, pin/MJ/previews are stored on disk and served via /api/hosted-images/...
_config_dir = os.path.dirname(os.path.abspath(__file__))
HOSTED_IMAGES_DIR = os.getenv(
    "HOSTED_IMAGES_DIR",
    os.path.join(_config_dir, "data", "hosted_images"),
)
# Absolute base URL for image links when there is no HTTP request (bulk jobs, Pinterest). Example: https://your-app.com
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")

# Pinterest: uses simple "Pin it" URL (no API key). No config needed.

# Updater (in-app check/update Docker images)
UPDATER_URL = os.getenv("UPDATER_URL", "http://localhost:6006")

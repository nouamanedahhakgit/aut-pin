"""
Seed ai_provider_models table with initial data from theme defaults.
Run after tables exist: python scripts/init_ai_provider_models.py
"""
import os
import sys

_script_dir = os.path.dirname(os.path.abspath(__file__))
_app_dir = os.path.dirname(_script_dir)
sys.path.insert(0, _app_dir)

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(_app_dir, ".env"))
except ImportError:
    pass

from db import get_connection, execute as db_execute


# Initial data (matches app.py OPENROUTER_MODELS, OPENAI_MODELS, LOCAL_MODELS)
INIT_OPENROUTER = [
    {"id": "google/gemini-2.5-pro", "label": "Gemini 2.5 Pro — $1.25in/$5out /1M  [Best SEO, 2M ctx]", "free": False},
    {"id": "anthropic/claude-opus-4.6", "label": "Claude Opus 4.6 — $15in/$75out /1M  [Best Quality, Creative]", "free": False},
    {"id": "anthropic/claude-3.7-sonnet", "label": "Claude 3.7 Sonnet — $3in/$15out /1M  [Top Writing Quality]", "free": False},
    {"id": "openai/gpt-4o", "label": "GPT-4o — $2.50in/$10out /1M  [Reliable, Great SEO]", "free": False},
    {"id": "deepseek/deepseek-v3.2", "label": "DeepSeek V3.2 — $0.14in/$0.28out /1M  [Best Value, Trending]", "free": False},
    {"id": "google/gemini-2.0-flash", "label": "Gemini 2.0 Flash — $0.10in/$0.40out /1M  [Fast & Cheap]", "free": False},
    {"id": "anthropic/claude-3.5-haiku", "label": "Claude 3.5 Haiku — $0.80in/$4out /1M  [Fast Claude]", "free": False},
    {"id": "openai/gpt-4o-mini", "label": "GPT-4o Mini — $0.15in/$0.60out /1M  [Budget OpenAI]", "free": False},
    {"id": "deepseek/deepseek-r1", "label": "DeepSeek R1 — $0.55in/$2.19out /1M  [Reasoning, Detailed]", "free": False},
    {"id": "meta-llama/llama-3.3-70b-instruct", "label": "Llama 3.3 70B — $0.12in/$0.30out /1M  [Open Source]", "free": False},
    {"id": "mistralai/mistral-large-2411", "label": "Mistral Large — $2in/$6out /1M  [EU Alternative]", "free": False},
    {"id": "minimax/minimax-m2.5", "label": "MiniMax M2.5", "free": False},
    {"id": "google/gemini-2.0-flash-exp:free", "label": "[FREE] Gemini 2.0 Flash Exp — $0  [Best Free]", "free": True},
    {"id": "deepseek/deepseek-r1:free", "label": "[FREE] DeepSeek R1 — $0  [Free Reasoning]", "free": True},
    {"id": "deepseek/deepseek-v3:free", "label": "[FREE] DeepSeek V3 — $0  [Free, Rate Limited]", "free": True},
    {"id": "meta-llama/llama-3.3-70b-instruct:free", "label": "[FREE] Llama 3.3 70B — $0  [Free Open Source]", "free": True},
    {"id": "qwen/qwen2.5-72b-instruct:free", "label": "[FREE] Qwen 2.5 72B — $0  [Free, Rate Limited]", "free": True},
    {"id": "mistralai/mistral-7b-instruct:free", "label": "[FREE] Mistral 7B — $0  [Free Basic]", "free": True},
]

INIT_OPENAI = [
    {"id": "gpt-4o", "label": "GPT-4o — $2.50in / $10out /1M  [Best Balance, Top SEO]"},
    {"id": "gpt-4o-mini", "label": "GPT-4o Mini — $0.15in / $0.60out /1M  [Best Budget]"},
    {"id": "o3-mini", "label": "o3-mini — $1.10in / $4.40out /1M  [Reasoning, Structured]"},
    {"id": "o1-mini", "label": "o1-mini — $1.10in / $4.40out /1M  [Reasoning, Fast]"},
    {"id": "o1", "label": "o1 — $15in / $60out /1M  [Advanced Reasoning]"},
    {"id": "gpt-4-turbo", "label": "GPT-4 Turbo — $10in / $30out /1M  [Legacy, High Quality]"},
    {"id": "gpt-4", "label": "GPT-4 — $30in / $60out /1M  [Legacy Classic]"},
]

INIT_LOCAL = [
    {"id": "qwen3:8b", "label": "Qwen 3 8B"},
    {"id": "llama3.2:3b", "label": "Llama 3.2 3B"},
    {"id": "mistral:7b", "label": "Mistral 7B"},
    {"id": "qwen3.5:9b", "label": "Qwen 3.5 9B"},
]


def main():
    with get_connection() as conn:
        cur = db_execute(conn, "SELECT COUNT(*) as n FROM ai_provider_models")
        row = cur.fetchone()
        if isinstance(row, dict):
            n = row.get("n", 0) or 0
        else:
            n = (row or (0,))[0]
        if n > 0:
            print("ai_provider_models already has data, skipping seed.")
            return
        for i, m in enumerate(INIT_OPENROUTER):
            db_execute(conn, "INSERT INTO ai_provider_models (provider, model_id, label, is_free, sort_order) VALUES (?, ?, ?, ?, ?)",
                       ("openrouter", m["id"], m["label"], 1 if m.get("free") else 0, i))
        for i, m in enumerate(INIT_OPENAI):
            db_execute(conn, "INSERT INTO ai_provider_models (provider, model_id, label, is_free, sort_order) VALUES (?, ?, ?, ?, ?)",
                       ("openai", m["id"], m["label"], 0, i))
        for i, m in enumerate(INIT_LOCAL):
            db_execute(conn, "INSERT INTO ai_provider_models (provider, model_id, label, is_free, sort_order) VALUES (?, ?, ?, ?, ?)",
                       ("local", m["id"], m.get("label") or m["id"], 0, i))
        conn.commit()
    print(f"Seeded ai_provider_models: {len(INIT_OPENROUTER)} OpenRouter, {len(INIT_OPENAI)} OpenAI, {len(INIT_LOCAL)} Local.")


if __name__ == "__main__":
    main()

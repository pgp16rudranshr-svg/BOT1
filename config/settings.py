import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "briefings"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Minimal .env loader without requiring external packages
def load_env_file(env_path: Path):
    if not env_path.is_file():
        return
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip("'\"")
            if key not in os.environ:
                os.environ[key] = val

load_env_file(BASE_DIR / ".env")

# Recipient configuration
RECIPIENT_NAME = os.getenv("RECIPIENT_NAME", "Rudransh Rastogi")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "")
AFFILIATION = os.getenv("AFFILIATION", "IIM Rohtak (Finance & Tech)")

# AI Synthesis configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")  # 'gemini', 'openai', or 'heuristic'
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Email SMTP configuration
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))  # 465 (SSL) or 587 (TLS)
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")  # Gmail App Password (16 characters)
EMAIL_FROM = os.getenv("EMAIL_FROM", SMTP_USER)

# Newsletter Schedule
DAILY_DELIVERY_TIME = os.getenv("DAILY_DELIVERY_TIME", "10:00")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")

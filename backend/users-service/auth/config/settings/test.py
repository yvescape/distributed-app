# config/settings/test.py
import os
from pathlib import Path
from dotenv import load_dotenv

# BASE_DIR pointe vers : auth/config/settings/test.py
# .env.dev est dans    : users-service/.env.dev
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # → auth/
ENV_FILE = BASE_DIR.parent / ".env.local"                   # → users-service/.env.dev

load_dotenv(ENV_FILE)  # ← injecte les variables AVANT from .base import **

from .base import *    # ← base.py trouve maintenant ALLOWED_HOSTS dans os.environ

# Écrase ce dont les tests n'ont pas besoin
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

SECRET_KEY = "test-secret-key-not-used-in-production"
ALLOWED_HOSTS = ["*"]
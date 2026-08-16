from pathlib import Path
import os

from dotenv import load_dotenv
from supabase import Client, create_client


# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

ENV_FILE = PROJECT_ROOT / ".env"


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv(ENV_FILE)


# =========================================================
# SUPABASE CONFIGURATION
# =========================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")

SUPABASE_KEY = os.getenv("SUPABASE_KEY")


# Support existing Vite frontend .env variables
if not SUPABASE_URL:
    SUPABASE_URL = os.getenv("VITE_SUPABASE_URL")

if not SUPABASE_KEY:
    SUPABASE_KEY = os.getenv("VITE_SUPABASE_ANON_KEY")


# =========================================================
# VALIDATION
# =========================================================

if not SUPABASE_URL:
    raise RuntimeError(
        f"SUPABASE_URL is not set. Checked: {ENV_FILE}"
    )

if not SUPABASE_KEY:
    raise RuntimeError(
        f"SUPABASE_KEY is not set. Checked: {ENV_FILE}"
    )


# =========================================================
# CREATE SUPABASE CLIENT
# =========================================================

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY,
)

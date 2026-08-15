from pathlib import Path
import os

from dotenv import load_dotenv
from supabase import Client, create_client

BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL is not set")

if not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_KEY is not set")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY,
)
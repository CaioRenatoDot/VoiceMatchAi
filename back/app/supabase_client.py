import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
# Use Service Role Key for backend administration (bypasses RLS), fallback to Anon Key if not provided
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY or "seu-projeto" in SUPABASE_URL:
    # We raise an error or log a warning if configuration is not filled yet
    print("[WARNING] Supabase environment variables not fully configured. Using placeholders.")

# Initialize the client. Under normal execution, this requires valid credentials.
# We'll catch errors locally if the user hasn't filled their credentials yet.
supabase_client: Client = None

if SUPABASE_URL and SUPABASE_KEY and "seu-projeto" not in SUPABASE_URL:
    try:
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("[INFO] Supabase client initialized successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to initialize Supabase client: {e}")
else:
    print("[INFO] Supabase client not initialized (missing or default config).")


def get_supabase_client() -> Client:
    """Returns the initialized Supabase client."""
    if supabase_client is None:
        raise RuntimeError("Supabase client is not initialized. Please verify your .env file.")
    return supabase_client

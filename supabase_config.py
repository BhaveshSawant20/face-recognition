import os
from supabase import create_client
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


# ✅ FAIL FAST (very important in production apps)
if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception(
        "Supabase credentials missing. Check your .env file."
    )


# Create client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

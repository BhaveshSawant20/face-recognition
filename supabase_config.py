import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

# Load env variables
load_dotenv()

def get_supabase_client() -> Client:

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("Supabase credentials missing in environment variables")
        st.stop()

    try:
        client = create_client(
            SUPABASE_URL,
            SUPABASE_KEY,
            options={
                "auto_refresh_token": False,
                "persist_session": False
            }
        )

        return client

    except Exception as e:
        st.error(f"Supabase connection error: {e}")
        st.stop()


# Singleton style client (important for Streamlit)
supabase = get_supabase_client()

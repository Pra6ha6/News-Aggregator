import os
import json
import streamlit as st
from supabase import create_client, Client
from streamlit_google_auth import Authenticate
from dotenv import load_dotenv

load_dotenv()

# Supabase Setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Google Auth Setup
    # Dynamic Redirect URI Detection
    env_redirect = os.getenv("REDIRECT_URI")
    # If on streamlit cloud, we can try to guess or use the env
    redirect_uri = env_redirect if env_redirect else "http://localhost:8501"
    
    # Log for user to check in Streamlit Cloud "Logs" tab
    print(f"DEBUG: Auth Manager initialized with Redirect URI: {redirect_uri}")
    if not env_redirect:
        print("WARNING: REDIRECT_URI env var is NOT set. Defaulting to localhost.")

    return Authenticate(
        secret_credentials_path=creds_path,
        cookie_name='news_aggregator_auth',
        cookie_key=os.getenv("COOKIE_SECRET", "news_aggregator_secret_key"),
        cookie_expiry_days=30,
        redirect_uri=redirect_uri,
    )

def sync_user_to_supabase(user_info):
    """Saves or updates user info in Supabase."""
    supabase = get_supabase_client()
    user_id = user_info.get("sub")
    email = user_info.get("email")
    
    data = {
        "id": user_id,
        "email": email,
        "name": user_info.get("name"),
        "picture": user_info.get("picture"),
        "last_login": "now()"
    }
    
    # Upsert logic
    try:
        supabase.table("profiles").upsert(data).execute()
    except Exception as e:
        st.error(f"Error syncing user to Supabase: {e}")

def get_user_preferences(user_id):
    supabase = get_supabase_client()
    try:
        response = supabase.table("profiles").select("preferences").eq("id", user_id).execute()
        if response.data:
            return response.data[0].get("preferences") or {}
    except Exception as e:
        st.error(f"Error fetching preferences: {e}")
    return {}

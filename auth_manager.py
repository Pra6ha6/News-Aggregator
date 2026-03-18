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
def get_auth_manager():
    # streamlit-google-auth often expects a client_secret.json file.
    # We can construct it from env vars if needed.
    redirect_uri = os.getenv("REDIRECT_URI", "http://localhost:8501")
    google_creds = {
        "web": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": [redirect_uri]
        }
    }
    
    # Save to a temporary file as streamlit-google-auth often requires a path
    creds_path = "google_creds.json"
    with open(creds_path, "w") as f:
        json.dump(google_creds, f)
        
    return Authenticate(
        secret_credentials_path=creds_path,
        cookie_name='news_aggregator_auth',
        cookie_key='news_aggregator_secret_key', # Should be in env for production
        cookie_expiry_days=30,
        redirect_uri=os.getenv("REDIRECT_URI", "http://localhost:8501"),
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

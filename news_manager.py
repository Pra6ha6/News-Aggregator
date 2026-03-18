import os
import requests
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2/"

# Categorized sources for triangulation
SOURCES = {
    "neutral": ["reuters", "associated-press", "bbc-news", "united-press-international"],
    "left": ["cnn", "the-guardian-uk", "msnbc", "the-huffington-post"],
    "right": ["fox-news", "the-washington-times", "breitbart-news", "national-review"]
}

def fetch_top_stories(country='us', category='general'):
    """Fetches a larger pool of headlines for better clustering and triangulation."""
    api_key = os.getenv("NEWS_API_KEY")
    # Using everything endpoint for more diversity if needed, or top-headlines for speed
    base_url = "https://newsapi.org/v2/top-headlines"
    
    params = {
        "apiKey": api_key,
        "country": country,
        "category": category,
        "pageSize": 50 # Fetch more for clustering
    }
            
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json().get("articles", [])
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

def group_by_topic(all_articles):
    """Simple grouping logic to find matching stories across perspectives."""
    # In a more advanced version, we would use embeddings to find related stories.
    # For now, we'll return the structures as is, or look for keyword matches in titles.
    return all_articles

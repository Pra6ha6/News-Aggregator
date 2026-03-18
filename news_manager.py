import requests
import os

# Full list of countries supported by News API (ISO 3166-1 alpha-2)
COUNTRIES = {
    "United Arab Emirates": "ae", "Argentina": "ar", "Austria": "at", "Australia": "au", "Belgium": "be",
    "Bulgaria": "bg", "Brazil": "br", "Canada": "ca", "Switzerland": "ch", "China": "cn", "Colombia": "co",
    "Cuba": "cu", "Czech Republic": "cz", "Germany": "de", "Egypt": "eg", "France": "fr", "United Kingdom": "gb",
    "Greece": "gr", "Hong Kong": "hk", "Hungary": "hu", "Indonesia": "id", "Ireland": "ie", "Israel": "il",
    "India": "in", "Italy": "it", "Japan": "jp", "South Korea": "kr", "Lithuania": "lt", "Latvia": "lv",
    "Morocco": "ma", "Mexico": "mx", "Malaysia": "my", "Nigeria": "ng", "Netherlands": "nl", "Norway": "no",
    "New Zealand": "nz", "Philippines": "ph", "Poland": "pl", "Portugal": "pt", "Romania": "ro", "Serbia": "rs",
    "Russia": "ru", "Saudi Arabia": "sa", "Sweden": "se", "Singapore": "sg", "Slovenia": "si", "Slovakia": "sk",
    "Thailand": "th", "Turkey": "tr", "Taiwan": "tw", "Ukraine": "ua", "United States": "us", "Venezuela": "ve",
    "South Africa": "za"
}

def fetch_top_stories(country='us', category='general', query=None):
    """Fetches a larger pool of headlines with optional custom query."""
    api_key = os.getenv("NEWS_API_KEY")
    base_url = "https://newsapi.org/v2/top-headlines"
    
    params = {
        "apiKey": api_key,
        "pageSize": 100 # Maximum allowed for variety
    }
    
    if query:
        # If custom query is provided, we search EVERYTHING for better results
        base_url = "https://newsapi.org/v2/everything"
        params["q"] = query
        params["sortBy"] = "relevancy"
        params.pop("country", None) # Country not supported in 'everything'
        params.pop("category", None)
    else:
        params["country"] = country
        params["category"] = category
            
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        articles = response.json().get("articles", [])
        
        # Filter out removed articles
        return [a for a in articles if a.get('title') and a.get('title') != '[Removed]']
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

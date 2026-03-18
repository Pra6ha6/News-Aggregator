import requests
import os

def get_api_key():
    try:
        with open("env_backup.txt", "r") as f:
            for line in f:
                if 'NEWS_API_KEY=' in line:
                    return line.split('=')[1].strip().strip('"')
    except:
        return os.getenv("NEWS_API_KEY")

def test_fallback_strategy():
    api_key = get_api_key()
    if not api_key: return

    strategies = [
        ("Top Headlines (IN)", "https://newsapi.org/v2/top-headlines?country=in&apiKey=" + api_key),
        ("Keyword Search (India)", "https://newsapi.org/v2/everything?q=India&sortBy=relevancy&apiKey=" + api_key),
        ("Top Headlines (GB)", "https://newsapi.org/v2/top-headlines?country=gb&apiKey=" + api_key),
        ("Keyword Search (UK)", "https://newsapi.org/v2/everything?q=UK&sortBy=relevancy&apiKey=" + api_key)
    ]

    print(f"{'Strategy':<30} | {'Status':<10} | {'Count'}")
    print("-" * 50)
    
    for name, url in strategies:
        try:
            response = requests.get(url)
            data = response.json()
            count = len(data.get("articles", []))
            print(f"{name:<30} | Success    | {count}")
        except Exception as e:
            print(f"{name:<30} | Error      | 0")

if __name__ == "__main__":
    test_fallback_strategy()

# utils/newsapi_verifier.py

import requests
import os

# Load your API key (replace with your key or use environment variable)
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "a29d68220d844851be5d03fa398128ab")

def verify_with_newsapi(query):
    """
    Verifies news using NewsAPI by searching for matching headlines or descriptions.
    Returns source names and URLs if found.
    """
    if NEWSAPI_KEY == "your_newsapi_key_here":
        return {"status": "error", "message": "NewsAPI key not set", "sources": [], "urls": []}

    url = f"https://newsapi.org/v2/everything?q={query}&language=en&pageSize=10&apiKey={NEWSAPI_KEY}"

    try:
        response = requests.get(url)
        data = response.json()

        if data["status"] != "ok":
            return {"status": "error", "message": data.get("message", "Unknown error"), "sources": [], "urls": []}

        articles = data.get("articles", [])
        if not articles:
            return {"status": "error", "message": "No articles found", "sources": [], "urls": []}

        sources = [article["source"]["name"] for article in articles]
        urls = [article["url"] for article in articles]

        return {"status": "success", "sources": sources, "urls": urls}

    except Exception as e:
        return {"status": "error", "message": str(e), "sources": [], "urls": []}

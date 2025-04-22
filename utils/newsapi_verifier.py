import requests
import streamlit as st

# Load your API key from Streamlit secrets
NEWSAPI_KEY = st.secrets["API_KEYS"]["NEWSAPI_KEY"]

def verify_with_newsapi(query):
    """
    Verifies news using NewsAPI by searching for matching headlines or descriptions.
    Returns source names and URLs if found.
    """
    if not NEWSAPI_KEY:
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

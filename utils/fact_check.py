import nltk

# Ensure required NLTK data is downloaded
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from bs4 import BeautifulSoup
import requests
from googlesearch import search

# ---------------------------------------------
# Step 1: Extract Keywords
# ---------------------------------------------

def extract_keywords(text):
    stop_words = set(stopwords.words("english"))
    words = word_tokenize(text.lower())
    keywords = [word for word in words if word.isalpha() and word not in stop_words]
    return keywords[:6]  # Limit to 6 keywords for better search precision

# ---------------------------------------------
# Step 2: Find most relevant official site dynamically
# ---------------------------------------------

def find_probable_official_site(keywords):
    try:
        query = f"{' '.join(keywords)} official site"
        url = f"https://duckduckgo.com/html/?q={query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        for link in soup.find_all("a", href=True):
            href = link["href"]
            if any(x in link.text.lower() for x in ["official", "gov", "edu"]):
                if "http" in href:
                    return href.split("/")[2]  # return domain
    except Exception as e:
        print(f"Error identifying official site: {e}")
    return None

# ---------------------------------------------
# Step 3: Search site using Google (or fallback)
# ---------------------------------------------

def google_search_links(query, site, max_links=2):
    headers = {"User-Agent": "Mozilla/5.0"}
    search_url = f"https://www.google.com/search?q=site:{site}+{query}"
    try:
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        links = []
        for a in soup.find_all("a"):
            href = a.get("href")
            if href and "/url?q=" in href:
                link = href.split("/url?q=")[1].split("&")[0]
                if link.startswith("http") and site in link:
                    links.append(link)
        return links[:max_links]
    except Exception as e:
        print(f"Google scrape error: {e}")
        try:
            query_string = f"site:{site} {query}"
            return list(search(query_string, num_results=max_links))
        except Exception as fallback_e:
            print(f"Fallback search error: {fallback_e}")
            return []

# ---------------------------------------------
# Step 4: Trusted Tamil and English News Sites
# ---------------------------------------------

TRUSTED_SITES = [
    "wikipedia.org",
    "thehindu.com",
    "bbc.com",
    "ndtv.com",
    "news18.com",
    "hindustantimes.com",
    "indiatoday.in",
    "timesofindia.indiatimes.com",
    "theprint.in",
    "reuters.com",
    "cnn.com",
    "scroll.in",
    "thewire.in",
    "altnews.in",
    "factly.in",
    "boomlive.in",
    "newslaundry.com",
    "deccanherald.com",
    "puthiyathalaimurai.com",
    "dailythanthi.com",
    "polimernews.com",
    "dinamalar.com",
    "dinakaran.com"
]


# ---------------------------------------------
# Step 5: Verify Function
# ---------------------------------------------
# ---------------------------------------------
# Step 5: Verify Function
# ---------------------------------------------

def verify_facts(text):
    keywords = extract_keywords(text)
    results = {}

    # Step 1: Try Official Site First
    official_site = find_probable_official_site(keywords)
    if official_site:
        links = google_search_links(' '.join(keywords), official_site)
        if links:
            results[official_site] = links

    # Step 2: Search Trusted Sources
    for site in TRUSTED_SITES:
        try:
            links = google_search_links(' '.join(keywords), site)
            if links:
                results[site] = links
        except Exception as e:
            print(f"Search error for {site}: {e}")

    return results
 
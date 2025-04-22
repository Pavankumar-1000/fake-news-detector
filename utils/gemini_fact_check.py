import os
import re
import json
import streamlit as st
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

# Load API Key from Streamlit secrets
GENAI_API_KEY = st.secrets["API_KEYS"]["GEMINI_API_KEY"]

if not GENAI_API_KEY:
    raise ValueError("Gemini API Key not found. Add GEMINI_API_KEY to your .streamlit/secrets.toml.")

# Configure Gemini
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")  # Or use "gemini-1.5-pro"

def fact_check_with_gemini(news_text: str) -> dict:
    news_text = news_text.strip()

    prompt = f"""
You are a smart AI fact-checker.

Your job is to **check if the given news is real or fake** using official websites (like government, university, or space agencies), Wikipedia, and trusted news sites (NDTV, The Hindu, BBC, etc.).

✅ STRICT INSTRUCTIONS:
- Ignore all spelling mistakes, grammar errors, and informal wording.
- Understand Tamil names, short forms (e.g., "mk stalin" → "M. K. Stalin", "tn" → "Tamil Nadu", "managaram" → "Maanagaram").
- Do **not correct** the user's sentence or comment on spelling. Focus only on the **truth of the news**.
- Output only the result in the required format.

Return exactly this format in plain JSON:

{{
  "verdict": "Real or Fake",
  "confidence": 0-100,
  "explanation": "Why it's true or false (1-2 lines only)",
  "sources": ["https://source1.com", "https://source2.com"]
}}

News to verify: {news_text}
"""

    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()

        # Attempt direct JSON parsing
        try:
            result_json = json.loads(result_text)
        except json.JSONDecodeError:
            # Try to extract a JSON object using regex
            match = re.search(r"\{[\s\S]+?\}", result_text)
            if match:
                try:
                    result_json = json.loads(match.group())
                except:
                    return _invalid_json_response(result_text)
            else:
                return _invalid_json_response(result_text)

        # Validate required keys
        required_keys = {"verdict", "confidence", "explanation", "sources"}
        if not required_keys.issubset(result_json.keys()):
            return _incomplete_keys_response(result_text)

        # Normalize and validate values
        verdict = result_json.get("verdict", "").strip().lower()
        if verdict not in ["real", "fake"]:
            return _invalid_json_response(result_text)

        return {
            "verdict": result_json["verdict"].capitalize(),
            "confidence": int(result_json.get("confidence", 0)),
            "explanation": result_json.get("explanation", ""),
            "sources": result_json.get("sources", []),
            "status": "success"
        }

    except ResourceExhausted as e:
        return {
            "verdict": "limit_exceeded",
            "confidence": 0,
            "explanation": "Your Gemini API usage limit has been exceeded.",
            "sources": [],
            "error": str(e)
        }

    except Exception as e:
        return {
            "verdict": "error",
            "confidence": 0,
            "explanation": f"Gemini API error: {str(e)}",
            "sources": []
        }

def _invalid_json_response(raw):
    return {
        "verdict": "error",
        "confidence": 0,
        "explanation": "Gemini API gave an invalid response.",
        "sources": [],
        "raw_response": raw
    }

def _incomplete_keys_response(raw):
    return {
        "verdict": "error",
        "confidence": 0,
        "explanation": "Gemini response is missing required fields.",
        "sources": [],
        "raw_response": raw
    }

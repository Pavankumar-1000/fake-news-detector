# utils/preprocess.py

import re
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords

# Download stopwords if not already
nltk.download('stopwords')

def clean_text(text):
    """
    Basic cleaning: remove symbols, numbers, extra spaces, etc.
    Supports both Tamil and English.
    """
    text = str(text)
    text = text.lower()
    text = re.sub(r"http\S+", "", text)  # remove URLs
    text = re.sub(r"[^a-zA-Z\u0B80-\u0BFF\s]", "", text)  # remove special chars, keep Tamil/English
    text = re.sub(r"\s+", " ", text).strip()
    return text

def correct_spelling(text):
    """
    Correct English spelling using TextBlob.
    Tamil is returned as-is (TextBlob doesn't support Tamil).
    """
    if re.search("[a-zA-Z]", text):  # If text contains English
        corrected = str(TextBlob(text).correct())
        return corrected
    else:
        return text  # Return Tamil as-is

def preprocess_text(text):
    """
    Complete preprocessing: clean, correct, etc.
    """
    text = clean_text(text)
    text = correct_spelling(text)
    return text


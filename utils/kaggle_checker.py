# utils/kaggle_checker.py

import os
import pandas as pd
from difflib import SequenceMatcher
from kaggle.api.kaggle_api_extended import KaggleApi

DATA_DIR = "data"
COMBINED_FILE = os.path.join(DATA_DIR, "news_dataset.csv")

# 1. Download dataset if missing
def download_kaggle_dataset():
    if not os.path.exists(COMBINED_FILE):
        os.makedirs(DATA_DIR, exist_ok=True)
        api = KaggleApi()
        api.authenticate()
        api.dataset_download_files('clmentbisaillon/fake-and-real-news-dataset', path=DATA_DIR, unzip=True)

        # Combine True and Fake datasets
        fake_df = pd.read_csv(os.path.join(DATA_DIR, "Fake.csv"))
        true_df = pd.read_csv(os.path.join(DATA_DIR, "True.csv"))

        fake_df['label'] = 'FAKE'
        true_df['label'] = 'REAL'

        combined = pd.concat([fake_df, true_df], ignore_index=True)
        combined = combined[['text', 'label']]
        combined.to_csv(COMBINED_FILE, index=False)

# 2. Match input with existing news
def check_against_kaggle(cleaned_input):
    download_kaggle_dataset()
    df = pd.read_csv(COMBINED_FILE)

    matches = []
    for _, row in df.iterrows():
        similarity = SequenceMatcher(None, cleaned_input, str(row['text'])).ratio()
        if similarity > 0.85:
            matches.append({
                "text": row["text"],
                "label": row["label"],
                "similarity": similarity
            })

    if matches:
        matches.sort(key=lambda x: x["similarity"], reverse=True)
        return {
            "match_found": True,
            "verdict": matches[0]["label"],
            "matches": matches
        }
    else:
        return {
            "match_found": False,
            "verdict": None,
            "matches": []
        }

import os
from kaggle.api.kaggle_api_extended import KaggleApi

DATASET_NAME = "clmentbisaillon/fake-and-real-news-dataset"
DEST_DIR = "data"
FILENAME = "news_dataset.csv"

def download_latest_dataset():
    os.makedirs(DEST_DIR, exist_ok=True)

    # Skip download if file already exists
    file_path = os.path.join(DEST_DIR, FILENAME)
    if os.path.exists(file_path):
        return  # Already downloaded

    api = KaggleApi()
    api.authenticate()

    # Download dataset zip and unzip
    api.dataset_download_files(DATASET_NAME, path=DEST_DIR, unzip=True)

    # Rename CSV if needed
    raw_files = os.listdir(DEST_DIR)
    for file in raw_files:
        if file.endswith(".csv") and file != FILENAME:
            src = os.path.join(DEST_DIR, file)
            dest = os.path.join(DEST_DIR, FILENAME)

            # If destination exists, remove it first
            if os.path.exists(dest):
                os.remove(dest)

            os.rename(src, dest)

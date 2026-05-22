import os
import re
from google.cloud import storage
from dotenv import load_dotenv

load_dotenv()

DEV_MODE = os.getenv("DEV_MODE", "True").lower() == "true"
GCS_BUCKET = os.getenv("GCS_BUCKET", "mi-bucket-f1")
RAW_PREFIX = "dev_raw" if DEV_MODE else "raw"

RAW_DATA_DIR = 'data/raw'
SILVER_DATA_DIR = 'data/silver'
CACHE_DIR = 'caching'

os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(SILVER_DATA_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

def slugify(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9]+', '_', text)
    return text.strip('_')

def guardar_a_parquet(df, filename):
    if df is not None and not df.empty:
        if DEV_MODE:
            df = df.head(10)
            
        filepath = os.path.join(RAW_DATA_DIR, f"{filename}.parquet")
        df.to_parquet(filepath, index=False)
        print(f"  -> [OK] Guardado local: {filepath}")

def gcs_client():
    return storage.Client()
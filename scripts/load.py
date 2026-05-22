import os
import sys
import shutil

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import RAW_PREFIX, RAW_DATA_DIR

MOCK_BUCKET_DIR = 'mock_gcs_bucket'

def upload_to_gcs_simulation():
    print("\n=== INICIANDO CARGA (SIMULACIÓN DATA LAKE LOCAL) ===")
    
    if not os.path.exists(RAW_DATA_DIR):
        print("No hay datos locales para cargar.")
        return

    for filename in os.listdir(RAW_DATA_DIR):
        if filename.endswith(".parquet"):
            filepath = os.path.join(RAW_DATA_DIR, filename)
            
            parts = filename.split('_')
            dataset = parts[0]
            year = parts[1] if len(parts) > 1 else "unknown"
            
            destino_dir = os.path.join(MOCK_BUCKET_DIR, RAW_PREFIX, dataset, f"year={year}")
            os.makedirs(destino_dir, exist_ok=True)
            
            destino_archivo = os.path.join(destino_dir, filename)
            shutil.copy(filepath, destino_archivo)
            print(f"  -> Archivo alojado en: gs://{MOCK_BUCKET_DIR}/{RAW_PREFIX}/{dataset}/year={year}/{filename}")
            
    print("=== CARGA COMPLETADA ===")

if __name__ == "__main__":
    upload_to_gcs_simulation()
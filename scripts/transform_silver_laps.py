import duckdb
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import RAW_DATA_DIR, SILVER_DATA_DIR

def process_silver_laps():
    print("\n" + "="*50)
    print("proesamos la capa silver: tabla de laps")
    print("="*50 + "\n")

    con = duckdb.connect(database=':memory:')

    # Consulta SQL corregida con el "Doble CAST" para DuckDB
    query_laps = f"""
    SELECT 
        DriverNumber,
        Driver,
        LapTime / 1e9 AS LapTime,
        LapNumber,
        Stint,
        
        -- Corrección DuckDB: Primero a TIMESTAMP normal, luego a TIME
        CAST(CAST(to_timestamp(PitInTime / 1000000000.0) AS TIMESTAMP) AS TIME) AS PitInTime,
        CAST(CAST(to_timestamp(PitOutTime / 1000000000.0) AS TIMESTAMP) AS TIME) AS PitOutTime,
        
        SpeedST,
        Compound,
        FreshTyre,
        Team,
        Position,
        
        CAST(regexp_extract(filename, 'laps_(\\d{{4}})', 1) AS INTEGER) AS year,
        regexp_extract(filename, 'laps_\\d{{4}}_(.*)\\.parquet', 1) AS eventname

    FROM '{RAW_DATA_DIR}/laps_*.parquet'
    WHERE LapTime IS NOT NULL
    ORDER BY year, eventname, Driver, LapNumber
    """
    
    print("Ejecutando Query SQL para crear tabla 'silver_laps'...")
    df_silver_laps = con.execute(query_laps).df()
    
    ruta_destino = f'{SILVER_DATA_DIR}/silver_laps.parquet'
    df_silver_laps.to_parquet(ruta_destino)
    
    print(f"-> Tabla guardada exitosamente en: {ruta_destino}")
    
    print("\n muestra de data enfocada en paradas de los pits")
    mask_pits = df_silver_laps['PitInTime'].notna()
    if mask_pits.any():
        print(df_silver_laps[mask_pits].head(10).to_string())
    else:
        print(df_silver_laps.head(10).to_string())
    
    print("\n" + "="*50)

if __name__ == "__main__":
    process_silver_laps()
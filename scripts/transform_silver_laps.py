import duckdb
import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import RAW_DATA_DIR, SILVER_DATA_DIR

def process_silver_laps_incremental():
    print("\n" + "="*50)
    print("procesando capa silver: metodo incrementra de laps ===")
    print("="*50 + "\n")

    con = duckdb.connect(database=':memory:')
    silver_table_path = f'{SILVER_DATA_DIR}/silver_laps.parquet'
    table_exists = os.path.exists(silver_table_path)

    # 1. incremento de eventosq ya existen en Silver
    if table_exists:
        print("Tabla Silver encontrada, aplicando incremento...")
        procesados_df = con.execute(f"SELECT DISTINCT eventname FROM '{silver_table_path}'").df()
        eventos_procesados = procesados_df['eventname'].tolist()
        
        if eventos_procesados:
            # Formateamos los eventos para la consulta SQL (ej: 'australian_grand_prix', 'chinese_grand_prix')
            eventos_str = ", ".join([f"'{e}'" for e in eventos_procesados])
            incremental_filter = f"AND eventname NOT IN ({eventos_str})"
        else:
            incremental_filter = ""
    else:
        print("tabla Silver NO encontrada")
        incremental_filter = ""

    # 2. CONSULTA SQL
    query_laps = f"""
    WITH raw_data AS (
        SELECT 
            DriverNumber,
            Driver,
            LapTime / 1e9 AS LapTime,
            LapNumber,
            Stint,
            
            -- Doble CAST seguro para evitar el error de zona horaria (TIME ZONE)
            CAST(CAST(to_timestamp(PitInTime / 1000000000.0) AS TIMESTAMP) AS TIME) AS PitInTime,
            CAST(CAST(to_timestamp(PitOutTime / 1000000000.0) AS TIMESTAMP) AS TIME) AS PitOutTime,
            
            SpeedST,
            Compound,
            FreshTyre,
            Team,
            Position,
            
            -- Expresiones regulares limpias para extraer el Año y Nombre del Evento desde el archivo
            CAST(regexp_extract(filename, 'laps_([0-9]+)', 1) AS INTEGER) AS year,
            regexp_extract(filename, 'laps_[0-9]+_([^\\.]+)\\.parquet', 1) AS eventname

        FROM '{RAW_DATA_DIR}/laps_*.parquet'
        WHERE LapTime IS NOT NULL
    )
    SELECT * FROM raw_data
    WHERE 1=1 {incremental_filter}
    ORDER BY year, eventname, Driver, LapNumber
    """
    
    print("Ejecutando Query SQL...")
    df_nuevos_datos = con.execute(query_laps).df()
    
    # 3. CONSOLIDACIÓN DE DATOS
    if df_nuevos_datos.empty:
        print("No hay carreras nuevas, tabla Silver está 100% actualizada.")
    else:
        print(f"Se encontraron {len(df_nuevos_datos)} filas de carreras nuevas para insertar...")
        
        if table_exists:            
            df_existente = pd.read_parquet(silver_table_path)
            df_final = pd.concat([df_existente, df_nuevos_datos], ignore_index=True)
        else:
            df_final = df_nuevos_datos
            
        # escribimos en el parquet de la capa Silver
        df_final.to_parquet(silver_table_path)
        print(f"-> Incremento aplicado, guardando tabla en: {silver_table_path}")

    # 4. resultado en github actions
    if os.path.exists(silver_table_path):
        df_mostrar = pd.read_parquet(silver_table_path)
        print(f"\n total filas en silver laps: {len(df_mostrar)} ---")
        mask_pits = df_mostrar['PitInTime'].notna()
        if mask_pits.any():
            print(df_mostrar[mask_pits].head(10).to_string())
        else:
            print(df_mostrar.head(10).to_string())
    
    print("\n" + "="*50)

if __name__ == "__main__":
    process_silver_laps_incremental()
import fastf1
import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import CACHE_DIR, slugify, guardar_a_parquet

fastf1.Cache.enable_cache(CACHE_DIR)

YEARS = [2025, 2026]
ROUNDS = [1, 2, 3]

def extract_schedule(year):
    print(f"\nExtrayendo calendario para {year}...")
    schedule = fastf1.get_event_schedule(year)
    guardar_a_parquet(schedule, f"schedule_{year}")

def extract_session(year, round_num):
    print(f"Extrayendo carrera - Año: {year} | Ronda: {round_num}...")
    try:
        session = fastf1.get_session(year, round_num, 'R')
        session.load(telemetry=False, weather=False, messages=False)
        event_name = slugify(session.event['EventName'])
        
        guardar_a_parquet(session.results, f"results_{year}_{event_name}")
        
        if session.laps is not None and len(session.laps) > 0:
            guardar_a_parquet(session.laps, f"laps_{year}_{event_name}")
            
    except Exception as e:
        print(f"  [!] Info ronda {round_num} del {year}: {e}")

if __name__ == "__main__":
    print("iniciando extraccion ")
    for year in YEARS:
        extract_schedule(year)
        for r in ROUNDS:
            extract_session(year, r)
    print("extraccion completaa")
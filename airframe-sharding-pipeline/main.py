import csv
import json
from pathlib import Path
from re import A
from threading import local
import pandas as pd
from dataclasses import asdict, dataclass, field
from typing import Optional
from datetime import datetime

# settings
OUTPUT_DIRECTORY = "airframe-sharding-pipeline/output/"

# paths
aircrafts_csv_path = "airframe-sharding-pipeline/data/aircraft_data.xlsx"

# ensure output directory exists before writing to it
Path(OUTPUT_DIRECTORY).mkdir(parents=True, exist_ok=True)

# datasets
aircrafts = pd.read_excel(aircrafts_csv_path)

# helper function to handle NaN values and enforce data types safely
def safe_get(val, default, cast_type):
    if pd.isna(val):
        return default
    try:
        return cast_type(val)
    except (ValueError, TypeError):
        return default

# define classses
@dataclass
class Aircraft:
    icao: str = ""
    faa_designator: str = ""
    manufacturer: str = ""
    model_faa: str = ""
    model_bada: str = ""
    engine_class : str = ""
    num_engines : int = 0
    last_update: str = ""
    aircraft_class : str = ""
    remark : str = ""
    operations_count : int = 0
    approach_speed_kts : int = 0
    approach_speed_min_kts : int = 0
    approach_speed_max_kts : int = 0
    length_ft : float = 0.0

# the following is gonna be some bad spaghetti code but it should do the job we want
for i, aircraft in aircrafts.iterrows():
    # fetch ICAO code using the exact column header from the data dictionary
    ident = safe_get(aircraft.get('ICAO_Code'), "", str)
    
    if not ident:
        continue # skip if no ICAO code is present to avoid unnamed files

    # set up aircraft object
    aircraft_obj = Aircraft(
        icao = ident,
        faa_designator = safe_get(aircraft.get('FAA_Designator'), "", str),
        manufacturer = safe_get(aircraft.get('Manufacturer'), "", str),
        model_faa = safe_get(aircraft.get('Model_FAA'), "", str),
        model_bada = safe_get(aircraft.get('Model_BADA'), "", str),
        engine_class = safe_get(aircraft.get('Physical_Class_Engine'), "", str),
        num_engines = safe_get(aircraft.get('Num_Engines'), 0, int),
        last_update = safe_get(aircraft.get('LastUpdate'), "", str),
        aircraft_class = safe_get(aircraft.get('Class'), "", str),
        remark = safe_get(aircraft.get('Remarks'), "", str), 
        operations_count = safe_get(aircraft.get('TMFS_Operations_FY24'), 0, int),
        approach_speed_kts = safe_get(aircraft.get('Approach_Speed_knot'), 0, int),
        approach_speed_min_kts = safe_get(aircraft.get('Approach_Speed_minimum_knot'), 0, int),
        approach_speed_max_kts = safe_get(aircraft.get('Approach_Speed_maximum_knot'), 0, int),
        length_ft = safe_get(aircraft.get('Length_ft'), 0.0, float)
    )
 
    # export
    json_doc_dumped_str = json.dumps(asdict(aircraft_obj), indent=4)
    
    with open(Path(OUTPUT_DIRECTORY, ident).with_suffix(".json"), "w+") as manifest:
        manifest.write(json_doc_dumped_str)
        
    print(f"exported {ident}!")
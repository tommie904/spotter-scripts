# spotter-scripts

Offline data-prep scripts for the Spotter project for MSFS. These are not part of the running app, they're run manually to turn raw source datasets into the sharded JSON files the app reads at runtime.

## airport-sharding-pipeline

Reads OurAirports CSV data (`airports.csv`, `runways.csv`, `airport-frequencies.csv`) and writes one JSON file per airport (keyed by ICAO ident) to `output/`. Each file bundles the airport record with its runways and frequencies.

`countries.csv`, `regions.csv`, `navaids.csv`, `FAACIFP18`, and `vgsi_*.csv` are staged in `data/` for future use.

Run:
```
python airport-sharding-pipeline/main.py
```

## airframe-sharding-pipeline

Reads aircraft performance data from `data/aircraft_data.xlsx` (FAA/BADA data) and writes one JSON file per aircraft (keyed by ICAO type code) to `output/`.

Run:
```
python airframe-sharding-pipeline/main.py
```

## Data sources

- [OurAirports](https://ourairports.com/) - airport, runway, navaid, and frequency data
- [FAA Aircraft Characteristics Database](https://www.faa.gov/airports/engineering/aircraft_char_database) - aircraft type data
- [FAA CIFP (Coded Instrument Flight Procedures)](https://www.faa.gov/air_traffic/flight_info/aeronav/digital_products/cifp/download/) - procedure data
- [FAA Visual Glide Slope Indicator (VGSI)](https://www.faa.gov/air_traffic/flight_info/aeronav/aero_data/vgsi/) - glideslope location data

## Dependencies

```
pip install -r requirements.txt
```

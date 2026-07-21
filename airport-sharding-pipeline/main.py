import json
from pathlib import Path
import pandas as pd
from dataclasses import asdict, dataclass, field
from typing import Optional

# settings
BASE_DIR = Path(__file__).resolve().parent
DATA_DIRECTORY = BASE_DIR / "data"
OUTPUT_DIRECTORY = BASE_DIR / "output"

OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)

# paths
airports_csv_path = DATA_DIRECTORY / "airports.csv"
runways_csv_path = DATA_DIRECTORY / "runways.csv"
airports_frequencies_csv_path = DATA_DIRECTORY / "airport-frequencies.csv"
airports_comments_csv_path = DATA_DIRECTORY / "airport-comments.csv"

# datasets
airports = pd.read_csv(airports_csv_path, skipinitialspace=True, skip_blank_lines=True)
runways = pd.read_csv(runways_csv_path, skipinitialspace=True, skip_blank_lines=True)
frequencies = pd.read_csv(airports_frequencies_csv_path, skipinitialspace=True, skip_blank_lines=True)
comments = pd.read_csv(airports_comments_csv_path, skipinitialspace=True, skip_blank_lines=True)

# clear it out, to avoid Nan values ^
airports = airports.where(pd.notna(airports), None)
runways = runways.where(pd.notna(runways), None)
frequencies = frequencies.where(pd.notna(frequencies), None)
comments = comments.where(pd.notna(comments), None)

def safe_get(val, default, cast_type):
    if pd.isna(val) or val is None:
        return default
    try:
        return cast_type(val)
    except (ValueError, TypeError):
        return default

# define classses
@dataclass
class AirportFrequency:
    #id: int
    #airport_ref: int
    #airport_ident: str
    type: str
    description: str
    frequency_mhz: float

@dataclass
class AirportComment: # deprecated
    id: int
    thread_ref: int
    airport_ref: int
    airport_ident: str
    date: str
    member_nickname: str
    subject: str
    body: str

@dataclass
class Runway:
    #id: int
    #airport_ref: Optional[int]
    #airport_ident: Optional[str]
    length_ft: Optional[int]
    width_ft: Optional[int]
    surface: str
    lighted: int
    #closed: int

    # low end rwy
    le_ident: str
    le_latitude_deg: Optional[float]
    le_longitude_deg: Optional[float]
    le_elevation_ft: Optional[int]
    le_heading_degT: Optional[float]
    le_displaced_threshold_ft: Optional[int]

    # high end rwy
    he_ident: str
    he_latitude_deg: Optional[float]
    he_longitude_deg: Optional[float]
    he_elevation_ft: Optional[int]
    he_heading_degT: Optional[float]
    he_displaced_threshold_ft: Optional[int]

@dataclass
class Airport:
    id: int
    ident: str
    type: str
    name: str
    latitude_deg: float
    longitude_deg: float
    elevation_ft: Optional[int]
    continent: str
    iso_country: str
    iso_region: str
    municipality: str
    scheduled_service: str
    icao_code: str
    iata_code: str
    gps_code: str
    local_code: str
    home_link: str
    wikipedia_link: str
    keywords: str
    runways: Optional[list[Runway]] = field(default_factory=list)
    comments: Optional[list[AirportComment]] = field(default_factory=list)
    frequencies: Optional[list[AirportFrequency]] = field(default_factory=list)
    # will put optional approach stuff here later in the future
    approaches: Optional[list] = field(default_factory=list)

# grouped data
grouped_rwys = runways.groupby("airport_ident")
grouped_freqs = frequencies.groupby("airport_ident")
grouped_comments = comments.groupby("airportIdent")

# get runways from ident
def get_runways(ident) -> list[Runway]:
    rwys: list[Runway] = []

    if ident in grouped_rwys.groups:
        lcl_rwys = grouped_rwys.get_group(ident)
    else:
        lcl_rwys = pd.DataFrame()

    for rwy in lcl_rwys.itertuples(index=False):
        r = Runway(
            length_ft=safe_get(getattr(rwy, "length_ft", None), 0, int),
            width_ft=safe_get(getattr(rwy, "width_ft", None), 0, int),
            surface=safe_get(getattr(rwy, "surface", None), "", str),
            lighted=safe_get(getattr(rwy, "lighted", None), 0, int),
            le_ident=safe_get(getattr(rwy, "le_ident", None), "", str),
            le_latitude_deg=safe_get(getattr(rwy, "le_latitude_deg", None), 0.0, float),
            le_longitude_deg=safe_get(getattr(rwy, "le_longitude_deg", None), 0.0, float),
            le_elevation_ft=safe_get(getattr(rwy, "le_elevation_ft", None), 0, int),
            le_heading_degT=safe_get(getattr(rwy, "le_heading_degT", None), 0.0, float),
            le_displaced_threshold_ft=safe_get(getattr(rwy, "le_displaced_threshold_ft", None), 0, int),
            he_ident=safe_get(getattr(rwy, "he_ident", None), "", str),
            he_latitude_deg=safe_get(getattr(rwy, "he_latitude_deg", None), 0.0, float),
            he_longitude_deg=safe_get(getattr(rwy, "he_longitude_deg", None), 0.0, float),
            he_elevation_ft=safe_get(getattr(rwy, "he_elevation_ft", None), 0, int),
            he_heading_degT=safe_get(getattr(rwy, "he_heading_degT", None), 0.0, float),
            he_displaced_threshold_ft=safe_get(getattr(rwy, "he_displaced_threshold_ft", None), 0, int)
        )
        rwys.append(r)
    return rwys

def get_frequencies(ident) -> list[AirportFrequency]:
    freqs: list[AirportFrequency] = []

    if ident in grouped_freqs.groups:
        lcl_freqs = grouped_freqs.get_group(ident)
    else:
        lcl_freqs = pd.DataFrame()

    for freq in lcl_freqs.itertuples(index=False):
        f = AirportFrequency(
            type=safe_get(getattr(freq, "type", None), "", str),
            description=safe_get(getattr(freq, "description", None), "", str),
            frequency_mhz=safe_get(getattr(freq, "frequency_mhz", None), 0.0, float)
        )
        freqs.append(f)
    return freqs

def get_comments(ident) -> list[AirportComment]:
    airport_comments: list[AirportComment] = []

    if ident in grouped_comments.groups:
        lcl_comments = grouped_comments.get_group(ident)
    else:
        lcl_comments = pd.DataFrame()

    for cmt in lcl_comments.itertuples(index=False):
        c= AirportComment(
            id=safe_get(getattr(cmt, "id", None), 0, int),
            thread_ref=safe_get(getattr(cmt, "threadRef", None), 0, int),
            airport_ref=safe_get(getattr(cmt, "airportRef", None), 0, int),
            airport_ident=safe_get(getattr(cmt, "airportIdent", None), "", str),
            date=safe_get(getattr(cmt, "date", None), "", str),
            member_nickname=safe_get(getattr(cmt, "memberNickname", None), "", str),
            subject=safe_get(getattr(cmt, "subject", None), "", str),
            body=safe_get(getattr(cmt, "body", None), "", str)
        )
        airport_comments.append(c)
    return airport_comments


def main() -> None:
    # the following is gonna be some bad spaghetti code but it should do the job we want
    for airport in airports.itertuples(index=False):
        ident = safe_get(getattr(airport, "ident", None), "", str) # icao code

        if not ident:
            continue

        # set up airport object
        airport_obj = Airport(
            id=safe_get(getattr(airport, "id", None), 0, int),
            ident=ident,
            type=safe_get(getattr(airport, "type", None), "", str),
            name=safe_get(getattr(airport, "name", None), "", str),
            latitude_deg=safe_get(getattr(airport, "latitude_deg", None), 0.0, float),
            longitude_deg=safe_get(getattr(airport, "longitude_deg", None), 0.0, float),
            elevation_ft=safe_get(getattr(airport, "elevation_ft", None), 0, int),
            continent=safe_get(getattr(airport, "continent", None), "", str),
            iso_country=safe_get(getattr(airport, "iso_country", None), "", str),
            iso_region=safe_get(getattr(airport, "iso_region", None), "", str),
            municipality=safe_get(getattr(airport, "municipality", None), "", str),
            scheduled_service=safe_get(getattr(airport, "scheduled_service", None), "", str),
            icao_code=safe_get(getattr(airport, "icao_code", None), "", str),
            iata_code=safe_get(getattr(airport, "iata_code", None), "", str),
            gps_code=safe_get(getattr(airport, "gps_code", None), "", str),
            local_code=safe_get(getattr(airport, "local_code", None), "", str),
            home_link=safe_get(getattr(airport, "home_link", None), "", str),
            wikipedia_link=safe_get(getattr(airport, "wikipedia_link", None), "", str),
            keywords=safe_get(getattr(airport, "keywords", None), "", str),
            runways=get_runways(ident),
            frequencies=get_frequencies(ident)
        )

        # todo : do extra processing stuff here for approaches and other stuff
        airport_dict = asdict(airport_obj)
        del airport_dict['comments'] # just get rid of it for now (7/16/26)

        # export
        with open(Path(OUTPUT_DIRECTORY, ident).with_suffix(".json"), "w") as manifest:
            json.dump(airport_dict, manifest, indent=4)

        print(f"exported {ident}!")


if __name__ == "__main__":
    main()

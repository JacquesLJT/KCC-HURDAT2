"""
This file was used to build out the business logic and confirm steps before transitioning into an API.

Can be ignored.
"""

from typing import Any, List

import geopandas as gpd
from pathlib import Path
from entities import Storm, BestTrackEntry

def import_hurricane_data(file_path: str):
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    storms = []
    hurricanes_since_1900 = []
    current_storm = None
    print(f"Importing data from {file_path}...")
    with path.open("r") as file:
        for line in file:
            parts = line.strip().split(",")
            if parts[0].startswith("AL") or parts[0].startswith("EP"):
                current_storm = Storm(
                    basin=parts[0][:2],
                    cyclone_number=int(parts[0][2:4]),
                    year=int(parts[0][4:8]),
                    name=parts[1].strip(),
                    is_hurricane=False,  # Default to False, will update if any entry has status "HU"
                    made_landfall=False,  # Default to False, will update if any storm entry indicates landfall
                    no_best_track_entries=int(parts[2].strip()),
                    best_track_entries=[]
                )
                storms.append(current_storm)
            else:
                if current_storm is not None:

                    if parts[3].strip() == "HU":
                        current_storm.is_hurricane = True
                        if current_storm.year >= 1900 and current_storm not in hurricanes_since_1900:
                            hurricanes_since_1900.append(current_storm)
                    
                    best_track_entry = BestTrackEntry(
                        year=int(parts[0][0:4]),
                        month=int(parts[0][4:6]),
                        day=int(parts[0][6:8]),
                        hour=int(parts[1][0:2]),
                        minute=int(parts[1][2:4]),
                        record_identifier=parts[2].strip(),
                        status=parts[3].strip(),
                        latitude=float(parts[4][:-1]) if parts[4][-1] == "N" else -float(parts[4][:-1]),
                        latitude_hemisphere=parts[4][-1],
                        longitude=float(parts[5][:-1]) if parts[5][-1] == "E" else -float(parts[5][:-1]),
                        longitude_hemisphere=parts[5][-1],
                        max_sustained_wind=int(parts[6].strip()),
                        min_pressure=int(parts[7].strip()),
                        wind_radii_34kt_NE=int(parts[8].strip()),
                        wind_radii_34kt_SE=int(parts[9].strip()),
                        wind_radii_34kt_SW=int(parts[10].strip()),
                        wind_radii_34kt_NW=int(parts[11].strip()),
                        wind_radii_50kt_NE=int(parts[12].strip()),
                        wind_radii_50kt_SE=int(parts[13].strip()),
                        wind_radii_50kt_SW=int(parts[14].strip()),
                        wind_radii_50kt_NW=int(parts[15].strip()),
                        wind_radii_64kt_NE=int(parts[16].strip()),
                        wind_radii_64kt_SE=int(parts[17].strip()),
                        wind_radii_64kt_SW=int(parts[18].strip()),
                        wind_radii_64kt_NW=int(parts[19].strip()),
                        radius_of_maximum_wind=int(parts[20].strip())
                    )
                    current_storm.best_track_entries.append(best_track_entry)
                
    print(f"Successfully imported {len(storms)} storms, but there are only {len(hurricanes_since_1900)} hurricanes since 1900.")

    return storms, hurricanes_since_1900

def import_coastline(file_path: str):
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    states = gpd.read_file(file_path, engine="pyogrio")
    if states.crs is None:
        print("Warning: States shapefile has no CRS. Assuming WGS84 (EPSG:4326).")
        states.set_crs(epsg=4326, inplace=True)

    florida = states[states["NAME"] == "Florida"]
    if florida.empty:
        raise ValueError("Florida not found in the shapefile.")
    
    return florida.union_all()  # Combine all geometries into a single geometry

def find_hurricanes_made_landfall(hurricanes: List[Storm], coastline: Any):
    hurricanes_made_landfall = []
    for hurricane in hurricanes:
        track = hurricane.to_shapely_linestring()
        if track is None:
            continue

        if track.intersects(coastline):
            hurricanes_made_landfall.append(hurricane)

    return hurricanes_made_landfall

def main():
    print("Hello from kcc-hurdat2!")
    storms, hurricanes_since_1900 = import_hurricane_data("data/hurdat2-1851-2025.txt")
    coastline = import_coastline("data/tl_2025_us_state/tl_2025_us_state.shp")
    hurricanes_made_landfall = find_hurricanes_made_landfall(hurricanes_since_1900, coastline)

    print(f"{len(hurricanes_made_landfall)} hurricanes made landfall in Florida since 1900.")
    
    # print(f"{hurricanes_since_1900[-1].to_geojson_linestring()}")

if __name__ == "__main__":
    main()

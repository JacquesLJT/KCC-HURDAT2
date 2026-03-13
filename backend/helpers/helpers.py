import geopandas as gpd
from pathlib import Path
from entities import Storm, BestTrackEntry
from typing import List, Any, Optional
from shapely.geometry import Point, LineString
from geopandas import GeoDataFrame

def load_storm_data(hurdat_file: str, states_shp_file: str) -> tuple[List[Storm], List[Storm], List[Storm], GeoDataFrame]:
    """
    Load storm data from the HURDAT2 file and return lists of all storms, hurricanes since 1900, and hurricanes that made landfall in Florida.
    """
    
    storms, hurricanes_since_1900 = import_hurricane_data(hurdat_file)
    state_geometry = import_shapefile(states_shp_file)
    hurricanes_made_landfall = find_hurricanes_made_landfall(hurricanes_since_1900, state_geometry, state_name="Florida")

    return storms, hurricanes_since_1900, hurricanes_made_landfall, state_geometry

def import_hurricane_data(file_path: str) -> tuple[List[Storm], List[Storm]]:
    """
    Import & parse the storm data from the specified file path, parsing out header/data rows, and building Python objects to store the imported data.
    """

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    storms: List[Storm] = []
    hurricanes_since_1900: List[Storm] = []
    current_storm: Optional[Storm] = None

    with open(file_path, "r") as f:
        for line in f:
            parts = line.strip().split(",")
            if parts[0].startswith("AL") or parts[0].startswith("EP"):  # AL or EP report the basin the storm originated from; AL meaning Atlantic, EP for Eastern Pacific
                current_storm = Storm(  # Initialize a new Storm object
                    id=parts[0],
                    basin=parts[0][:2],
                    cyclone_number=int(parts[0][2:4]),
                    year=int(parts[0][4:8]),
                    name=parts[1].strip(),
                    is_hurricane=False,  # Default to False, will update if any entry has status "HU"
                    made_landfall=False,  # Default to False, will update if any storm entry indicates landfall
                    date_of_landfall="",  # Default to empty string, will update later
                    max_wind_speed=0,  # Default to 0, will update
                    no_best_track_entries=int(parts[2].strip()),
                    best_track_entries=[],
                    polyline=None,
                )
                storms.append(current_storm)
            else:
                if current_storm is not None:
                    if parts[3].strip() == "HU":  # If part[3] contains "HU", this storm is a hurricane
                        current_storm.is_hurricane = True
                        if current_storm.year >= 1900 and current_storm not in hurricanes_since_1900:  # Only interested in hurricanes from 1900 onward
                            hurricanes_since_1900.append(current_storm)

                    current_storm.max_wind_speed = max(current_storm.max_wind_speed, int(parts[6].strip()))
                    
                    best_track_entry = BestTrackEntry(  # Initialize new BestTrackEntry object for each row
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

                    # Build storm polyline as list of (lat, lon)
                    if current_storm.polyline is None:
                        current_storm.polyline = []
                    current_storm.polyline.append((best_track_entry.latitude, best_track_entry.longitude))

    return storms, hurricanes_since_1900

def import_shapefile(file_path: str) -> GeoDataFrame:
    """
    Import the shapefiles for interestion analysis later.
    Used to determine which of the hurricanes made landfall in Florida
    """
    
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    states = gpd.read_file(file_path, engine="pyogrio")
    if states.crs is None:
        print("Warning: States shapefile has no CRS. Assuming WGS84 (EPSG:4326).")
        states.set_crs(epsg=4326, inplace=True)
    
    return states

def find_hurricanes_made_landfall(hurricanes: List[Storm], state_geometry: Any, state_name: Optional[str] = None) -> List[Storm]:
    hurricanes_made_landfall = []
    
    if state_name:  # Allowing state_name to be passed as a parameter so we could use other states even if we're only interested in Florida
        state_geom = state_geometry[state_geometry["NAME"] == state_name]
        if state_geom.empty:
            raise ValueError(f"{state_name} not found in the shapefile.")
        state_geom = state_geom.union_all()  # Combine all geometries into a single geometry
    else:
        state_geom = state_geometry.union_all()  # Combine all geometries into a single geometry
    
    for hurricane in hurricanes:
        hurricane.made_landfall = False
        hurricane.date_of_landfall = ""

        entries = hurricane.best_track_entries
        if not entries:
            continue

        previous_point = None

        for best_track_point in entries:
            current_point = Point(best_track_point.longitude, best_track_point.latitude)  # For each best track point, build a shapely point so we can find if it's in the geometry

            if state_geom.covers(current_point):
                hurricane.made_landfall = True
                hurricane.date_of_landfall = (  # If the point is in the geometry, track the date of landfall
                    f"{best_track_point.month:02d}/{best_track_point.day:02d}/{best_track_point.year}"
                )
                hurricanes_made_landfall.append(hurricane)
                break

            if previous_point is not None:
                segment = LineString([
                    (previous_point.x, previous_point.y),
                    (current_point.x, current_point.y)
                ])

                if segment.intersects(state_geom):  # Some points may not fall within the geometry, but a line segment will cross the geometry
                    hurricane.made_landfall = True
                    hurricane.date_of_landfall = (
                        f"{best_track_point.month:02d}/{best_track_point.day:02d}/{best_track_point.year}"
                    )
                    hurricanes_made_landfall.append(hurricane)
                    break

            previous_point = current_point

    return hurricanes_made_landfall
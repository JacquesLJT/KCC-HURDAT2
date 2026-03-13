from dataclasses import dataclass
from typing import List
from entities.BestTrackEntry import BestTrackEntry
from shapely.geometry import LineString

@dataclass
class Storm:
    id: str
    basin: str
    cyclone_number: int
    year: int
    name: str
    is_hurricane: bool
    made_landfall: bool
    date_of_landfall: str
    max_wind_speed: int
    no_best_track_entries: int
    best_track_entries: List[BestTrackEntry]
    polyline: List[tuple[float, float]] | None

    def to_coordinates(self):
        if self.polyline:
            return self.polyline
        if not self.best_track_entries:
            return None
        return [(entry.latitude, entry.longitude) for entry in self.best_track_entries]
    
    def to_geojson_linestring(self):
        coordinates = self.to_coordinates()
        if coordinates is None:
            return None
        return {
            "type": "LineString",
            "coordinates": [(lon, lat) for lat, lon in coordinates]  # GeoJSON uses (longitude, latitude)
        }
    
    def to_shapely_linestring(self):
        coordinates = self.to_coordinates()
        if coordinates is None:
            return None
        return LineString([(lon, lat) for lat, lon in coordinates])  # Shapely also uses (longitude, latitude)
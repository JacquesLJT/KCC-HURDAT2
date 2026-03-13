from dataclasses import dataclass

@dataclass
class BestTrackEntry:
    year: int
    month: int
    day: int
    hour: int
    minute: int
    record_identifier: str
    status: str
    latitude: float
    latitude_hemisphere: str
    longitude: float
    longitude_hemisphere: str
    max_sustained_wind: int
    min_pressure: int
    wind_radii_34kt_NE: int
    wind_radii_34kt_SE: int
    wind_radii_34kt_SW: int
    wind_radii_34kt_NW: int
    wind_radii_50kt_NE: int
    wind_radii_50kt_SE: int
    wind_radii_50kt_SW: int
    wind_radii_50kt_NW: int
    wind_radii_64kt_NE: int
    wind_radii_64kt_SE: int
    wind_radii_64kt_SW: int
    wind_radii_64kt_NW: int
    radius_of_maximum_wind: int
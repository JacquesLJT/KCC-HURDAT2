import { useMemo, useState } from "react";
import Map from "./Map";

type Storm = {  // Store the required fields from the api response
    id: string | number;
    name: string;
    polyline: [number, number][];
    max_wind_speed: number;
    date_of_landfall: string;
    best_track_entries: [];
};

type GeoJsonGeometry = {
    type: string;
    coordinates: unknown;
};

type GeoJsonFeature = {
    type: "Feature";
    geometry: GeoJsonGeometry;
    properties?: Record<string, unknown>;
};

type GeoJsonFeatureCollection = {
    type: "FeatureCollection";
    features: GeoJsonFeature[];
};

type StormSelectorProps = {
    storms: Storm[];
    stateGeometry? : GeoJsonFeatureCollection | null;
}

export default function StormSelector({ storms, stateGeometry }: StormSelectorProps) {
    const [selectedId, setSelectedId] = useState<string>(
        storms.length > 0 ? String(storms[0].id) : ""
    );

    const selected = useMemo(() => {
        return storms.find((storm) => String(storm.id) === selectedId) ?? storms[0] ?? null;  // Set the selected storm
    }, [storms, selectedId]);

    if (!storms.length || !selected) {
        return <p>No storms available.</p>;
    }

    return (
        <>
            <div id="storm-wrapper">
                <div id="selector-wrapper">
                    <p id="selector-label">Hurricane</p>
                    <select
                        id="storm-selector"
                        value={selectedId}
                        onChange={(e) => setSelectedId(e.target.value)}
                    >
                        {storms.map((storm) => (
                            <option key={String(storm.id)} value={String(storm.id)}>
                                {storm.name} ({storm.id})
                            </option>
                        ))}
                    </select>
                </div>
                <div id="storm-info">
                    <p><span>Max windspeed</span> {selected.max_wind_speed} kt</p>
                    <p><span>Date of landfall</span> {selected.date_of_landfall}</p>
                </div>
            </div>
            <div id="map-wrapper">
                <Map  // Pass the selected storm path, best track points, and state geometry to the map
                    path={selected.polyline ?? []} 
                    bestTrackPoints={selected.best_track_entries}
                    stateGeometry={stateGeometry}
                />
            </div>
        </>
    );
}
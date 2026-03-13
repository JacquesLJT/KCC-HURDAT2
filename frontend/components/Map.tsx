import { useEffect, useRef, useMemo } from "react";
import L from "leaflet"
import "leaflet/dist/leaflet.css"

type BestTrackPoint = {  // Required fields from the best track points that are passed
    year: number,
    month: number,
    day: number,
    hour: number,
    minute: number,
    max_sustained_wind: number,
    min_pressure: number,
}

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

type MapProps = {
    path: [number, number][];
    bestTrackPoints: BestTrackPoint[];
    stateGeometry?: GeoJsonFeatureCollection | null;
}

export default function Map({ path, bestTrackPoints, stateGeometry }: MapProps) {
    const mapRef = useRef<HTMLDivElement | null>(null);
    const polylineRef = useRef<L.Polyline | null>(null);
    const mapInstance = useRef<L.Map | null>(null);
    const markerRef = useRef<L.Marker | null>(null);
    const pointMarkersRef = useRef<L.LayerGroup | null>(null);
    const stateLayerRef = useRef<L.GeoJSON | null>(null);

    const hurricaneIcon = L.divIcon({  // Set up custom spinning hurricane map icon
        html: '<i class="fa-solid fa-hurricane fa-spin fa-spin-reverse fa-3x"></i>',
        className: '',
        iconSize: [45, 36],
        iconAnchor: [22, 18]
    });

    const pointIcon = L.divIcon({  // Set up custom icon for each best track point
        html: '<div style="width:10px;height:10px;border-radius:999px;background:#fff;border:2px solid #0f172a;"></div>',
        className: '',
        iconSize: [14, 14],
        iconAnchor: [7, 7]
    });

    const pointsWithPath = useMemo(() => {
        return path.map((latLng, index) => ({
            latLng,
            point: bestTrackPoints[index]
        })).filter((item) => item.point);
    }, [path, bestTrackPoints]);


    useEffect(() => {  // Sets up the map
        if (!mapRef.current) return;

        const map = L.map(mapRef.current).setView([27.994402, -81.760254], 6);  // Initial view and zoom level

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors",
        }).addTo(map);

        mapInstance.current = map;

        requestAnimationFrame(() => {
            map.invalidateSize();
        });

        return () => {
            stateLayerRef.current = null;
            map.remove();
        };
    }, []);

    useEffect(() => {  // Add in the state geometry overlay
        if (!mapInstance.current) return;

        if (stateLayerRef.current) {
            stateLayerRef.current.remove();
            stateLayerRef.current = null;
        }

        if (!stateGeometry) return;

        stateLayerRef.current = L.geoJSON(stateGeometry as GeoJSON.GeoJsonObject, {
            style: {
                color: "#1d4ed8",
                weight: 2,
                fillColor: "#60a5fa",
                fillOpacity: 0.18,
            }
        }).addTo(mapInstance.current);
    }, [stateGeometry])

    useEffect(() => {  // Add in the hurricane path
        if (!mapInstance.current || path.length === 0) return;

        if (polylineRef.current) {
            polylineRef.current.remove();
        }

        polylineRef.current = L.polyline(path, {
            color: "red",
            weight: 4,
        }).addTo(mapInstance.current);

        mapInstance.current.fitBounds(polylineRef.current.getBounds());  // Resize the bounds of the map to fit the entire storm path
        mapInstance.current.invalidateSize();

        // Create the marker for the storm
        if (!markerRef.current) {
            markerRef.current = L.marker(path[0], { icon: hurricaneIcon }).addTo(mapInstance.current);
        } else {
            markerRef.current.setLatLng(path[0]);
        }

        // Create marker for storm info
        if (pointMarkersRef.current) {
            pointMarkersRef.current.remove();
        }

        pointMarkersRef.current = L.layerGroup(  // custom marker to display import storm info
            pointsWithPath.map(({ latLng, point }) => {
                const pressureText = point.min_pressure ?? "N/A";
                const popupHtml = `
                    <div style="min-width: 160px;">
                        <div><strong>${point.month}/${point.day}/${point.year} ${point.hour}:${point.minute}</strong></div>
                        <div>Wind: ${point.max_sustained_wind} kt</div>
                        <div>Pressure: ${pressureText} mb</div>
                    </div>
                `;

                return L.marker(latLng, { icon: pointIcon }).bindPopup(popupHtml);
            })
        ).addTo(mapInstance.current);


        let i = 0;

        const interval = setInterval(() => {  // Interval moves the hurricane marker along the storm path
            if (!markerRef.current) return;

            markerRef.current.setLatLng(path[i]);
            // const currentPointMarker = pointsWithPath[i];
            // if (currentPointMarker && pointMarkersRef.current) {
            //     pointMarkersRef.current.eachLayer((layer) => {
            //         if (layer instanceof L.Marker) {
            //             layer.closePopup();
            //         }
            //     });
            // }
            i++

            if (i >= path.length) {
                // clearInterval(interval);
                i = 0
            }
        }, 200);

        return () => clearInterval(interval);

    }, [path, pointsWithPath])

    return <div ref={mapRef} style={{ height: "100%", width: "100%" }} />;
}
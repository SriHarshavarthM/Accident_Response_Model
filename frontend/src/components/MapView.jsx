import { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './MapView.css';

// Fix for default marker icons in React-Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Custom icons for different severity levels
const createSeverityIcon = (severity) => {
    const colors = {
        CRITICAL: '#ff006e',
        HIGH: '#ff5c33',
        MEDIUM: '#ffbe0b',
        LOW: '#06d6a0'
    };

    return L.divIcon({
        className: 'custom-marker',
        html: `
      <div class="marker-pin ${severity.toLowerCase()}" style="background-color: ${colors[severity]}">
        <span class="marker-pulse" style="background-color: ${colors[severity]}"></span>
      </div>
    `,
        iconSize: [30, 30],
        iconAnchor: [15, 30],
        popupAnchor: [0, -30]
    });
};

// Demo locations (India)
const DEMO_LOCATIONS = [
    { lat: 28.6139, lng: 77.2090 }, // Delhi
    { lat: 19.0760, lng: 72.8777 }, // Mumbai
    { lat: 13.0827, lng: 80.2707 }, // Chennai
    { lat: 12.9716, lng: 77.5946 }, // Bangalore
];

function MapView({ incidents = [] }) {
    // Default center on India
    const center = [20.5937, 78.9629];
    const zoom = 5;

    // Add demo locations to incidents without coords
    const incidentsWithCoords = incidents.map((inc, idx) => ({
        ...inc,
        lat: inc.lat || DEMO_LOCATIONS[idx % DEMO_LOCATIONS.length].lat,
        lng: inc.lng || DEMO_LOCATIONS[idx % DEMO_LOCATIONS.length].lng
    }));

    return (
        <div className="map-container">
            <MapContainer
                center={center}
                zoom={zoom}
                className="leaflet-map"
                scrollWheelZoom={true}
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                    url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                />

                {incidentsWithCoords.map((incident) => (
                    <Marker
                        key={incident.id}
                        position={[incident.lat, incident.lng]}
                        icon={createSeverityIcon(incident.severity)}
                    >
                        <Popup className="custom-popup">
                            <div className="popup-content">
                                <div className={`popup-severity ${incident.severity.toLowerCase()}`}>
                                    {incident.severity}
                                </div>
                                <h4>{incident.incident_type?.replace(/_/g, ' ')}</h4>
                                <p className="popup-id">{incident.incident_id}</p>
                                <p className="popup-status">Status: {incident.status}</p>
                                <p className="popup-vehicles">Vehicles: {incident.vehicles_involved}</p>
                                <button
                                    className="popup-btn"
                                    onClick={() => window.location.href = `/incident/${incident.id}`}
                                >
                                    View Details
                                </button>
                            </div>
                        </Popup>
                    </Marker>
                ))}
            </MapContainer>
        </div>
    );
}

export default MapView;

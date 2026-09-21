import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Polyline, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Navigation } from 'lucide-react';
import { formatMiles } from '../utils/formatters';

function ChangeView({ bounds }) {
  const map = useMap();
  useEffect(() => {
    if (bounds && bounds.length === 2) {
      map.fitBounds(bounds, { padding: [40, 40], maxZoom: 12 });
    }
  }, [bounds, map]);
  return null;
}

function createMinimalIcon(type) {
  let label = '•';
  let bg = '#0f172a';
  let text = '#ffffff';

  switch (type) {
    case 'origin':
      label = '1';
      bg = '#0f172a';
      break;
    case 'pickup':
      label = '2';
      bg = '#2563eb';
      break;
    case 'dropoff':
      label = '3';
      bg = '#0f172a';
      break;
    case 'fuel':
      label = '⛽';
      bg = '#d97706';
      break;
    case 'break_30m':
      label = '☕';
      bg = '#0284c7';
      break;
    case 'rest_10h':
      label = '🛏️';
      bg = '#4f46e5';
      break;
    default:
      label = '•';
      bg = '#64748b';
  }

  const html = `
    <div style="
      background-color: ${bg};
      color: ${text};
      width: 26px;
      height: 26px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 11px;
      font-weight: 700;
      box-shadow: 0 2px 6px rgba(0,0,0,0.2);
      border: 2px solid #ffffff;
      transform: translate(-13px, -13px);
    ">
      ${label}
    </div>
  `;

  return L.divIcon({
    html: html,
    className: 'minimal-map-marker',
    iconSize: [26, 26],
    iconAnchor: [13, 13],
    popupAnchor: [0, -14]
  });
}

export default function RouteMap({ routeData }) {
  if (!routeData || !routeData.coordinates || routeData.coordinates.length === 0) {
    return (
      <div className="bg-white border border-slate-200 rounded-xl h-[400px] flex items-center justify-center text-slate-400 text-sm">
        <span>Enter trip parameters and calculate route to view map</span>
      </div>
    );
  }

  const defaultCenter = routeData.coordinates[0] || [39.8283, -98.5795];

  return (
    <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
      {/* Map Header */}
      <div className="px-5 py-3.5 bg-white border-b border-slate-200 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Navigation className="w-4 h-4 text-slate-700" />
          <h3 className="text-sm font-semibold text-slate-900">Route Map & Stop Locations</h3>
          <span className="text-xs px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-mono font-medium border border-slate-200">
            {formatMiles(routeData.total_miles)}
          </span>
        </div>

        {/* Minimal Legend */}
        <div className="flex items-center flex-wrap gap-3 text-xs text-slate-600">
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-slate-900 inline-block"></span> 1. Start</span>
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-blue-600 inline-block"></span> 2. Pickup</span>
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-slate-900 inline-block"></span> 3. Dropoff</span>
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-amber-600 inline-block"></span> Fuel</span>
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-sky-600 inline-block"></span> 30m Break</span>
          <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-indigo-600 inline-block"></span> 10h Rest</span>
        </div>
      </div>

      {/* Map */}
      <div className="h-[440px] w-full relative z-0">
        <MapContainer
          center={defaultCenter}
          zoom={5}
          scrollWheelZoom={false}
          className="h-full w-full bg-slate-100"
        >
          <ChangeView bounds={routeData.bounds} />
          
          {/* Crisp Light CartoDB Positron Tiles */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
          />

          {/* Clean Route Polyline */}
          <Polyline
            positions={routeData.coordinates}
            pathOptions={{ color: '#1e3a8a', weight: 4, opacity: 0.85 }}
          />

          {/* Markers */}
          {routeData.markers && routeData.markers.map((marker, idx) => (
            <Marker
              key={idx}
              position={[marker.lat, marker.lng]}
              icon={createMinimalIcon(marker.type)}
            >
              <Popup>
                <div className="text-slate-900 min-w-[160px] py-1">
                  <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                    {marker.label}
                  </div>
                  <div className="text-sm font-semibold text-slate-900 mt-0.5">
                    {marker.city || marker.name}
                  </div>
                  <div className="mt-1.5 text-xs text-slate-600 space-y-0.5">
                    <div>Odometer: {marker.mile} mi</div>
                    {marker.time && <div>Time: {marker.time}</div>}
                    {marker.duration && <div>Duration: {marker.duration}</div>}
                  </div>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>
    </div>
  );
}

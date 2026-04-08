import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default marker icons in React-Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const defaultCenter: [number, number] = [-5.8797, -35.1783]; // RN / Natal bounds approx

export default function RouteMap() {
  const destinations = [
    { id: 1, name: 'Ponta Negra (Natal)', coords: [-5.8797, -35.1783] as [number, number] },
    { id: 2, name: 'Praia da Pipa', coords: [-6.2289, -35.0531] as [number, number] },
    { id: 3, name: 'Tambaú (João Pessoa)', coords: [-7.1147, -34.8219] as [number, number] },
  ];

  return (
    <div className="mb-8">
      <div className="flex justify-between items-end mb-4">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Mapa da Rota</h2>
          <p className="text-gray-500 text-sm">Visão geral do seu trajeto</p>
        </div>
      </div>
      <div className="rounded-[24px] overflow-hidden shadow-sm border border-gray-100 h-[250px] relative z-0">
        <MapContainer center={defaultCenter} zoom={7} scrollWheelZoom={false} style={{ height: '100%', width: '100%' }}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {destinations.map(dest => (
            <Marker key={dest.id} position={dest.coords}>
              <Popup>
                <span className="font-medium">{dest.name}</span>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>
    </div>
  );
}

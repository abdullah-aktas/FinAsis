import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import axios from 'axios';
import 'leaflet/dist/leaflet.css';

const MapView = () => {
  const [cities, setCities] = useState([]);
  const [selectedCity, setSelectedCity] = useState(null);
  const [markets, setMarkets] = useState([]);

  useEffect(() => {
    axios.get('/cities/')
      .then(res => setCities(res.data.cities))
      .catch(err => console.error(err));
  }, []);

  const handleMarkerClick = (city) => {
    setSelectedCity(city);
    axios.get(`/city-markets/${city.id}/`)
      .then(res => setMarkets(res.data.markets))
      .catch(err => setMarkets([]));
  };

  // Varsayılan harita merkezi (örnek: Türkiye)
  const defaultPosition = [39.0, 35.0];

  return (
    <div className="card" style={{ height: '500px', width: '100%' }}>
      <MapContainer center={defaultPosition} zoom={6} style={{ height: '100%', width: '100%', borderRadius: '14px', boxShadow: '0 2px 12px rgba(0,0,0,0.08)' }}>
        <TileLayer
          attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {cities.map(city => (
          <Marker
            key={city.id}
            position={city.coordinates && city.coordinates.x !== undefined ? [city.coordinates.x, city.coordinates.y] : defaultPosition}
            eventHandlers={{
              click: () => handleMarkerClick(city)
            }}
          >
            <Popup>
              <div style={{ minWidth: 180 }}>
                <h4 style={{ marginBottom: 4 }}>{city.name}</h4>
                <p style={{ margin: 0, fontSize: 14 }}>{city.description}</p>
                <p style={{ margin: '8px 0 0 0', fontWeight: 500 }}><b>Pazar Büyüklüğü:</b> {city.market_size}</p>
                {selectedCity && selectedCity.id === city.id && markets.length > 0 && (
                  <div style={{ marginTop: 8 }}>
                    <h5 style={{ fontSize: 15, margin: '8px 0 4px 0' }}>Pazarlar:</h5>
                    <ul style={{ paddingLeft: 18, margin: 0 }}>
                      {markets.map(market => (
                        <li key={market.product_id} style={{ fontSize: 14, marginBottom: 2 }}>
                          <b>{market.product}</b>: Fiyat <b>{market.price}</b>, Arz <b>{market.supply}</b>, Talep <b>{market.demand}</b>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
};

export default MapView; 
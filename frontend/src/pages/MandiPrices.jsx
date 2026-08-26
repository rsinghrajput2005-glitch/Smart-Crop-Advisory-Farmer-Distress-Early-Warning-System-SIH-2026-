import { useState, useEffect } from 'react';
import { Store, MapPin } from 'lucide-react';
import { getMandiData, getFarmerData } from '../services/api';
import { getBestMandi, formatPrice } from '../utils/helpers';
import MandiRow from '../components/MandiRow';
import './MandiPrices.css';

export default function MandiPrices() {
  const [mandis, setMandis] = useState([]);
  const [farmer, setFarmer] = useState(null);

  useEffect(() => {
    Promise.all([getMandiData(), getFarmerData()]).then(([m, f]) => {
      setMandis(m);
      setFarmer(f);
    });
  }, []);

  if (!mandis.length || !farmer) return null;

  const bestMandi = getBestMandi(mandis);
  const sortedMandis = [...mandis].sort((a, b) => b.pricePerQuintal - a.pricePerQuintal);

  return (
    <div className="page-container mandi-page">
      <div className="mandi-header-card">
        <div className="mandi-header-info">
          <h1><Store size={24} style={{ verticalAlign: 'middle', marginRight: 8 }} />Mandi Prices</h1>
          <p>Current {farmer.crop} prices near {farmer.location}</p>
        </div>
        <div className="mandi-header-best">
          <div className="best-label">Best Available Price</div>
          <div className="best-price">{formatPrice(bestMandi.pricePerQuintal)}/q</div>
          <div className="best-mandi"><MapPin size={14} style={{ verticalAlign: 'middle' }} /> {bestMandi.name}</div>
        </div>
      </div>

      <div className="mandi-list-header">
        <h2 className="section-title"><Store size={20} /> Nearby Mandis</h2>
        <span className="mandi-count">{mandis.length} mandis found</span>
      </div>

      {sortedMandis.map(mandi => (
        <MandiRow
          key={mandi.id}
          name={mandi.name}
          distance={mandi.distance}
          pricePerQuintal={mandi.pricePerQuintal}
          isBest={mandi.id === bestMandi.id}
          lastUpdated={mandi.lastUpdated}
          trend={mandi.trend}
        />
      ))}
    </div>
  );
}
